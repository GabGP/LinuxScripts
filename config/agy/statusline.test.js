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
    model: { id: "gemini-3.8-flash", display_name: "Gemini 3.8 Flash (High)", effort: "high" },
    agent_state: "thinking",
    fast_mode: true,
    context_window: {
      context_window_size: win,
      total_input_tokens: used,
      total_output_tokens: output,
    },
    cost: { total_cost_usd: 0.12 },
    quota: {
      "gemini-5h": { remaining_fraction: 0.68, reset_in_seconds: 7510 },
      "gemini-weekly": { remaining_fraction: 0.55, reset_in_seconds: 3 * 86400 + 4 * 3600 + 10 },
    },
    vcs: { type: "git" },
    ...extra,
  });
}

function assert(cond, msg) { if (!cond) throw new Error(msg); }
const has = (out, s) => assert(out.includes(s), `expected "${s}" in "${out}"`);
const lacks = (out, s) => assert(!out.includes(s), `unexpected "${s}" in "${out}"`);

const cases = [
  [
    "full agy dual quota buckets and git branch",
    sampleAgy(),
    (o) => {
      has(o, "Gemini 3.8 Flash");
      lacks(o, "(High)");
      has(o, "high ⚡");
      has(o, "143k/1M");
      has(o, "$0.12");
      has(o, "5h 32% ↻2h05m");
      has(o, "7d 45% ↻3d04h");
    },
  ],
  [
    "3p quota buckets for claude model",
    sampleAgy({
      extra: {
        model: { id: "claude-opus-5-5", display_name: "Claude Opus 5.5", effort: "high" },
        quota: {
          "3p-5h": { remaining_fraction: 0.90, reset_in_seconds: 3600 },
          "3p-weekly": { remaining_fraction: 0.70, reset_in_seconds: 86400 * 2 },
        },
      },
    }),
    (o) => {
      has(o, "Claude Opus 5.5");
      has(o, "5h 10% ↻1h00m");
      has(o, "7d 30% ↻2d00h");
    },
  ],
  [
    "single generic quota fallback",
    sampleAgy({
      extra: {
        quota: { used_percentage: 25, reset_in_seconds: 1800 },
      },
    }),
    (o) => has(o, "quota 25% ↻0h30m"),
  ],
  [
    "resets_at timestamp countdown",
    sampleAgy({
      extra: {
        quota: { "gemini-5h": { used_percentage: 20, resets_at: Math.floor(Date.now() / 1000) + 3600 } },
      },
    }),
    (o) => has(o, "5h 20% ↻1h00m"),
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
    "dual rate limits direct object",
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
    sampleAgy({ extra: { agent_state: "idle", fast_mode: false, model: { id: "test", display_name: "test" } } }),
    (o) => { has(o, "idle"); lacks(o, "⚡"); },
  ],
  [
    "effort level fallback when state is missing",
    sampleAgy({ extra: { agent_state: undefined, model: { id: "test", display_name: "test" }, effort: { level: "high" }, fast_mode: false } }),
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
