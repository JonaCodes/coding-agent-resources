---
name: research
description: Use any time you need to research something, whether inside the repo, on a specific site, or on the general web
---

## Execution

For any task that requires fetching information from anywhere, delegate the research to one or more `gpt-5.6-luna` subagents with high reasoning.

This includes researching repository files, specific sites, and the general web. The number of subagents you spawn should be proportional to the task. For example, if you need to research an entire repository, assign one subagent per domain in the repository. You may also divide the work by research area, such as one subagent for a module in the repository and another for a web search.

Give each subagent a concrete, well-scoped question. Instruct the subagents to return a summary of their findings, with specific quotes backing the important findings you are researching.
