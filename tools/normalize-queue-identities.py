"""Make configured operational queues select one current name/identifier per patient.

Pure SQL transformation, compatible with MySQL 5.7; does not change clinical rows.
Call normalize(sql). Apply reviewed results through OpenMRS systemsetting API.
"""
import re

def current_rows(table):
    if table == 'patient_identifier':
        return '''(SELECT eis_current.* FROM patient_identifier eis_current
 WHERE eis_current.voided=0 AND NOT EXISTS (
  SELECT 1 FROM patient_identifier eis_rank
  WHERE eis_rank.patient_id=eis_current.patient_id
   AND eis_rank.identifier_type=eis_current.identifier_type AND eis_rank.voided=0
   AND ((COALESCE(eis_rank.preferred,0)=1 AND COALESCE(eis_current.preferred,0)=0)
    OR (COALESCE(eis_rank.preferred,0)=COALESCE(eis_current.preferred,0)
     AND eis_rank.patient_identifier_id BETWEEN 0 AND eis_current.patient_identifier_id
     AND eis_rank.patient_identifier_id!=eis_current.patient_identifier_id))))'''
    if table == 'person_name':
        return '''(SELECT eis_current.* FROM person_name eis_current
 WHERE eis_current.voided=0 AND NOT EXISTS (
  SELECT 1 FROM person_name eis_rank WHERE eis_rank.person_id=eis_current.person_id
   AND eis_rank.voided=0
   AND ((COALESCE(eis_rank.preferred,0)=1 AND COALESCE(eis_current.preferred,0)=0)
    OR (COALESCE(eis_rank.preferred,0)=COALESCE(eis_current.preferred,0)
     AND eis_rank.person_name_id BETWEEN 0 AND eis_current.person_name_id
     AND eis_rank.person_name_id!=eis_current.person_name_id))))'''
    return '(SELECT eis_current.* FROM '+table+' eis_current WHERE eis_current.voided=0)'

def normalize(sql):
    if '/* EIS_CURRENT_QUEUE_IDENTITY_V1 */' in sql:return sql
    # Only table references after FROM/JOIN, followed by an explicit alias.
    pattern=r'\b(FROM|JOIN)\s+(patient_identifier|person_name|person|patient)\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\b'
    def replace(match):
        if match[3].upper() in {'ON','WHERE','JOIN','LEFT','RIGHT','INNER','GROUP','ORDER','UNION'}:
            raise ValueError('Unaliased table needs explicit review')
        return match[1]+' '+current_rows(match[2].lower())+' '+match[3]
    result=re.sub(pattern,replace,sql,flags=re.I)
    if result==sql:return sql
    return '/* EIS_CURRENT_QUEUE_IDENTITY_V1 */\n'+result
