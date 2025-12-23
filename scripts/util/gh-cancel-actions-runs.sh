#!/usr/bin/env bash
set -euo pipefail

# Bulk-cancel *not completed* GitHub Actions workflow runs from a repo.
#
# Requirements: bash, curl, jq
#
# Auth:
#   - Classic PAT: scope "repo" (private repos need this; public repos still need write access)
#   - Fine-grained PAT: Repository -> Actions: write
#
# Usage:
#   GITHUB_TOKEN=... ./gh-cancel-actions-runs.sh OWNER REPO
#
# Optional env:
#   STATUS=                # only cancel runs with this status (default: unset)
#   EXCLUDE_STATUS=completed # cancel runs not matching this status (default: completed)
#   CONCURRENCY=1          # cancel in parallel (default: 1)
#   DRY_RUN=1              # print what would be canceled (default: 0)
#   API=https://api.github.com

OWNER="${1:?owner required}"
REPO="${2:?repo required}"

: "${GITHUB_TOKEN:?set GITHUB_TOKEN}"
API="${API:-https://api.github.com}"
STATUS="${STATUS:-}"
EXCLUDE_STATUS="${EXCLUDE_STATUS:-completed}"
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

cancel_run() {
  local run_id="$1"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "DRY_RUN cancel run_id=${run_id}"
    return 0
  fi

  # 202 = accepted
  curl -fsS -o /dev/null -w "%{http_code}\n" "${hdrs[@]}" \
    -X POST "${API}/repos/${OWNER}/${REPO}/actions/runs/${run_id}/cancel" \
  | awk -v id="$run_id" '
      $1=="202"{print "canceled run_id="id; next}
      {print "FAILED run_id="id" http="$1; exit 1}
    '
}

export -f cancel_run
export OWNER REPO API STATUS EXCLUDE_STATUS CONCURRENCY DRY_RUN
export GITHUB_TOKEN

page=1
while :; do
  json="$(list_runs_page "$page")"

  # Stop when there are no more runs.
  count="$(jq -r '.workflow_runs | length' <<<"$json")"
  [[ "$count" == "0" ]] && break

  jq -r --arg st "$STATUS" --arg ex "$EXCLUDE_STATUS" '
    .workflow_runs[]
    | select(($st != "") ? (.status == $st) : (($ex == "") or (.status != $ex)))
    | .id
  ' <<<"$json" \
  | xargs -n1 -P "${CONCURRENCY}" bash -c 'cancel_run "$@"' _

  page=$((page + 1))
done
