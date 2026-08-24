const assert = require("assert");
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const validationPath = path.resolve(
    __dirname,
    "../../../openmrs/apps/registration/fieldValidation.js"
);
const context = {
    Bahmni: { Registration: {} },
    console
};

vm.createContext(context);
vm.runInContext(fs.readFileSync(validationPath, "utf8"), context);

const validator = context.Bahmni.Registration.customValidator.RUN.method;
const normalize = context.Bahmni.Registration.customValidator.RUN.normalize;

[
    "12345678-5",
    "12.345.678-5",
    "5126663-3",
    "6-K",
    "00000006-k"
].forEach((run) => assert.strictEqual(validator("RUN", run), true, `${run} debe ser válido`));

[
    "12.345.678-4",
    "0-0",
    "00.000.000-0",
    "12345678",
    "ABC",
    "12.345.678-X",
    ""
].forEach((run) => {
    const expected = run === "";
    assert.strictEqual(validator("RUN", run), expected, `${run || "vacío"} produjo resultado inesperado`);
});

assert.strictEqual(normalize("12.345.678-5"), "12345678-5");
assert.strictEqual(normalize(" 00000006-k "), "6-K");

console.log("RUN validator: OK");
