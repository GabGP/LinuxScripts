#!/usr/bin/env node
const fs = require("fs");
const { execSync } = require("child_process");

const LARGE_WINDOW_MIN = 1_000_000;
const BAND_TOP_LARGE = 400_000;
const LARGE_THRESHOLDS = { yellow: 100_000, orange: 200_000, red: 400_000 };
const SMALL_THRESHOLDS = { yellow: 0.50, orange: 0.75, red: 0.90 };
const RATE_LIMIT_THRESHOLDS = { yellow: 70, red: 90 };

const noColor = "NO_COLOR" in process.env && process.env.NO_COLOR !== "";
const c = {
  bold: (s) => (noColor ? s : `\x1b[1m${s}\x1b[0m`),
  dim: (s) => (noColor ? s : `\x1b[2m${s}\x1b[0m`),
  green: (s) => (noColor ? s : `\x1b[32m${s}\x1b[0m`),
  yellow: (s) => (noColor ? s : `\x1b[33m${s}\x1b[0m`),
  orange: (s) => (noColor ? s : `\x1b[38;5;208m${s}\x1b[0m`),
  red: (s) => (noColor ? s : `\x1b[31m${s}\x1b[0m`),
};
const SEP = noColor ? " · " : "\x1b[2;90m · \x1b[0m";

function formatTokens(n) {
  if (n >= 1_000_000) {
    const m = n / 1_000_000;
    const rounded = Math.round(m * 10) / 10;
    return Number.isInteger(rounded) ? `${rounded}M` : `${rounded.toFixed(1)}M`;
  }
  if (n >= 1_000) return `${Math.round(n / 1_000)}k`;
  return `${n}`;
}

function getContextColor(used, windowSize) {
  if (windowSize >= LARGE_WINDOW_MIN) {
    if (used < LARGE_THRESHOLDS.yellow) return c.green;
    if (used < LARGE_THRESHOLDS.orange) return c.yellow;
    if (used < LARGE_THRESHOLDS.red) return c.orange;
    return c.red;
  }
  const ratio = used / windowSize;
  if (ratio < SMALL_THRESHOLDS.yellow) return c.green;
  if (ratio < SMALL_THRESHOLDS.orange) return c.yellow;
  if (ratio < SMALL_THRESHOLDS.red) return c.orange;
  return c.red;
}

function formatCountdown(resetsAtOrSeconds) {
  let secs = 0;
  if (typeof resetsAtOrSeconds === "number") {
    secs = resetsAtOrSeconds > 1e9
      ? resetsAtOrSeconds - Math.floor(Date.now() / 1000)
      : resetsAtOrSeconds;
  } else if (typeof resetsAtOrSeconds === "string") {
    const parsed = new Date(resetsAtOrSeconds).getTime();
    if (!Number.isNaN(parsed)) {
      secs = Math.floor((parsed - Date.now()) / 1000);
    }
  }
  if (secs <= 0) return "";
  const mins = Math.round(secs / 60);
  if (mins <= 0) return "";
  const hours = Math.floor(mins / 60);
  const text = hours >= 24
    ? `${Math.floor(hours / 24)}d${String(hours % 24).padStart(2, "0")}h`
    : `${hours}h${String(mins % 60).padStart(2, "0")}m`;
  return ` ${c.dim(`↻${text}`)}`;
}

function formatLimit(label, limit, withCountdown) {
  if (!limit || typeof limit !== "object") return null;
  let used = limit.used_percentage;
  if (typeof used !== "number" && typeof limit.remaining_fraction === "number") {
    used = (1 - limit.remaining_fraction) * 100;
  }
  if (typeof used !== "number" || Number.isNaN(used)) return null;
  const pct = Math.round(used);
  const color = pct >= RATE_LIMIT_THRESHOLDS.red ? c.red
    : pct >= RATE_LIMIT_THRESHOLDS.yellow ? c.yellow : (s) => s;
  const resetVal = limit.reset_in_seconds ?? limit.reset_time ?? limit.resets_at;
  const countdown = withCountdown ? formatCountdown(resetVal) : "";
  return color(`${label} ${pct}%`) + countdown;
}

