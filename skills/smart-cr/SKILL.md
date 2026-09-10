---
name: smart-cr
description: Review staged, unstaged, or all local Git changes with a YAGNI-focused process that scales from a main-agent review to focused review subagents.
manual-only: true
disable-model-invocation: true
---

# Smart CR

Review only. Do not edit code unless the user later asks for fixes.

## Measure the requested diff

Infer the scope from the user's request: `unstaged/untracked` (i.e not added with `git add .`), `staged`, or `both`. Unchanged committed files are irrelevant. Default to `both` when unspecified. From the repository root, run:

```bash
python3 skills/smart-cr/scripts/change_stats.py --scope <unstaged|staged|both>
```

Use its JSON to choose the review tier. `meaningful_files` excludes documentation, lockfiles, generated artifacts, tests, fixtures, snapshots, and other non-code files. The review must **not** inspect the complete requested diff.

## Review categories

1. **Functions and parameters:** Is every new or changed function necessary for the implementation now, rather than a possible future need? What about new function parameters - do we really need them all?
2. **Contracts and interfaces:** Is every new or changed contract/interface and each field necessary now?
3. **Abstractions:** Is every new or changed abstraction justified by the current implementation?
4. **YAGNI principle:** Is any changed code merely compatibility logic, fallback behavior, future-proofing, or scaffolding that can be removed?
5. **Duplication and reuse:** For new code additions, is similar code likely to exist already? If duplication is plausible, read `docs/index.md`, follow only relevant documentation pointers, and inspect likely implementations. Decide whether reuse or a focused DRY refactor is warranted. Do not claim duplication from superficial similarity.
6. **General bugs and data integrity issues:** Not crazy edge cases or convoluted scenarios, but meaningful issues and where data might get duplicated/deleted unintentionally.

## Scale the review

Apply the first matching tier:

1. **Tiny:** 1–2 meaningful files and every meaningful file has fewer than 30 changed lines. Use zero subagents and perform the review yourself.
2. **Minimal:** 5 or fewer meaningful files and every meaningful file has fewer than 50 changed lines. Spawn exactly one review subagent and assign all review categories to it.
3. **Larger:** spawn one review subagent per review category. If concurrency is limited, start remaining category reviewers as slots become available.

Give each subagent the diff scope, assigned category, and an instruction to review only. Use a lean/no-history fork. Reviewers must not edit files, implement fixes, or broaden the review. Require concrete findings with file and line references, reasoning, and a concise simplification suggestion; they should explicitly say when nothing was found.

Note:

- A main-agent or single-subagent review must cover all five categories distinctly.
- All review subagents should be Luna subagents with High reasoning.
- Each review agent/sub-agent should be focused **only** on its specific task, without creeping to general code reviews; make this explicit and critical in their instructions. Saying "no relevant issues found" is fine.

## Adjudicate and report

Wait for every reviewer. Treat reviewer output as hypotheses. Retain only concrete, current-scope findings whose simplification has merit; discard speculative or overenthusiastic findings, or those unrelated specifically to their task.

Report:

- retained findings ordered by confidence or simplification value, with file/line references and rationale;
- discarded reviewer findings, with a short dismissal reason;
- an explicit statement when either group is empty.

Do not make changes. Leave the final decision to the user.
