<div align="center">
  <img src="./assets/kata.png" width="120" />
  <h1>Kata</h1>
  <p><b>Engineering habits you already know, turned into skills Gemini CLI, Claude Code, and Codex can run.</b></p>
  <a href="https://github.com/7xmohamed/Kata/stargazers"><img src="https://img.shields.io/github/stars/7xmohamed/Kata?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/7xmohamed/Kata/releases"><img src="https://img.shields.io/github/v/tag/7xmohamed/Kata?label=version&style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://twitter.com/7xmohamed"><img src="https://img.shields.io/badge/follow-7xmohamed-red?style=flat-square&logo=Twitter" alt="Twitter"></a>
</div>

<br/>

## Why

Kata (型, かた) is a Japanese term for a practiced form. It is a sequence drilled until it becomes reflex.

A good engineer does not just write code. They think through requirements, review their own work, debug systematically, design interfaces that feel intentional, and read primary sources. They write clearly, and learn new domains by producing output, not consuming content.

AI makes you faster. It doesn't make you think more clearly, ship more carefully, or understand more deeply. Kata packages these habits into skills Gemini CLI, Claude Code, and Codex can run.

## Skills

Eight engineering habits, each installed as a slash command for your AI CLI.

| Skill | When | What it does |
| :--- | :--- | :--- |
| [`/think`](skills/think/SKILL.md) | Before building anything new | Challenges the problem, pressure-tests the design, validates architecture before any code is written. |
| [`/design`](skills/design/SKILL.md) | Building frontend interfaces | Produces distinctive UI with a committed aesthetic direction, not generic defaults. |
| [`/check`](skills/check/SKILL.md) | After a task, before merging | Reviews the diff, auto-fixes safe issues, flags destructive commands, verifies with evidence. |
| [`/hunt`](skills/hunt/SKILL.md) | Any bug or unexpected behavior | Systematic debugging. Root cause confirmed before any fix is applied. |
| [`/write`](skills/write/SKILL.md) | Writing or editing prose | Rewrites prose to sound natural in English. Strips AI patterns and formulaic phrasing. |
| [`/learn`](skills/learn/SKILL.md) | Diving into an unfamiliar domain | Six-phase research workflow: collect, digest, outline, fill in, refine, then self-review and publish. |
| [`/read`](skills/read/SKILL.md) | Any URL or PDF | Fetches content as clean Markdown with platform-specific routing. Special handling for GitHub, PDFs, WeChat, and Feishu. |
| [`/health`](skills/health/SKILL.md) | Auditing AI CLI setup | Checks configuration files, rules, skills, hooks, MCP, and behavior. Flags issues by severity. |

Each skill is a folder with reference docs, helper scripts, and gotchas from real failures.

## Chaining Skills

Skills are designed to be chained together, but transitions are manual. Each skill stops after completing its task and waits for you to decide the next step.

**Common workflows:**

- **Design a feature**: `/think` → approve → say "implement X" → `/check` → merge
- **Research and write**: `/read` (fetch sources) → `/learn` (synthesize) → `/write` (polish)
- **Debug and verify**: `/hunt` (find root cause) → fix → `/check` (review changes)

Each arrow represents a manual user action. Skills don't automatically trigger each other.

## Install

**Gemini CLI** (global, all skills)

```bash
npx skills add 7xmohamed/Kata -a gemini-cli -g -y
```

**Claude Code**

```bash
claude plugin add 7xmohamed/Kata -g
```

**Codex**

```bash
npx skills add 7xmohamed/Kata -a codex -g -y
```

**Compatibility**

`/health` is optimized for Gemini CLI but provides diagnostic value across all platforms. The other skills are written to use the host environment's native question, search, fetch, and agent mechanisms. `/check` runs parallel specialist reviewers when the host supports them; otherwise it performs the same passes inline.

## Extras

### Statusline

A minimal statusline for Gemini CLI showing context window usage, 5-hour quota, and 7-day quota, all in one line with no noise.

