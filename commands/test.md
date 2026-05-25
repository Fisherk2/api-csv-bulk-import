---
description: Run TDD workflow — write failing tests, implement, verify. For bugs, use the Prove-It pattern.
agent: tezcatlipoca
---

Invoke the @skills/test-driven-development/SKILL.md.

## Related Skills
Skills that complement the testing workflow:

- **Error Handling Tests**: @skills/error-handling-patterns/SKILL.md — Test error paths and resilience patterns
- **Visual Consistency**: @skills/design-taste-frontend/SKILL.md — Verify visual consistency and design quality in frontend

## Escalation to Incident Response
If debugging detects a **production incident** (e.g., users affected, service degradation), escalate to:
- @skills/incident-response/SKILL.md — Incident triage, communication, and postmortem workflow

---

For new features:
1. Write tests that describe the expected behavior (they should FAIL)
2. Implement the code to make them pass
3. Refactor while keeping tests green

For bug fixes (Prove-It pattern):
1. Write a test that reproduces the bug (must FAIL)
2. Confirm the test fails
3. Implement the fix
4. Confirm the test passes
5. Run the full test suite for regressions

For browser-related issues, also invoke @skills/browser-testing-with-devtools/SKILL.md to verify with Chrome DevTools MCP.