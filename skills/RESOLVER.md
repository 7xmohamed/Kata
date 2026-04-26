# Kata Skill Resolver

Routing table from trigger phrases to skills. The AI CLI matches automatically via each SKILL.md `description`. This file is the human-readable index and the source of truth for `verify-skills.sh`. When you change a skill's scope, update this table too.

> **Read the skill file before acting.** When two skills could both match, read both. They are designed to chain: `/think` → implement → `/check`.

## By Workflow Phase

### Pre-build

| Trigger | Skill |
|---------|-------|
| New feature / architecture decision / "how should I design this" / "should I build this" / "is it worth it" | `skills/think/SKILL.md` |
| UI / component / page / visual interface / frontend | `skills/design/SKILL.md` |

### Post-build

| Trigger | Skill |
|---------|-------|
| Done implementing / before merging / "review this" / "look at this code" | `skills/check/SKILL.md` |
| Review issue / review PR / triage / "check if there are issues" | `skills/check/SKILL.md` (Triage Mode) |

### Diagnostic

| Trigger | Skill |
|---------|-------|
| Error / crash / test failing / unexpected behavior / "why is this not working" | `skills/hunt/SKILL.md` |
| AI ignoring instructions / hook not firing / MCP issue / config audit | `skills/health/SKILL.md` |

### Content

| Trigger | Skill |
|---------|-------|
| Message contains http(s) URL / any web link / PDF path / "read this" / "summarize this" | `skills/read/SKILL.md` |
| Writing / editing / polishing / "make this sound better" / "remove AI tone" | `skills/write/SKILL.md` |
| Deep research on an unfamiliar domain / six-phase research to draft / synthesizing sources into an article | `skills/learn/SKILL.md` |

## Disambiguation

When multiple skills could match, apply these rules in order:

1. **Most specific wins**: `/design` is more specific than `/think` (UI decisions only). If the user says "design a login page", use `/design`.
2. **URL routes to content type**: Message has URL → `/read` first to get Markdown → if it's long research material, chain to `/learn`; if it just needs a quick summary, stop at `/read` output.
3. **Fix vs review**: Code is delivered or at PR stage → `/check`; code doesn't run or behaves wrong → `/hunt`. Both could match "look at this", so decide by checking if there's a concrete error symptom.
4. **Config vs code error**: AI ignoring instructions / hooks not firing / MCP broken → `/health`; user's code throwing an exception → `/hunt`.
5. **Long-form output vs polish**: Writing from scratch to a finished draft → `/learn`; already have a draft and want it edited → `/write`.
6. **Judgment vs debugging**: "Should I keep this?" + no error → `/think` Evaluation Mode; "Why doesn't this work?" + error → `/hunt`.
7. **Fallback**: When both still seem ambiguous, read both SKILL.md "Not for" sections and use the exclusion clauses to decide. Still ambiguous? Ask the user.

## Chaining

Skill transitions are always manual. There is no auto-chaining. Each skill stops and waits for your next instruction.

- `/think` produces a plan → user says "implement it" → implement → user says "/check" → `/check` reviews
- `/read` fetches multiple URLs → user says "/learn" → `/learn` synthesizes
- `/learn` produces a draft → user says "/write" → `/write` polishes
- `/hunt` finds root cause → user says "fix it" → fix → user says "/check" → `/check` confirms no side effects
- `/health` finds a config issue → user says "fix it" → fix → user says "/health" → re-run `/health`

## Latent vs Deterministic

Kata skills are all fat skills (Markdown carrying judgment). Deterministic constraints live in `scripts/verify-skills.sh` and `rules/*.md`. Before adding a new capability, ask:

- Needs judgment / adapts to context / asks follow-up questions? → skill
- Same input always produces same output / just validation or lookup? → script or rule

Don't encode lint checks as skills. Don't stuff "how to research an unfamiliar domain" into a shell script. See the decision table in `GEMINI.md` / `CLAUDE.md` / `AGENTS.md`.
