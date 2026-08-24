const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "../../..");
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");
const json = (relativePath) => JSON.parse(read(relativePath));

const classic = json("openmrs/apps/registration/app.json");
const v2 = json("openmrs/apps/registration/v2/app.json");
const sources = read("masterdata/configuration/idgen/identifierSource.csv");
const attributes = read("masterdata/configuration/personattributetypes/personAttributeTypes.csv");
const liquibase = read("masterdata/configuration/liquibase/liquibase.xml");

assert.match(sources, /,Patient Identifier,RUT\*,[^\r\n]*,RUT\*,/, "La fuente histórica RUT* debe conservarse");
assert.match(sources, /ed8eead4-146b-4548-84ea-cb897ff82d6e,[^\r\n]*,HCSBA,/, "Debe existir una fuente institucional HCSBA independiente");
assert.strictEqual(classic.config.defaultIdentifierPrefix, "HCSBA");
assert.strictEqual(v2.patientInformation.defaultIdentifierPrefix, "HCSBA");
assert.strictEqual(classic.config.showEnterID, false);

assert.strictEqual(classic.config.showSecondLastName, true);
assert.deepStrictEqual(classic.config.patientNameDisplayOrder, ["firstName", "middleName", "lastName", "secondLastName"]);

assert.deepStrictEqual(classic.config.mandatoryPersonAttributes, [
  "biologicalSex",
  "genderIdentity",
  "nationality",
  "countryOfOrigin",
  "basicHealthInsurance"
]);

const metadata = classic.config.identifierMetadata;
assert.strictEqual(metadata.RUN.typeCode, "1");
assert.strictEqual(metadata["Folio comprobante de parto"].typeCode, "3");
assert.strictEqual(metadata.Pasaporte.typeCode, "4");
assert.strictEqual(metadata["Documento país de origen"].typeCode, "5");
assert.strictEqual(metadata["Acta de nacimiento país de origen"].typeCode, "BAH-AN");
assert.strictEqual(metadata["Otro identificador"].typeCode, "BAH-OTR");

for (const name of classic.config.mandatoryPersonAttributes.concat(["socialName", "healthInsurer", "fixedPhoneNumber", "email"])) {
  assert.ok(attributes.includes(`,${name},`), `Falta el atributo de persona ${name}`);
}

assert.strictEqual(classic.config.addressHierarchy.showAddressFieldsTopDown, true);
assert.strictEqual(classic.config.addressHierarchy.strictAutocompleteFromLevel, "cityVillage");
assert.match(liquibase, /eis_patient_identifiers\.xml/);
assert.match(liquibase, /eis_registration_contact_order\.xml/);

for (const relativePath of [
  "masterdata/configuration/concepts/eisDemographics.csv",
  "masterdata/configuration/concepts/eisContact.csv",
  "masterdata/configuration/concepts/eisHealthInsurers.csv"
]) {
  assert.ok(read(relativePath).split(/\r?\n/).length > 2, `${relativePath} no contiene catálogo`);
}

console.log("HCSBA EIS registration configuration: OK");
