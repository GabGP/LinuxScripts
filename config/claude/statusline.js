#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");

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
  alert: (s) => (noColor ? s : `\x1b[1;97;41m ${s} \x1b[0m`),
};
const SEP = noColor ? " · " : "\x1b[2;90m · \x1b[0m";

// Cheapest to most expensive: green, yellow, orange, red. `max` gets a red badge.
const MODEL_TIER_COLORS = [["haiku", c.green], ["sonnet", c.yellow], ["opus", c.orange], ["fable", c.red]];
const EFFORT_COLORS = new Map([
  ["low", c.green], ["medium", c.yellow], ["high", c.orange], ["xhigh", c.red], ["max", c.alert],
]);
const plain = (s) => s;

function getModelColor(model) {
  const name = `${model?.id || ""} ${model?.display_name || ""}`.toLowerCase();
  return MODEL_TIER_COLORS.find(([tier]) => name.includes(tier))?.[1] || plain;
}

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

const RUNNING_ICON = process.env.STATUSLINE_RUNNING_ICON || process.env.CLAUDE_TIMER_RUNNING_ICON || "⏱";
const DONE_ICON = process.env.STATUSLINE_DONE_ICON || process.env.CLAUDE_TIMER_DONE_ICON || "✓";

const ACTIVE_AGENT_STATES = new Set([
  "thinking",
  "working",
  "running",
  "tool_use",
  "tool-use",
  "tool_call",
  "executing",
  "busy",
  "active",
  "streaming",
  "generating",
  "prompting",
]);

function isAgentActive(data) {
  if (data.timer?.status === "active") return true;
  if (data.timer?.status === "paused" || data.timer?.status === "done") return false;
  if (data.is_running === true || data.is_streaming === true || data.loading === true) return true;
  const raw = (data.agent_state || data.status || data.state || "").toLowerCase().trim();
  if (!raw) return false;
  if (raw === "idle" || raw === "done" || raw === "none" || raw === "needs-input" || raw === "waiting") {
    return false;
  }
  return (
    ACTIVE_AGENT_STATES.has(raw) ||
    raw.startsWith("tool") ||
    raw.includes("think") ||
    raw.includes("work") ||
    raw.includes("run") ||
    raw.includes("gen")
  );
}

function formatDuration(ms, active) {
  if (ms < 1000) return active ? "0s" : "<1s";
  const secs = active ? Math.floor(ms / 1000) : Math.round(ms / 1000);
  if (secs < 60) return `${secs}s`;
  const mins = Math.floor(secs / 60);
  const remSecs = secs % 60;
  if (mins < 60) return `${mins}m${String(remSecs).padStart(2, "0")}s`;
  const hours = Math.floor(mins / 60);
  const remMins = mins % 60;
  return `${hours}h${String(remMins).padStart(2, "0")}m`;
}

function getTimerStatePath(data, prefix = "claude") {
  if (process.env.STATUSLINE_TIMER_FILE) {
    return process.env.STATUSLINE_TIMER_FILE;
  }
  const sid = data.session_id
    || process.env.CLAUDE_SESSION_ID
    || (process.ppid ? `pid-${process.ppid}` : "")
    || (data.cwd ? Buffer.from(data.cwd).toString("hex").slice(0, 16) : "default");
  const safeSid = String(sid).replace(/[^a-zA-Z0-9_-]/g, "_");
  return path.join(os.tmpdir(), `${prefix}-timer-${safeSid}.json`);
}

function resolveTimer(data, prefix = "claude") {
  if (data.timer && typeof data.timer === "object") {
    const isAct = data.timer.status === "active";
    const dur = data.timer.duration_ms ?? ((data.timer.duration_seconds || 0) * 1000);
    return { active: isAct, durationMs: dur, formatted: formatDuration(dur, isAct) };
  }

  if (!data.agent_state && !data.status && !data.state) {
    return null;
  }

  const timerFile = getTimerStatePath(data, prefix);
  const active = isAgentActive(data);
  const now = Date.now();

  let prev = null;
  try {
    if (fs.existsSync(timerFile)) {
      prev = JSON.parse(fs.readFileSync(timerFile, "utf8"));
    }
  } catch {}

  const isStale = prev && prev.lastUpdate && (now - prev.lastUpdate > 24 * 3600 * 1000);
  if (isStale) prev = null;

  if (active) {
    let startTime;
    if (!prev || prev.status !== "active" || !prev.startTime) {
      startTime = now;
      try {
        fs.writeFileSync(timerFile, JSON.stringify({ status: "active", startTime, durationMs: 0, lastUpdate: now }), "utf8");
      } catch {}
      return { active: true, durationMs: 0, formatted: "0s" };
    } else {
      startTime = prev.startTime;
      const durationMs = Math.max(0, now - startTime);
      try {
        fs.writeFileSync(timerFile, JSON.stringify({ status: "active", startTime, durationMs, lastUpdate: now }), "utf8");
      } catch {}
      return { active: true, durationMs, formatted: formatDuration(durationMs, true) };
    }
  } else {
    if (prev && prev.status === "active") {
      const startTime = prev.startTime || now;
      const durationMs = Math.max(0, now - startTime);
      try {
        fs.writeFileSync(timerFile, JSON.stringify({ status: "paused", durationMs, lastUpdate: now }), "utf8");
      } catch {}
      return { active: false, durationMs, formatted: formatDuration(durationMs, false) };
    } else if (prev && prev.status === "paused") {
      const durationMs = prev.durationMs || 0;
      return { active: false, durationMs, formatted: formatDuration(durationMs, false) };
    } else {
      return null;
    }
  }
}

function formatTimerSegment(timerInfo, c, noColor) {
  if (!timerInfo) return null;
  const { active, formatted } = timerInfo;
  if (active) {
    const text = `${RUNNING_ICON} ${formatted}`;
    return noColor ? text : c.yellow(text);
  } else {
    if (noColor) return `${DONE_ICON} ${formatted}`;
    return `${c.green(DONE_ICON)} ${c.dim(formatted)}`;
  }
}

try {
  const raw = fs.readFileSync(0, "utf8");
  const data = JSON.parse(raw);
  if (!data || typeof data !== "object") throw new Error();
  const segments = [];

  const modelName = data.model?.display_name || data.model?.id;
  if (modelName) segments.push(c.bold(getModelColor(data.model)(modelName)));

  const effort = data.effort?.level;
  const fast = Boolean(data.fast_mode);
  const effortText = effort && (EFFORT_COLORS.get(String(effort).toLowerCase()) || plain)(effort);
  if (effort || fast) segments.push(effort ? (fast ? `${effortText} ⚡` : effortText) : "⚡");

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

  const timer = resolveTimer(data, "claude");
  const timerSegment = formatTimerSegment(timer, c, noColor);
  if (timerSegment) segments.push(timerSegment);

  const fiveHour = formatLimit("5h", data.rate_limits?.five_hour, true);
  if (fiveHour) segments.push(fiveHour);
  const sevenDay = formatLimit("7d", data.rate_limits?.seven_day, true);
  if (sevenDay) segments.push(sevenDay);

  console.log(segments.join(SEP));
} catch {
  console.log("statusline: bad input");
  process.exit(0);
}
