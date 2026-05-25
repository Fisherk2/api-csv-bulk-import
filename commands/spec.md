---
description: Start spec-driven development — write a structured specification before writing code
agent: quetzalcoatl
---

## PRE-FLIGHT Checks
Before starting the spec, perform these checks:

1. **Agent Instructions Length** (`agent-md-refactor`):
   - Check if `AGENTS.md` exceeds 200 lines.
   - If so, suggest running @skills/agent-md-refactor/SKILL.md to refactor it before proceeding.

2. **README Existence** (`crafting-effective-readmes`):
   - Check if a `README.md` exists in the project root.
   - If not, suggest running @skills/crafting-effective-readmes/SKILL.md to create one.

---

Invoke the @skills/spec-driven-development/SKILL.md.

## Related Skills
Skills that complement the spec workflow:

- **Backend Architecture**: @skills/clean-ddd-hexagonal/SKILL.md — Clean Architecture + DDD + Hexagonal patterns
- **Design Patterns**: @skills/design-patterns/SKILL.md — GoF and enterprise patterns for recurring problems
- **Architecture Diagrams**: @skills/architecture-diagrams/SKILL.md — Document system architecture with Mermaid/PlantUML/C4
- **UI/UX Design**: @skills/ui-ux-design-pro/SKILL.md — Professional UI/UX design with design systems and high-fidelity prototyping

---

Begin by understanding what the user wants to build. Ask clarifying questions about:
1. The objective and target users
2. Core features and acceptance criteria
3. Tech stack preferences and constraints
4. Known boundaries (what to always do, ask first about, and never do)

Then generate a structured spec covering all six core areas: objective, commands, project structure, code style, testing strategy, and boundaries.

Save the spec as `SPEC.md` in the project root and confirm with the user before proceeding.