Color coding: green below 70%, yellow at 70–85%, red above 85% for context; blue, magenta, red for quota thresholds.

```bash
curl -sL https://raw.githubusercontent.com/7xmohamed/Kata/main/scripts/setup-statusline.sh | bash
```

The script writes `~/.gemini/statusline.sh` and injects the `statusLine` key into `~/.gemini/settings.json` atomically, refusing to touch a corrupted settings file.

### English Coaching

Most AI models were trained on far more English than any other language, so every prompt in your native tongue goes through an invisible translation layer. Switch to English and the reasoning sharpens, answers get more precise, and every session doubles as language practice.

Gemini corrects your mistakes inline, tagging each one with its pattern name so you learn the rule, not just the fix.

```bash
# Gemini CLI
mkdir -p ~/.gemini/rules && curl -fsSL https://raw.githubusercontent.com/7xmohamed/Kata/main/rules/english.md -o ~/.gemini/rules/english.md

# Codex
mkdir -p ~/.codex && curl -fsSL https://raw.githubusercontent.com/7xmohamed/Kata/main/rules/english.md >> ~/.codex/AGENTS.md
```

## Uninstall

```bash
# Remove all skills
npx skills remove 7xmohamed/Kata -g

# Remove statusline
rm -f ~/.gemini/statusline.sh
# Then remove the statusLine key from ~/.gemini/settings.json

# Remove English Coaching (Gemini CLI)
rm -f ~/.gemini/rules/english.md

# Remove English Coaching (Codex): remove the English Coaching block from ~/.codex/AGENTS.md
```

## Structure

```text
skills/
├── RESOLVER.md        -- central trigger → skill routing table
├── check/             -- code review before merging
│   ├── agents/        -- reviewer-security.md, reviewer-architecture.md
│   └── references/    -- persona-catalog.md
├── design/            -- production-grade frontend UI
├── health/            -- AI CLI config audit
│   └── agents/        -- inspector-context.md, inspector-control.md
├── hunt/              -- systematic debugging
├── learn/             -- research to published output
├── read/              -- fetch URL or PDF as Markdown
├── think/             -- design and validate before building
└── write/             -- natural prose in English
    └── references/    -- write-en.md
.gemini-plugin/        -- Gemini plugin registry
.claude-plugin/        -- Claude plugin registry
.codex-plugin/         -- Codex plugin registry
rules/                 -- Global AI behavior instructions
  english.md           -- English coaching rule
  anti-patterns.md     -- AI anti-patterns reference
scripts/
  setup-statusline.sh  -- install the statusline into ~/.gemini/
  statusline.sh        -- the statusline script itself
  verify-skills.sh     -- CI validator: frontmatter, versions, references
GEMINI.md              -- project config for Gemini CLI
CLAUDE.md              -- project config for Claude Code
CODEX.md               -- project config for Codex (Cursor)
AGENTS.md              -- generic rules for other AI Agents
```

Each skill has a `SKILL.md` loaded on demand by the active AI agent. `skills/RESOLVER.md` is the human-readable index of which trigger maps to which skill; keep it in sync when you change a skill's scope.

## Background

Eight skills for the habits that actually matter. Each does one thing, has a clear trigger, and stays out of the way. They are not complete by design, but rather just the right amount done well.

Every rule the author writes becomes a ceiling. The model can only do what the instructions say and can't go further. Kata goes the other direction. Each skill sets a clear goal and the constraints that matter, then steps back. As models improve, that restraint pays compound interest.

Built from patterns across real projects, refined through actual use. Every gotcha traces to a real failure.

The `/health` skill implements the six-layer audit framework: `GEMINI.md → rules → skills → hooks → subagents → verifiers`.

## Verify

Before any commit, run the integrity check:

```bash
./scripts/verify-skills.sh
```

This validates frontmatter in every `SKILL.md`, checks version parity with `.gemini-plugin/marketplace.json`, confirms all file references exist, and ensures every skill appears in `RESOLVER.md`.

## License

MIT License. Feel free to use Kata and contribute.
