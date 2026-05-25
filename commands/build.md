---
description: Implement the next task incrementally — build, test, verify, commit
agent: tezcatlipoca
---

Invoke the @skills/incremental-implementation/SKILL.md alongside @skills/test-driven-development/SKILL.md.

## Related Skills
Skills that complement the build workflow:

- **Code Quality**: @skills/solid/SKILL.md — Apply SOLID principles, TDD, and clean code
- **Error Handling**: @skills/error-handling-patterns/SKILL.md — Implement resilient error handling patterns
- **UI/UX Implementation**: @skills/ui-ux-design-pro/SKILL.md — Implement UI from design specifications
- **Frontend Consistency**: @skills/design-taste-frontend/SKILL.md — Validate visual consistency and design quality
- **Shell Scripts**: @skills/bash-defensive-patterns/SKILL.md — Write robust shell scripts with defensive patterns
- **Domain Logic**: @skills/clean-ddd-hexagonal/SKILL.md — Implement domain logic using DDD and Clean Architecture

---

Pick the next pending task from the plan. For each task:

1. Read the task's acceptance criteria
2. Load relevant context (existing code, patterns, types)
3. Write a failing test for the expected behavior (RED)
4. Implement the minimum code to pass the test (GREEN)
5. Run the full test suite to check for regressions
6. Run the build to verify compilation
7. Commit with a descriptive message
8. Mark the task complete and move to the next one

If any step fails, follow the @skills/debugging-and-error-recovery/SKILL.md.