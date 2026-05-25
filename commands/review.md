---
description: Conduct a five-axis code review — correctness, readability, architecture, security, performance
agent: huitzilopochtli
---

Invoke the @skills/code-review-and-quality/SKILL.md.

## Related Skills
Skills that complement the review workflow:

- **Code Quality**: @skills/solid/SKILL.md — Evaluate code using SOLID principles and clean code
- **Error Handling**: @skills/error-handling-patterns/SKILL.md — Review error handling and resilience patterns
- **Design Patterns**: @skills/design-patterns/SKILL.md — Review use of design patterns and architectural decisions
- **Refactoring**: @skills/refactoring-patterns/SKILL.md — Apply named refactoring transformations for structural improvements
- **Frontend Review**: @skills/design-taste-frontend/SKILL.md — Review frontend for visual consistency and design quality

---

Review the current changes (staged or recent commits) across all five axes:

1. **Correctness** — Does it match the spec? Edge cases handled? Tests adequate?
2. **Readability** — Clear names? Straightforward logic? Well-organized?
3. **Architecture** — Follows existing patterns? Clean boundaries? Right abstraction level?
4. **Security** — Input validated? Secrets safe? Auth checked? (Use @skills/security-and-hardening/SKILL.md)
5. **Performance** — No N+1 queries? No unbounded ops? (Use @skills/performance-optimization/SKILL.md)

Categorize findings as Critical, Important, or Suggestion.
Output a structured review with specific file:line references and fix recommendations.