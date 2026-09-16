const assert = require("assert");
const fs = require("fs");
const path = require("path");

const liquibasePath = path.resolve(
    __dirname,
    "../../../masterdata/configuration/liquibase"
);

const eisChangeLogs = fs.readdirSync(liquibasePath)
    .filter((name) => /^eis.*\.xml$/i.test(name));

assert.ok(eisChangeLogs.length > 0, "Debe existir al menos un changelog EIS para validar");

const forbidden = [
    /<createTable\b/i,
    /<addColumn\b/i,
    /<createView\b/i,
    /\bCREATE\s+(?:TABLE|VIEW|TRIGGER|PROCEDURE|FUNCTION)\b/i,
    /\bALTER\s+TABLE\b/i
];

for (const name of eisChangeLogs) {
    const content = fs.readFileSync(path.join(liquibasePath, name), "utf8");
    for (const pattern of forbidden) {
        assert.ok(
            !pattern.test(content),
            `${name} contiene DDL EIS propio que debe migrarse a eis_interoperability: ${pattern}`
        );
    }
}

console.log(`EIS schema isolation: OK (${eisChangeLogs.length} changelog)`);
