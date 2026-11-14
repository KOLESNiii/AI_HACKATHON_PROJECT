# Agent Instructions

This repository is a collaborative hackathon project developed by four human contributors, each potentially using autonomous coding agents.

## 1. Primary objectives

- Deliver a working, demonstrable product within the hackathon deadline.
- Prioritise a functional end-to-end vertical slice over unnecessary abstraction.
- Optimise for development speed, maintainability, and parallel work.
- Prefer simple, proven solutions unless complexity provides a clear benefit.
- Do not introduce unnecessary dependencies, frameworks, or infrastructure.

## 2. Repository orientation

Before making changes:

1. Read `README.md` for project goals, setup and commands.
2. Read `docs/architecture.md` for system boundaries and interfaces.
3. Read `docs/decisions.md` for established technical decisions.
4. Inspect the relevant Git history and current working tree.
5. If available, use Graphify to understand existing dependencies before exploring large portions of the codebase.

Useful Graphify commands:

```bash
graphify query "How does this subsystem work?"
graphify explain "RelevantSymbol"
graphify path "SourceSymbol" "TargetSymbol"
```

If the graph is missing or stale, refresh it with `graphify update .`. Never treat generated graph information as more authoritative than current source code.

## 3. Agent collaboration rules

Multiple agents may operate on this repository concurrently.

- Assume another contributor may be editing a different part of the codebase.
- Prefer tasks with clearly separated file ownership.
- Before beginning a substantial change, communicate the intended scope and affected files to the human operator.
- Never overwrite or revert another contributor's work without explicit authorisation.
- Never use destructive Git commands to resolve an unexpected working-tree state.
- Do not modify unrelated files simply to reformat or refactor them.
- Keep shared interfaces stable. Coordinate changes to API contracts, database schemas, configuration, and shared types.
- Prefer small, independently reviewable changes over large rewrites.
- Do not create commits, branches, or pull requests unless requested by the human operator or explicitly delegated for the task.

When an overlapping edit or conflicting requirement is discovered, stop the conflicting work and request coordination.

## 4. Architecture and design

- Follow the existing project structure and conventions.
- Keep modules cohesive and responsibilities clear.
- Prefer explicit interfaces between independently developed components.
- Avoid circular dependencies and hidden coupling.
- Do not introduce new frameworks without a concrete justification.
- Document significant architectural changes in `docs/architecture.md`.
- Record important trade-offs in `docs/decisions.md`.

When introducing a new integration, document:

- Its purpose.
- Its inputs and outputs.
- Its configuration requirements.
- Its failure behaviour.

## 5. Implementation standards

- Write readable, idiomatic code appropriate to the language.
- Use type annotations or static typing where supported.
- Handle errors explicitly at external boundaries.
- Validate untrusted input.
- Prefer existing project utilities over duplicate implementations.
- Avoid premature optimisation.
- Avoid speculative features not required by the task.
- Keep comments focused on non-obvious intent and constraints.
- Do not leave placeholder implementations represented as complete features.

## 6. Testing and verification

Before reporting completion:

1. Run the relevant formatter and linter, if configured.
2. Run tests covering the changed behaviour.
3. Run the project's type checker, if configured.
4. Verify that new integrations match their documented interfaces.
5. Inspect the diff for accidental changes.
6. Report any verification steps that could not be completed.

Add or update tests for meaningful behaviour changes.

Do not claim that tests pass unless they have actually been executed.

## 7. Git workflow

- `main` is the integration branch and should remain demonstrable.
- Use short-lived branches such as `feat/auth`, `feat/dashboard`, `fix/api-timeout`, or `chore/ci`.
- Prefer small pull requests with a clear purpose.
- Do not force-push shared branches.
- Do not commit secrets, local environment files, build outputs, or dependency directories.
- Do not use `git reset --hard`, `git clean -fd`, or similarly destructive operations without explicit permission.
- Keep commit messages descriptive; Conventional Commits are preferred.

For pull requests, summarise the change, verification performed, and any required coordination.

## 8. Parallel development boundaries

Where possible, divide work into independent areas such as:

- Frontend and user experience.
- Backend and business logic.
- Data, integrations, and persistence.
- Infrastructure, testing, and integration.

These are example workstreams, not permanent ownership assignments.

Changes crossing workstream boundaries should be agreed before implementation. Establish API contracts and shared data types early.

Avoid simultaneous edits to central configuration files, dependency manifests, database migrations, and shared interfaces.

## 9. Security and configuration

- Never commit credentials, tokens, private keys, or production secrets.
- Use environment variables for configuration.
- Maintain an `.env.example` containing placeholder values only.
- Avoid logging sensitive information.
- Do not execute untrusted downloaded scripts without inspection.
- Ask before making destructive database changes, deleting user data, deploying publicly, or incurring paid infrastructure costs.

## 10. Documentation and handoff

Keep documentation concise and useful.

Update the README when setup or usage changes.

Update architecture documentation when component responsibilities or interfaces change.

At the end of a task, provide:

- A summary of what changed.
- Important files modified.
- Tests or checks executed.
- Remaining limitations or risks.
- Any follow-up actions needed from other contributors.

## 11. Decision-making priorities

When requirements are ambiguous, prefer:

1. Correctness and a working demonstration.
2. Compatibility with existing interfaces.
3. Minimal implementation complexity.
4. Fast iteration and testability.
5. Extensibility only where clearly justified.

Ask for clarification when an ambiguity would materially affect architecture, interfaces, security, or other contributors' work.

## 12. Hackathon-specific guidance

- Keep the main branch in a demo-ready state.
- Build a complete vertical slice as early as possible.
- Prefer mocked external services when live integrations are unreliable.
- Keep a reproducible local development setup.
- Avoid large refactors close to the submission deadline.
- Prioritise integration and bug fixes as the deadline approaches.
- Do not sacrifice working functionality for speculative polish.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
