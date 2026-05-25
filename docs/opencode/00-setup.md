# OpenCode Setup

This guide explains how to configure OpenCode for this template — slash commands, agent personas, skills, and the complete SDD workflow.

> **For a complete reference of all skills and commands**, see [USER_GUIDE.md](../../USER_GUIDE.md).

---

## Prerequisites

- **OpenCode IDE** — The only IDE compatible with this template
- **Node.js >= 18** and **bun**
- **Git**

---

## What OpenCode Does Automatically

### 1. Loads Slash Commands

The `commands/` directory is automatically detected by OpenCode. Type `/` in the chat to see all available commands:

| Command | Phase | What it does |
|---------|-------|--------------|
| `/spec` | DEFINE | Creates a structured specification before writing code |
| `/plan` | PLAN | Breaks specifications into small, ordered tasks |
| `/build` | BUILD | Incremental implementation with TDD |
| `/test` | VERIFY | Writes failing tests, implements, refactors |
| `/review` | REVIEW | Multi-axis code review before merge |
| `/code-simplify` | REVIEW | Simplifies complex code without changing behavior |
| `/ship` | SHIP | Pre-launch checklist, gradual deployment, monitoring |

Commands also automatically trigger complementary skills. For example, `/build` activates `incremental-implementation` plus `solid`, `error-handling-patterns`, `ui-ux-design-pro`, and others depending on the task.

### 2. Provides Agent Personas

The `agents/` directory contains **99 agents**: 3 primary agents (SDD orchestration) and 96 specialized subagents. The 3 main agents are directly invocable:

- `huitzilopochtli` — General purpose, full lifecycle in any domain
- `quetzalcoatl` — Architect of Specifications: analyze, design, plan
- `tezcatlipoca` — Build Agent: execute validated implementation plans

> For the complete subagent catalog (90+ specialists in frontend, backend, devops, testing, security, etc.), see [09-agent-index.md](./09-agent-index.md).

Commands like `/review` and `/ship` automatically compose multiple agents.

### 3. Discovers Skills

The 43 skills live in `skills/<skill-name>/SKILL.md`. OpenCode agents receive instructions (via `AGENTS.md`) to:

1. Detect when a skill applies to the current task
2. Load the skill using the built-in `skill` tool
3. Follow the skill's workflow step by step

Skills are activated both through slash commands and automatically based on context — designing an API activates `api-and-interface-design`, building UI activates `frontend-ui-engineering`, debugging activates `debugging-and-error-recovery`, and so on.

---

## First Steps After Opening the Project

### 1. Install Plugin Dependencies

```bash
cd .opencode && bun install && cd ..
```

### 2. Configure Context7 (Optional but Recommended)

Context7 provides up-to-date documentation for any library or framework:

```bash
npx ctx7@latest setup
```

Once configured, the `find-docs` skill automatically retrieves current API documentation when you ask about any library.

### 3. Start with the Meta-Skill

Load the [Meta-Skill](../../skills/using-agent-skills/SKILL.md) to discover which skill applies to your current task. It contains:
- A **decision tree** that maps task types (implement code, design API, debug, etc.) to the appropriate skill
- **Core operational behaviors** that apply to all skills (surface assumptions, manage confusion, object)
- A **Quick Reference** table that summarizes each skill by phase

> This is the canonical entry point for skill discovery. Both agents and humans should consult it when unsure which skill applies.

### 4. Run Your First Workflow

```bash
/spec "Describe what you want to build"
/plan
/build
/test
/review
/ship
```

---

> **📖 For the complete anatomy of skills (diagram, key principles, how skills work):** see [USER_GUIDE.md > Skills Reference](../../USER_GUIDE.md#skills-reference). This setup guide focuses only on OpenCode configuration.

---

## Configuration Files

### AGENTS.md

This file defines agent personas, their rules, and orchestration. It instructs agents to:
- Always check if a skill applies before acting
- Follow skills exactly when they apply
- Never skip required workflows (spec, plan, test)
- Surface assumptions and actively manage confusion

### .opencode/package.json

Contains the required OpenCode plugin dependency:

```json
{
  "dependencies": {
    "@opencode-ai/plugin": "1.15.0"
  }
}
```

---

## Troubleshooting

| Problem | Possible Cause | Solution |
|---------|----------------|----------|
| `/spec` doesn't work | Plugin not installed | Run `cd .opencode && bun install` |

> **For the complete troubleshooting table (Context7, skills, and more):** see [USER_GUIDE.md](../../USER_GUIDE.md#troubleshooting).

---

## Related Documentation

| Guide | Covers |
|------|--------|
| [Meta-Skill (using-agent-skills)](../../skills/using-agent-skills/SKILL.md) | Decision tree for skill discovery, core operational behaviors, failure modes, and Quick Reference index of all skills |
| [USER_GUIDE.md](../../USER_GUIDE.md) | Complete reference of the 43 skills, commands, and workflows |
| [08-orchestration-patterns.md](./08-orchestration-patterns.md) | Agent personas, orchestration patterns, and decision matrix |
| [09-agent-index.md](./09-agent-index.md) | Complete catalog of the 99 agents classified by domain |