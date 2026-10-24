// Local shortlist page for logo concepts. No dependencies.
//
//   node picker.mjs DIR [--port 4777] [--name Brand] [--light-bg #F4F5F7] [--light-fg #0E1018]
//                       [--dark-bg #0B0C0F] [--dark-fg #ECEEF2]
//                       [--light-accent #0E9F74] [--dark-accent #3CCB98]
// Parts marked class="accent" (filled) or class="accent-line" (stroked) take the
// accent colours; without the flags they stay currentColor.
//
// Shows every DIR/*.svg (re-read on each page load, so new concepts appear on refresh):
// large on light and dark, in a nav bar next to the brand name, and at 32 and 16 px.
// Marks should draw with currentColor so they pick up each theme's colour.
// Optional DIR/captions.json: { "file.svg": { "title": "...", "idea": "...", "group": "..." } }.
// Stars and the note are saved to DIR/picks.json (latest) and DIR/picks.log (history),
// so the agent can read the user's choice straight from disk.
// Listens on 127.0.0.1 only. Inside a per-command sandbox, run it unsandboxed or the
// browser cannot reach it.
import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const dir = args.find((a) => !a.startsWith("--") && !args[args.indexOf(a) - 1]?.startsWith("--"));
if (!dir) {
  console.error("usage: node picker.mjs DIR [--port 4777] [--name Brand]");
  process.exit(1);
}
const opt = (k, d) => (args.includes(`--${k}`) ? args[args.indexOf(`--${k}`) + 1] : d);
const port = Number(opt("port", "4777"));
const brand = opt("name", "Brand");
const C = {
  lbg: opt("light-bg", "#F4F5F7"), lfg: opt("light-fg", "#0E1018"),
  dbg: opt("dark-bg", "#0B0C0F"), dfg: opt("dark-fg", "#ECEEF2"),
  la: opt("light-accent", ""), da: opt("dark-accent", ""),
};
const accentCss =
  (C.la ? `.l .accent{fill:${C.la}}.l .accent-line{stroke:${C.la}}` : "") +
  (C.da ? `.d .accent{fill:${C.da}}.d .accent-line{stroke:${C.da}}` : "");
const picksPath = path.join(dir, "picks.json");
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

function marks() {
  let caps = {};
  try { caps = JSON.parse(fs.readFileSync(path.join(dir, "captions.json"), "utf8")); } catch {}
  return fs.readdirSync(dir).filter((f) => f.endsWith(".svg")).sort().map((file) => ({
    file,
    svg: fs.readFileSync(path.join(dir, file), "utf8").replace(/<\?xml[^>]*>/, "").replace(/<!DOCTYPE[^>]*>/i, ""),
    title: caps[file]?.title || file.replace(/\.svg$/, ""),
    idea: caps[file]?.idea || "",
    group: caps[file]?.group || "Concepts",
  }));
}

