/* PRS core: PRS = Σ (βi × Gi). Pure functions, shared by the browser and the node test. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.PRS = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  /** Effect-allele dosage (0, 1, 2) from a diploid genotype string such as "AG". */
  function dosageFromGenotype(genotype, effectAllele) {
    if (typeof genotype !== "string" || genotype.length !== 2) {
      throw new Error("genotype must be two alleles, e.g. 'AG'");
    }
    var g = genotype.toUpperCase(), e = String(effectAllele).toUpperCase();
    return (g[0] === e ? 1 : 0) + (g[1] === e ? 1 : 0);
  }

  /**
   * snps: [{ id, beta, dosage }] — dosage may be fractional (imputed), must be within [0, 2].
   * Returns { total, contributions: [{ id, beta, dosage, contribution }] }.
   */
  function compute(snps) {
    var total = 0;
    var contributions = snps.map(function (s) {
      var beta = Number(s.beta), dosage = Number(s.dosage);
      if (!isFinite(beta)) throw new Error(s.id + ": beta must be a number");
      if (!isFinite(dosage) || dosage < 0 || dosage > 2) {
        throw new Error(s.id + ": dosage must be within [0, 2]");
      }
      var c = s.beta * s.dosage;
      total += c;
      return { id: s.id, beta: beta, dosage: dosage, contribution: c };
    });
    return { total: total, contributions: contributions };
  }

  return { compute: compute, dosageFromGenotype: dosageFromGenotype };
});
