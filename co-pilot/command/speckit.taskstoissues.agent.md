---
description: Convert existing tasks into actionable, dependency-ordered GitHub issues for the feature based on available design artifacts.
tools: ['github/github-mcp-server/issue_write']
---

## Context

{arguments}

## Outline

1. **Load task context**: Use the tasks provided in the context above. If no tasks are available, report an error and suggest running `speckit.tasks` first.

2. **Validate repository context**: Only proceed if the context indicates this is a GitHub repository. If the repository remote is not a GitHub URL, output a warning and stop.

> [!CAUTION]
> ONLY PROCEED TO NEXT STEPS IF THE CONTEXT CONFIRMS A GITHUB REPOSITORY

3. **Convert tasks to GitHub issues**: For each task in the list, format a GitHub issue with:
   - **Title**: Task description (without the checkbox and ID prefix)
   - **Body**: Include task ID, phase, dependencies, file path, and parallel marker if present
   - **Labels**: Suggest appropriate labels (e.g., `enhancement`, phase name, user story label)

> [!CAUTION]
> UNDER NO CIRCUMSTANCES EVER CREATE ISSUES IN REPOSITORIES THAT DO NOT MATCH THE REMOTE URL
