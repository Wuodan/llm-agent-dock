#!/usr/bin/env bash
set -euo pipefail

# Count and sanity-check Docker Hub tags for wuodan/aicage against your expected base/tool matrix.
# Assumptions:
# - Tag names contain BOTH the tool token and the base token somewhere in the tag name
#   (e.g. "codex-ubuntu-latest", "cline-debian-0.0.1", etc.)
# - If your tag scheme differs, adjust match_tag() below.

repo="wuodan/aicage"
page_size=100

bases=(act ubuntu fedora node alpine debian)
tools=(claude copilot cline codex qwen droid opencode goose gemini)

fetch_all_tags() {
  local url="https://hub.docker.com/v2/repositories/${repo}/tags/?page_size=${page_size}"
  while [[ -n "$url" && "$url" != "null" ]]; do
    local json
    json="$(curl -fsSL "$url")"
    echo "$json" | jq -r '.results[].name'
    url="$(echo "$json" | jq -r '.next')"
  done
}

# Echo "tool base" if tag matches exactly one tool and exactly one base, else return non-zero.
match_tag() {
  local tag="$1"
  local t="" b=""

  for x in "${tools[@]}"; do
    if [[ "$tag" == *"$x"* ]]; then
      if [[ -n "$t" && "$t" != "$x" ]]; then
        return 1  # ambiguous tool
      fi
      t="$x"
    fi
  done

  for x in "${bases[@]}"; do
    if [[ "$tag" == *"$x"* ]]; then
      if [[ -n "$b" && "$b" != "$x" ]]; then
        return 1  # ambiguous base
      fi
      b="$x"
    fi
  done

  [[ -n "$t" && -n "$b" ]] || return 1
  printf "%s %s\n" "$t" "$b"
}

main() {
  mapfile -t tags < <(fetch_all_tags | sort -u)
  echo "Remote unique tag count: ${#tags[@]}"
  echo

  # Matched matrix
  declare -A seen

  # Counters (must be associative; initialize explicitly under `set -u`)
  declare -A per_base=()
  declare -A per_tool=()

  declare -a unmatched=()

  for tag in "${tags[@]}"; do
    if out="$(match_tag "$tag" 2>/dev/null)"; then
      tool="${out%% *}"
      base="${out##* }"
      seen["$tool|$base"]=1

      : "${per_base["$base"]:=0}"
      : "${per_tool["$tool"]:=0}"
      per_base["$base"]=$(( per_base["$base"] + 1 ))
      per_tool["$tool"]=$(( per_tool["$tool"] + 1 ))
    else
      unmatched+=("$tag")
    fi
  done

  echo "Tags per base (matched by substring):"
  for b in "${bases[@]}"; do
    printf "  %-8s %s\n" "$b" "${per_base[$b]:-0}"
  done
  echo

  echo "Tags per tool (matched by substring):"
  for t in "${tools[@]}"; do
    printf "  %-8s %s\n" "$t" "${per_tool[$t]:-0}"
  done
  echo

  echo "Missing combinations (expected 9 tools per base => 54 combos):"
  missing=0
  for b in "${bases[@]}"; do
    for t in "${tools[@]}"; do
      if [[ -z "${seen["$t|$b"]+x}" ]]; then
        echo "  missing: tool=$t base=$b"
        missing=$((missing + 1))
      fi
    done
  done
  echo "Missing combo count: $missing"
  echo

  if ((${#unmatched[@]} > 0)); then
    echo "Unmatched/ambiguous tags (didn't map cleanly to exactly 1 tool + 1 base):"
    printf '  %s\n' "${unmatched[@]}"
    echo
    echo "If these are valid tags, your naming scheme likely doesn't include plain tool/base tokens."
    echo "Adjust match_tag() to parse your actual tag format."
  fi
}

main "$@"
