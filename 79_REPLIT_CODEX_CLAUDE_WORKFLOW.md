# 79_REPLIT_CODEX_CLAUDE_WORKFLOW

## Purpose

Defines how to use Claude, Codex, Replit, and developers together without confusion.

---

## Roles

### Claude
Best for:
- architecture
- PRDs
- canon
- product logic
- reviewing implementation
- refining prompts
- explaining systems

### Codex
Best for:
- code implementation
- file edits
- repo changes
- tests
- bug fixes

### Replit
Best for:
- running prototype
- testing app flows
- deployment experiments
- quick iteration

### Human Developer
Best for:
- architecture decisions
- production hardening
- security review
- final deployment

---

## Correct Workflow

1. Use canon files for context.
2. Use sprint ticket file for task.
3. Give Codex one ticket at a time.
4. Test in Replit/local.
5. Review output against acceptance criteria.
6. Move to next ticket.

---

## What To Send First

To a developer/Codex, send:
- `45_DEVELOPER_HANDOFF_MASTER_INDEX.md`
- `03_EVERCRAFTED_MVP_SCOPE.md`
- `35_MVP_ACCEPTANCE_CRITERIA.md`
- current sprint ticket file

---

## Do Not Send Everything At Once

Do not dump all 80 files into a coding task.

Use the master index plus the current sprint/ticket.

---

## Example Codex Instruction

“Use the Evercrafted handoff docs as reference. Implement Sprint 1 Ticket 1.2 only. Do not build future marketplace, Moodoor, or advanced evaluator systems. Follow the acceptance criteria exactly.”
