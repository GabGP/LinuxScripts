#!/usr/bin/env node
const fs = require("fs");

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
    return Number.isInteger(m) ? `${m}M` : `${m.toFixed(1)}M`;
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

function formatCountdown(resetsAt) {
  if (typeof resetsAt !== "number") return "";
  const mins = Math.round((resetsAt * 1000 - Date.now()) / 60_000);
  if (mins <= 0) return "";
  const hours = Math.floor(mins / 60);
  const text = hours >= 24
    ? `${Math.floor(hours / 24)}d${String(hours % 24).padStart(2, "0")}h`
    : `${hours}h${String(mins % 60).padStart(2, "0")}m`;
  return ` ${c.dim(`↻${text}`)}`;
}

function formatLimit(label, limit, withCountdown) {
  const used = limit?.used_percentage;
  if (typeof used !== "number" || Number.isNaN(used)) return null;
  const pct = Math.round(used);
  const color = pct >= RATE_LIMIT_THRESHOLDS.red ? c.red
    : pct >= RATE_LIMIT_THRESHOLDS.yellow ? c.yellow : (s) => s;
  return color(`${label} ${pct}%`) + (withCountdown ? formatCountdown(limit.resets_at) : "");
}

try {
  const raw = fs.readFileSync(0, "utf8");
  const data = JSON.parse(raw);
  if (!data || typeof data !== "object") throw new Error();
  const segments = [];

  const modelName = data.model?.display_name || data.model?.id;
  if (modelName) segments.push(c.bold(modelName));

  const effort = data.effort?.level;
  const fast = Boolean(data.fast_mode);
  if (effort || fast) segments.push(effort ? (fast ? `${effort} ⚡` : effort) : "⚡");

  const win = data.context_window?.context_window_size || 200_000;
  const winStr = formatTokens(win);
  const usage = data.context_window?.current_usage;
  if (!usage) {
    segments.push(c.dim(`–/${winStr}`));
  } else {
    const used = (usage.input_tokens || 0)
      + (usage.cache_creation_input_tokens || 0)
      + (usage.cache_read_input_tokens || 0);
    const bandTop = win >= LARGE_WINDOW_MIN ? BAND_TOP_LARGE : win;
    const filled = Math.min(4, Math.max(0, Math.ceil((used / bandTop) * 4)));
    const bar = "▮".repeat(filled) + "▯".repeat(4 - filled);
    segments.push(getContextColor(used, win)(`${bar} ${formatTokens(used)}/${winStr}`));
  }

  const cost = data.cost?.total_cost_usd;
  if (typeof cost === "number" && !Number.isNaN(cost)) segments.push(`$${cost.toFixed(2)}`);

  const fiveHour = formatLimit("5h", data.rate_limits?.five_hour, true);
  if (fiveHour) segments.push(fiveHour);
  const sevenDay = formatLimit("7d", data.rate_limits?.seven_day, true);
  if (sevenDay) segments.push(sevenDay);

  console.log(segments.join(SEP));
} catch {
  console.log("statusline: bad input");
  process.exit(0);
}
