# IDEAS — Git config & commit signing (GPG / SSH)

This document summarizes the agreed, **practical** approach for detecting Git commit signing on the host and deciding **what to mount into a container** so `git commit` works without surprises.

The focus is:
- do not guess paths
- ask Git / GnuPG what they actually use
- work repo-first, not global-first

---

## 1. Git config: where is the *effective* global config?

Do **not** assume `~/.gitconfig`.

Git may use:
- `~/.gitconfig`
- `$XDG_CONFIG_HOME/git/config`
- an explicit `GIT_CONFIG_GLOBAL`

### Reliable way (Git is the source of truth)

```bash
git config --global --show-origin --list 2>/dev/null   | sed -n 's|^file:\([^[:space:]]*\).*|\1|p'   | sed -n '1p'
```

Result:
- absolute path to the **actual** global config file Git is using

This path can safely be mounted read-only into the container.

---

## 2. Do I need signing at all? (repo-effective check)

Do **not** care where the setting comes from (global vs local).

What matters is: *will Git try to sign in this repo?*

### Canonical check (effective value)

```bash
git config commit.gpgsign
```

- `true`  → Git **will** try to sign commits
- empty / `false` → no signing required

This works because:
- Git merges system + global + local + worktree config
- the repo directory is mounted anyway, so local config is visible in-container

---

## 3. Which signing method is used? (GPG vs SSH)

### Check signing backend

```bash
git config gpg.format
```

- empty / unset → **GPG (openpgp)**  ← default
- `ssh`         → **SSH signing**

You only need to check this **if** `commit.gpgsign=true`.

---

## 4. GPG signing (classic, default)

### Where are the keys?

There is **no fixed path**. Ask GnuPG:

```bash
gpgconf --list-dirs homedir
```

Typical results:
- Linux/macOS: `~/.gnupg`
- Windows (Gpg4win): `%APPDATA%\gnupg`

This directory contains:
- private keys
- trustdb
- gpg.conf
- agent config

### What to mount

Mount the directory returned by `gpgconf` into the container user’s home:

```text
host:<GNUPGHOME>  →  container:/home/<user>/.gnupg
```

### Do I need to mount a gpg-agent socket?

**No. Not required.**

Facts:
- `gpg-agent` is auto-started by `gpg`
- Git does *not* require the agent to be running beforehand
- Mounting sockets is only useful if you want to reuse the *host* agent
  (cached passphrases, smartcards, etc.)

**Cross-platform rule:**
- Linux host → optional, advanced
- Windows host → not usable / don’t try
- Default: **do not mount agent sockets**

### What must be in the image

Minimum:
- `gpg`
- `gpg-agent`
- one `pinentry` (e.g. `pinentry-curses`)
- TTY (`docker run -it`) if passphrase prompting is needed

---

## 5. SSH signing (less common, but real)

SSH signing is enabled if:

```bash
git config gpg.format
# → ssh
```

In this case:
- Git uses `ssh-keygen -Y sign`
- GPG is not involved

### Where are the keys?

Usually:
```
~/.ssh
```

(There is no standard command like `gpgconf` for this; SSH signing reuses normal SSH keys.)

### What to mount

```text
host:~/.ssh  →  container:/home/<user>/.ssh
```

Read-only is usually sufficient.

---

## 6. Recommended decision logic (host side)

Pseudocode:

```text
if git config commit.gpgsign == true:
    if git config gpg.format == ssh:
        mount ~/.ssh
    else:
        mount $(gpgconf --list-dirs homedir)
mount resolved global git config file
```

Notes:
- repo-local config is already available via the repo mount
- no need to distinguish global vs local signing config
- no need to pre-start gpg-agent

---

## 7. Why this approach is correct

- Uses **Git’s effective config**, not guesses
- Works the same on Linux, macOS, Windows
- Works in CI and containers
- Avoids fragile path assumptions
- Matches Git / GnuPG behavior exactly

---

## 8. Explicit non-goals

This approach does **not** try to:
- detect manual `git commit -S`
- forward host gpg-agent sockets by default
- reimplement Git’s config precedence rules

Those are either edge cases or unnecessary complexity.

---

## Bottom line

- Ask Git if signing is needed (`commit.gpgsign`)
- Ask Git *how* it signs (`gpg.format`)
- Ask GnuPG where keys live (`gpgconf`)
- Mount only what is actually required

This is the minimal, robust, cross-platform solution.
