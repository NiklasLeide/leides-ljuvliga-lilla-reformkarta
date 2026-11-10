// amne.js — ämnesregeln för bevakningen (Sprint 15 T5, DEC-020).
// Utredningar och direktiv är kandidater när huvudämnet är skolväsendet, från förskola till komvux,
// OAVSETT departement. Högskola, yrkeshögskola, studiemedel och statsbidragsförordningar spåras inte.
// Används av riksdagen.js (direktiv från andra departement än U-dep) och rss.js (departementsuppdrag
// på regeringen.se). Kandidat ≠ spåras: människan (veckorutinen) avgör.
'use strict';

// Titelord som pekar på skolväsendet. Medvetet brett — hellre en kandidat för mycket än en miss
// (Dir. 2026:105 "allvarliga våldsdåd i skolmiljöer" kom från Justitiedepartementet).
const AMNESORD = /skol|förskol|elev|lärar|läroplan|kursplan|betyg|gymnasie|komvux|vuxenutbildning|fritidshem|undervisning|språkutveckl/i;
// regeringen.se:s policyområden (RSS-kategorier) för skolväsendet.
const AMNE_KATEGORIER = ['Barn- och ungdomsutbildning', 'Utbildning för vuxna'];
// DEC-020: spåras inte.
const EJ_SPARAS = /yrkeshögskol|högskol|universitet|studiemedel|statsbidrag/i;

function arSkolamne({ titel = '', kategorier = [] } = {}) {
  if (EJ_SPARAS.test(titel)) return false;
  return AMNESORD.test(titel) || kategorier.some(k => AMNE_KATEGORIER.includes(k));
}

module.exports = { AMNESORD, AMNE_KATEGORIER, EJ_SPARAS, arSkolamne };
