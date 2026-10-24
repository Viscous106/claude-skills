// Route showcase: every route in colour treatments and real contexts, as one static page.
//
//   node showcase.mjs ROUTES_DIR [--name Brand] [--tagline "Pay for what you got."] [--out showcase.html] [--mono]
//
// ROUTES_DIR holds one folder per route, each with mark.svg and lockup.svg (optional:
// mark-small.svg used at 16-32 px, wordmark.svg, notes.md whose first paragraph becomes
// the route description). Marks draw with currentColor; the part marked class="accent" /
// "accent-line" takes the treatment's accent colour. Colours default to the Porcelain
// tokens and can be changed in TREATMENTS below. Writes OUT (default ROUTES_DIR/showcase.html),
// which opens straight from disk (file://) and needs no server.
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const dir = args[0];
if (!dir) {
  console.error('usage: node showcase.mjs ROUTES_DIR [--name Brand] [--tagline "..."] [--out file.html]');
  process.exit(1);
}
const opt = (k, d) => (args.includes(`--${k}`) ? args[args.indexOf(`--${k}`) + 1] : d);
const brand = opt("name", "Brand");
const tagline = opt("tagline", "");
const out = opt("out", path.join(dir, "showcase.html"));

const INK = "#0E1018", PORC = "#F4F5F7", NIGHT = "#0B0C0F", MOON = "#ECEEF2";
const MINT = "#0E9F74", MINT_D = "#3CCB98", AZURE = "#1F6BFF";
const TREATMENTS = [
  { name: "Ink", bg: PORC, fg: INK, acc: INK },
  { name: "Ink + mint", bg: PORC, fg: INK, acc: MINT },
  { name: "Night + mint", bg: NIGHT, fg: MOON, acc: MINT_D },
  { name: "Mint", bg: PORC, fg: MINT, acc: MINT },
  { name: "Ink + azure", bg: PORC, fg: INK, acc: AZURE },
  { name: "Azure", bg: PORC, fg: AZURE, acc: AZURE },
  { name: "White on mint", bg: MINT, fg: "#FFFFFF", acc: INK },
  { name: "White on ink", bg: INK, fg: "#FFFFFF", acc: MINT_D },
];

// --mono: no accent colour; the accent part takes the same colour as the rest
// (fill-opacity facets then show as tints of that colour).
if (args.includes("--mono")) {
  const seen = new Set();
  for (const t of TREATMENTS) {
    t.acc = t.fg;
    t.name = t.name.replace(/ \+ (mint|azure)$/, "");
    t.hide = seen.has(t.name);
    seen.add(t.name);
  }
}