function page() {
  const ms = marks();
  const groups = [...new Set(ms.map((m) => m.group))];
  const card = (m) => `
    <article class="card" data-file="${esc(m.file)}">
      <header><span class="file">${esc(m.file)}</span>
        <button type="button" class="star" aria-pressed="false" aria-label="Star ${esc(m.title)}">☆ Star</button></header>
      <div class="big"><div class="l m">${m.svg}</div><div class="d m">${m.svg}</div></div>
      <h3>${esc(m.title)}</h3>${m.idea ? `<p>${esc(m.idea)}</p>` : ""}
      <div class="nav l"><span class="m s28">${m.svg}</span><b>${esc(brand)}</b><span class="m s32">${m.svg}</span><span class="m s16">${m.svg}</span></div>
      <div class="nav d"><span class="m s28">${m.svg}</span><b>${esc(brand)}</b><span class="m s32">${m.svg}</span><span class="m s16">${m.svg}</span></div>
    </article>`;
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(brand)} logo shortlist</title>
<style>
:root{--lbg:${C.lbg};--lfg:${C.lfg};--dbg:${C.dbg};--dfg:${C.dfg};--line:#e3e5ea;--sub:#5d6371;--ok:#0e9f74}
*{box-sizing:border-box}body{margin:0;background:#fff;color:#14161c;font:14px/1.5 system-ui,sans-serif}
.wrap{max-width:1280px;margin:0 auto;padding:28px 20px 130px;display:grid;gap:26px}
h1{margin:0;font-size:26px;letter-spacing:-.02em}h2{margin:0 0 10px;font-size:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.card{border:1px solid var(--line);border-radius:14px;padding:12px;display:grid;gap:10px;min-width:0}
.card.on{border-color:var(--ok);box-shadow:0 0 0 3px #e3f6ef}
.card header{display:flex;justify-content:space-between;align-items:center}
.file{font:12px ui-monospace,monospace;color:var(--sub);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.star{border:1px solid var(--line);background:#fff;border-radius:99px;padding:3px 11px;cursor:pointer}
.star[aria-pressed=true]{background:#e3f6ef;border-color:var(--ok);color:var(--ok)}
.big{display:grid;grid-template-columns:1fr 1fr;gap:6px}.big .m{aspect-ratio:1;border-radius:10px;padding:18%}
.l{background:var(--lbg);color:var(--lfg)}.d{background:var(--dbg);color:var(--dfg)}
.m svg{width:100%;height:100%;display:block}
h3{margin:0;font-size:15px}.card p{margin:0;color:var(--sub);font-size:13px}
.nav{display:flex;align-items:center;gap:8px;border-radius:9px;padding:8px 10px;font-size:15px}
.nav b{flex:1;letter-spacing:-.01em}.s28{width:28px;height:28px}.s32{width:32px;height:32px}.s16{width:16px;height:16px}
.bar{position:fixed;left:0;right:0;bottom:0;background:#fffffff0;border-top:1px solid var(--line);padding:12px 20px}
.bar div{max-width:1280px;margin:0 auto;display:flex;gap:12px;flex-wrap:wrap;align-items:center}
#picks{flex:1 1 220px;font:13px ui-monospace,monospace}#note{flex:2 1 300px;padding:9px 12px;border:1px solid var(--line);border-radius:9px}
#st{font-size:12px;color:var(--sub)}:focus-visible{outline:2px solid #1f6bff;outline-offset:2px}
${accentCss}
</style></head><body><div class="wrap">
<div><h1>${esc(brand)} logo shortlist</h1><p style="color:var(--sub);margin:4px 0 0">${ms.length} concepts. Star the ones you like, say what to change in the note. Refresh to see new concepts.</p></div>
${groups.map((g) => `<section><h2>${esc(g)}</h2><div class="grid">${ms.filter((m) => m.group === g).map(card).join("")}</div></section>`).join("")}
</div>
<div class="bar"><div><span id="picks">Nothing starred yet</span><input id="note" placeholder="Note, e.g. like 03 but heavier" aria-label="Note"><span id="st"></span></div></div>
<script>
const st=document.getElementById("st"),note=document.getElementById("note"),pk=document.getElementById("picks");let picks=new Set(),t;
function paint(){document.querySelectorAll(".card").forEach(c=>{const on=picks.has(c.dataset.file);c.classList.toggle("on",on);const b=c.querySelector(".star");b.setAttribute("aria-pressed",on);b.textContent=on?"★ Starred":"☆ Star"});pk.textContent=picks.size?[...picks].join("  "):"Nothing starred yet"}
function save(){clearTimeout(t);t=setTimeout(()=>{st.textContent="Saving…";fetch("/api/picks",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({files:[...picks],note:note.value.trim()})}).then(r=>{st.textContent=r.ok?"Saved":"Not saved"}).catch(()=>st.textContent="Server not reachable")},500)}
document.addEventListener("click",e=>{const b=e.target.closest(".star");if(!b)return;const f=b.closest(".card").dataset.file;picks.has(f)?picks.delete(f):picks.add(f);paint();save()});
note.addEventListener("input",save);
fetch("/api/picks").then(r=>r.json()).then(v=>{picks=new Set(v.files||[]);note.value=v.note||"";paint()}).catch(()=>{});
</script></body></html>`;
}

http.createServer((req, res) => {
  if (req.method === "GET" && req.url === "/") {
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" });
    return res.end(page());
  }
  if (req.url === "/api/picks" && req.method === "GET") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(fs.existsSync(picksPath) ? fs.readFileSync(picksPath) : "{}");
  }
  if (req.url === "/api/picks" && req.method === "POST") {
    let raw = "";
    req.on("data", (c) => { raw += c; if (raw.length > 50000) req.destroy(); });
    return req.on("end", () => {
      try {
        const v = JSON.parse(raw);
        const known = new Set(fs.readdirSync(dir));
        const out = {
          files: (Array.isArray(v.files) ? v.files : []).filter((f) => typeof f === "string" && known.has(f)),
          note: typeof v.note === "string" ? v.note.slice(0, 1000) : "",
          updatedAt: new Date().toISOString(),
        };
        fs.writeFileSync(picksPath, JSON.stringify(out, null, 2) + "\n");
        fs.appendFileSync(path.join(dir, "picks.log"), JSON.stringify(out) + "\n");
        res.writeHead(204); res.end();
      } catch { res.writeHead(400); res.end("bad json"); }
    });
  }
  res.writeHead(404); res.end("not found");
}).listen(port, "127.0.0.1", () => console.log(`${brand} logo shortlist on http://localhost:${port}  (dir: ${dir})`));
