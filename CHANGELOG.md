# Registro de Cambios (Changelog)

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Sin Lanzar]

## [2.1.2] - 2026-05-25

### Cambiado

#### Comandos — Agentes de Review y Ship Reasignados

- `commands/review.md` — Agente cambiado de `quetzalcoatl` a `huitzilopochtli`.
  - El comando `/review` ahora orquesta la revisión de código bajo el **General Purpose Agent**, permitiendo tanto análisis como correcciones directas.
  - Consistente con el flujo SDD donde `huitzilopochtli` maneja las fases mixtas (revisión + escritura) para finalizar especificaciones y ciclos de desarrollo.
- `commands/ship.md` — Agente cambiado de `quetzalcoatl` a `huitzilopochtli`.
  - El comando `/ship` ahora ejecuta el fan-out paralelo (code-reviewer, security-auditor, test-engineer) y la síntesis go/no-go bajo el **General Purpose Agent**, aprovechando su capacidad de orquestación multi-agente y escritura de documentación.

#### Configuración — Modelos Dedicados por Agente Primario

- `opencode.json` — Nuevo esquema de modelos para los 3 agentes primarios:
  - **Modelo principal**: `opencode/deepseek-v4-flash-free` → `opencode-go/kimi-k2.6`
  - `huitzilopochtli` → `opencode-go/qwen3.6-plus` (modelo dedicado para tareas full-lifecycle)
  - `quetzalcoatl` → `opencode-go/glm-5.1` (modelo analítico para planificación y especificaciones)
  - `tezcatlipoca` → `opencode-go/deepseek-v4-pro` (modelo para ejecución de builds y tests)
- Agentes `build` y `plan` legacy deshabilitados (`disable: true`) — ya reemplazados por el pipeline SDD.
- Agente `explore` actualizado: `opencode/nemotron-3-super-free` → `opencode-go/deepseek-v4-flash`.
- Agente `general` configurado con `opencode-go/minimax-m2.5`.

### Cambiado

#### Meta-Skill — Árbol de Descubrimiento Completado

- `skills/using-agent-skills/SKILL.md` — Añadidas 3 skills faltantes al árbol de descubrimiento y tabla Quick Reference:
  - `clean-code` — Rama en Implementing code ("Writing clean, readable code?") y Reviewing code ("Needs clean code practices?")
  - `code-simplification` — Rama en Reviewing code ("Code too complex?")
  - `deprecation-and-migration` — Rama en Deploying/launching ("Need to deprecate old code?")
- Conteo de skills en tabla Quick Reference corregido: 39 → **42 únicas** (+ 1 meta-skill = 43 total).

#### Documentación Consolidada

- `USER_GUIDE.md` — Reestructuración para eliminar duplicación:
  - Tabla de agentes primarios eliminada del Quick Start (ya existía en Agent Personas).
  - Tablas detalladas por fase (Define, Plan, Build, Verify, Review, Ship, Extra) reemplazadas por referencia al meta-skill como fuente canónica.
  - Sección Common Tasks movida a Skills Reference (Adding a New Skill) y Agent Personas (Adding a New Agent).
  - Documentación de formatos de agente y reglas unificada bajo Agent Personas.
- `README.md` — Actualizaciones menores:
  - Enlace a CONTRIBUTING.md con anchor específico (`#añadir-una-nueva-skill`).
  - Añadido enlace a USER_GUIDE.md en tabla de documentación.
  - Estilos de color Mermaid eliminados del diagrama de flujo.

#### Troubleshooting Expandido

- `USER_GUIDE.md` — Tabla de troubleshooting expandida de **4 a 8 filas**:
  - "Skills won't load": causa ampliada a sesión no reiniciada.
  - Nueva: "New skills not recognized" — reiniciar OpenCode tras instalar skills.
  - Nueva: "Agent not found or not available" — revisar `disable`/`hidden` en `opencode.json`.
  - Nueva: "Excel MCP won't start" — `uvx` no instalado o Python < 3.10.
  - Nueva: "Git push fails with repository moved" — URL remota desactualizada.
- `README.md` — Mismas 5 nuevas filas añadidas (traducidas al español).

#### Configuración

- `opencode.json` — Servidor Excel MCP cambiado de `"enabled": true` a `"enabled": false` para evitar errores en entornos sin `uvx` instalado.

### Corregido

- `docs/opencode/00-setup.md` — Conteo de skills corregido: 33 → **43** en dos referencias.
- `skills/using-agent-skills/SKILL.md` — 3 skills faltantes en árbol de descubrimiento y tabla Quick Reference (clean-code, code-simplification, deprecation-and-migration).

## [2.1.0] - 2026-05-24

### Cambios Importantes

Este lanzamiento representa una **reestructuración profunda** del ecosistema de agentes y la configuración del proyecto:

- **Catálogo completo de agentes**: Implementación de 90+ subagentes desde cero, reemplazando los 5 agentes especialistas anteriores por una arquitectura de 3 agentes primarios (huitzilopochtli, quetzalcoatl, tezcatlipoca) + 93 subagentes organizados por dominio.
- **Migración de agentes**: 108 agentes en revisión → 12 agentes con arquitectura SDD → 99+ agentes estandarizados con formato OpenCode.
- **Nueva orquestación**: Separación de orchestration-patterns.md y agent-index.md como documentos independientes, reemplazo de SUBAGENT DELEGATION genérico por tablas concretas por agente.
- **Configuración OpenCode desde cero**: Primer archivo `opencode.json` con permisos, modelos, servidores MCP y agentes.
- **Plugin SDD mejorado**: Auto-detección de agente, reglas de rol condicionales, rotación de log de auditoría, eliminación de inyección automática de meta-skill.

### Agregado

#### Catálogo Completo de Agentes (95 agentes nuevos)

