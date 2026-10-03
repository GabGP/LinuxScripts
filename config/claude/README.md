# Claude Code Custom Statusline

A lightweight, zero-dependency Node.js statusline script for [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) CLI, complete with an automated unit test suite.

---

## ✨ Features

- **Model & Effort Indicators**: Displays active model name (`Opus 5.5`, `Sonnet 5.5`) along with effort level (`high`, `low`) and fast mode badge (`⚡`).
- **Context Window Usage Gauge**:
  - 4-bar visual meter (`▮▮▯▯`) calibrated to context size (e.g. 400k threshold band for 1M models, proportional for standard models).
  - Human-friendly token formatting (`143k/1M`, `180k/200k`).
  - Dynamic color thresholds: Green (<100k or <50%), Yellow (<200k or <75%), Orange (<400k or <90%), and Red.
  - Excludes transient output tokens to accurately reflect prompt/cache context window occupancy.
- **Session Cost**: Real-time total session cost formatted in USD (e.g. `$0.84`).
- **Rate Limit Trackers with Reset Countdowns**:
  - 5-hour rate limit percentage + time-remaining countdown (e.g. `5h 32% ↻2h05m`).
  - 7-day rate limit percentage + countdown (e.g. `7d 44% ↻3d04h` or `7d 90% ↻5h30m`).
  - Warning color triggers at 70% (yellow) and 90% (red).
- **Environment & Terminal Aware**:
  - Respects standard `NO_COLOR` environment variable.
  - Graceful fallback on malformed or empty stdin JSON.

---

## 📁 Files

```text
config/claude/
├── statusline.js       # Main statusline script (receives JSON via stdin)
├── statusline.test.js  # Automated unit test suite (16 test cases)
└── README.md           # Documentation and configuration reference
```

---

## ⚙️ Configuration

To activate the statusline in Claude Code, reference it in `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "node ~/.claude/statusline.js",
    "padding": 0
  }
}
```

The script can be installed automatically via `setup.sh` or symlinked manually:

```bash
mkdir -p ~/.claude
ln -sf "$(pwd)/config/claude/statusline.js" ~/.claude/statusline.js
```

---

## 🧪 Testing

Run the included unit test suite using Node.js:

```bash
node config/claude/statusline.test.js
```

The test runner tests 16 scenarios including:
- Full output rendering with multiple rate limits
- Reset countdown formatting (days, hours, minutes, past expirations)
- Context window token formatting & threshold bands across 200k and 1M models
- Fast mode and effort level badge toggling
- Graceful handling of missing fields or invalid JSON
