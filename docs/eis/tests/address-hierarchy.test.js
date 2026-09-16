const assert = require("assert");
const fs = require("fs");
const path = require("path");

const hierarchyPath = path.resolve(
    __dirname,
    "../../../masterdata/configuration/addresshierarchy/addresshierarchy.csv"
);

const rows = fs.readFileSync(hierarchyPath, "utf8").trim().split(/\r?\n/);
const regionCodes = new Set();
const provinceCodes = new Set();
const communeCodes = new Set();

rows.forEach((row) => {
    const columns = row.split(",");
    assert.strictEqual(columns.length, 4, `Fila territorial inválida: ${row}`);
    assert.strictEqual(columns[0], "Chile%ISO3166-152");

    const region = columns[1].match(/%REG-(\d{2})$/);
    const province = columns[2].match(/%PROV-(\d{3})$/);
    const commune = columns[3].match(/%COM-(\d{5})$/);
    assert(region && province && commune, `Códigos territoriales inválidos: ${row}`);
    assert.strictEqual(province[1].slice(0, 2), region[1]);
    assert.strictEqual(commune[1].slice(0, 3), province[1]);

    regionCodes.add(region[1]);
    provinceCodes.add(province[1]);
    assert(!communeCodes.has(commune[1]), `Comuna duplicada: ${commune[1]}`);
    communeCodes.add(commune[1]);
});

assert.strictEqual(rows.length, 347);
assert.strictEqual(regionCodes.size, 17);
assert.strictEqual(provinceCodes.size, 57);
assert(communeCodes.has("01101"), "Debe incluir Iquique");
assert(communeCodes.has("13101"), "Debe incluir Santiago");
assert(communeCodes.has("99999"), "Debe incluir valor ignorado EIS");

console.log("Address hierarchy: OK");
