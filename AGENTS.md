# Repository guidance

These are repository defaults. Explicit task requirements take precedence. If an instruction conflicts with architecture or safety, stop and report the conflict instead of silently redesigning the system.

## Architecture

- Deterministic calculations belong in Python, SQL, or analytics code. LLMs handle intent, planning, orchestration, interpretation, and communication.
- Keep provider-specific SDK logic at the provider/LLM boundary.
- Prefer the existing modular monolith and small, measured changes over speculative abstractions.
- See [architecture](docs/architecture.md), [agent workflow](docs/agentic-workflow.md), and [tool system](docs/tool-system.md) for details.

## Tool failures and privacy

- `ToolExecutionError` is an expected, controlled domain failure; preserve its authored message in the failed `ToolResult`.
- `BaseTool.execute()` converts unexpected ordinary exceptions to `ToolResult(error="Tool execution failed.")`. Do not catch `BaseException`; `KeyboardInterrupt` and `SystemExit` must propagate.
- Never log raw tool arguments or outputs, prompts, secrets, or raw exception/error text from unexpected failures.
- Request IDs, step numbers, tool names, success/failure status, and aggregate counts are acceptable where established. See [observability guidance](docs/observability).

## Verification and dependencies

- Standard checks: `python -m ruff check .` and `python -m pytest -q`. Run `git diff --check` before completion.
- Do not use Ruff `--fix` unless the task explicitly calls for mutation/fixing.
- `pyproject.toml` contains direct dependencies; `requirements.lock` and `requirements-dev.lock` are generated artifacts. Do not add dependencies without demonstrated need.
- CI workflows are the source of truth for specialized checks, lock freshness, and pinned tooling; see [CI](.github/workflows/ci.yml).

## Changes and Git

- Keep diffs minimal and scoped. Inspect `git status` and diffs before proposing completion, and preserve unrelated pre-existing work.
- Do not stage, commit, push, or deploy unless explicitly authorized. Avoid broad staging such as `git add .` unless explicitly requested.

## Deployment safety

- The [deployment workflow](.github/workflows/deploy.yml) is the source of truth. Preserve GitHub OIDC and exact tested-SHA deployment behavior; do not introduce static AWS credentials.
- Do not add or change ECS desired count unless the task explicitly requires it. Avoid unnecessary cloud cost.
