const assert = require("assert");
const fs = require("fs");
const path = require("path");

const identifiers = fs.readFileSync(
    path.resolve(
        __dirname,
        "../../../masterdata/configuration/liquibase/eis_patient_identifiers.xml"
    ),
    "utf8"
);

const validatorClass = "org.openmrs.module.eisidentity.validation.RunIdentifierValidator";

assert.match(
    identifiers,
    /eis-patient-identifier-passport-[\s\S]*?<preConditions onFail="MARK_RAN">[\s\S]*?name = 'Pasaporte'/,
    "La migración debe conservar el tipo Pasaporte histórico de HCSBA y sus pacientes"
);
assert.match(
    identifiers,
    /property_value" valueComputed="CONCAT\([\s\S]*?SELECT uuid FROM patient_identifier_type[\s\S]*?name = 'Pasaporte'/,
    "La lista de identificadores adicionales debe reutilizar el UUID real de Pasaporte"
);

assert.match(
    identifiers,
    new RegExp(`<column name="validator" value="${validatorClass.replace(/\./g, "\\.")}"\\s*/>`),
    "El tipo RUN debe activar el validador autoritativo del módulo EIS Identity"
);
assert.match(
    identifiers,
    /<preConditions onFail="HALT">[\s\S]*?<columnExists tableName="patient_identifier_type" columnName="validator"\/>/,
    "La activación debe detenerse si la plataforma no soporta la columna validator"
);
assert.match(
    identifiers,
    /validator IS NULL OR validator = '' OR validator = 'org\.openmrs\.module\.eisidentity\.validation\.RunIdentifierValidator'/,
    "La migración no debe sobrescribir silenciosamente otro validador"
);

console.log("RUN backend validator metadata: OK");
