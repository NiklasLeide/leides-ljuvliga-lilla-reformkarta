#!/usr/bin/env node
// extract.js — identifierar-extraktion för bevakningsautomatiseringen (Sprint 10).
// Läser data/reforms.json, data/uppdrag.json, data/utredningar.json och bygger
// ett runtime-manifest över alla dokumentidentifierare (Prop/SOU/Dir/utrednings-
// beteckningar). Manifestet committas ALDRIG — det beräknas vid varje körning
// (designbeslut: stateless diff, se PROJECT_STATUS Sprint 10).
//
// Endast STRUKTURERADE fält läses: ref, beteckning, prop, direktiv[].nr,
// betankanden[].nr samt kallor[].text (citatetiketter). Fritextfält (kort,
// fulltext, noteringar, what, ...) ingår INTE — träffar får aldrig fabriceras
// ur löptext.
//
// Inga npm-beroenden. Körbar som CLI: `node scripts/bevakning/extract.js [dataDir]`
// skriver manifestet som JSON till stdout. Exporteras även som funktion för T2.

'use strict';

const fs = require('fs');
const path = require('path');

// Normaliserande mönster. Hela strängen (efter trim) måste matcha för fältvärden;
// för citatetiketter (kallor.text) söks mönstren inuti strängen, men fortfarande
// med strikta format så diarienummer (U2025/02427) m.m. inte ger falska träffar.
const PATTERNS = {
  props: /\bProp\.?\s*(\d{4}\/\d{2}:\d+)\b/g,
  sou: /\bSOU\s*(\d{4}:\d+)\b/g,
  dir: /\bDir\.?\s*(\d{4}:\d+)\b/g,
  // Kommittébeteckning: departementsprefix + årtal:löpnummer, t.ex. "U 2023:03",
  // "Fi 2024:05", "S 2025:11". Kräver mellanslag — diarienummer (U2025/02427) matchar inte.
  utredningar: /\b(U|Fi|S|Ju|A|Ku|N|M|Fö|UD)\s+(\d{4}:\d{2})\b/g,
};

function normalize(category, match) {
  switch (category) {
    case 'props': return `Prop. ${match[1]}`;
    case 'sou': return `SOU ${match[1]}`;
    case 'dir': return `Dir. ${match[1]}`;
    case 'utredningar': return `${match[1]} ${match[2]}`;
    default: throw new Error(`Okänd kategori: ${category}`);
  }
}

function readJson(filePath) {
  let raw;
  try {
    raw = fs.readFileSync(filePath, 'utf8');
  } catch (err) {
    throw new Error(`Kunde inte läsa datafil: ${filePath} (${err.message})`);
  }
  try {
    return JSON.parse(raw);
  } catch (err) {
    throw new Error(`Ogiltig JSON i ${filePath}: ${err.message}`);
  }
}

// Manifestbyggare med deduplicering: samma beteckning från flera källor blir
// EN post med alla källreferenser i `referenser`-arrayen.
function createManifest() {
  const buckets = { props: new Map(), sou: new Map(), dir: new Map(), utredningar: new Map() };

  function add(category, id, ref) {
    const bucket = buckets[category];
    if (!bucket.has(id)) bucket.set(id, { id, referenser: [] });
    const entry = bucket.get(id);
    // Undvik exakta dubbletter (samma fil + post + fält)
    const dup = entry.referenser.some(r =>
      r.kalla_fil === ref.kalla_fil && r.kalla_post === ref.kalla_post && r.falt === ref.falt);
    if (!dup) entry.referenser.push(ref);
  }

  // Extrahera alla mönsterträffar ur ett strängvärde
  function scan(value, ref) {
    if (typeof value !== 'string' || !value) return;
    for (const [category, pattern] of Object.entries(PATTERNS)) {
      pattern.lastIndex = 0;
      let m;
      while ((m = pattern.exec(value)) !== null) add(category, normalize(category, m), { ...ref });
    }
  }

  function toJSON() {
    const out = {};
    for (const [category, bucket] of Object.entries(buckets)) {
      out[category] = [...bucket.values()].sort((a, b) => a.id.localeCompare(b.id, 'sv'));
    }
    return out;
  }

  return { scan, toJSON };
}

