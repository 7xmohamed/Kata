# Kata 1.1 ??

Personal skill collection for Gemini CLI. Eight skills covering the complete engineering workflow: think, design, check, hunt, write, learn, read, health. Now with advanced Architecture, Security, and Synthesis modes.

## Structure

```
skills/
├── RESOLVER.md   -- central trigger → skill routing table
├── check/        -- code review before merging
│   ├── agents/   -- reviewer-security.md, reviewer-architecture.md
│   └── references/  -- persona-catalog.md
├── design/       -- production-grade frontend UI
├── health/       -- Gemini CLI config audit
│   └── agents/   -- inspector-context.md, inspector-control.md
├── hunt/         -- systematic debugging
├── learn/        -- research to published output
├── read/         -- fetch URL or PDF as Markdown
├── think/        -- design and validate before building
└── write/        -- natural prose in English
    └── references/  -- write-zh.md, write-en.md
.gemini-plugin/
  marketplace.json    -- plugin registry for npx/plugin distribution
```

Each skill has a `SKILL.md` (loaded on demand by Gemini). Supporting content lives in subdirectories. `skills/RESOLVER.md` is the human-readable index of "which trigger goes to which skill"; keep it in sync when you change a skill's scope.

## Skill vs Script: Latent vs Deterministic

Before adding a new capability, decide which layer it belongs in. Kata's eight skills are all **fat skills** (Markdown carrying judgment). Anything that is pure verification, lookup, or table-driven enforcement belongs in `scripts/` or `rules/`, not in a SKILL.md.

| Question | YES → | NO → |
|----------|-------|------|
| Does the user need the model to think, adapt, or ask? | **Skill** | Script / rule |
| Does the same input always produce the same output? | **Script / rule** | Skill |
| Does it depend on the user's project environment? | **Skill** | Script / rule |
| Is it a lookup, list, or status check? | **Script / rule** | Probably skill |
| Does behavior shift with conversation context? | **Skill** | Script / rule |

Examples in this repo:
- `verify-skills.sh` = script (frontmatter / references / version parity, all deterministic)
- `rules/english.md` = rule (applies in every session, no judgment needed)
- `/think`, `/hunt`, `/check` = skills (each reads the situation and decides)
- `/health` diagnostics = skill (tier-aware, context-sensitive)
- Six-layer tier assessment = skill (needs judgment about project size and signals)

Rule of thumb: if you catch yourself writing "if X then Y" enumeration inside a SKILL.md, it probably wants to be a script. If you catch yourself writing "the agent should use good judgment" inside a shell script, that part wants to be a skill.

## Verification

Run `./scripts/verify-skills.sh` before any commit. If the diff is non-trivial, also run `/check`.

## Commit Convention

`{type}: {description}` -- types: feat, fix, refactor, docs, chore

## Release Convention

- Title: `V{version} {Codename} {emoji}` -- e.g., V0.1.0 Start
- Tag: `v{version}` (lowercase v)
- Body: Markdown format, structure as follows:

```
<div align="center">
  <img src="..." width="120" />
  <h1>Kata V{version}</h1>
  <p><em>tagline</em></p>
</div>

### Changelog

1. **SkillName**: One sentence on what changed and its user effect.
2. ...

### 更新日志

1. **技能名**: 一句话说清楚改了什么以及对用户的影响。
2. ...

Update: `npx skills add 7xmohamed/Kata@latest` · ⭐ [7xmohamed/Kata](https://github.com/7xmohamed/Kata)
```

- Each item: `**Label**: one sentence` -- bold label is the skill or module name, description leads with what changed
- Style: engineer-facing, no marketing language; one-to-one bilingual mapping
- Footer: update command + star + repo link