**Migración y Estandarización (3 fases):**
- `agents/` — Migración de 108 agentes en revisión a 12 agentes con arquitectura SDD
- Segunda migración: 101 agentes adicionales movidos desde `agents-review/` a `agents/`
- Estandarización de 85 subagentes al formato Rich Extended OpenCode con frontmatter YAML completo
- Metadata tuning completo para 99 agentes (modelos, permisos, descripciones, colores)
- Corrección de permisos en todos los agentes (modos primary/subagent, restricciones de herramientas)
- Corrección: agente `platform-engineer` ocultado de la sesión de OpenCode (`hidden: true`)
- Configuración rápida para agente de Windsurf

**Nuevos Agentes Primarios:**
- `agents/huitzilopochtli.md` — General Purpose Agent (ciclo completo entre dominios)
- `agents/quetzalcoatl.md` — Architect of Specifications (análisis y planificación, reemplaza a `analysis`)
- `agents/tezcatlipoca.md` — Build Agent (ejecución de planes, reemplaza a `implement`)

**Nuevos Subagentes por Dominio (95 agentes):**

| Dominio | Agentes |
|---------|---------|
| Backend & APIs | backend-developer, typescript-pro, python-pro, golang-pro, rust-engineer, java-architect, csharp-developer, fastapi-developer, graphql-architect, spring-boot-engineer, django-developer, laravel-specialist, php-pro, nextjs-developer, elixir-expert, ruby-pro, kotlin-specialist, websocket-engineer, microservices-architect, cpp-pro, javascript-pro, fullstack-developer |
| Frontend & Mobile | frontend-developer, react-specialist, vue-expert, angular-architect, nextjs-developer, flutter-expert, swift-expert, mobile-developer, mobile-app-developer |
| Database & Data | database-optimizer, postgres-pro, sql-pro, data-analyst, data-engineer, data-scientist, data-researcher, database-administrator |
| DevOps & Infra | docker-expert, kubernetes-specialist, terraform-engineer, devops-engineer, build-engineer, sre-engineer, cloud-architect, platform-engineer, network-engineer, azure-infra-engineer, deployment-engineer |
| Security & Compliance | security-auditor, dependency-manager, legal-advisor |
| Testing & Quality | test-engineer, code-reviewer, accessibility-tester, chaos-engineer, refactorer, error-detective, error-coordinator |
| Debugging | debugger |
| AI / ML | ai-engineer, llm-architect, mlops-engineer, machine-learning-engineer, nlp-engineer, prompt-engineer |
| DX & Tooling | cli-developer, tooling-engineer, mcp-developer, dx-optimizer, context-manager |
| Processes & Incidents | git-workflow-manager, incident-responder, project-manager, scrum-master, legacy-modernizer |
| Specialized Domains | fintech-engineer, payment-integration, blockchain-developer, game-developer, iot-engineer, embedded-systems |
| Documentation & Research | docs-writer, research-analyst, knowledge-synthesizer, scientific-literature-researcher, search-specialist |
| Product & Business | business-analyst, product-manager, competitive-analyst, content-marketer, market-researcher, sales-engineer, seo-specialist, trend-analyst, ux-researcher |

**Subagentes existentes actualizados:** code-reviewer, test-engineer, security-auditor, debugger, database-optimizer, dependency-manager — movidos al nuevo formato OpenCode y añadidos a las tablas de delegación.

#### Nueva Documentación de Orquestación

- `docs/opencode/08-orchestration-patterns.md` — Catálogo de 7 patrones de orquestación respaldados + 4 antipatrones con árbol de decisión:
  1. Direct invocation (sin orquestación)
  2. Single-persona slash command
  3. Parallel fan-out with merge (ej: `/ship`)
  4. Sequential pipeline como comandos slash (DEFINE→PLAN→BUILD→VERIFY→REVIEW→SHIP)
  5. Research isolation (preservación de contexto)
  6. General-purpose agent (huitzilopochtli, ciclo de vida completo)
  7. Specialized primary agent con delegación selectiva (quetzalcoatl/tezcatlipoca → subagentes)
- `docs/opencode/09-agent-index.md` — Catálogo completo de agentes clasificado por dominio con tablas dedicadas: Backend & APIs, Frontend & Mobile, Database & Data, DevOps & Infra, Security & Compliance, Testing & Quality, Debugging, AI/ML, DX & Tooling, Processes & Incidents, Specialized Domains, Documentation & Research, Product & Business. Incluye secciones de Primary Agents y subagentes por tipo de sistema.

#### Delegación de Agentes Primarios

- `agents/huitzilopochtli.md` — Tabla completa SUBAGENT DELEGATION con todos los dominios y agentes disponibles.
- `agents/quetzalcoatl.md` — Tabla de subagentes relevantes para análisis: code-reviewer, security-auditor, database-optimizer, test-engineer, accessibility-tester, dependency-manager, debugger, research-analyst, docs-writer, business-analyst.
- `agents/tezcatlipoca.md` — Tabla de subagentes relevantes para build: todos los lenguajes, frameworks, DevOps, DB, testing, más debugger, refactorer, error-detective.

#### Plugin SDD Pipeline Mejorado

- `.opencode/plugins/sdd-pipeline.ts` — Nuevas capacidades:
  - **Auto-detección de agente**: Detecta automáticamente patrones de agente en el prompt y aplica reglas de rol condicionales.
  - **Reglas de rol dinámicas**: Según el agente detectado (quetzalcoatl/tezcatlipoca), inyecta restricciones específicas de herramientas en system prompt.
  - **Rotación de log de auditoría**: Registro de herramientas ejecutadas por agente con límite de 100 entradas.
  - **Eliminación de inyección automática de meta-skill**: El meta-skill ya NO se inyecta automáticamente, se carga bajo demanda.
  - **Patrones de intento en inglés**: Añadidos patrones de detección en inglés para el comando `/spec`.
- `.opencode/plugins/README.md` — Actualizado para reflejar eliminación de meta-skill injection y auto-detección de agente.

