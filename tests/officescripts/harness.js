// Draait een gecompileerd Office Script tegen een nagebootste werkmap (alleen de API die de scripts gebruiken).
// Gebruik: node harness.js script.js invoer.json uitvoer.json
const fs = require("fs");
const vm = require("vm");
const [, , scriptPad, invoerPad, uitvoerPad] = process.argv;
const bladen = JSON.parse(fs.readFileSync(invoerPad, "utf8"));
const actief = { naam: null };
const logs = [];

function maakBlad(naam) {
  const cellen = bladen[naam];
  const breedte = () => Math.max(0, ...cellen.map((r) => r.length));
  const lees = (r, c) => (cellen[r] && cellen[r][c] !== undefined ? cellen[r][c] : "");
  const bereik = (r0, c0, nr, nc) => ({
    getRowIndex: () => r0, getColumnIndex: () => c0, getRowCount: () => nr, getColumnCount: () => nc,
    getValues: () => Array.from({ length: nr }, (_, i) => Array.from({ length: nc }, (_, j) => lees(r0 + i, c0 + j))),
    setValues: (w) => {
      if (w.length !== nr || w.some((rij) => rij.length !== nc)) throw new Error(`setValues: afmeting past niet op ${naam}`);
      w.forEach((rij, i) => rij.forEach((v, j) => {
        if (typeof v !== "string" && typeof v !== "number" && typeof v !== "boolean") throw new Error(`ongeldige waarde ${v}`);
        while (cellen.length <= r0 + i) cellen.push([]);
        cellen[r0 + i][c0 + j] = v;
      }));
    },
    clear: () => { for (let i = r0; i < r0 + nr; i++) for (let j = c0; j < c0 + nc; j++) if (cellen[i]) cellen[i][j] = ""; },
    setNumberFormat: (f) => { if (typeof f !== "string") throw new Error("setNumberFormat"); },
    getFormat: () => ({ autofitColumns: () => {}, getFont: () => ({ setBold: () => {} }) }),
  });
  return {
    getName: () => naam,
    activate: () => { actief.naam = naam; },
    getRangeByIndexes: (r, c, nr, nc) => {
      if (nr < 1 || nc < 1) throw new Error("lege range");
      return bereik(r, c, nr, nc);
    },
    getUsedRange: () => {
      let r0 = Infinity, c0 = Infinity, r1 = -1, c1 = -1;
      cellen.forEach((rij, i) => rij.forEach((v, j) => {
        if (v !== "" && v !== undefined && v !== null) { r0 = Math.min(r0, i); c0 = Math.min(c0, j); r1 = Math.max(r1, i); c1 = Math.max(c1, j); }
      }));
      return r1 < 0 ? undefined : bereik(r0, c0, r1 - r0 + 1, c1 - c0 + 1);
    },
    _breedte: breedte,
  };
}

const werkmap = {
  getWorksheet: (naam) => (naam in bladen ? maakBlad(naam) : undefined),
  addWorksheet: (naam) => { if (naam in bladen) throw new Error("bestaat al"); bladen[naam] = []; return maakBlad(naam); },
};
const context = vm.createContext({ console: { log: (...a) => logs.push(a.join(" ")) }, ExcelScript: { ClearApplyTo: { contents: "Contents" } } });
vm.runInContext(fs.readFileSync(scriptPad, "utf8") + "\nmain(__werkmap);", Object.assign(context, { __werkmap: werkmap }));
fs.writeFileSync(uitvoerPad, JSON.stringify({ bladen, actief: actief.naam, logs }));