const read = (f) => (fs.existsSync(f) ? fs.readFileSync(f, "utf8").replace(/<\?xml[^>]*>/, "") : "");
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const routes = fs.readdirSync(dir).filter((d) => fs.existsSync(path.join(dir, d, "mark.svg"))).sort().map((d) => {
  const p = (f) => path.join(dir, d, f);
  const notes = read(p("notes.md"));
  const para = notes.split(/\n\s*\n/).map((s) => s.trim()).find((s) => s && !s.startsWith("#")) || "";
  return {
    id: d, mark: read(p("mark.svg")), small: read(p("mark-small.svg")) || read(p("mark.svg")),
    lockup: read(p("lockup.svg")) || read(p("mark.svg")), word: read(p("wordmark.svg")),
    title: (notes.match(/^#\s+(.+)$/m) || [, d])[1], desc: para.replace(/\s+/g, " "),
  };
});

const tile = (t, svg, cls = "") =>
  `<div class="t ${cls}" style="--bg:${t.bg};--fg:${t.fg};--acc:${t.acc}">${svg}</div>`;

const section = (r) => `
<section class="route">
  <h2>${esc(r.title)}</h2>${r.desc ? `<p class="desc">${esc(r.desc)}</p>` : ""}
  <h3>Lockup</h3>
  <div class="row lock">${tile(TREATMENTS[1], r.lockup, "wide")}${tile(TREATMENTS[2], r.lockup, "wide")}</div>
  <h3>Colour treatments</h3>
  <div class="row">${TREATMENTS.filter((t) => !t.hide).map((t) => `<figure>${tile(t, r.mark, "sq")}<figcaption>${t.name}</figcaption></figure>`).join("")}</div>
  <h3>In place</h3>
  <div class="ctx">
    <figure><div class="browser light"><div class="tab">${tile(TREATMENTS[1], r.small, "fav")}<span>${esc(brand)} · Dashboard</span></div><div class="tab dim"><span>New tab</span></div></div>
      <div class="browser dark"><div class="tab">${tile(TREATMENTS[2], r.small, "fav")}<span>${esc(brand)} · Dashboard</span></div><div class="tab dim"><span>New tab</span></div></div><figcaption>Browser tab, 16 px</figcaption></figure>
    <figure><div class="nav light">${tile(TREATMENTS[1], r.lockup, "navlock")}<i></i><i></i><i></i><b></b></div>
      <div class="nav dark">${tile(TREATMENTS[2], r.lockup, "navlock")}<i></i><i></i><i></i><b></b></div><figcaption>Dashboard nav</figcaption></figure>
    <figure class="pair">${tile(TREATMENTS[7], r.mark, "avatar")}${tile(TREATMENTS[1], r.mark, "avatar")}<figcaption>GitHub avatar (circle crop)</figcaption></figure>
    <figure class="pair">${tile(TREATMENTS[7], r.mark, "app")}${tile(TREATMENTS[6], r.mark, "app")}<figcaption>App icon</figcaption></figure>
    <figure><div class="social" style="--bg:${PORC}">${tile(TREATMENTS[1], r.lockup, "soclock")}${tagline ? `<p>${esc(tagline)}</p>` : ""}</div><figcaption>Social share card (1200 x 630, scaled)</figcaption></figure>
    <figure><div class="ladder">${[16, 24, 32, 48, 64].map((s) => `<div style="width:${s}px;height:${s}px">${tile(TREATMENTS[1], s <= 32 ? r.small : r.mark, "lad")}</div>`).join("")}</div><figcaption>16 · 24 · 32 · 48 · 64 px</figcaption></figure>
  </div>
</section>`;

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(brand)} logo routes</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600&display=swap">
<style>
*{box-sizing:border-box}body{margin:0;background:#fff;color:${INK};font:14px/1.5 Onest,system-ui,sans-serif}
main{max-width:1240px;margin:0 auto;padding:32px 20px 80px;display:grid;gap:56px}
h1{margin:0;font-size:28px;letter-spacing:-.02em}h2{margin:0;font-size:22px;letter-spacing:-.01em}
h3{margin:22px 0 10px;font-size:13px;font-weight:500;color:#5d6371}.desc{margin:6px 0 0;max-width:70ch;color:#3b404c}
.route{border-top:1px solid #e3e5ea;padding-top:28px}
.t{background:var(--bg);color:var(--fg);display:grid;place-items:center}.t svg{width:100%;height:100%;display:block}
.t .accent{fill:var(--acc)}.t .accent-line{stroke:var(--acc)}
.row{display:flex;flex-wrap:wrap;gap:10px}.row figure{margin:0;width:112px}
.sq{width:112px;height:112px;border-radius:14px;padding:22px;box-shadow:inset 0 0 0 1px #0000000f}
figcaption{font-size:12px;color:#5d6371;margin-top:6px}
.lock .wide{flex:1 1 380px;height:120px;border-radius:14px;padding:26px 40px}
.ctx{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:22px}.ctx figure{margin:0}
.browser{display:flex;gap:2px;padding:8px 8px 0;border-radius:10px 10px 0 0;margin-bottom:6px}
.browser.light{background:#dfe1e6}.browser.dark{background:#202227}
.tab{display:flex;align-items:center;gap:8px;padding:8px 12px;border-radius:8px 8px 0 0;font-size:12px;min-width:0}
.light .tab{background:#fff;color:#1d1f24}.dark .tab{background:#35373d;color:#e8e9ec}.tab.dim{background:transparent!important;opacity:.6}
.fav{width:16px;height:16px;background:transparent!important}
.nav{display:flex;align-items:center;gap:10px;height:52px;padding:0 14px;border-radius:12px;margin-bottom:6px}
.nav.light{background:#fff;box-shadow:inset 0 0 0 1px #e6e8ec}.nav.dark{background:#121317;box-shadow:inset 0 0 0 1px #23262d}
.navlock{height:26px;width:auto;flex:0 0 auto;background:transparent!important}.navlock svg{height:26px;width:auto}
.nav i{display:block;width:54px;height:12px;border-radius:99px;background:currentColor;opacity:.12}.nav.light i{color:${INK}}.nav.dark i{color:${MOON}}
.nav b{margin-left:auto;width:28px;height:28px;border-radius:50%;background:#fde8c8}
.pair{display:flex;flex-wrap:wrap;gap:12px;align-items:center}.pair figcaption{width:100%}
.avatar{width:96px;height:96px;border-radius:50%;padding:20px;box-shadow:inset 0 0 0 1px #0000000f}
.app{width:96px;height:96px;border-radius:22px;padding:20px;box-shadow:inset 0 0 0 1px #0000000f}
.social{background:var(--bg);aspect-ratio:1200/630;border-radius:12px;display:grid;place-items:center;align-content:center;gap:10px;box-shadow:inset 0 0 0 1px #e6e8ec}
.soclock{height:54px;background:transparent!important}.soclock svg{height:54px;width:auto}.social p{margin:0;font-size:15px;color:#3b404c}
.ladder{display:flex;align-items:end;gap:14px;padding:14px;border-radius:12px;background:${PORC}}.lad{width:100%;height:100%;background:transparent!important}
</style></head><body><main>
<header><h1>${esc(brand)} logo routes</h1><p class="desc">${routes.length} route${routes.length === 1 ? "" : "s"}, each in eight colour treatments and in the places the logo will live. Generated from the route folders; regenerate after any change.</p></header>
${routes.map(section).join("")}
</main></body></html>`;

fs.writeFileSync(out, html);
console.log(`wrote ${out} (${routes.length} routes)`);
