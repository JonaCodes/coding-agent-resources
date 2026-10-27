---
name: senior-plan-review
description: Do not use this skill unless the user explicitly asks.
manual-only: true
disable-model-invocation: true
---

Review the current plan against the user's requirements and relevant existing code, then update it to use the simplest approach that satisfies the task.

Spin up a Sol subagent using model `gpt-6.1-sol` with `high` reasoning and fresh context. Give it the plan, the user's requirements, relevant constraints, and pointers to the documentation and code needed to assess the plan.

Ask the subagent to look for:

- Over-engineering, unnecessary abstractions, extra layers, and broader refactors than the task requires.
- Work included "just in case" for hypothetical future features, reuse, extensibility, or scale.
- Premature optimization without evidence of a current performance need.
- Extra configuration, dependencies, fallback paths, or implementation steps without a concrete current use.

Evaluate the findings and remove or simplify parts that add complexity without meeting a present requirement. Keep safeguards, edge case handling, and architectural constraints that are needed for correctness or supported behavior. When complexity has a concrete justification, retain it and make that reason clear in the plan.

Resolve dependent steps after simplifying so the revised plan remains coherent and actionable. If a simplification depends on an unresolved product decision, flag that decision rather than silently dropping a requirement.

Update the existing plan file in place when one exists; otherwise provide the revised plan in the conversation. Briefly explain material simplifications or state that no changes were needed. Do not implement the plan as part of this review.
