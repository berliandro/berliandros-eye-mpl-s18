# Agent instructions

## Goal workflow (docs/goals)

- Goals are tracked as Markdown files under `docs/goals/`.
- `docs/goals/active/` holds goals currently in progress.
- `docs/goals/finished/` holds completed goals (archived).
- When an agent finishes a goal, it MUST move the corresponding Markdown file from `docs/goals/active/` to `docs/goals/finished/` (do not leave it in active).
- All markdown files in the project are archived under `docs/goals/finished/` as a snapshot; new goal prompts go in `docs/goals/active/`.
- Preserve the relative directory structure when archiving to avoid filename collisions.
