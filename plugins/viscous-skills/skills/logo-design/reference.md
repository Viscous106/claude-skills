# Logo design: research digest

Compiled 2026-10-24 from studio process write-ups, brand guideline pages, rebrand case
studies and existing agent logo skills. Load this when you want the evidence behind the
playbook in `SKILL.md`, or the avoid list for a category. Claims marked [unverified]
came from search snippets, not pages read.

## How studios work

- **Brief first.** Rand on NeXT: "it is needs, not wants, ideas, not type styles which
  determine what its form should be." Logo Geek (Ian Paget) writes a goals list from a
  questionnaire and annotates every presented option against it.
- **Verbal before visual.** Johnson Banks for Mozilla: 5 verbal themes, a personality
  ("Gutsy, Independent, Buoyant, For Good"), a 7-point brief, then routes, each grown
  from one stated idea.
- **Volume.** Paget sketches "hundreds of ideas" over at least a day on paper; Jacob
  Cass filled 6 A3 pages and cut to 2. Chermayeff & Geismar & Haviv settle the idea in
  pencil before touching the computer.
- **Idea grid.** Shumate's 4 sources (corporate activity, ideals, name, abstract) x 3
  mark types (wordmark, lettermark, symbol) = 12 cells; 3 sketches each = 36 ideas.
- **Routes.** 3-5 is the norm (Koto showed 4; Mozilla went 7 → 4 → 3 → 1). Each route
  shown in context mock-ups. Rand's counter-model: one solution with a rationale booklet.
- **Refinement.** Koto: 5 rounds over 24 days. Paget: 4-6 weeks. Pentagram ran
  "hundreds of tests" just to fix Mastercard's 3 colours.

## Craft numbers

- Haviv's criteria: appropriate, distinctive and memorable, simple ("reproduce at any
  pixel size").
- Overshoot: round forms 1-3% past flat lines; Karow suggests 3% for O, 5% for a
  pointed A; pointed apexes need more than rounds.
- Equal visual weight (Material keylines): on a 24 grid, square 18, circle 20; on 192,
  square 152, circle 176, rectangle 176 x 128.
- Squeeze a square about 1% to make it look square (Hoefler & Frere-Jones).
- Horizontals read heavier than verticals: make them thinner. White-on-black reads
  heavier (irradiation): thin the reversed artwork by eye.
- Material icons: one stroke weight (2 dp) for every stroke.
- The golden ratio is mostly myth: the Apple logo fits phi only under a definition "so
  vague as to be worthless" (David Cole). Grids guide; the eye decides.
- Construction from circles is real: Twitter's 2012 bird is three sets of overlapping
  circles (Doug Bowman); every Mastercard letter contains a portion of a circle; Slack's
  mark is two primitives on a grid.
- Recognition: 81% recognised Mastercard's symbol without the name.

## Logo system and files

- Variants: primary lockup, symbol, wordmark (some brands forbid it alone, e.g. GitLab),
  horizontal and stacked, colour, black, white.
- Clear space as a unit of the logo: GitLab 1x the x-height of its "a"; Frappe uses
  icon height X, icon-to-wordmark gap X/4, clear space X/2.
- Minimum size examples: GitLab 20 px, Resend 24 px (16 px in extremes), Mixpanel 24 px,
  Proper Sky symbol 24 px, Polygon lockup 112 px.
- Favicons (Evil Martians, updated Jan 2026): `favicon.ico` 32 (add 16 only if blurry),
  `icon.svg` with an internal `@media (prefers-color-scheme: dark)` block,
  `apple-touch-icon.png` 180 with the logo about 140 px on a solid background,
  `icon-192/512.png`, maskable 512 with content inside the central 409 px circle.
  Link the ICO with `sizes="32x32"` so Chrome prefers the SVG.
- App icon master 1024 x 1024 sRGB, no alpha, no pre-rounded corners [unverified].
  Share image 1200 x 630 [unverified]. Social avatars are cropped to circles.
- Slack cut 11 colours to 4 because 11 "suffered against any background color other
  than white." At most 2 typefaces.

## Wordmarks