function extractManifest(dataDir) {
  const dir = dataDir || path.join(__dirname, '..', '..', 'data');
  const reforms = readJson(path.join(dir, 'reforms.json'));
  const uppdrag = readJson(path.join(dir, 'uppdrag.json'));
  const utredningar = readJson(path.join(dir, 'utredningar.json'));

  const manifest = createManifest();

  // --- reforms.json: array av reformer. Strukturerat fält: ref ---
  if (!Array.isArray(reforms)) throw new Error('reforms.json: förväntade en array');
  reforms.forEach(r => {
    manifest.scan(r.ref, {
      kalla_fil: 'reforms.json',
      kalla_post: r.id,
      falt: 'ref',
      registrerad_status: r.status ?? null,
      registrerat_datum: null,
    });
  });

  // --- uppdrag.json: objekt {reformId: uppdrag}. Strukturerat fält: kallor[].text
  // (kort/fulltext är fritext och ingår inte) ---
  if (typeof uppdrag !== 'object' || uppdrag === null || Array.isArray(uppdrag)) {
    throw new Error('uppdrag.json: förväntade ett objekt');
  }
  Object.entries(uppdrag).forEach(([uid, u]) => {
    (u.kallor || []).forEach((k, i) => {
      manifest.scan(k.text, {
        kalla_fil: 'uppdrag.json',
        kalla_post: uid,
        falt: `kallor[${i}].text`,
        registrerad_status: u.typ ?? null,
        registrerat_datum: null,
      });
    });
    (u.relaterade || []).forEach((rel, ri) => {
      (rel.kallor || []).forEach((k, i) => {
        manifest.scan(k.text, {
          kalla_fil: 'uppdrag.json',
          kalla_post: uid,
          falt: `relaterade[${ri}].kallor[${i}].text`,
          registrerad_status: rel.typ ?? null,
          registrerat_datum: null,
        });
      });
    });
  });

  // --- utredningar.json: array. Strukturerade fält: beteckning, prop,
  // direktiv[].nr, betankanden[].nr, kallor[].text ---
  if (!Array.isArray(utredningar)) throw new Error('utredningar.json: förväntade en array');
  utredningar.forEach(u => {
    const base = { kalla_fil: 'utredningar.json', kalla_post: u.id, registrerad_status: u.status ?? null };
    manifest.scan(u.beteckning, { ...base, falt: 'beteckning', registrerat_datum: u.tillsatt ?? null });
    manifest.scan(u.prop, { ...base, falt: 'prop', registrerat_datum: null });
    (u.direktiv || []).forEach((d, i) => {
      manifest.scan(d.nr, { ...base, falt: `direktiv[${i}].nr`, registrerat_datum: d.datum ?? null });
    });
    (u.betankanden || []).forEach((b, i) => {
      manifest.scan(b.nr, { ...base, falt: `betankanden[${i}].nr`, registrerat_datum: b.datum ?? null });
    });
    (u.kallor || []).forEach((k, i) => {
      manifest.scan(k.text, { ...base, falt: `kallor[${i}].text`, registrerat_datum: null });
    });
  });

  return manifest.toJSON();
}

module.exports = { extractManifest, PATTERNS };

// CLI: skriv manifestet till stdout. Valfritt argument: alternativ datakatalog.
if (require.main === module) {
  try {
    const manifest = extractManifest(process.argv[2]);
    process.stdout.write(JSON.stringify(manifest, null, 2) + '\n');
    const counts = Object.entries(manifest).map(([k, v]) => `${k}=${v.length}`).join(' ');
    process.stderr.write(`Manifest: ${counts}\n`);
  } catch (err) {
    console.error('FEL:', err.message);
    process.exit(1);
  }
}
