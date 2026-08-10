# 84_WHAT_TO_SEND_CODEX_REPLIT

## Purpose

This file defines what to give Codex, Replit, or another coding agent.

---

# Codex / Replit Rule

Never give the coding agent all 90 files and say “build this.”

Give:
1. master context
2. MVP scope
3. current ticket
4. acceptance criteria

---

# Initial Setup Prompt

Send:

- `03_EVERCRAFTED_MVP_SCOPE.md`
- `35_MVP_ACCEPTANCE_CRITERIA.md`
- `45_DEVELOPER_HANDOFF_MASTER_INDEX.md`
- `38_SPRINT_1_FOUNDATION_TICKETS.md`
- `74_FRONTEND_FILE_STRUCTURE.md`
- `75_BACKEND_FILE_STRUCTURE.md`

Then say:

“Implement Sprint 1 only. Do not build marketplace, Moodoor, evaluator, adaptive intelligence, or future systems. Follow the acceptance criteria exactly.”

---

# For Frontend Task

Send:
- relevant sprint ticket
- `30_FRONTEND_APPLICATION_ARCHITECTURE.md`
- `36_REACT_COMPONENT_HIERARCHY.md`
- `76_REACT_DESIGN_SYSTEM.md`

---

# For Backend Task

Send:
- relevant sprint ticket
- `31_BACKEND_SERVICE_ARCHITECTURE.md`
- `71_DATABASE_TABLE_DEFINITIONS.sql`
- `72_API_OPENAPI_SPEC.yaml`
- `73_TYPESCRIPT_SHARED_TYPES.ts`

---

# For Visualizer Task

Send:
- `09_PLACEMENT_ENGINE_SPEC.md`
- `10_PLACEMENT_VISUALIZATION_ENGINE_SPEC.md`
- `33_VISUALIZER_RENDER_PIPELINE.md`
- current visualizer source files

---

# Example Codex Prompt

Use this:

“Use the attached Evercrafted docs as reference. Implement only Sprint 4 from `41_SPRINT_4_PLACEMENT_ENGINE_TICKETS.md`. Do not build UI beyond what is required for testing. The placement engine must be deterministic and must follow `09_PLACEMENT_ENGINE_SPEC.md`. Return code changes and explain how to test them.”

---

# Important

Every coding task should have:
- one sprint
- one ticket
- one acceptance checklist
- no future-scope distractions
