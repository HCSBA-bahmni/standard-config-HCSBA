const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

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

const validators = context.Bahmni.Registration.customValidator;
const cases = {
    phoneNumber: {
        valid: ["912345678"],
        invalid: ["812345678", "221234567", "+56912345678", "91234567"]
    },
    fixedPhoneNumber: {
        valid: ["221234567", "612345678"],
        invalid: ["712345678", "912345678", "+56221234567", "22123456"]
    },
    alternatePhoneNumber: {
        valid: ["912345678", "221234567", "612345678"],
        invalid: ["712345678", "112345678", "+56912345678", "91234567"]
    }
};

for (const [field, values] of Object.entries(cases)) {
    assert.ok(validators[field], `Falta validador integrado para ${field}`);
    for (const value of values.valid) {
        assert.strictEqual(validators[field].method(field, value), true, `${field} debe aceptar ${value}`);
    }
    for (const value of values.invalid) {
        assert.strictEqual(validators[field].method(field, value), false, `${field} debe rechazar ${value}`);
    }
}

console.log("EIS contact validators: OK");
