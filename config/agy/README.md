# Antigravity CLI (`agy`) Custom Statusline

A lightweight, zero-dependency Node.js statusline script for the [Antigravity CLI](https://antigravity.google) (`agy`), designed to faithfully mirror the visual design, token gauge, and rate-limit countdowns of the Claude Code statusline.

---

## ✨ Features

- **Model & Agent State Indicators**: Displays active model name (`Gemini 3.8 Flash`, `Gemini 3.8 Pro`, etc.) along with real-time agent state (`thinking ⚡`, `working ⚡`, `idle`) or effort level.
- **Context Window Usage Gauge**:
  - 4-bar visual meter (`▮▮▯▯`) calibrated to context size (e.g. 400k threshold band for 1M models, proportional for standard models).
  - Clean token formatting (`143k/1M`, `1.2M/2M`).
  - Dynamic color thresholds: Green (<100k or <50%), Yellow (<200k or <75%), Orange (<400k or <90%), and Red.
  - Excludes output tokens to accurately display context window occupancy.
- **Session Cost**: Real-time session cost in USD (e.g. `$0.12`).
- **Quota & Rate Limit Trackers with Reset Countdowns**:
  - Live quota percentage (`quota 32%`) and reset countdowns (`↻2h05m`, `↻3d04h`).
  - Dual rate limits support (5-hour and 7-day).
  - Warning color triggers at 70% (yellow) and 90% (red).
- **Environment & Terminal Aware**:
  - Full support for `NO_COLOR` environment variable.
  - Safe error handling and graceful fallback on empty or malformed stdin JSON.

---

## 📁 Files

```text
config/agy/
├── statusline.js       # Main statusline script (receives JSON via stdin)
├── statusline.test.js  # Automated unit test suite (19 test cases)
└── README.md           # Documentation and configuration reference
```

---

## ⚙️ Configuration

### 1. Via `settings.json`

Add or update the `statusLine` block in `~/.gemini/antigravity-cli/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "node ~/.gemini/antigravity-cli/statusline.js",
    "enabled": true,
    "stack_with_default": false,
    "padding": 0
  }
}
```

> [!TIP]
> Setting `"stack_with_default": true` will render this custom statusline *below* the default `agy` statusline rather than replacing it.

### 2. Via CLI Slash Commands

You can also test or manage the statusline dynamically inside an active `agy` session:

```text
/statusline ~/.gemini/antigravity-cli/statusline.js   # Load and preview script
/statusline on                                      # Enable statusline
/statusline off                                     # Disable statusline
/statusline reset                                   # Revert to default statusline
```

### 3. Installation via `setup.sh`

Run `setup.sh` in this repository to automatically symlink the statusline to `~/.gemini/antigravity-cli/statusline.js`.

---

## 🧪 Testing

Run the automated test suite using Node.js:

```bash
node config/agy/statusline.test.js
```

The test runner covers 19 test cases including:
- Standard `agy` payloads (`total_input_tokens`, `agent_state`, `quota`)
- Claude-compatible fallback structures (`current_usage`, `rate_limits`)
- Gemini 1M and 2M token formatting
- Quota countdown calculations (hours, minutes, days, and past expirations)
- Warning threshold colors and error handling
