# 🧠 llm-agent-dock

**llm-agent-dock** is a modular, multi-arch Docker build system for **agentic coding assistants** such as *Cline*, *Codex*, and *Factory.AI Droid*.  
It provides a shared, “fat” base environment and builds thin layers for each assistant using a matrix.  

---

## 🚀 Goal

Simplify the deployment and development of LLM-powered coding tools by offering:
- Pre-built, ready-to-run environments for multiple assistants  
- Unified, reproducible base images  
- Automated **multi-architecture** builds (`amd64`, `arm64`)  
- Easy extension for new tools or environments  

---

## 🧩 Architecture Overview

Each image combines:
- One **base** (from a configurable list of public, pre-loaded OS images)
- One **agentic tool layer**

The project defines this matrix and builds all combinations.

---

## 🧰 Current Components

### Base Images (extendable)
1. `ghcr.io/catthehacker/ubuntu:act-latest`
2. `ghcr.io/devcontainers/images/universal:2-linux`
3. `ubuntu:24.04`

### Agent Tools (extendable)
1. `cline`
2. `codex`
3. `factory.ai droid`

---

## 🧱 Repository Structure

| Path | Purpose |
|------|----------|
| `scripts/` | Build helpers and local test utilities |
| `tests/` | Smoke tests for built images |
| `doc/ai/plan/` | Generated execution plans and logs |
| `AGENTS.md` | Agent definitions and responsibilities |
| `TASK.md` | Initial Codex directive |
| `README.md` | This document |

---

## 🧭 How to Extend

### Add a new base
1. Todo ...

### Add a new tool
1. Todo ...

---

## ⚙️ Automation

The AI agent coordinates:
- Subtask planning under `doc/ai/plan/`
- File generation (Dockerfiles, docs, scripts)
- Commit orchestration and task completion

See [AGENTS.md](./AGENTS.md) and [TASK.md](./TASK.md) for details.

---

## 📜 License

MIT — use freely, modify openly, credit appreciated.
