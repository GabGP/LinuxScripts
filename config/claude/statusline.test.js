const { spawnSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const SCRIPT = path.join(__dirname, "statusline.js");
const WIN_1M = 1_000_000;
const COLOR = { NO_COLOR: "" };

function run(input, env = {}) {
  const r = spawnSync("node", [SCRIPT], {
    input,
    env: { ...process.env, NO_COLOR: "1", ...env },
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
  [
    "timer in progress explicit seconds",
    sample({ extra: { timer: { status: "active", duration_ms: 14000 } } }),
    (o) => has(o, "⏱ 14s"),
  ],
  [
    "timer in progress minutes format",
    sample({ extra: { timer: { status: "active", duration_ms: 65000 } } }),
    (o) => has(o, "⏱ 1m05s"),
  ],
  [
    "timer paused explicit seconds",
    sample({ extra: { timer: { status: "paused", duration_ms: 14000 } } }),
    (o) => has(o, "✓ 14s"),
  ],
  [
    "timer paused subsecond shows <1s",
    sample({ extra: { timer: { status: "paused", duration_ms: 300 } } }),
    (o) => has(o, "✓ <1s"),
  ],
  [
    "timer paused hours format",
    sample({ extra: { timer: { status: "paused", duration_ms: 3665000 } } }),
    (o) => has(o, "✓ 1h01m"),
  ],
  [
    "custom timer icons via env vars",
    sample({ extra: { timer: { status: "active", duration_ms: 5000 } } }),
    (o) => has(o, "⏳ 5s"),
    { STATUSLINE_RUNNING_ICON: "⏳" },
  ],
  [
    "custom done icon via env vars",
    sample({ extra: { timer: { status: "paused", duration_ms: 5000 } } }),
    (o) => has(o, "✔ 5s"),
    { STATUSLINE_DONE_ICON: "✔" },
  ],
  ...[
    ["Haiku 5.5", "claude-haiku-5-5", "\x1b[32m"],
    ["Sonnet 5.5", "claude-sonnet-5-5", "\x1b[33m"],
    ["Opus 5.5", "claude-opus-5-5", "\x1b[38;5;208m"],
    ["Fable 5.1", "claude-fable-5-1", "\x1b[31m"],
  ].map(([name, id, code]) => [
    `model color ${name}`,
    sample({ extra: { model: { id, display_name: name }, effort: undefined } }),
    (o) => has(o, `\x1b[1m${code}${name}\x1b[0m`),
    COLOR,
  ]),
  [
    "unknown model has no tier color",
    sample({ extra: { model: { id: "some-model", display_name: "Some Model" }, effort: undefined } }),
    (o) => has(o, "\x1b[1mSome Model\x1b[0m"),
    COLOR,
  ],
  ...[
    ["low", "\x1b[32mlow\x1b[0m"],
    ["medium", "\x1b[33mmedium\x1b[0m"],
    ["high", "\x1b[38;5;208mhigh\x1b[0m"],
    ["xhigh", "\x1b[31mxhigh\x1b[0m"],
    ["max", "\x1b[1;97;41m max \x1b[0m"],
  ].map(([level, colored]) => [
    `effort color ${level}`,
    sample({ extra: { effort: { level } } }),
    (o) => has(o, colored),
    COLOR,
  ]),
  ["unknown effort has no color", sample({ extra: { effort: { level: "turbo" } } }), (o) => has(o, "\x1b[0mturbo\x1b[2;90m"), COLOR],
  ["fast badge follows colored effort", sample({ extra: { effort: { level: "max" }, fast_mode: true } }), (o) => has(o, "\x1b[1;97;41m max \x1b[0m ⚡"), COLOR],
  ["no color keeps max plain", sample({ extra: { effort: { level: "max" } } }), (o) => has(o, "Opus 5.5 · max · ")],
];

let failed = 0;
for (const [name, input, check, extraEnv] of cases) {
  const { stdout, status } = run(input, extraEnv);
  try { check(stdout, status); console.log(`ok ${name}`); }
  catch (e) { failed++; console.log(`FAIL ${name}: ${e.message}`); }
}

// Dynamic prompt lifecycle test (start -> in-progress -> answer returns paused -> next prompt resets)
const lifecycleSession = `claude-lifecycle-${Date.now()}`;
const lifecycleFile = path.join(os.tmpdir(), `claude-timer-${lifecycleSession}.json`);

try {
  // Step 1: User sends prompt (active)
  const step1 = run(JSON.stringify({ agent_state: "running", session_id: lifecycleSession }));
  has(step1.stdout, "⏱ 0s");

  // Step 2: Answer returns (idle -> paused)
  const step2 = run(JSON.stringify({ agent_state: "idle", session_id: lifecycleSession }));
  has(step2.stdout, "✓");

  // Step 3: Stays paused while idle
  const step3 = run(JSON.stringify({ agent_state: "idle", session_id: lifecycleSession }));
  has(step3.stdout, "✓");

  // Step 4: Next prompt starts -> timer resets to 0s
  const step4 = run(JSON.stringify({ agent_state: "running", session_id: lifecycleSession }));
  has(step4.stdout, "⏱ 0s");

  console.log("ok prompt timer dynamic lifecycle transitions");
} catch (e) {
  failed++;
  console.log(`FAIL prompt timer dynamic lifecycle transitions: ${e.message}`);
} finally {
  try { fs.unlinkSync(lifecycleFile); } catch {}
}

process.exit(failed ? 1 : 0);
