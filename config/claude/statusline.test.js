const { spawnSync } = require("child_process");
const path = require("path");

const SCRIPT = path.join(__dirname, "statusline.js");
const WIN_1M = 1_000_000;

function run(input) {
  const r = spawnSync("node", [SCRIPT], {
    input,
    env: { ...process.env, NO_COLOR: "1" },
    encoding: "utf-8",
  });
  return { stdout: r.stdout.trim(), status: r.status };
}

function sample({ used = 143_000, win = WIN_1M, output = 0, extra = {} } = {}) {
  return JSON.stringify({
    model: { id: "claude-opus-5-5", display_name: "Opus 5.5" },
    effort: { level: "high" },
    fast_mode: false,
    context_window: {
      context_window_size: win,
      current_usage: { input_tokens: 1000, output_tokens: output, cache_creation_input_tokens: 2000, cache_read_input_tokens: used - 3000 },
    },
    cost: { total_cost_usd: 0.84 },
    rate_limits: {
      five_hour: { used_percentage: 32, resets_at: Math.floor(Date.now() / 1000) + 2 * 3600 + 5 * 60 + 10 },
      seven_day: { used_percentage: 44, resets_at: Math.floor(Date.now() / 1000) + 3 * 86400 + 4 * 3600 + 10 },
    },
    ...extra,
  });
}

function assert(cond, msg) { if (!cond) throw new Error(msg); }
const has = (out, s) => assert(out.includes(s), `expected "${s}" in "${out}"`);
const lacks = (out, s) => assert(!out.includes(s), `unexpected "${s}" in "${out}"`);

const cases = [
  ["full example", sample(), (o) => assert(o === "Opus 5.5 · high · ▮▮▯▯ 143k/1M · $0.84 · 5h 32% ↻2h05m · 7d 44% ↻3d04h", `got "${o}"`)],
  ["past reset hides countdown", sample({ extra: { rate_limits: { five_hour: { used_percentage: 5, resets_at: 1 } } } }), (o) => { has(o, "5h 5%"); lacks(o, "↻"); lacks(o, "7d"); }],
  ["7d under a day shows hours", sample({ extra: { rate_limits: { seven_day: { used_percentage: 90, resets_at: Math.floor(Date.now() / 1000) + 5 * 3600 + 30 * 60 + 10 } } } }), (o) => has(o, "7d 90% ↻5h30m")],
  ["no resets_at", sample({ extra: { rate_limits: { five_hour: { used_percentage: 5 } } } }), (o) => { has(o, "5h 5%"); lacks(o, "↻"); }],
  ...[50, 150, 300, 600].map((k) => [`${k}k on 1M`, sample({ used: k * 1000 }), (o) => has(o, `${k}k/1M`)]),
  ["haiku 200k window", sample({ used: 180_000, win: 200_000 }), (o) => has(o, "180k/200k")],
  ["output tokens excluded", sample({ used: 100_000, output: 200_000 }), (o) => { has(o, "100k/1M"); lacks(o, "300k"); }],
  ["null usage", sample({ extra: { context_window: { context_window_size: WIN_1M, current_usage: null } } }), (o) => has(o, "–/1M")],
  ["no effort, no fast", sample({ extra: { effort: undefined } }), (o) => ["high", "low", "⚡"].forEach((s) => lacks(o, s))],
  ["fast mode", sample({ extra: { fast_mode: true } }), (o) => has(o, "high ⚡")],
  ["no rate limits", sample({ extra: { rate_limits: undefined } }), (o) => { lacks(o, "5h"); lacks(o, "7d"); }],
  ["no cost", sample({ extra: { cost: undefined } }), (o) => lacks(o, "$")],
  ["invalid json", "not valid json {", (o, st) => { has(o, "statusline: bad input"); assert(st === 0, `exit ${st}`); }],
];

let failed = 0;
for (const [name, input, check] of cases) {
  const { stdout, status } = run(input);
  try { check(stdout, status); console.log(`ok ${name}`); }
  catch (e) { failed++; console.log(`FAIL ${name}: ${e.message}`); }
}
process.exit(failed ? 1 : 0);