#### Configuración OpenCode Nativa

- `opencode.json` — Primer archivo de configuración nativa de OpenCode creado desde cero:
  - **Modelos**: `opencode/deepseek-v4-flash-free` (principal), `openrouter/z-ai/glm-4.5-air:free` (small), `opencode/nemotron-3-super-free` (explore).
  - **Permisos bash**: Esquema completo de 30+ patrones allow/deny (git, ls, grep, find, etc.) con protección de archivos `.env`.
  - **Permisos read**: Allow general con denegación de archivos `.env`.
  - **Agentes**: `build` y `plan` deshabilitados (`disable: true`), `platform-engineer` oculto.
  - **Instrucciones**: CONTRIBUTING.md, WORKFLOW.md, SPEC.md, USER_GUIDE.md, orchestration-patterns.md.
  - **Servidores MCP**: `context7` (remote) + `excel` (local) + `jupyter` (local, deshabilitado).
  - **Eliminación de referencia de index de skills**: Ya no se referencia porque el plugin lo carga automáticamente.

#### Skills Existentes Integradas (7 adicionales desde skills-review)

- Integración de 7 nuevas skills al proyecto, estandarizadas al formato del proyecto (kebab-case, SKILL.md con Common Rationalizations, Red Flags, Verification):
  - `api-spec-generation/` — Generación de specs OpenAPI/AsyncAPI con naming consistente y formatos de error
  - `changelog-generate/` — Generación de CHANGELOG.md en formato Keep a Changelog
  - `clean-code/` — Código legible y mantenible (naming, funciones pequeñas, manejo de errores)
  - `db-migration/` — Planificación y ejecución de migraciones con estrategias de rollback
  - `dependency-audit/` — Escaneo de dependencias para CVEs, paquetes desactualizados y licencias
  - `docker-optimize/` — Optimización de Dockerfiles con multi-stage, caching y hardening
  - `performance-analysis/` — Análisis estático de rendimiento (N+1 queries, complejidad, memoria, caché)
- `env-setup/` — Skill existente movido a la fase DEFINE como PRE-FLIGHT
- `skills/using-agent-skills/SKILL.md` — Integración de las 7 skills en el árbol de Skill Discovery y tabla Quick Reference
- `skills-lock.json` — Actualizado con registros de todas las skills

#### Nuevas Skills de Hoja de Cálculo (2 adicionales, total: 43 — 42 ingeniería + 1 meta-skill)

- `skills/xlsx/` — Manipulación de archivos de hoja de cálculo (.xlsx, .csv, .tsv) con fórmulas, formato, scripts de recálculo y esquemas OOXML ISO/IEC 29500-4:2016. Incluye validadores para docx, pptx y redlining. Basado en `anthropics/skills@xlsx` (89.1K installs).
- `skills/excel-analysis/` — Análisis de datos con pandas: tablas dinámicas, gráficos, estadística descriptiva y limpieza de datos. Basado en `davila7/claude-code-templates@excel analysis` (1.6K installs).

#### Nuevos Servidores MCP (Model Context Protocol)

- **Excel MCP Server** (`uvx excel-mcp-server stdio`) — Lectura, escritura, formateo, tablas, gráficos, tablas dinámicas, fórmulas y manipulación de hojas de cálculo. Habilitado por defecto en `opencode.json`.
- **Jupyter Notebook MCP Server** (`uvx mcp-jupyter-notebook`) — Control completo sobre sesiones Jupyter: ejecución de código, celdas markdown, gestión de paquetes pip, inspección de variables, kernel lifecycle y 30+ herramientas MCP. Incluye modo servidor (remote Jupyter) y modo local (kernel directo). PostgreSQL tools opcional. Pre-configurado como `enabled: false`.
- `docs/opencode/03-mcp-servers.md` — Ampliado con configuración detallada de ambos servidores: Quick Start con Docker/local, tabla de variables de entorno, modos de operación, ejemplos de uso.

#### Renombrado de Agentes Principales

- `agents/analysis.md` → `agents/quetzalcoatl.md` — Arquitecto de Especificaciones
- `agents/implement.md` → `agents/tezcatlipoca.md` — Build Agent

### Cambiado

#### Meta-Skill y Descubrimiento de Skills

- `skills/using-agent-skills/SKILL.md` — Árbol de descubrimiento expandido con:
  - 7 nuevas skills integradas desde skills-review en sus fases correspondientes.
  - Nueva rama para hojas de cálculo: `Working with spreadsheets? → xlsx / excel-analysis`.
  - Tabla Quick Reference actualizada con todas las skills integradas y 2 filas en fase "Extra".

#### Documentación de Agentes

- `agents/huitzilopochtli.md` — Tabla SUBAGENT DELEGATION actualizada con catálogo completo de 10+ dominios.
- `agents/quetzalcoatl.md` — Tabla de subagentes para análisis: code-reviewer, security-auditor, database-optimizer, test-engineer, accessibility-tester, dependency-manager, debugger, research-analyst, docs-writer, business-analyst.
- `agents/tezcatlipoca.md` — Tabla de subagentes para build: lenguajes, frameworks, DevOps, DB, testing, debugger, refactorer, error-detective.
- `agents/code-reviewer.md`, `agents/test-engineer.md`, `agents/security-auditor.md` — Formato actualizado con frontmatter YAML extendido.
- `agents/analysis.md` → `agents/quetzalcoatl.md` — Renombrado y refinado como complemento del nuevo flujo.
- `agents/implement.md` → `agents/tezcatlipoca.md` — Migrado al nuevo nombre.
- `docs/opencode/00-setup.md` — Referencias de agentes actualizadas a 3 agentes primarios.
- Patrones de iteración corregidos para agentes orquestadores (5-10 pasos).

#### Documentación de Orquestación