- Two routes: fully custom, or a licensed face with reworked letters (Collins set
  Dropbox in Sharp Grotesk; Pentagram set Mastercard in FF Mark and rounded it to echo
  the circles).
- Rand set NeXT in lowercase because "NEXT" reads as "EXIT", and made the "e" the focus.
- Mackey Saturday: sketch the name repeatedly, trace with minimal anchors, compare
  letters against each other. Kern optically; flip the word to judge spacing unread.
- No universal mark-to-wordmark ratio; common practice is mark height 1-2x cap height
  [unverified]. Fix it per lockup.

## Dev-tool and web3 marks: what the best do

| Brand | Mark | Lesson |
|---|---|---|
| Vercel | solid triangle, redrawn with the Geist typeface | mark and type share one geometry; black or white only; accent colour never touches the logo |
| Linear | wordmark primary, symbol "for tight layouts" | the wordmark carries recognition; monochrome preferred; flattened an early gradient sphere |
| Stripe | wordmark (2016); 2025 symbol is one diagonal line from the i-dot | a symbol promoted from a detail of the wordmark |
| GitHub | Invertocat, unchanged since 2008 | no effects or gradients; highest contrast when unsure |
| Resend | wordmark first, R lettermark | clear space half a cap height; minimum 24 px |
| Coinbase (Moniker) | circle with a square cut out | "hundreds of concepts"; had to clear legal review in many countries; "we didn't want people to have to work to get it" |
| Base (Moniker, 2025) | blue square, "the block" | an on-chain idea abstracted to plain geometry; one colour, fixed radius |
| Uniswap | detailed unicorn, 4 size variants | cautionary: community said the micro version "breaks down at 16x16" |
| Phantom (Bakken & Baeck) | ghost | trust through warmth and approachability, not security symbols |
| OpenAI (2025) | blossom refined, wordmark promoted | consolidation; the wordmark now does more of the work |

Patterns: one idea reducible to one glyph; monochrome first with colour kept out of the
mark; the wordmark carries the brand and the symbol is shorthand; mark and typeface
designed together; small sizes designed deliberately; trust shown by restraint and
clarity, not by padlocks; rebrands usually evolve rather than replace.

## Avoid list (owned shapes and clichés)

- Owned: hexagon or isometric box (Chainlink, Arbitrum); soft-cornered solid square
  (Base); one diagonal in a square (Stripe); circle with a square cut out (Coinbase);
  solid triangle (Vercel, Sentry); octahedron or diamond on its own (Ethereum: reads as
  the ETH token); disc cut by diagonals (Linear); lightning bolt (Supabase); three
  interlocking loops (OpenAI); asterisk or starburst (Claude); italic red wordmark
  (Optimism); ghost, fox, unicorn; gradient orb (Zora); circle with a dot (The Graph).
- The git branch-and-merge node icon belongs to Git and GitHub's visual language: the
  obvious trap for any brand with "merge" or "git" in the name.
- Web3 clichés: hexagon networks, node-and-edge meshes, chain links, coins, letters
  struck through with bars, purple-to-blue gradients, 3D and glass, neon on black, cubes.
- AI clichés: sparkles, asterisks, neural meshes, brains, robot heads, glowing orbs,
  rainbow gradients, eyes, chat bubbles.
- Trust clichés: shield with a tick, padlock, seal or rosette, fingerprint, handshake,
  scales.
- Process traps: gradients as a crutch, a mark that only works large, a symbol that
  needs explaining, more than 2 typefaces, uneven kerning, designing to your own taste
  instead of the brief.

## AI and SVG workflows

- Existing skills worth reading: `kaankiziltug/logo-design-skill` (MIT; brief, cliché
  list, 8-12 concepts, black-only 256 viewBox, svg audit and preview-sheet scripts, a
  reference library of about 1,400 logos, a "craft pass"; "Drawing in SVG code is drawing
  blind"); `neonwatty/logo-designer-skill` (MIT; concepts in parallel subagents with
  different creative lenses to break convergence; the author's write-up after 119 SVGs:
  "geometric fidelity and icon legibility are different goals").
  `anthropics/skills` has no logo skill; `canvas-design` names the aesthetic before
  rendering and refines instead of adding.
