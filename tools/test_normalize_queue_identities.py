import importlib.util,sqlite3,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('n',Path(__file__).with_name('normalize-queue-identities.py'));n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
class CurrentQueueIdentityTest(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.db.executescript('''CREATE TABLE person(person_id INT,uuid TEXT,voided INT);
   CREATE TABLE person_name(person_name_id INT,person_id INT,given_name TEXT,preferred INT,voided INT);
   CREATE TABLE patient_identifier(patient_identifier_id INT,patient_id INT,identifier_type INT,identifier TEXT,preferred INT,voided INT);
   INSERT INTO person VALUES(1,'current',0),(2,'retired',1),(3,'different-person',0);
   INSERT INTO person_name VALUES(10,1,'Previous',0,0),(20,1,'Current',1,0),(30,3,'Current',1,0);
   INSERT INTO patient_identifier VALUES(10,1,1,'OLD',0,0),(20,1,1,'CURRENT',1,0),(30,1,1,'VOIDED',1,1),(40,1,2,'PASSPORT',0,0),(50,3,1,'OTHER',0,0);''')
  self.sql='SELECT p.uuid,pn.given_name,pi.identifier FROM person p JOIN person_name pn ON pn.person_id=p.person_id JOIN patient_identifier pi ON pi.patient_id=p.person_id WHERE pi.identifier_type=1 ORDER BY p.uuid;'
 def test_current_identifier_and_name_without_deleting_historical_values(self):
  rows=self.db.execute(n.normalize(self.sql)).fetchall()
  self.assertEqual(rows,[('current','Current','CURRENT'),('different-person','Current','OTHER')])
  self.assertEqual(self.db.execute('SELECT count(*) FROM patient_identifier').fetchone()[0],5)
 def test_separation_automatically_restores_two_distinct_cards(self):
  self.db.executescript("UPDATE person SET voided=0 WHERE person_id=2; UPDATE person_name SET person_id=2,preferred=1 WHERE person_name_id=10; UPDATE patient_identifier SET patient_id=2,preferred=1 WHERE patient_identifier_id=10;")
  self.assertEqual(len(self.db.execute(n.normalize(self.sql)).fetchall()),3)
 def test_rank_fallback_is_deterministic_and_per_identifier_type(self):
  self.db.execute('UPDATE patient_identifier SET preferred=0 WHERE patient_id=1')
  rows=self.db.execute(n.normalize(self.sql)).fetchall()
  self.assertEqual(rows[0][2],'OLD')
  sql='SELECT pi.identifier FROM patient_identifier pi WHERE pi.patient_id=1 ORDER BY pi.identifier_type;'
  self.assertEqual(self.db.execute(n.normalize(sql)).fetchall(),[('OLD',),('PASSPORT',)])
 def test_idempotent(self):self.assertEqual(n.normalize(n.normalize(self.sql)),n.normalize(self.sql))
if __name__=='__main__':unittest.main()
