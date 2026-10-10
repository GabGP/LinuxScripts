---
name: gemini-worker
description: Runs a task on Gemini 3.8 Flash (High) through the agy CLI as a background shell command. Use when the user asks for Gemini, Gemini workers, or a second opinion from a non-Claude model.
---

# Gemini worker

Gemini runs as a plain background command. Do not spawn a subagent for it: a model in the
middle retypes the brief and rewrites the report. Needs `agy` and `node` on the PATH.

## Launch

1. Write the brief to a file that git will not pick up: a gitignored folder of the project,
   or the session scratchpad. The file reaches Gemini byte for byte, so quotes, backticks
   and `$` need no escaping.
2. From the root of the project Gemini should work in, make one Bash call with
   `run_in_background: true`:

       bash ~/.claude/skills/gemini-worker/gemini.sh accept-edits < <brief-file>

   Use `plan` instead of `accept-edits` for a read-only question. For several workers, send
   one background call per brief in the same message.
3. Do not poll. Each call notifies when it exits, after 9 minutes at most (agy stops at 540 s).

## Result

- Exit 0: stdout is Gemini's report, ending with a
  `[gemini-3.8-flash-high · conv <id> · <secs>s · <tok> tok]` footer.
- Exit 1: stdout starts with `[gemini call failed: <status>]`, followed by the raw agy output.
- Every call adds one line to `~/.claude/gemini-calls.log`, with the directory it ran in.

The report is Gemini's own claim. Audit `git status` and the diff before relying on it.