- `docs/opencode/08-orchestration-patterns.md` — Separado del catálogo de agentes. Ahora incluye:
  - 7 patrones de orquestación respaldados con reglas de composición.
  - 4 antipatrones documentados (Router, Persona-chaining, Sequential orchestrator, Deep persona trees).
  - Árbol de decisión para seleccionar el patrón correcto.
  - Reglas para personas (single role, no invocan otras personas).
- `docs/opencode/09-agent-index.md` — Nuevo documento separado con catálogo completo clasificado por dominio.

#### Documentación Principal

- `docs/ai-agent-setup/opencode-setup.md` — Traducido al inglés (was alemán/inglés mezclado).
- `docs/ai-agent-setup/skill-anatomy.md` — Actualizado con referencias cruzadas al meta-skill y USER_GUIDE.md.
- `CONTRIBUTING.md` — Delegada anatomía y formato de skills a `docs/opencode/02-skills.md` (eliminada duplicación). Añadida sección de Referencias y registro del agente `implement`.
- `README.md` — Restructuración mayor:
  - Conteo de skills corregido: **43** (42 ingeniería + 1 meta-skill).
  - Árbol de estructura de proyecto completado con las 43 skills reales (faltaban 10).
  - Quick Start: nuevo paso **#5 (Opcional) Jupyter Notebook MCP Server**.
  - URLs de repositorios actualizadas a agent-jupyter-toolkit (GitHub).
- `USER_GUIDE.md` — Actualizaciones:
  - **Skills Reference**: Nueva subsección **Extra — Specialized tools and utilities**.
  - **Quick Start**: Nuevo paso **#4 (Optional) Jupyter Notebook MCP Server**.
  - **Troubleshooting**: Nueva fila para "Jupyter MCP won't connect".
  - **Project Structure Tree**: Skills añadidos al listado, encabezado corregido a 43 skills.
- `WORKFLOW.md` — Eliminada referencia a un plan ya ejecutado.

#### Configuración y Permisos

- `opencode.json` — Configuración desde cero:
  - Centralización de todos los permisos bash (30+ patrones de git, grep, find, etc.).
  - Protección de archivos `.env` en bash y read permissions.
  - Eliminación de comandos git redundantes del agente test-engineer.
  - Agregados comandos de análisis faltantes.
  - Corrección de lint de configuración.
  - Servidores MCP añadidos: context7 (remote), excel (local), jupyter (local).
- `skills-lock.json` — Actualizado con registros de todas las skills integradas y nuevas.

### Corregido

- **Sincronización de conteo de skills**: README.md, USER_GUIDE.md y árbol de proyecto actualizados de 33→43.
- **README.md**: Árbol de skills incompleto — faltaban 10 entradas. Ahora completo con las 43.
- `.opencode/plugins/README.md` — Tabla corrupta: columna extra eliminada (`|---|---|---|` → `|---|---|`).
- `CONTRIBUTING.md` — Enlace roto a `docs/opencode/02-skills.md#estructura-skillmd` corregido.
- URLs de repositorios Jupyter actualizadas al monorepo `agent-jupyter-toolkit`.
- `skills-lock.json` — 3 `skillPath` erróneos corregidos (skills existentes).
- `skills/incident-response/SKILL.md` — Enlace roto reparado.
- Formato de referencias a skills en comandos y skills base (backticks eliminados).

## [2.0.0] - 2026-05-21

### Importante (Cambios Rupturantes)

Este lanzamiento representa una **reestructuración profunda** de la plataforma:

- **Migración de Claude Code a OpenCode nativo**: Los hooks de Claude Code han sido reemplazados por un plugin SDD Pipeline nativo
- **Eliminación de soporte multi-agente**: Se eliminan configuraciones de Claude Code, Gemini CLI, Copilot, Cursor y Windsurf
- **Reorganización de directorios**: `commands/` ahora reside en la raíz del proyecto (con symlink en `.opencode/commands/`)
- **Documentación unificada**: `AGENTS_GUIDE.md` eliminado y fusionado en `references/orchestration-patterns.md`

### Agregado

#### Nuevo Plugin SDD Pipeline

- `.opencode/plugins/sdd-pipeline.ts` - Lifecycle plugin con 5 hooks nativos de OpenCode:
  - `experimental.chat.system.transform` - Inyecta meta-skill en system prompt
  - `chat.message` - Detecta intención y sugiere comandos
  - `tool.execute.before` - Bloquea comandos destructivos y separa roles
  - `tool.execute.after` - Auditoría de herramientas
  - `experimental.session.compacting` - Re-inyecta meta-skill y persiste estado
- `.opencode/plugins/README.md` - Documentación del plugin
- Migración de `.opencode/` de pnpm a bun (gestor nativo de OpenCode)

#### Nuevas Skills (4 adicionales, total: 33)

- `refactoring-patterns` - Transformaciones de refactorización nombradas
- `error-handling-patterns` - Patrones de manejo de errores (exceptions, Result types, graceful degradation)
- `architecture-diagrams` - Diagramas de arquitectura con Mermaid, PlantUML, C4 model
- `incident-response` - Flujo de respuesta a incidentes (triage, comunicación, postmortem)

#### Nuevas Referencias Técnicas (16+ documentos)

**Arquitectura (9+ documentos):**
- `references/arch-c4-context-diagram.md` - Diagrama de contexto C4
- `references/arch-class-diagram.md` - Diagrama de clases
- `references/arch-component-diagram.md` / `arch-component-diagram-2.md` - Diagramas de componentes
- `references/arch-data-flow-diagram.md` - Diagrama de flujo de datos
- `references/arch-deployment-diagram.md` / `arch-deployment-diagram-2.md` - Diagramas de despliegue
- `references/arch-migration-template.sql` - Template de migración SQL
- `references/arch-sequence-diagram.md` - Diagrama de secuencia
- `references/arch-system-architecture-diagram.md` - Diagrama de arquitectura de sistema
- `references/arch-validate-schema.sh` - Script de validación de esquemas

