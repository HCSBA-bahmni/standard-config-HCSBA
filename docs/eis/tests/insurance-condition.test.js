const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const script = fs.readFileSync(
    path.resolve(__dirname, "../../../openmrs/apps/registration/attributesConditions.js"),
    "utf8"
);
const context = {Bahmni: {Registration: {AttributesConditions: {}}}};
vm.createContext(context);
vm.runInContext(script, context);

const rule = context.Bahmni.Registration.AttributesConditions.rules.basicHealthInsurance;
const isaprePatient = {
    basicHealthInsurance: {conceptUuid: "e8200001-0000-4000-8000-000000000002"}
};
assert.deepStrictEqual(Array.from(rule(isaprePatient).show), ["isapreInstitution"]);

const fonasaPatient = {
    basicHealthInsurance: {conceptUuid: "e8200001-0000-4000-8000-000000000001"},
    healthInsurer: {conceptUuid: "e8200067-0000-4000-8000-000000000067"}
};
const result = rule(fonasaPatient);
assert.deepStrictEqual(Array.from(result.hide), ["isapreInstitution"]);
assert.strictEqual(fonasaPatient.healthInsurer, undefined, "Cambiar desde ISAPRE debe limpiar la aseguradora previa");

console.log("ISAPRE conditional section: OK");