try {
  const raw = fs.readFileSync(0, "utf8");
  const data = JSON.parse(raw);
  if (!data || typeof data !== "object") throw new Error();
  const segments = [];

  // 1. Model display name (cleaned of redundant effort suffix)
  let modelName = data.model?.display_name || data.model?.id || "";
  const effort = data.model?.effort || data.effort?.level;
  if (effort && modelName.toLowerCase().includes(effort.toLowerCase())) {
    modelName = modelName.replace(/ \([^)]+\)$/, "");
  }
  if (modelName) segments.push(c.bold(modelName));

  // 2. Effort / Agent state indicator
  const state = data.agent_state;
  const fast = Boolean(data.fast_mode);
  const badge = effort || state;
  if (badge || fast) {
    const isWorking = state === "working" || state === "thinking";
    const icon = (fast || isWorking) ? " ⚡" : "";
    segments.push(badge ? `${badge}${icon}` : "⚡");
  }

  // 3. Context window usage meter
  const win = data.context_window?.context_window_size || 1_000_000;
  const winStr = formatTokens(win);
  const ctx = data.context_window;
  const usage = ctx?.current_usage;

  const hasUsage = ctx && (usage !== null && (usage !== undefined || typeof ctx.total_input_tokens === "number"));
  if (!hasUsage || ctx?.current_usage === null) {
    segments.push(c.dim(`–/${winStr}`));
  } else {
    const used = usage
      ? ((usage.input_tokens || 0) + (usage.cache_creation_input_tokens || 0) + (usage.cache_read_input_tokens || 0))
      : (ctx.total_input_tokens ?? 0);
    const bandTop = win >= LARGE_WINDOW_MIN ? BAND_TOP_LARGE : win;
    const filled = Math.min(4, Math.max(0, Math.ceil((used / bandTop) * 4)));
    const bar = "▮".repeat(filled) + "▯".repeat(4 - filled);
    segments.push(getContextColor(used, win)(`${bar} ${formatTokens(used)}/${winStr}`));
  }

  // 4. Session cost (if provided)
  const cost = data.cost?.total_cost_usd;
  if (typeof cost === "number" && !Number.isNaN(cost)) {
    segments.push(`$${cost.toFixed(2)}`);
  }

  // 5. Rate Limits / Quotas (5h and 7d/weekly)
  const is3P = data.model?.id?.toLowerCase().includes("claude");
  const fiveKey = is3P ? "3p-5h" : "gemini-5h";
  const weekKey = is3P ? "3p-weekly" : "gemini-weekly";

  const five = data.rate_limits?.five_hour
    || data.quota?.[fiveKey]
    || data.quota?.["gemini-5h"]
    || data.quota?.["3p-5h"]
    || data.quota?.["5h"];

  const week = data.rate_limits?.seven_day
    || data.quota?.[weekKey]
    || data.quota?.["gemini-weekly"]
    || data.quota?.["3p-weekly"]
    || data.quota?.["weekly"]
    || data.quota?.["7d"];

  if (five) {
    const f = formatLimit("5h", five, true);
    if (f) segments.push(f);
  }
  if (week) {
    const w = formatLimit("7d", week, true);
    if (w) segments.push(w);
  }
  if (!five && !week && data.quota) {
    const q = formatLimit("quota", data.quota, true);
    if (q) segments.push(q);
  }

  // 6. Git Branch (if inside a repo)
  let gitBranch = "";
  if (data.vcs?.type === "git" || data.cwd) {
    try {
      gitBranch = execSync("git rev-parse --abbrev-ref HEAD", {
        cwd: data.cwd || process.cwd(),
        timeout: 300,
        encoding: "utf8",
        stdio: ["pipe", "pipe", "ignore"],
      }).trim();
    } catch {}
  }
  if (gitBranch) {
    segments.push(c.dim(noColor ? gitBranch : ` ${gitBranch}`));
  }

  console.log(segments.join(SEP));
} catch {
  console.log("statusline: bad input");
  process.exit(0);
}
