const { spawnSync } = require("child_process");
const path = require("path");

const SCRIPT = path.join(__dirname, "statusline.js");
const WIN_1M = 1_000_000;
const WIN_2M = 2_000_000;

function run(input) {
  const r = spawnSync("node", [SCRIPT], {
    input,
    env: { ...process.env, NO_COLOR: "1" },
    encoding: "utf-8",
  });
  return { stdout: r.stdout.trim(), status: r.status };
}

function sampleAgy({ used = 143_000, win = WIN_1M, output = 1200, extra = {} } = {}) {
  return JSON.stringify({
    model: { id: "gemini-3.8-flash", display_name: "Gemini 3.8 Flash" },
    agent_state: "thinking",
    fast_mode: true,
    context_window: {
      context_window_size: win,
      total_input_tokens: used,
      total_output_tokens: output,
    },
    cost: { total_cost_usd: 0.12 },
    quota: {
      used_percentage: 32,
      reset_in_seconds: 2 * 3600 + 5 * 60 + 10,
    },
    ...extra,
  });
}

function assert(cond, msg) { if (!cond) throw new Error(msg); }
const has = (out, s) => assert(out.includes(s), `expected "${s}" in "${out}"`);
const lacks = (out, s) => assert(!out.includes(s), `unexpected "${s}" in "${out}"`);

const cases = [
  [
    "full agy example",
    sampleAgy(),
    (o) => assert(o === "Gemini 3.8 Flash · thinking ⚡ · ▮▮▯▯ 143k/1M · $0.12 · quota 32% ↻2h05m", `got "${o}"`),
  ],
  [
    "quota remaining_fraction conversion",
    sampleAgy({ extra: { quota: { remaining_fraction: 0.68, reset_in_seconds: 7510 } } }),
    (o) => has(o, "quota 32% ↻2h05m"),
  ],
  [
    "quota multi-day countdown",
    sampleAgy({ extra: { quota: { used_percentage: 45, reset_in_seconds: 3 * 86400 + 4 * 3600 + 10 } } }),
    (o) => has(o, "quota 45% ↻3d04h"),
  ],
  [
    "resets_at timestamp countdown",
    sampleAgy({ extra: { quota: { used_percentage: 20, resets_at: Math.floor(Date.now() / 1000) + 3600 } } }),
    (o) => has(o, "quota 20% ↻1h00m"),
  ],
  [
    "claude-style current_usage fallback",
    sampleAgy({
      extra: {
        context_window: {
          context_window_size: WIN_1M,
          current_usage: { input_tokens: 1000, cache_creation_input_tokens: 2000, cache_read_input_tokens: 140_000 },
        },
      },
    }),
    (o) => has(o, "▮▮▯▯ 143k/1M"),
  ],
  [
    "dual rate limits (5h & 7d)",
    sampleAgy({
      extra: {
        quota: undefined,
        rate_limits: {
          five_hour: { used_percentage: 30, reset_in_seconds: 1800 },
          seven_day: { used_percentage: 60, reset_in_seconds: 86400 },
        },
      },
    }),
    (o) => { has(o, "5h 30% ↻0h30m"); has(o, "7d 60% ↻1d00h"); },
  ],
  [
    "gemini 2M token format",
    sampleAgy({ used: 1_200_000, win: WIN_2M }),
    (o) => has(o, "1.2M/2M"),
  ],
  ...[50, 150, 300, 600].map((k) => [`${k}k on 1M`, sampleAgy({ used: k * 1000 }), (o) => has(o, `${k}k/1M`)]),
  ["haiku/small 200k window", sampleAgy({ used: 180_000, win: 200_000 }), (o) => has(o, "180k/200k")],
  ["output tokens excluded from used meter", sampleAgy({ used: 100_000, output: 200_000 }), (o) => { has(o, "100k/1M"); lacks(o, "300k"); }],
  ["past reset hides countdown", sampleAgy({ extra: { quota: { used_percentage: 5, reset_in_seconds: 0 } } }), (o) => { has(o, "quota 5%"); lacks(o, "↻"); }],
  [
    "idle state without fast mode",
    sampleAgy({ extra: { agent_state: "idle", fast_mode: false } }),
    (o) => { has(o, "idle"); lacks(o, "⚡"); },
  ],
  [
    "effort level fallback when state is missing",
    sampleAgy({ extra: { agent_state: undefined, effort: { level: "high" }, fast_mode: false } }),
    (o) => has(o, "high"),
  ],
  [
    "null context usage",
    sampleAgy({ extra: { context_window: { context_window_size: WIN_1M, current_usage: null } } }),
    (o) => has(o, "–/1M"),
  ],
  [
    "no cost",
    sampleAgy({ extra: { cost: undefined } }),
    (o) => lacks(o, "$"),
  ],
  [
    "invalid json input",
    "bad input json {",
    (o, st) => { has(o, "statusline: bad input"); assert(st === 0, `exit ${st}`); },
  ],
];

let failed = 0;
for (const [name, input, check] of cases) {
  const { stdout, status } = run(input);
  try {
    check(stdout, status);
    console.log(`ok ${name}`);
  } catch (e) {
    failed++;
    console.log(`FAIL ${name}: ${e.message}`);
  }
}
process.exit(failed ? 1 : 0);
