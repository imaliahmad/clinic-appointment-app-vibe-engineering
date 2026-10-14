#!/usr/bin/env bash
# Stop hook: runs when Claude finishes a turn.
# Exit 0 = let Claude finish. Exit 2 = tests failed; output goes back to Claude to fix.

cd "$CLAUDE_PROJECT_DIR" || exit 0

# Skip if no Python file changed (modified or new). Needs a git repo.
if [ -z "$(git status --porcelain -- '*.py' 2>/dev/null)" ]; then
  exit 0
fi

uv run pytest -q -x >&2
rc=$?

# 0 = all passed, 5 = no tests collected yet (early in the project)
if [ "$rc" -eq 0 ] || [ "$rc" -eq 5 ]; then
  exit 0
fi

echo "Tests failed. Fix the code (not the tests, unless a test is wrong) before finishing." >&2
exit 2
