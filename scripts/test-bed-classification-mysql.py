"""Real isolated MySQL/Liquibase contract test. Never accepts a remote host or clinical DB.

Requires mysql client, Java, PR19_LIQUIBASE_CLASSPATH and an already running disposable
MySQL instance on 127.0.0.1:13319. All schemas are new pr19_catalog_<run>_* schemas.
No DROP, patient data, or server/service configuration changes are performed.
"""
from pathlib import Path
import datetime,json,os,shutil,subprocess,uuid,xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
mysql=os.environ.get('PR19_MYSQL_CLIENT') or shutil.which('mysql')
classpath=os.environ.get('PR19_LIQUIBASE_CLASSPATH')
if not mysql or not classpath:raise SystemExit('Set PR19_MYSQL_CLIENT and PR19_LIQUIBASE_CLASSPATH; use a disposable local server.')
changelog=root/'masterdata/configuration/liquibase/hcsba_bed_classification.xml'
ns={'l':'http://www.liquibase.org/xml/ns/dbchangelog/1.9'}
master=ET.parse(changelog.with_name('liquibase.xml'))
assert any(el.attrib.get('file')==changelog.name and el.attrib.get('relativeToChangelogFile')=='true' for el in master.getroot()),'Missing master include'
catalog=json.loads((root/'docs/bed-classification-catalog.json').read_text(encoding='utf-8'))['tags']
run=datetime.datetime.now().strftime('%Y%m%d%H%M%S')+uuid.uuid4().hex[:4]
def query(sql,db=None):
    args=[mysql,'--no-defaults','--protocol=TCP','--host=127.0.0.1','--port=13319','--user=root','--default-character-set=utf8mb4','--batch','--raw','--skip-column-names']
    if db:args.append('--database='+db)
    r=subprocess.run(args,input=sql,text=True,encoding='utf-8',capture_output=True)
    if r.returncode:raise RuntimeError(r.stderr)
    return r.stdout.strip()
def setup(suffix,seed=''):
    db='pr19_catalog_'+run+'_'+suffix
    query('CREATE DATABASE `'+db+'` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
    query('''CREATE TABLE users(user_id INT PRIMARY KEY);
INSERT INTO users VALUES(1);
CREATE TABLE bed_tag(bed_tag_id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255) NOT NULL,creator INT NOT NULL,date_created DATETIME NOT NULL,voided BOOLEAN NOT NULL DEFAULT FALSE,uuid CHAR(38) NOT NULL UNIQUE,FOREIGN KEY(creator) REFERENCES users(user_id));
CREATE TABLE global_property(property VARCHAR(255) PRIMARY KEY,property_value TEXT,description TEXT,uuid CHAR(38) NOT NULL UNIQUE);
CREATE TABLE bed_type(bed_type_id INT PRIMARY KEY,name VARCHAR(255),display_name VARCHAR(10));
CREATE TABLE bed_tag_map(bed_tag_map_id INT PRIMARY KEY,bed_id INT NOT NULL,bed_tag_id INT NOT NULL,uuid CHAR(38) UNIQUE,FOREIGN KEY(bed_tag_id) REFERENCES bed_tag(bed_tag_id));
'''+seed,db)
    return db
def apply(db,expected=0):
    args=['java','-cp',classpath,'liquibase.integration.commandline.Main','--driver=com.mysql.cj.jdbc.Driver','--url=jdbc:mysql://127.0.0.1:13319/'+db+'?useSSL=false&allowPublicKeyRetrieval=true','--username=root','--changeLogFile='+changelog.name,'--logLevel=warning','update']
    r=subprocess.run(args,cwd=changelog.parent,text=True,encoding='utf-8',errors='replace',capture_output=True)
    if bool(r.returncode)!=bool(expected):raise AssertionError(r.stdout+'\n'+r.stderr)
    return {'exit':r.returncode,'preconditionRejected': 'precondition' in (r.stdout+r.stderr).lower()} if expected else {'exit':0}
results={'server':query('SELECT VERSION();'),'engine':'MySQL real + Liquibase 4.4.3','schemas':[]}
db=setup('clean');apply(db)
before=query('SELECT * FROM bed_tag ORDER BY bed_tag_id; SELECT * FROM global_property ORDER BY property;',db)
assert query('SELECT COUNT(*) FROM bed_tag;',db)=='12'
assert query('SELECT COUNT(*) FROM global_property;',db)=='14'
assert query('SELECT COUNT(*) FROM DATABASECHANGELOG;',db)=='12'
apply(db)
assert query('SELECT * FROM bed_tag ORDER BY bed_tag_id; SELECT * FROM global_property ORDER BY property;',db)==before
results['schemas'].append({'name':db,'case':'clean installation and repeated update','passed':True})
seed="""INSERT INTO bed_tag VALUES(100,'Clasificación: Adulto',1,'2026-01-01',0,'existing-adult');
INSERT INTO global_property VALUES('hcsba.bedTag.description.existing-adult','Descripción local personalizada','local','existing-property');
INSERT INTO bed_type VALUES(7,'MINSAL_CRITICA_UCI','Crít. UCI');
INSERT INTO bed_tag_map VALUES(200,700,100,'existing-map');"""
db=setup('existing',seed)
preserved=query('SELECT * FROM bed_type; SELECT * FROM bed_tag_map; SELECT * FROM bed_tag WHERE bed_tag_id=100; SELECT * FROM global_property;',db)
apply(db);apply(db)
after=query("SELECT * FROM bed_type; SELECT * FROM bed_tag_map; SELECT * FROM bed_tag WHERE bed_tag_id=100; SELECT * FROM global_property WHERE uuid='existing-property';",db)
assert after==preserved
assert query('SELECT COUNT(*) FROM bed_tag;',db)=='12'
results['schemas'].append({'name':db,'case':'existing UUID, custom description, bed map and legacy type preserved','passed':True})
for suffix,seed in [
 ('duplicate',"INSERT INTO bed_tag VALUES(100,'Clasificación: Adulto',1,NOW(),0,'adult-1'),(101,'Clasificación: Adulto',1,NOW(),0,'adult-2');"),
 ('voided',"INSERT INTO bed_tag VALUES(100,'Clasificación: Adulto',1,NOW(),1,'adult-void');"),
 ('uuidconflict',"INSERT INTO bed_tag VALUES(100,'Otra etiqueta',1,NOW(),0,'"+catalog[0]['uuid']+"');"),
 ('caseconflict',"INSERT INTO bed_tag VALUES(100,'CLASIFICACIÓN: ADULTO',1,NOW(),0,'adult-upper');"),
]:
    db=setup(suffix,seed);before=query('SELECT * FROM bed_tag ORDER BY bed_tag_id;',db)
    rejection=apply(db,expected=1)
    assert rejection['preconditionRejected']
    assert query('SELECT * FROM bed_tag ORDER BY bed_tag_id;',db)==before
    assert query('SELECT COUNT(*) FROM global_property;',db)=='0'
    results['schemas'].append({'name':db,'case':suffix+' rejected before inserting metadata','passed':True})
print(json.dumps(results,indent=2,ensure_ascii=False))
