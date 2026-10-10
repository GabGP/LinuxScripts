#!/usr/bin/env bash
# Runs one task on Gemini via agy in the current directory, logs the call, prints the
# response plus a footer.
# Usage: gemini.sh [plan|accept-edits] < brief.md   (task on stdin)
set -u
MODEL=gemini-3.8-flash-high
MODE=${1:-plan}
case "$MODE" in plan|accept-edits) ;; *) echo "bad mode: $MODE" >&2; exit 2 ;; esac
PROMPT=$(cat)
[ -n "${PROMPT//[[:space:]]/}" ] || { echo "empty task on stdin" >&2; exit 2; }

LOG="$HOME/.claude/gemini-calls.log"
OUT=$(mktemp)
trap 'rm -f "$OUT"' EXIT

agy -p "$PROMPT" --model "$MODEL" --mode "$MODE" \
  --output-format json --print-timeout 540s >"$OUT" 2>&1 </dev/null
CODE=$?

MODEL="$MODEL" MODE="$MODE" CODE="$CODE" OUT="$OUT" LOG="$LOG" node -e '
const fs = require("fs");
const { MODEL, MODE, CODE, OUT, LOG } = process.env;
const raw = fs.readFileSync(OUT, "utf8");
let r = null;
try { r = JSON.parse(raw.slice(raw.indexOf("{"))); } catch {}
const conv = r?.conversation_id ?? "-";
const status = r?.status ?? `UNPARSED(exit ${CODE})`;
const secs = r?.duration_seconds != null ? r.duration_seconds.toFixed(1) : "-";
const tok = r?.usage?.total_tokens ?? "-";
fs.appendFileSync(LOG, [new Date().toISOString(), MODEL, MODE, status, conv, `${secs}s`, `${tok}tok`, process.cwd()].join("\t") + "\n");
if (!r || status !== "SUCCESS") { console.log(`[gemini call failed: ${status}]\n${raw}`); process.exit(1); }
console.log(`${r.response.trimEnd()}\n\n[${MODEL} · conv ${conv} · ${secs}s · ${tok} tok]`);
'
