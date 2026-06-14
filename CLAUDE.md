# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Studyen** is a single-page web tool for learning English vocabulary in the AI/ML domain. It targets Chinese-speaking developers who read English AI documentation and want to improve their reading and speaking skills.

The MVP is deliberately minimal:
- **Single static `index.html`** (Tailwind via CDN, vanilla JS, Web Speech API, localStorage)
- **Python scripts** (`scripts/`) that call DeepSeek API + CMU dict to generate the vocabulary JSON
- **GitHub Actions** (`.github/workflows/`) for scheduled updates

Full requirements: see `doc/REQUIREMENTS.md`. Current implementation plan: see `doc/plan/new/plan-B-mvp.md`.

## Plan Governance Rules (CRITICAL)

These rules govern how Claude must behave in this repository:

1. **Archive every plan** produced in plan mode.
   - On plan creation, write/duplicate it to `doc/plan/new/<descriptive-name>.md`
   - **Do NOT** delete from `doc/plan/new/` when starting implementation — leave it there until user confirms completion
   - When the user confirms the plan is fully implemented, **move** it from `doc/plan/new/` to `doc/plan/done/` (use `git mv` to preserve history)

2. **Do not implement without authorization.** If the user has not explicitly said "do it" / "go ahead" / "implement this", stay in discussion / planning mode. Surface options with `AskUserQuestion` rather than guessing.

3. **Ask, don't assume.** If any requirement is ambiguous — UI style, edge case behavior, scope of a feature, naming — ask via `AskUserQuestion` before writing code or committing to a design. Never fill in unknowns with your best guess.

4. **Document decisions in `doc/`.** Requirements, design notes, and architectural decisions belong in `doc/REQUIREMENTS.md` or topic-specific files under `doc/`. Keep these documents in sync with code changes that alter scope.

5. **Never commit secrets.** API keys (e.g., `DEEPSEEK_API_KEY`) go through environment variables / GitHub Secrets only. Never paste them into code, `.env`, or commit messages. `.env` is gitignored; only `.env.example` is tracked.

## High-Level Architecture

```
GitHub Repository
├── data/
│   ├── vocab.json              ← generated vocabulary (committed, consumed by HTML)
│   └── vocab.template.json     ← user-submitted words waiting to be enriched
├── scripts/
│   ├── build_vocab.py          ← entry point: orchestrates the full pipeline
│   ├── cmu_lookup.py           ← CMU Pronouncing Dictionary lookup + ARPAbet→IPA
│   ├── prompts.py              ← DeepSeek prompt templates
│   └── requirements.txt
├── .github/workflows/
│   └── update-vocab.yml        ← scheduled + manual + push-triggered runs
└── index.html                  ← the entire frontend (no build step)
```

**Data flow:**
1. User manually adds words via the HTML UI → stored in browser localStorage
2. User clicks "导出待补全词" → downloads a `vocab.template.json`
3. User commits that JSON to the repo → GitHub Actions runs `build_vocab.py`
4. Script calls DeepSeek for meanings/examples, CMU for IPA, merges into `vocab.json`
5. User refreshes the HTML to see new words

**Key architectural choices** (see `doc/plan/done/plan-A-extended.md` for what was rejected):
- No backend, no build step, no framework — the page is just `index.html`
- localStorage only — no cloud sync in MVP
- Web Speech API for TTS — no paid TTS service in MVP
- DeepSeek for LLM — chosen for cost; Claude/OpenAI were alternatives

## Common Commands

These will be relevant once Phase 1+ of `doc/plan/new/plan-B-mvp.md` lands:

```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# Run the vocab builder locally (requires DEEPSEEK_API_KEY env var)
export DEEPSEEK_API_KEY=sk-...
python scripts/build_vocab.py

# Open the app locally — just open the file, no server needed
open index.html      # macOS
# or visit file:// URL in browser
```

There is currently **no build, no lint, no test runner** for this project — that is intentional per the MVP scope. If you add them, update this section.

## Working in This Repo

- When modifying the data schema in `vocab.json`, update `doc/REQUIREMENTS.md` §5 and the schema comments in `scripts/build_vocab.py` together. The HTML reads fields by name; mismatches will break silently.
- When adding new categories, extend the enum in `scripts/prompts.py` `SYSTEM_PROMPT` AND the HTML filter dropdown — both must stay in sync.
- The CMU→IPA mapping in `scripts/cmu_lookup.py` is intentionally simple. If users report pronunciation issues, expand the mapping table rather than reaching for an external library without user approval.