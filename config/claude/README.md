# Claude Code Custom Statusline

A lightweight, zero-dependency Node.js statusline script for [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) CLI, complete with an automated unit test suite.

---

## ✨ Features

- **Model & Effort Indicators**: Displays active model name (`Opus 5.5`, `Sonnet 5.5`) along with effort level (`high`, `low`) and fast mode badge (`⚡`).
  - Model name colored by cost tier: Haiku green, Sonnet yellow, Opus orange, Fable red. Unrecognized models stay uncolored.
  - Effort colored by intensity: `low` green, `medium` yellow, `high` orange, `xhigh` red, and `max` as a white-on-red badge so it cannot be missed.
- **Context Window Usage Gauge**:
  - 4-bar visual meter (`▮▮▯▯`) calibrated to context size (e.g. 400k threshold band for 1M models, proportional for standard models).
  - Human-friendly token formatting (`143k/1M`, `180k/200k`).
  - Dynamic color thresholds: Green (<100k or <50%), Yellow (<200k or <75%), Orange (<400k or <90%), and Red.
  - Excludes transient output tokens to accurately reflect prompt/cache context window occupancy.
- **Session Cost**: Real-time total session cost formatted in USD (e.g. `$0.84`).
- **Turn Execution Stopwatch & Pause Indicator**:
  - Automatically starts counting when a prompt is sent (`agent_state: "running"`, `"thinking"`, etc.).
  - Displays an in-progress icon (`⏱`) with live elapsed time during generation (`⏱ 14s`, `⏱ 1m05s`).
  - Pauses automatically when the answer returns (`agent_state: "idle"`), displaying the completed turn duration with done checkmark (`✓ 14s`).
  - Stays paused displaying the last prompt's duration while idle and seamlessly resets to `0s` when a new prompt is sent.
  - Fully customizable icons via `STATUSLINE_RUNNING_ICON` (default `⏱`) and `STATUSLINE_DONE_ICON` (default `✓`), supporting Nerd Fonts (e.g. `󰔛` / `󰄬`).
- **Rate Limit Trackers with Reset Countdowns**:
  - 5-hour rate limit percentage + time-remaining countdown (e.g. `5h 32% ↻2h05m`).
  - 7-day rate limit percentage + countdown (e.g. `7d 44% ↻3d04h` or `7d 90% ↻5h30m`).
  - Warning color triggers at 70% (yellow) and 90% (red).
- **Environment & Terminal Aware**:
  - Respects standard `NO_COLOR` environment variable.
  - Graceful fallback on malformed or empty stdin JSON.

---

## 🖥️ Output Examples

### Standard Mode (Default)
**Prompt In Progress (Running):**
```text
Opus 5.5 · high · ▮▮▯▯ 143k/1M · $0.84 · ⏱ 14s · 5h 32% ↻2h05m · 7d 44% ↻3d04h
```

**Answer Returned (Paused / Done):**
```text
Opus 5.5 · high · ▮▮▯▯ 143k/1M · $0.84 · ✓ 14s · 5h 32% ↻2h05m · 7d 44% ↻3d04h
```

### Fast Mode Enabled (`⚡` badge)
When Fast Mode is toggled on (e.g. `/fast`), the `⚡` badge appears persistently alongside the effort level in both running and idle states:
```text
Opus 5.5 · high ⚡ · ▮▮▯▯ 143k/1M · $0.84 · ✓ 14s · 5h 32% ↻2h05m · 7d 44% ↻3d04h
```

---

## 📁 Files

```text
config/claude/
├── statusline.js       # Main statusline script (receives JSON via stdin)
├── statusline.test.js  # Automated unit test suite (36 test cases + lifecycle suite)
└── README.md           # Documentation and configuration reference
```

---

## ⚙️ How to Activate

> [!NOTE]
> `settings.json` is stored locally in `~/.claude/settings.json` and is not committed to the repository because it contains user environment configurations and personal preferences. To activate this statusline in Claude Code, add the configuration below to your local `~/.claude/settings.json`.

### 1. Via `settings.json`

To activate the statusline in Claude Code, reference it in `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "node ~/.claude/statusline.js",
    "padding": 0,
    "refreshInterval": 1
  }
}
```

> [!TIP]
> Setting `"refreshInterval": 1` enables live second-by-second timer ticking in the statusline while prompts are actively streaming.

The script can be installed automatically via `setup.sh` or symlinked manually:

```bash
mkdir -p ~/.claude
ln -sf "$(pwd)/config/claude/statusline.js" ~/.claude/statusline.js
```

### 2. Custom Icons

You can customize the running and finished timer icons via environment variables:

```bash
export STATUSLINE_RUNNING_ICON="󰔛"
export STATUSLINE_DONE_ICON="󰄬"
```

---

## 🧪 Testing

Run the included unit test suite using Node.js:

```bash
node config/claude/statusline.test.js
```

The test runner covers 36 test cases and dynamic prompt lifecycle verification, including:
- Dynamic prompt execution timer start (`⏱ 0s`), live ticking, and paused display (`✓ 14s`)
- Multi-step prompt lifecycle transitions (active -> paused -> reset on next prompt)
- Sub-second execution formatting (`✓ <1s`) and minute/hour formatting (`1m05s`, `1h01m`)
- Custom icon overrides via environment variables (`STATUSLINE_RUNNING_ICON`, `STATUSLINE_DONE_ICON`)
- Full output rendering with multiple rate limits
- Reset countdown formatting (days, hours, minutes, past expirations)
- Context window token formatting & threshold bands across 200k and 1M models
- Fast mode and effort level badge toggling
- Model tier and effort level colors (and plain output under `NO_COLOR`)
- Graceful handling of missing fields or invalid JSON
