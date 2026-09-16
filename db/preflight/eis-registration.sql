-- Inventario de sólo lectura previo al registro EIS HCSBA.
-- No devuelve valores de identificadores ni datos demográficos de pacientes.

SELECT DATABASE() AS database_name, @@version AS mysql_version,
       @@character_set_database AS character_set_database,
       @@collation_database AS collation_database;

SELECT property, property_value
FROM global_property
WHERE property IN ('openmrs.version','bahmni.extraPatientIdentifierTypes','layout.name.format')
ORDER BY property;

-- OpenMRS no mantiene un catálogo SQL de módulos estable entre versiones.
-- El estado de eisidentity/idgen/webservices.rest se verifica por REST y logs
-- durante el smoke test, no consultando una tabla openmrs_module opcional.

SELECT patient_identifier_type_id, uuid, name, required, retired, uniqueness_behavior,
       location_behavior, validator
FROM patient_identifier_type
WHERE name IN ('Patient Identifier','RUN','RUN Provisorio','Folio comprobante de parto',
               'Pasaporte','Documento país de origen','Acta de nacimiento país de origen',
               'Identificador provisorio FONASA','IPA','IPE','Ficha clínica local','Otro identificador')
   OR uuid IN ('0286b492-05b1-4bf3-a8ae-8c60dff87f41',
               '5663f9bc-068b-4857-b098-02276b9de9b1',
               'c4a9a5de-c35a-43e2-83f1-fc8fcd3b48c7',
               'a20b6e2f-8cc7-4264-a868-899f59b0c866',
               '823c4762-7d5a-4a8f-b651-5bd4a87a056e')
ORDER BY name;

SELECT pit.name AS identifier_type,
       COUNT(*) AS active_identifiers,
       SUM(pi.identifier LIKE 'RUN*%') AS run_star_prefix,
       SUM(pi.identifier LIKE 'RUT*%') AS rut_star_prefix,
       SUM(pi.identifier LIKE 'HCSBA%') AS hcsba_prefix
FROM patient_identifier pi
JOIN patient_identifier_type pit ON pit.patient_identifier_type_id = pi.identifier_type
WHERE pi.voided = 0
GROUP BY pit.patient_identifier_type_id, pit.name
ORDER BY pit.name;

SELECT uuid, name, format, foreign_key, searchable, retired
FROM person_attribute_type
WHERE name IN ('phoneNumber','fixedPhoneNumber','alternatePhoneNumber','otherPhoneType','email',
               'preferredContactChannel','contactRestrictions','requiresThirdPartySupport','socialName',
               'biologicalSex','genderIdentity','nationality','countryOfOrigin',
               'basicHealthInsurance','healthInsurer')
   OR uuid LIKE '5a754f06-05d8-42f8-a820-%'
ORDER BY name;

SELECT uuid, name, hl7_code, unique_id, retired
FROM concept_reference_source
WHERE name = 'EIS-820' OR uuid = '8a62dfe1-3248-4cf0-a820-000000000820';

SELECT COUNT(*) AS existing_eis_concepts
FROM concept
WHERE uuid LIKE '27d277f1-1f5b-4f9a-a111-820%' OR uuid LIKE 'e820%';

SELECT COUNT(*) AS address_hierarchy_rows FROM address_hierarchy_entry;

-- Ejecutar sólo si el módulo IDGen está instalado y las tablas existen.
SELECT table_name
FROM information_schema.tables
WHERE table_schema = DATABASE() AND table_name LIKE 'idgen%'
ORDER BY table_name;
