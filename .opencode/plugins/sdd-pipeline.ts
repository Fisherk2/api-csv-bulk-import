import type { Plugin } from "@opencode-ai/plugin"
import { readFileSync, writeFileSync, existsSync, mkdirSync, appendFileSync } from "fs"
import { join } from "path"

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SddState {
  pipeline_phase: string
  active_spec: string | null
  current_task: string | null
  completed_tasks: string[]
  pending_tasks: string[]
  agent_type: string
}

interface MessageEvent {
  message?: { content?: string }
  parts?: unknown[]
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const INTENT_PATTERNS: Record<string, string[]> = {
  "/spec": [
    "nueva feature", "requisito", "idea", "necesito", "quiero crear",
    "new feature", "requirement", "spec", "especificacion", "especifica",
    "create", "define", "write spec", "documentation", "specification",
    "what should", "design", "describe", "proposal", "need a feature",
  ],
  "/plan": [
    "planifica", "divide", "tasks", "plan", "divide en tareas",
    "divide en", "desglosa", "breakdown",
    "task breakdown", "planning", "organize", "steps", "milestones",
    "task list", "todos", "to-do", "story points", "estimate",
  ],
  "/build": [
    "implementa", "codifica", "construye", "implement", "build", "code",
    "escribe el codigo", "escribe codigo",
    "write code", "create file", "add functionality", "make", "generate",
    "develop", "produce", "set up", "scaffold", "boilerplate",
    "create function", "create class", "create module", "create component",
  ],
  "/test": [
    "test", "prueba", "pruebas", "testing",
    "unit test", "integration test", "e2e", "specs", "coverage",
    "assert", "mock", "stub", "tdd", "red-green",
  ],
  "/review": [
    "revisa", "review", "codigo", "code review", "revisar codigo",
    "code quality", "audit", "inspect", "check code", "verify code",
    "static analysis", "lint", "clean code", "best practices",
  ],
  "/ship": [
    "ship", "deploy", "lanza", "lanzamiento", "deployment", "publicar",
    "release", "publish", "launch", "go live", "rollout",
    "staging", "production", "ci/cd", "pipeline", "deliver",
  ],
  "/code-simplify": [
    "simplifica", "refactor", "limpia", "simplify", "simplificar",
    "simplify code", "clean up", "refactor code", "improve code",
    "technical debt", "complex", "duplicate", "extract method",
    "reduce complexity", "make it simpler", "cleanup",
  ],
}

const DESTRUCTIVE_PATTERNS = ["rm -rf", "git push --force", "DROP TABLE", "DROP DATABASE"]

const AGENT_DETECT_PATTERNS: Record<string, RegExp[]> = {
  huitzilopochtli: [/GENERAL PURPOSE AGENT/],
  quetzalcoatl: [/ARCHITECT OF SPECIFICATIONS PLANNER/, /Planning & Documentation Architect/],
  tezcatlipoca: [/PLAN EXECUTER/, /BUILD-MODE Agent/],
}

const SPEC_SECTIONS = ["objective", "commands", "structure", "code style", "testing", "boundaries"]

const MAX_AUDIT_LINES = 500

// ---------------------------------------------------------------------------
// Plugin
// ---------------------------------------------------------------------------

export const SddPipelinePlugin: Plugin = async (ctx) => {
  const { directory } = ctx

  // ── Paths ────────────────────────────────────────────────────────────────
  const projectDir = directory || process.cwd()
  const pluginsDir = join(projectDir, ".opencode", "plugins")
  const statePath = join(pluginsDir, ".sdd-state.json")
  const auditLogPath = join(pluginsDir, ".sdd-audit.log")

  // ── Load persisted SDD state ─────────────────────────────────────────────
  const defaultState: SddState = {
    pipeline_phase: "idle",
    active_spec: null,
    current_task: null,
    completed_tasks: [],
    pending_tasks: [],
    agent_type: "unknown",
  }

  const sddState: SddState = { ...defaultState }
  try {
    if (existsSync(statePath)) {
      const saved = JSON.parse(readFileSync(statePath, "utf-8"))
      Object.assign(sddState, saved)
    }
  } catch {
    // Corrupted state — use defaults
  }

  // ── Helpers ──────────────────────────────────────────────────────────────

  const saveState = () => {
    try {
      if (!existsSync(pluginsDir)) mkdirSync(pluginsDir, { recursive: true })
      writeFileSync(statePath, JSON.stringify(sddState, null, 2))
    } catch {
      // Ignore write errors
    }
  }

  const audit = (source: string, detail: string) => {
    try {
      const timestamp = new Date().toISOString()
      const entry = `[${timestamp}] [${source}] ${detail}\n`

      // Rotate if file exceeds max lines (keeps most recent half)
      if (existsSync(auditLogPath)) {
        const content = readFileSync(auditLogPath, "utf-8")
        const lines = content.split("\n")
        if (lines.length >= MAX_AUDIT_LINES) {
          writeFileSync(auditLogPath, lines.slice(-(MAX_AUDIT_LINES / 2)).join("\n") + "\n")
        }
      }

      appendFileSync(auditLogPath, entry)
    } catch {
      // Ignore logging errors
    }
  }

  // ── Agent detection ────────────────────────────────────────────────────

  const detectAgentType = (systemParts: string[]): string => {
    for (const part of systemParts) {
      for (const [agentType, patterns] of Object.entries(AGENT_DETECT_PATTERNS)) {
        if (patterns.some((p) => p.test(part))) {
          return agentType
        }
      }
    }
    return "unknown"
  }

  // ── Build role rules per agent type ────────────────────────────────────

  const buildRoleRules = (): string[] => {
    switch (sddState.agent_type) {
      case "huitzilopochtli":
        return [
          "### Role Rules",
          "You are the **General Purpose Agent** — full lifecycle across domains.",
          "- Research, plan, write code, document, execute. No SDD restrictions apply.",
          "- You have write/edit access. Use it responsibly.",
        ]
      case "quetzalcoatl":
        return [
          "### Role Rules",
          "You are the **Architect of Specifications** — PLANNING & DOCUMENTATION MODE.",
          "- Read, plan, design, review, document. NEVER write or edit code.",
          "- Produce specs, plans, ADRs, diagrams, and documentation only.",
        ]
      case "tezcatlipoca":
        return [
          "### Role Rules",
          "You are the **Build Agent** — BUILD MODE.",
          "- Implement, build, test, configure, execute plans.",
          "- Write code, run tests. NEVER modify SPEC.md or specs/ files.",
        ]
      default:
        return [
          "### Role Rules",
          `Operating as: **${sddState.agent_type}**.`,
          "If you are an analysis agent: read, plan, review. NEVER write code.",
          "If you are an implement agent: build, test. NEVER modify specs.",
        ]
    }
  }

  // ── Build injected context strings ───────────────────────────────────────

  const buildSddContext = (): string => {
    const lines = [
      "## SDD Pipeline State",
      `- Phase: ${sddState.pipeline_phase}`,
      `- Active spec: ${sddState.active_spec ?? "none"}`,
      `- Current task: ${sddState.current_task ?? "none"}`,
      `- Agent type: ${sddState.agent_type}`,
      `- Completed: ${sddState.completed_tasks.join(", ") || "none"}`,
      `- Pending: ${sddState.pending_tasks.join(", ") || "none"}`,
      "",
      "---",
      "",
      ...buildRoleRules(),
    ]
    return lines.join("\n")
  }

  // ── Hooks ────────────────────────────────────────────────────────────────

  return {

    /**
     * Fires before each LLM call to build the system prompt.
     * Injects SDD pipeline state so the agent
     * always has the orchestration guides available from the FIRST message.
     */
    "experimental.chat.system.transform": async (
      _input: unknown,
      output: unknown,
    ) => {
      try {
        const out = output as { system: string[] }

        // Detect which agent persona is active from system prompt parts
        const detected = detectAgentType(out.system)
        if (detected !== sddState.agent_type) {
          sddState.agent_type = detected
          saveState()
          audit("system.transform", `Agent detected and persisted: ${detected}`)
        }

        // Inject SDD state at the beginning so it appears early in the system prompt
        out.system.unshift(buildSddContext())
        audit("system.transform", `Injected SDD state (agent: ${sddState.agent_type})`)
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err)
        console.error("[sdd-pipeline] Error in system.transform:", msg)
      }
    },

    /**
     * Fires when a new message is received.
     * Detects user intent and suggests the matching SDD slash command.
     */
    "chat.message": async (
      _input: unknown,
      output: unknown,
    ) => {
      try {
        const out = output as MessageEvent
        const content = out?.message?.content ?? ""
        if (!content) return

        const lower = content.toLowerCase()
        for (const [command, keywords] of Object.entries(INTENT_PATTERNS)) {
          if (keywords.some((kw) => lower.includes(kw))) {
            console.log(
              `[sdd-pipeline] Intent detected: "${command}" — type ${command} to proceed`,
            )
            audit("chat.message", `intent=${command}`)
            break
          }
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err)
        console.error("[sdd-pipeline] Error in chat.message:", msg)
      }
    },

    /**
     * Fires before a tool executes.
     * Blocks destructive commands and enforces quetzalcoatl/tezcatlipoca role separation.
     */
    "tool.execute.before": async (
      input: unknown,
      output: unknown,
    ) => {
      const inp = input as { tool?: string } | undefined
      const out = output as { args?: Record<string, unknown> } | undefined

      try {
        const tool = inp?.tool ?? ""
        const args = out?.args ?? {}

        // --- Always block destructive commands ---
        if (tool === "Bash" || tool === "bash") {
          const cmd = (args.command as string) ?? ""
          for (const pattern of DESTRUCTIVE_PATTERNS) {
            if (cmd.includes(pattern)) {
              audit("tool.before", `BLOCKED ${tool}: destructive command`)
              throw new Error(
                "[sdd-pipeline] Destructive command blocked. Use safe alternatives.",
              )
            }
          }
        }

        // --- Block quetzalcoatl agents from writing code ---
        if (sddState.agent_type === "quetzalcoatl") {
          if (tool === "Edit" || tool === "Write") {
            audit("tool.before", `BLOCKED ${tool}: quetzalcoatl agent writing code`)
            throw new Error(
              "[sdd-pipeline] Quetzalcoatl agent cannot write code. Switch to BUILD mode with /build.",
            )
          }
        }

        // --- Block tezcatlipoca agents from modifying specs ---
        if (sddState.agent_type === "tezcatlipoca") {
          const filePath = ((args.filePath ?? args.file) as string) ?? ""
          if (filePath.includes("SPEC.md") || filePath.includes("specs/")) {
            audit("tool.before", `BLOCKED ${tool}: tezcatlipoca agent modifying specs`)
            throw new Error(
              "[sdd-pipeline] Tezcatlipoca agent cannot modify specs. Use /spec to request changes.",
            )
          }
        }
      } catch (err: unknown) {
        // Re-throw our own blocking errors; log everything else
        if (err instanceof Error && err.message.includes("sdd-pipeline")) throw err
        const msg = err instanceof Error ? err.message : String(err)
        console.error("[sdd-pipeline] Error in tool.before:", msg)
      }
    },

    /**
     * Fires after a tool returns a result.
     * Lightweight audit logging.
     */
    "tool.execute.after": async (
      input: unknown,
    ) => {
      try {
        const inp = input as { tool?: string } | undefined
        audit("tool.after", `${inp?.tool ?? "unknown"} completed`)
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err)
        console.error("[sdd-pipeline] Error in tool.after:", msg)
      }
    },

    /**
     * Fires during context compaction.
     * Persists the SDD pipeline state.
     */
    "experimental.session.compacting": async (
      _input: unknown,
      output: unknown,
    ) => {
      try {
        const out = output as { context?: string[] }

        out.context?.push(buildSddContext())

        // Persist state on compaction (replaces the missing session.ended hook)
        saveState()
        audit("session.compacting", "Injected SDD state + persisted state")
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err)
        console.error("[sdd-pipeline] Error in session.compacting:", msg)
      }
    },
  }
}

export default SddPipelinePlugin
