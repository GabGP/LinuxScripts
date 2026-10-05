# Antigravity CLI (`agy`) Custom Statusline

A lightweight, zero-dependency Node.js statusline script for the [Antigravity CLI](https://antigravity.google) (`agy`), designed to faithfully mirror the visual design, token gauge, rate-limit countdowns, and behavior of the Claude Code statusline.

---

## ✨ Features

- **Model & Effort Indicators**: Displays active model name (`Gemini 3.8 Flash`, `Claude Opus 5.5`, etc.) with clean effort level (`high`, `low`) and fast mode badge (`⚡`).
- **Strict Fast Mode Mirroring**: The lightning bolt (`⚡`) only appears when `fast_mode` is enabled, matching Claude Code's exact indicator logic.
- **Context Window Usage Gauge**:
  - 4-bar visual meter (`▮▮▯▯`) calibrated to context size (400k threshold band for 1M/2M models, proportional for standard models).
  - Clean token formatting (`145k/1M`, `1.2M/2M`).
  - Dynamic color thresholds: Green (<100k or <50%), Yellow (<200k or <75%), Orange (<400k or <90%), and Red.
  - Excludes transient output tokens to accurately display context window occupancy.
- **Dual Rate-Limit & Quota Trackers with Reset Countdowns**:
  - Automatically resolves multi-bucket quotas (`gemini-5h`, `gemini-weekly`, `3p-5h`, `3p-weekly`) into standard `5h` and `7d` trackers.
  - Formats live usage percentage and time-remaining countdowns (e.g. `5h 9% ↻4h30m · 7d 45% ↻3d08h`).
  - Warning color triggers at 70% (yellow) and 90% (red).
- **Turn Execution Stopwatch & Pause Indicator**:
  - Automatically starts counting when a prompt is sent (`agent_state: "thinking"`, `"working"`, etc.).
  - Displays an in-progress icon (`⏱`) with live elapsed time during generation (`⏱ 14s`, `⏱ 1m05s`).
  - Pauses automatically when the answer returns (`agent_state: "idle"`), displaying the completed turn duration with done checkmark (`✓ 14s`).
  - Stays paused displaying the last prompt's duration while idle and seamlessly resets to `0s` when a new prompt is sent.
  - Fully customizable icons via `STATUSLINE_RUNNING_ICON` (default `⏱`) and `STATUSLINE_DONE_ICON` (default `✓`), supporting Nerd Fonts (e.g. `󰔛` / `󰄬`).
- **Git Branch Integration**:
  - Automatically queries the active repository branch and renders ` main` (omitted if not in a repository).
- **Session Cost**: Real-time session cost in USD if reported by the model backend.
- **Environment & Terminal Aware**:
  - Full support for `NO_COLOR` environment variable.
  - Safe error handling and graceful fallback on empty or malformed stdin JSON.

---

## 🖥️ Output Examples

### Standard Mode (Default)
**Prompt In Progress (Running):**
```text
Gemini 3.8 Flash · high · ▮▮▯▯ 145k/1M · $0.12 · ⏱ 14s · 5h 9% ↻4h30m · 7d 45% ↻3d08h ·  main
```

**Answer Returned (Paused / Done):**
```text
Gemini 3.8 Flash · high · ▮▮▯▯ 145k/1M · $0.12 · ✓ 14s · 5h 9% ↻4h30m · 7d 45% ↻3d08h ·  main
```

### Fast Mode Enabled (`⚡` badge)
When Fast Mode is toggled on (e.g. `/fast`), the `⚡` badge appears persistently alongside the effort level in both running and idle states:
```text
Gemini 3.8 Flash · high ⚡ · ▮▮▯▯ 145k/1M · $0.12 · ✓ 14s · 5h 9% ↻4h30m · 7d 45% ↻3d08h ·  main
```

---

## 📁 Files

```text
config/agy/
├── statusline.js       # Main statusline script (receives JSON via stdin)
├── statusline.test.js  # Automated unit test suite (28 test cases + lifecycle suite)
└── README.md           # Documentation and configuration reference
```

---

## ⚙️ How to Activate

> [!NOTE]
> `settings.json` is stored locally in `~/.gemini/antigravity-cli/settings.json` and is not committed to the repository because it contains user-specific workspace history and pre-approved command permissions. To activate this statusline, configure your local `settings.json` as shown below.

### 1. Via `settings.json`

Add or update the `statusLine` block in `~/.gemini/antigravity-cli/settings.json`:

**Linux / macOS:**
```json
{
  "statusLine": {
    "type": "command",
    "command": "node ~/.gemini/antigravity-cli/statusline.js",
    "enabled": true,
    "stack_with_default": false,
    "padding": 0,
    "refreshInterval": 1
  }
}
```

**Windows:**
```json
{
  "statusLine": {
    "type": "command",
    "command": "node C:\\Users\\<USER>\\.gemini\\antigravity-cli\\statusline.js",
    "enabled": true,
    "stack_with_default": false,
    "padding": 0,
    "refreshInterval": 1
  }
}
```

> [!TIP]
> Setting `"refreshInterval": 1` enables live second-by-second timer ticking in the statusline while prompts are actively streaming.
> Setting `"stack_with_default": true` will render this custom statusline *below* the default `agy` statusline rather than replacing it.

### 2. Custom Icons

You can customize the running and finished timer icons via environment variables in `~/.bashrc` or your shell profile:

```bash
export STATUSLINE_RUNNING_ICON="󰔛"
export STATUSLINE_DONE_ICON="󰄬"
```

### 3. Via CLI Slash Commands

You can test or manage the statusline dynamically inside an active `agy` session:

```text
/statusline on      # Enable statusline
/statusline off     # Disable statusline
/statusline reset   # Revert to default statusline
```

### 4. Installation via `setup.sh`

Run `setup.sh` in this repository to automatically symlink or install the statusline to `~/.gemini/antigravity-cli/statusline.js`.

---

## 🧪 Testing

Run the automated test suite using Node.js:

```bash
node config/agy/statusline.test.js
```

The test runner covers 28 test cases and dynamic prompt lifecycle verification, including:
- Dynamic prompt execution timer start (`⏱ 0s`), live ticking, and paused display (`✓ 14s`)
- Multi-step prompt lifecycle transitions (active -> paused -> reset on next prompt)
- Sub-second execution formatting (`✓ <1s`) and minute/hour formatting (`1m05s`, `1h01m`)
- Custom icon overrides via environment variables (`STATUSLINE_RUNNING_ICON`, `STATUSLINE_DONE_ICON`)
- Dual multi-bucket quota resolution (`gemini-5h`/`weekly` and `3p-5h`/`weekly`)
- Strict fast-mode `⚡` toggle validation
- Git branch segment formatting
- Gemini 1M and 2M token formatting
- Quota countdown calculations (hours, minutes, days, and past expirations)
- Threshold color grading and malformed JSON recovery