**Refactoring (5+ documentos):**
- `references/refactoring-smell-catalog.md` - Catálogo de code smells
- `references/refactoring-composing-methods.md` - Composición de métodos
- `references/refactoring-moving-features.md` - Movimiento entre objetos
- `references/refactoring-organizing-data.md` - Organización de datos
- `references/refactoring-simplifying-conditionals.md` - Simplificación de condicionales
- `references/refactoring-workflow.md` - Flujo de trabajo de refactorización

#### Nuevo Agente Especialista

- `agents/implement.md` - Agente de implementación con restricción de confidencialidad de contenido

#### Nuevos Directorios

- `commands/` - Comandos custom en la raíz del proyecto (con symlink desde `.opencode/commands/`)
- `tasks/` - Directorio con `todo.md` y `plan.md` para el comando `/plan`

#### Infraestructura

- `.opencode/bun.lock` - Lock file de bun para gestor de paquetes
- `.gitignore` - Añadidos archivos de estado del pipeline SDD

### Cambiado

#### Documentación Principal

- `README.md` - Reestructuración completa:
  - Propuesta de valor clara en la descripción
  - Nueva sección de Características (30+ skills, 7 comandos, 5 agentes)
  - Prerrequisitos (Node.js >= 18, pnpm, OpenCode IDE, Git)
  - Quick Start de 5 pasos copy-pasteables
  - Migración de npm a pnpm
  - Bug fix en diagrama Mermaid (nodo G suelto eliminado)
  - Nuevas secciones: Estructura del Proyecto, Configuración, Troubleshooting
- `USER_GUIDE.md` - Reestructuración mayor (615 → 408 líneas):
  - Progresión piramidal: Quick Start → Comandos → Skills → Agentes → Tareas → Referencia
  - Eliminación de duplicación de skills (cada skill aparece una vez en su fase primaria)
  - Skills cross-phase usan nota corta + enlace a entrada canónica
  - Nueva sección Common Tasks (crear skills, agentes, Context7)
  - Eliminación de referencias a 'Skill Extra' y guías de otros agentes IA
  - Deduplicación bidireccional con opencode-setup.md y skill-anatomy.md

#### Meta-Skill y Comandos

- `skills/using-agent-skills/SKILL.md` - Integración de 12 Skill Extras en flowchart y Quick Reference
- **7 comandos actualizados** (`spec`, `plan`, `build`, `test`, `review`, `code-simplify`, `ship`):
  - Eliminado parámetro `model` fijo para flexibilidad
  - Agentes cambiados según el flujo (analysis/implement según corresponda)
  - Añadidas referencias a Skill Extras según su fase

#### Skills Base (8 actualizados)

- `spec-driven-development`, `incremental-implementation`, `frontend-ui-engineering`
- `debugging-and-error-recovery`, `code-review-and-quality`, `code-simplification`
- `documentation-and-adrs`, `shipping-and-launch`
- Formato de referencias mejorado (sin backticks en @skills/)
- Añadidas referencias profundas a Skill Extras correspondientes

#### Documentación de Agentes

- `AGENTS.md` - Limpiado (meta-skill ahora lo inyecta el plugin SDD)
- `agents/analysis.md` - Refactorizado como complemento del flujo analysis → implement
- `references/orchestration-patterns.md` - AGENTS_GUIDE.md fusionado, secciones Claude Code eliminadas
- `CONTRIBUTING.md` - Añadida sección de Referencias y registro del agente implement
- `docs/ai-agent-setup/opencode-setup.md` - Mejorado con referencias al meta-skill
- `docs/ai-agent-setup/skill-anatomy.md` - Añadidas referencias a meta-skill y USER_GUIDE.md

#### Enlaces y Referencias

- **42 enlaces internos corregidos** en 12 archivos `.md` (rutas a `references/`, `agents/`, URLs oficiales)
- Enlaces de `references/` actualizados (CHEATSHEET, art-of-readme, standard-readme, etc.)
- Enlaces en skills de clean-code, clean-ddd-hexagonal, crafting-effective-readmes, solid

### Removido

- `hooks/` - Directorio completo de hooks de Claude Code (7 archivos):
  - `hooks.json`, `SDD-CACHE.md`, `SIMPLIFY-IGNORE.md`
  - `sdd-cache-post.sh`, `sdd-cache-pre.sh`, `session-start.sh`
  - `simplify-ignore-test.sh`, `simplify-ignore.sh`
- `.claude/commands/` - 7 comandos de Claude Code
- `.claude-plugin/` - Plugin de Claude Code (marketplace.json, plugin.json)
- `.gemini/commands/` - 7 comandos de Gemini CLI
- `CLAUDE.md` - Placeholder de Claude Code
- `.github/workflows/test-plugin-install.yml` - CI de Claude Code
- `AGENTS_GUIDE.md` - Fusionado en `references/orchestration-patterns.md`
- `docs/ai-agent-setup/` - Guías de otros agentes (5 archivos):
  - `copilot-setup.md`, `cursor-setup.md`, `gemini-cli-setup.md`
  - `windsurf-setup.md`, `getting-started.md`
- `docs/ai-agent-setup/prompt-anatomy.md` - Sección CI/CD eliminada (no relevante)

### Corregido

- `skills-lock.json` - 3 `skillPath` erróneos corregidos
- `skills/incident-response/SKILL.md` - Enlace roto reparado
- Formato de referencias a skills en 7 comandos y 8 skills base (backticks eliminados)
- Término 'Skill Extra' eliminado de `USER_GUIDE.md` (reemplazado por referencias por fase)
- `LICENSE` y `README.md` - Error de tipado corregido
- Diagrama Mermaid en `README.md` - Nodo G suelto eliminado
- 42 enlaces internos rotos en 12 archivos `.md`

## [1.2.1] - 2026-05-13

