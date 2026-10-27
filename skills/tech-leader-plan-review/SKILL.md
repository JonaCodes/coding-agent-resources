---
name: tech-leader-plan-review
description: Do not use this skill unless the user explicitly asks.
manual-only: true
disable-model-invocation: true
---

Review the current plan and update it to address concrete correctness problems.

Spin up an Astra subagent using model `gpt-6-astra` with `high` reasoning and fresh context. Give it the plan, the user's requirements, relevant constraints, and pointers to the documentation and code needed to assess the plan.

Ask the subagent to check for:

- Logic bugs, incorrect assumptions, and missing steps that would prevent the plan from working.
- Reasonable edge cases arising from the expected inputs and supported behavior.
- Data flow problems, including where data comes from, how it changes, where it is stored or passed, and how failures affect that flow.

Keep the review grounded in current requirements and the existing code. Do not expand the plan for speculative scenarios or unrelated improvements.

Evaluate the findings and incorporate justified fixes into the plan. Preserve the user's intended scope and resolve dependent steps so the revised plan is coherent. If a finding depends on an unresolved product decision, flag that decision rather than inventing a requirement.

Update the existing plan file in place when one exists; otherwise provide the revised plan in the conversation. Briefly explain material changes or state that no changes were needed. Do not implement the plan as part of this review.
