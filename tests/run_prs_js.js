// Runs the real browser PRS code (assets/js/prs.js) against tests/prs_cases.json.
// Usage: node tests/run_prs_js.js [repoRoot]
const path = require("path");
const fs = require("fs");

const root = process.argv[2] || path.join(__dirname, "..");
const PRS = require(path.join(root, "assets/js/prs.js"));
const data = JSON.parse(fs.readFileSync(path.join(root, "tests/prs_cases.json"), "utf8"));

const failures = [];
for (const c of data.cases) {
  const got = PRS.compute(c.snps).total;
  if (Math.abs(got - c.expected) > 1e-9) failures.push(`${c.name}: expected ${c.expected}, got ${got}`);
}
for (const c of data.invalid) {
  let threw = false;
  try { PRS.compute(c.snps); } catch (e) { threw = true; }
  if (!threw) failures.push(`${c.name}: should have thrown`);
}
for (const g of data.genotype) {
  const got = PRS.dosageFromGenotype(g.genotype, g.effect);
  if (got !== g.dosage) failures.push(`${g.genotype}/${g.effect}: expected ${g.dosage}, got ${got}`);
}

const total = data.cases.length + data.invalid.length + data.genotype.length;
if (failures.length) {
  failures.forEach((f) => console.log("FAIL " + f));
  console.log(`${total - failures.length}/${total} JS PRS checks passed`);
  process.exit(1);
}
console.log(`${total}/${total} JS PRS checks passed`);