### Corregido

- `USER_GUIDE.md` - Corrige hipervínculo de un archivo inexistente

## [1.2.0] - 2026-05-13

### Agregado

#### Nuevas Skills de UI/UX (2 skills + 13 referencias + CLI tool)

**Skills:**
- `ui-ux-design-pro` - Skill senior de diseño UI/UX para interfaces premium production
- `design-taste-frontend` - Skill de UI/UX Engineer senior

**Referencias Técnicas (13 documentos):**
- `references/accessibility.md` - Accesibilidad WCAG 2.1 AA
- `references/animation-and-motion.md` - Animaciones y movimiento
- `references/cognitive-principles.md` - Principios cognitivos
- `references/color-system.md` - Sistema de colores
- `references/component-patterns.md` - Patrones de componentes
- `references/critique-protocol.md` - Protocolo de crítica
- `references/depth-and-elevation.md` - Profundidad y elevación
- `references/design-directions.md` - Direcciones de diseño
- `references/icon-patterns.md` - Patrones de iconos
- `references/real-world-patterns.md` - Patrones del mundo real
- `references/spacing-and-layout.md` - Espaciado y layout
- `references/token-architecture.md` - Arquitectura de tokens
- `references/typography.md` - Tipografía

**CLI Tool Integrado:**
- `skills/ui-ux-design-pro/cli/` - Herramienta CLI con comandos:
  - `audit` - Auditoría de interfaces
  - `generate` - Generación de componentes
  - `icons` - Búsqueda de iconos
  - `search` - Búsqueda de patrones de diseño
- 40+ archivos CSV con patrones de diseño y stacks tecnológicos
- Casos de prueba para fintech y SaaS

**Agente de Análisis Mejorado:**
- Integración robusta de Context7 para fetch de documentación
- Cuestionario refinado antes del modo build
- Optimización de carga de tokens en sesiones
- Pregunta de actualización de documentación tras modo build

### Cambiado

- `CONTRIBUTING.md` - Añadido paso para actualizar documentación al añadir o eliminar skills
- Documentación de skills - Actualizado conteo de skills disponibles (29 total)
- Tabla de agentes en reglas de contribución - Actualizada

### Corregido

- Hipervínculos que no apuntaban a ningún destino del proyecto

## [1.1.2] - 2026-05-12

### Agregado

- `docs/` - Corrección de hipervínculos referenciales a ficheros del proyecto y adición de tabla de contenidos (ToC) a la guía de usuarios.

### Corregido

- `docs/` - Arreglos en la guía de cómo redactar un prompt para agentes IA (mejora de claridad y consistencia).

## [1.1.1] - 2026-05-12

### Agregado

- `agents/analysis.md` - Establece pautas restrictivas para prevenir la invocación de la herramienta `edit`:
  - Sección `TOOL RESTRICTIONS (ENFORCED)` con tabla de herramientas prohibidas
  - Directrices en `ROLE & DIRECTIVE` que refuerzan el "ANALYSIS MODE"
  - Ejemplo práctico de respuesta ante solicitudes de construcción
  - Reglas de interacción actualizadas (Edit/Write/Patch → proveer plan)

### Corregido

- `specs/design/DESING.md` - Corrige nombre del fichero (estaba escrito como `DESING.md`)

## [1.1.0] - 2026-05-11

### Agregado

#### Nuevos Skills (6 adicionales, total: 27)

**Arquitectura y Diseño:**
- `clean-ddd-hexagonal` - Clean Architecture + DDD + Hexagonal para backend services
- `design-patterns` - 20+ patrones de diseño documentados (Adapter, Builder, Command, Composite, Decorator, DTO, Facade, Factory, Identity-Map, Lazy-Load, Mediator, Observer, Proxy, Repository, Service-Layer, State, Strategy, Template-Method, Unit-of-Work, Chain-of-Responsibility)
- `solid` - Principios SOLID aplicados al desarrollo profesional
- `bash-defensive-patterns` - Patrones defensivos para scripts en Bash production-grade
- `crafting-effective-readmes` - Creación de READMEs efectivos con templates (OSS, internal, personal)
- `agent-md-refactor` - Refactorización de AGENTS.md siguiendo progressive disclosure

#### Nuevas Referencias Técnicas (20+ documentos)

**Código Limpio:**
- `code-smells.md` - Catálogo de code smells
- `comments-formatting.md` - Disciplina de comentarios y formato
- `error-handling.md` - Patrones de manejo de errores
- `functions-and-methods.md` - Diseño de funciones pequeñas
- `naming-conventions.md` - Convenciones de nomenclatura
- `testing-principles.md` - Principios de testing

**Arquitectura:**
- `architecture.md` - Principios arquitectónicos
- `complexity.md` - Gestión de complejidad
- `object-design.md` - Diseño orientado a objetos
- `solid-principles.md` - Referencia completa SOLID
- `tdd.md` - Test-Driven Development

**DDD y Patrones Arquitectónicos:**
- `CHEATSHEET.md` - Referencia rápida DDD
- `CQRS-EVENTS.md` - CQRS y Domain Events
- `DDD-STRATEGIC.md` - Strategic DDD (Bounded Contexts, Ubiquitous Language)
- `DDD-TACTICAL.md` - Tactical DDD (Aggregates, Value Objects, Repositories)
- `HEXAGONAL.md` - Arquitectura Hexagonal (Ports & Adapters)
- `LAYERS.md` - Arquitectura en Capas
- `TESTING.md` - Estrategias de testing en DDD

**READMEs:**
- `art-of-readme.md` - El arte de hacer README
- `make-a-readme.md` - Guía práctica de READMEs
- `standard-readme-spec.md` - Especificación Standard README
- `standard-readme-example-maximal.md` - Ejemplo completo
- `standard-readme-example-minimal.md` - Ejemplo mínimo

#### Nuevo Agente Especialista