- Image models: Midjourney for unexpected symbols, Ideogram for lettering; then rebuild
  the chosen direction as clean geometry. Recraft V4 outputs native SVG and has an MCP
  server (`https://mcp.recraft.ai/mcp`); its path-quality claims are unverified.
- Copyright: the US Copyright Office (Part 2 report, Jan 2025) holds purely AI output
  and prompts alone uncopyrightable; human selection, arrangement and modification can
  be protected (Thaler v. Perlmutter). Trademark rights come from use and
  distinctiveness; AI marks risk lookalikes from training data. A platform's "commercial
  use OK" is not clearance.
- Tools: resvg (most spec-faithful renderer, `--query-bbox` for centring), librsvg,
  inkscape CLI (text to path, stroke to path, union), picosvg (strokes and clips to
  plain paths), svgo (preset-default keeps viewBox and title), vtracer and potrace for
  tracing, oxipng for PNGs, `npx realfavicon check` against a running site.
- Checks: size ladder 16-64 px with nearest-neighbour upscale; blur (squint); silhouette;
  reversed weight; mirror and rotate for unintended readings; structure audit; WCAG 3:1
  non-text contrast for logos used as links or icons; shelf test against peers.

## Originality checks

- WIPO Global Brand Database: image upload finds visually similar marks; combine with
  Vienna codes (the free Vienna Classification Assistant suggests them).
- USPTO: no reverse image search; use 6-digit design search codes plus text
  descriptions, and consider marks that sound or mean the same.
- Code searches differ between offices and miss look-alikes; professional clearance adds
  a visual review. Reverse image search (Google Lens, TinEye) as a first pass.

## Sources

Studio process and craft: logogeek.uk (optical corrections, process, idea generation,
mistakes); logodesignlove.com/sagi-haviv-interview; printmag.com interview with
Chermayeff, Geismar and Haviv; paulrand.design (NeXT, 1997); pentagram.com/work/mastercard;
pentagram.com/work/slack; itsnicethat.com (Koto process lecture); johnsonbanks.co.uk
(Mozilla routes and design development); stopdesign.com (Twitter bird, 2012);
core77.com (Apple golden ratio); en.wikipedia.org/wiki/Overshoot_(typography);
myfonts.com (optical illusions in geometric type); m1.material.io/style/icons.html;
design.gitlab.com/brand-logo/core-logo; smashingmagazine.com (10 common mistakes);
justcreative.com (process); digitalsynopsis.com (logotype); uspto.gov (design search
codes); wipo.int (Global Brand Database 2014, Vienna assistant 2020).

Brands: vercel.com/geist/brands; basement.studio (scaling Vercel); linear.app/brand;
brand.github.com/foundations/logo; designcompass.org (Stripe 2025 symbol);
blog.sentry.io/new-logo; resend.com/design/brand/logo; supabase.com/brand-assets;
chain.link/brand-assets; optimism.io/brand; gov.uniswap.org (brand update RFC);
creativereview.co.uk (Coinbase by Moniker; OpenAI refresh); logos-world.net (Base 2025);
ethereum.org/en/assets; polygon.technology/brand-guidelines; thegraph.com/brand;
phantom.com (new brand identity); abduzeedo.com (Anthropic identity);
logotyp.us (crypto and blockchain logos report).

AI and tooling: github.com/anthropics/skills (canvas-design, brand-guidelines);
github.com/kaankiziltug/logo-design-skill (SKILL.md, references/svg-construction.md);
github.com/neonwatty/logo-designer-skill and neonwatty.com/posts/foil-icon-design-claude-code;
github.com/op7418/logo-generator-skill; recraft.ai/docs/mcp-reference;
evilmartians.com (How to Favicon); realfavicongenerator.net (CLI); svgo.dev (preset-default);
github.com/linebender/resvg; github.com/visioncortex/vtracer; github.com/googlefonts/picosvg;
copyrightalliance.org (AI report part 2); ebaqdesign.com (Midjourney logo workflow).
