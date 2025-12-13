#!/usr/bin/env bash
set -euo pipefail

# Bulk-delete *completed* GitHub Actions workflow runs from a repo.
#
# Requirements: bash, curl, jq
#
# Auth:
#   - Classic PAT: scope "repo" (private repos need this; public repos still need write access to delete)
#   - Fine-grained PAT: Repository -> Actions: write
#
# Usage:
#   GITHUB_TOKEN=... ./gh-delete-actions-runs.sh OWNER REPO
#
# Optional env:
#   STATUS=completed        # only delete runs with this status (default: completed)
#   CONCURRENCY=1           # delete in parallel (default: 1)
#   DRY_RUN=1               # print what would be deleted (default: 0)
#   API=https://api.github.com

OWNER="${1:?owner required}"
REPO="${2:?repo required}"

: "${GITHUB_TOKEN:?set GITHUB_TOKEN}"
API="${API:-https://api.github.com}"
STATUS="${STATUS:-completed}"
CONCURRENCY="${CONCURRENCY:-1}"
DRY_RUN="${DRY_RUN:-0}"

hdrs=(
  -H "Accept: application/vnd.github+json"
  -H "Authorization: Bearer ${GITHUB_TOKEN}"
  -H "X-GitHub-Api-Version: 2022-11-28"
)

list_runs_page() {
  local page="$1"
  curl -fsSL "${hdrs[@]}" \
    "${API}/repos/${OWNER}/${REPO}/actions/runs?per_page=100&page=${page}"
}

delete_run() {
  local run_id="$1"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "DRY_RUN delete run_id=${run_id}"
    return 0
  fi

  # 204 = deleted
  curl -fsS -o /dev/null -w "%{http_code}\n" "${hdrs[@]}" \
    -X DELETE "${API}/repos/${OWNER}/${REPO}/actions/runs/${run_id}" \
  | awk -v id="$run_id" '
      $1=="204"{print "deleted run_id="id; next}
      {print "FAILED run_id="id" http="$1; exit 1}
    '
}

export -f delete_run
export OWNER REPO API STATUS DRY_RUN
export GITHUB_TOKEN

page=1
while :; do
  json="$(list_runs_page "$page")"

  # Stop when there are no more runs.
  count="$(jq -r '.workflow_runs | length' <<<"$json")"
  [[ "$count" == "0" ]] && break

  # Pick run IDs you want to delete:
  # - default: only completed runs (STATUS=completed)
  # If you really want *everything*, set STATUS="" and remove the select() below.
  while IFS= read -r rid; do
    delete_run "$rid"
  done < <(
    jq -r --arg st "$STATUS" '
      .workflow_runs[]
      | select(($st == "") or (.status == $st))
      | .id
    ' <<<"$json"
  )

  page=$((page + 1))
done