- `analysis` - Agente de análisis con modo `ask-user-question` para diagnosticar y resolver problemas técnicos

#### Archivos de Proyecto Base

- `.env.example` - Plantilla de variables de entorno
- `.gitmessage` - Plantilla para mensajes de commit
- `Dockerfile` - Configuración Docker base
- `docker-compose.yml` - Orquestación de contenedores
- `Makefile` - Comandos make para automatización
- `WORKFLOW.md` - Documentación del flujo de trabajo
- `requirements.txt` - Dependencias Python base
- `scripts/build.sh` - Script de build
- `scripts/lint.sh` - Script de linting
- `scripts/setup.sh` - Script de setup inicial
- `scripts/test.sh` - Script de testing
- `docs/API_REFERENCE.md` - Referencia de API
- `docs/ARCHITECTURE.md` - Documentación arquitectónica
- `docs/SETUP.md` - Guía de configuración
- `specs/design/DESING.md` - Especificaciones de diseño
- `specs/design/components.md` - Documentación de componentes
- `specs/design/style-guide.md` - Guía de estilos
- `specs/design/user-flow.md` - Flujos de usuario

#### Expansión de .gitignore

Nuevas secciones agregadas al `.gitignore`:

- **Docker y Contenedores:** `.docker/`, `docker-compose.override.yml`, `*.kubeconfig`
- **Lenguajes Adicionales:** Go (vendor/), Rust (target/), Java/Maven (target/, .mvn/), Ruby (vendor/bundle/)
- **Frameworks Web:** Next.js (.next/), Vite/Webpack (dist/), Laravel (storage/*.key), Django (*.pot, *.mo)
- **Cloud e Infraestructura:** AWS (.aws/credentials), SSH (*.pem, *.key), GCP (service-account*.json), Terraform (*.tfstate, .terraform/)
- **Testing y Coverage:** `.nyc_output/`, `lcov.info`, `junit/`, `allure-results/`
- **Entornos Locales:** `local.properties`, `local.gradle`, `*.local`, `*.override`

### Cambiado

- `USER_GUIDE.md` - Actualizada con información sobre skills adicionales y flujo de invocación
- `AGENTS_GUIDE.md` → `references/orchestration-patterns.md` - Actualizada según guía de contribución con agente de análisis (luego fusionada en orchestration-patterns.md)
- `skills/using-agent-skills/SKILL.md` - Mejorada la detección contextual de skills
- Skills existentes (6) - Modificados para seguir lineamientos de la guía de contribución:
  - `agent-md-refactor`, `bash-defensive-patterns`, `clean-ddd-hexagonal`
  - `crafting-effective-readmes`, `design-patterns`, `solid`
- Árbol de archivos del proyecto - Establecida estructura definitiva de directorios
- `AGENTS.md` - Añadida referencia a skills disponibles

### Removido

- `skills/e2e-testing-patterns` - Eliminado (ya existe skill específica para TDD: `test-driven-development`)

### Corregido

- (ninguno en esta versión)

## [1.0.0] - 2026-05-09

### Agregado

#### Skills de Desarrollo (21 en total)

**Fase Definir:**
- `idea-refine` - Pensamiento divergente/convergente para explorar ideas
- `spec-driven-development` - Creación de especificaciones antes de codificar

**Fase Planear:**
- `planning-and-task-breakdown` - Descomposición en tareas verificables

**Fase Construir:**
- `incremental-implementation` - Implementación en slices verticales
- `test-driven-development` - Red-Green-Refactor con test pyramid
- `context-engineering` - Optimización del contexto del agente
- `source-driven-development` - Decisiones basadas en documentación oficial
- `frontend-ui-engineering` - Componentes production-quality
- `api-and-interface-design` - Contrato primero, Hyrum's Law

**Fase Verificar:**
- `browser-testing-with-devtools` - Chrome DevTools MCP para debugging
- `debugging-and-error-recovery` - Triage de 5 pasos

**Fase Revisar:**
- `code-review-and-quality` - Revisión de 5 ejes
- `code-simplification` - Claridad sobre complejidad
- `security-and-hardening` - OWASP Top 10 prevention
- `performance-optimization` - Core Web Vitals

**Fase Lanzar:**
- `git-workflow-and-versioning` - Trunk-based development
- `ci-cd-and-automation` - Shift Left, quality gates
- `deprecation-and-migration` - Code-as-liability mindset
- `documentation-and-adrs` - Registros de decisiones arquitectónicas
- `shipping-and-launch` - Pre-launch checklists

**Meta-skill:**
- `using-agent-skills` - Descubrimiento e invocación de skills

#### Comandos Personalizados

- **`/spec`** - Crear especificaciones
- **`/plan`** - Planificar implementación
- **`/build`** - Construir incrementalmente
- **`/test`** - Ejecutar pruebas
- **`/review`** - Revisión de calidad
- **`/code-simplify`** - Simplificar código
- **`/ship`** - Lanzar a producción

#### Agentes Especialistas

- `code-reviewer` - Senior Staff Engineer
- `test-engineer` - QA Specialist
- `security-auditor` - Security Engineer

#### Herramientas de la Plantilla

- **Context7** - Fetch de documentación actualizada para librerías/frameworks

#### Documentación

- `README.md` - Guía rápida con diagrama Mermaid
- `USER_GUIDE.md` - Referencia completa de 21 skills
- `AGENTS_GUIDE.md` → `references/orchestration-patterns.md` - Personas de agentes y orquestación (luego fusionada en orchestration-patterns.md)
- `CONTRIBUTING.md` - Directrices de contribución (Español)
- `skill-anatomy.md` - Anatomía y formato de skills
- `opencode-setup.md` - Configuración específica de OpenCode

#### Referencias

- `testing-patterns.md` - Patrones de testing
- `security-checklist.md` - OWASP Top 10
- `performance-checklist.md` - Core Web Vitals
- `accessibility-checklist.md` - WCAG 2.1 AA
- `orchestration-patterns.md` - Patrones de orquestación

### Cambiado

- Reorganización de estructura de directorios
- Consistencia en formato de documentación

### Deprecado

- (ninguno en esta versión inicial)

### Removido

- (ninguno en esta versión inicial)

### Corregido

- (ninguno en esta versión inicial)

### Seguridad

- SKILL.md de `security-and-hardening` incluye OWASP Top 10 prevention
- Principios de menor privilegio en configuración de agentes
- Validación de entrada en workflows de skills

---

## Información del Proyecto

### Repositorio
- **Nombre**: Plantilla Dev AI
- **Descripción**: Espacio de trabajo nativo para OpenCode con metodología Spec-Driven Development, 33 skills integradas, 5 agentes especialistas y pipeline SDD automatizado
- **Repositorio**: https://github.com/Fisherk2/spec-driven-develop-opencode-workspace
- **Licencia**: MIT License

### Stack Tecnológico
- **Plataforma**: OpenCode Agentic Workspace
- **Pipeline**: SDD Pipeline Plugin (5 hooks nativos de OpenCode)
- **Skills**: 43 skills de desarrollo profesional (42 + 1 meta-skill)
- **Agentes**: 5 especialistas (analysis, implement, code-reviewer, test-engineer, security-auditor)
- **Documentación**: Context7 para APIs actualizadas · Markdown con diagramas Mermaid
- **Gestión de paquetes**: Bun (`.opencode/`)
- **Control de Versiones**: Git

### Documentación Relacionada

- **[README.md](README.md)** - Guía rápida y flujo de trabajo
- **[USER_GUIDE.md](USER_GUIDE.md)** - Referencia completa de 43 skills
- **[references/orchestration-patterns.md](references/orchestration-patterns.md)** - Agentes y orquestación (AGENTS_GUIDE.md fusionado)
- **[skills/using-agent-skills/SKILL.md](skills/using-agent-skills/SKILL.md)** - Meta-skill orquestador: descubrimiento e invocación de skills
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Directrices de contribución

### Instrucciones de Actualización

#### Desde Versiones Anteriores

**Al actualizar desde 1.x.x a 2.0.0:**

1. **Migración de Claude Code a OpenCode**: Los hooks de Claude Code (`hooks/`) ya no funcionan. Han sido reemplazados por el plugin SDD Pipeline nativo (`.opencode/plugins/sdd-pipeline.ts`). Elimina cualquier referencia a `hooks/` en tu configuración.
2. **Comandos reubicados**: Los comandos ahora residen en `commands/` (raíz del proyecto). Si usabas rutas absolutas a `.opencode/commands/`, actualízalas.
3. **Guías de setup eliminadas**: Las guías para Copilot, Cursor, Gemini CLI y Windsurf ya no están disponibles. Este proyecto es exclusivo para OpenCode.
4. **Documentación unificada**: `AGENTS_GUIDE.md` ya no existe. Su contenido está en `references/orchestration-patterns.md`.
5. **Nuevo gestor de paquetes**: `.opencode/` migró de pnpm a bun. Ejecuta `bun install` en `.opencode/` si usas el plugin SDD.
6. **Nuevos agentes**: El flujo `analysis → implement` reemplaza al antiguo agente único de construcción.

**Al actualizar desde 2.0.0 a 2.1.0:**

1. **Nuevos skills disponibles**: `xlsx` y `excel-analysis` se instalan automáticamente al actualizar. Solo reinicia OpenCode para que se carguen.
2. **Nuevos servidores MCP**: `opencode.json` incluye dos nuevos servidores:
   - `excel`: Habilitado por defecto. Ejecuta `uvx excel-mcp-server stdio` para verificar que funciona.
   - `jupyter`: Deshabilitado por defecto. Para activarlo, inicia un servidor Jupyter (Docker o local), cambia `"enabled": false` a `"enabled": true` en `opencode.json`, y reinicia OpenCode.
3. **Documentación MCP**: La guía `docs/opencode/03-mcp-servers.md` ha sido ampliada con la configuración detallada de ambos servidores.
4. **Revisa conteo de skills**: El total real es 43 (42 ingeniería + 1 meta-skill). Verifica que `README.md` y `USER_GUIDE.md` reflejen este número.
5. **Nueva fase Extra**: Las skills de hojas de cálculo ahora aparecen en una sección "Extra" en `USER_GUIDE.md` y en el meta-skill.

#### Para Versiones Futuras
Al actualizar de 2.1.0 en adelante:

1. **Revisa el CHANGELOG** para cambios rupturantes
2. **Ejecuta lint/typecheck** después de actualizar skills
3. **Verifica comandos personalizados** en tu configuración de OpenCode
4. **Revisa nuevas integraciones** en la documentación del proyecto

### Contribuyendo al CHANGELOG

Al contribuir a este proyecto:

1. **Agrega entradas** a la sección `[Sin Lanzar]`
2. **Sigue versionado semántico** para cambios rupturantes
3. **Usa categorías apropiadas** (Agregado, Cambiado, Deprecado, Removido, Corregido, Seguridad)
4. **Incluye fechas** en formato `YYYY-MM-DD`
5. **Proporciona descripciones claras** explicando el impacto de los cambios
6. **Agrupa por fase** (Definir, Planear, Construir, Verificar, Revisar, Lanzar)
7. **Referencia issues relacionados** o pull requests cuando aplique

### Por Qué Este CHANGELOG Importa

Este CHANGELOG sirve como documentación viva que:

- **Rastrea la evolución** de la plantilla de desarrollo asistido por IA
- **Comunica cambios** a usuarios y contribuyentes
- **Proporciona guía de actualización** para lanzamientos futuros
- **Documenta decisiones arquitectónicas** y su racional
- **Habilita procesos de lanzamiento automatizados** con seguimiento estructurado de cambios