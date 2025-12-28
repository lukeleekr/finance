# Execution Plan Template

**Version:** 1.0
**Purpose:** Standard template for generating structured, actionable execution plans from PRDs or feature requirements.

---

## Instructions for Plan Generation

You are an expert Technical Product Manager and System Architect. Your task is to receive complex development requirements and decompose them into a structured, manageable, and highly disciplined execution plan.

---

## 1. Execution Sequence

The agent must process the input following this strict sequence:

### Phase 1: Task Analysis
- Deconstruct the core pillars of the request
- Identify architectural constraints and UI/UX requirements
- Map requirements to PRD sections (if PRD exists)
- Identify "Must-Haves" (P1) vs. "Nice-to-Haves" (P2+)

### Phase 2: Tech Stack Audit
- Determine necessary libraries, APIs, and frameworks
- Validate against existing project stack
- Flag any new dependencies requiring evaluation

### Phase 3: Complexity Assessment
- Flag tasks involving high algorithmic complexity
- Identify multi-model orchestration requirements
- Mark tasks requiring external API integration
- Assess risk levels (Low/Medium/High)

### Phase 4: Task Decomposition
Divide the project into modular components by layer:

| Layer | Scope |
|-------|-------|
| **UI/UX Layer** | Visual components, layout, interactions, styling |
| **Logic/Engine Layer** | Backend processing, business logic, calculations |
| **Data Layer** | Database schema, queries, migrations, persistence |
| **Integration Layer** | External APIs, model pipelines, third-party services |
| **Validation/QA Layer** | Testing, edge-case handling, stress-testing |

### Phase 5: Dependency Mapping
- Identify prerequisite relationships between tasks
- Flag critical path items
- Mark tasks that can be parallelized

### Phase 6: Milestone Grouping
- Group tasks into deliverable milestones
- Each milestone should produce demonstrable functionality
- Align milestones with PRD priority phases (P1 → P2 → P3 → P4)

### Phase 7: Output Generation
- Present finalized, categorized issue list
- Generate dependency graph (if complex)
- Summarize milestone deliverables

---

## 2. Core Standards

All execution plans must adhere to these standards:

| Standard | Description |
|----------|-------------|
| **Categorization** | Every task classified by layer (FE/BE/AI/DB/DevOps/QA) |
| **Independence** | Tasks are self-contained and loosely coupled for modular development |
| **Context Awareness** | Task scope fits within 200k token context window for AI-assisted coding |
| **Traceability** | Every task links to specific PRD requirement ID |
| **Testability** | Every task includes test requirements |
| **Estimability** | Every task has effort estimate |

---

## 3. Issue Template

All decomposed tasks must use this template:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK: [ID]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID:             [PHASE]-[LAYER]-[NUMBER]
                Example: P1-BE-001, P1-FE-003, P2-AI-001

Title:          [Concise action-oriented title]
                Example: "Implement RSS feed fetcher with rate limiting"

Category:       [FE | BE | AI | DB | DevOps | QA | Integration]

Priority:       [P1 | P2 | P3 | P4]
                P1 = MVP (must have for launch)
                P2 = Phase 2 (important, not blocking)
                P3 = Phase 3 (enhances value)
                P4 = Phase 4 (future consideration)

Effort:         [S | M | L | XL]
                S  = < 4 hours
                M  = 4-16 hours (1-2 days)
                L  = 16-40 hours (3-5 days)
                XL = 40+ hours (1+ week, consider breaking down)

Risk:           [Low | Medium | High]
                Low    = Well-understood, minimal unknowns
                Medium = Some complexity or external dependency
                High   = Significant unknowns, new technology, or critical path

PRD Reference:  [Section or Requirement ID from PRD]
                Example: "Section 5.2.1 - Daily Key News Highlights (DH-01, DH-02)"

Milestone:      [Milestone name this task belongs to]
                Example: "M1: Data Pipeline Foundation"

─────────────────────────────────────────────────────────────────────────────────
SUMMARY
─────────────────────────────────────────────────────────────────────────────────
[One paragraph describing what this task accomplishes and why it matters]

─────────────────────────────────────────────────────────────────────────────────
TECHNICAL SPECIFICATION
─────────────────────────────────────────────────────────────────────────────────
Components:
  - [Specific files, modules, or components to create/modify]
  - [Endpoints, functions, or classes to implement]
  - [Database tables or schema changes]

Technical Details:
  - [Implementation approach]
  - [Key algorithms or patterns to use]
  - [Configuration or environment requirements]

─────────────────────────────────────────────────────────────────────────────────
ACCEPTANCE CRITERIA
─────────────────────────────────────────────────────────────────────────────────
[ ] [Concrete, testable condition #1]
[ ] [Concrete, testable condition #2]
[ ] [Concrete, testable condition #3]
...

─────────────────────────────────────────────────────────────────────────────────
TEST REQUIREMENTS
─────────────────────────────────────────────────────────────────────────────────
Unit Tests:
  - [Specific unit test cases required]

Integration Tests:
  - [Integration test scenarios]

Manual Verification:
  - [Steps for manual QA if applicable]

─────────────────────────────────────────────────────────────────────────────────
DEPENDENCIES
─────────────────────────────────────────────────────────────────────────────────
Blocked By:     [List of task IDs that must complete first]
                Example: P1-DB-001, P1-BE-002
                Use "None" if no blockers

Blocks:         [List of task IDs waiting on this task]
                Example: P1-FE-005, P1-AI-001
                Use "None" if nothing blocked

Parallel With:  [Tasks that can be developed simultaneously]
                Example: P1-FE-001, P1-FE-002

─────────────────────────────────────────────────────────────────────────────────
NOTES
─────────────────────────────────────────────────────────────────────────────────
[Optional: Additional context, edge cases, open questions, or implementation hints]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 4. Milestone Template

Group related tasks into milestones:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MILESTONE: [ID] - [Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID:             M[Number]
                Example: M1, M2, M3

Name:           [Descriptive milestone name]
                Example: "Data Pipeline Foundation"

Priority:       [P1 | P2 | P3 | P4]

Description:    [What is delivered when this milestone completes]

Deliverables:
  - [Tangible output #1]
  - [Tangible output #2]

Success Criteria:
  - [How we know this milestone is complete]

Tasks Included:
  - [Task ID]: [Task Title]
  - [Task ID]: [Task Title]
  - ...

Total Effort:   [Sum of task efforts]

Critical Path:  [Sequence of dependent tasks that determines minimum duration]
                Example: P1-DB-001 → P1-BE-002 → P1-BE-003 → P1-FE-001

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Execution Plan Summary Template

Every execution plan should begin with this summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTION PLAN SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project:        [Project Name]
PRD Version:    [PRD version this plan implements]
Plan Version:   [Execution plan version]
Created:        [Date]
Author:         [Author]

─────────────────────────────────────────────────────────────────────────────────
SCOPE OVERVIEW
─────────────────────────────────────────────────────────────────────────────────
This execution plan covers: [Brief description of what phases/features are included]

Not included in this plan: [What is deferred to future plans]

─────────────────────────────────────────────────────────────────────────────────
MILESTONE OVERVIEW
─────────────────────────────────────────────────────────────────────────────────
| Milestone | Priority | Tasks | Effort | Dependencies |
|-----------|----------|-------|--------|--------------|
| M1: ...   | P1       | X     | Y hrs  | None         |
| M2: ...   | P1       | X     | Y hrs  | M1           |
| ...       | ...      | ...   | ...    | ...          |

─────────────────────────────────────────────────────────────────────────────────
TASK COUNT BY CATEGORY
─────────────────────────────────────────────────────────────────────────────────
| Category    | P1  | P2  | P3  | P4  | Total |
|-------------|-----|-----|-----|-----|-------|
| Frontend    |     |     |     |     |       |
| Backend     |     |     |     |     |       |
| AI/LLM      |     |     |     |     |       |
| Database    |     |     |     |     |       |
| DevOps      |     |     |     |     |       |
| QA          |     |     |     |     |       |
| Integration |     |     |     |     |       |
| **Total**   |     |     |     |     |       |

─────────────────────────────────────────────────────────────────────────────────
RISK SUMMARY
─────────────────────────────────────────────────────────────────────────────────
High-Risk Tasks:
  - [Task ID]: [Brief description of risk]

Key Assumptions:
  - [Assumption #1]
  - [Assumption #2]

─────────────────────────────────────────────────────────────────────────────────
CRITICAL PATH
─────────────────────────────────────────────────────────────────────────────────
[Visual representation of the longest dependency chain]

Example:
  M1: P1-DB-001 → P1-DB-002 → P1-BE-001 → P1-BE-002
                                    ↓
  M2:                          P1-FE-001 → P1-FE-002 → P1-FE-003
                                    ↓
  M3:                          P1-AI-001 → P1-AI-002

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 6. Category Definitions

| Category | Code | Scope |
|----------|------|-------|
| Frontend | FE | React/Next.js components, styling, client-side logic |
| Backend | BE | FastAPI endpoints, business logic, server-side processing |
| AI/LLM | AI | Model integration, prompt engineering, embeddings |
| Database | DB | Schema design, migrations, queries, Supabase config |
| DevOps | DO | CI/CD, deployment, monitoring, infrastructure |
| QA | QA | Test suites, validation scripts, quality gates |
| Integration | INT | External API connections, third-party services |

---

## 7. Effort Estimation Guidelines

| Size | Hours | Complexity Indicators |
|------|-------|----------------------|
| **S** | < 4 hrs | Single component, well-defined, no unknowns |
| **M** | 4-16 hrs | Multiple components, some complexity, minimal unknowns |
| **L** | 16-40 hrs | Cross-cutting concerns, moderate complexity, some unknowns |
| **XL** | 40+ hrs | Major feature, high complexity, significant unknowns |

**Rule:** If a task is XL, consider breaking it into smaller L or M tasks.

---

## 8. Checklist Before Finalizing Plan

- [ ] Every task has unique ID following naming convention
- [ ] Every task maps to a PRD requirement
- [ ] Every task has acceptance criteria
- [ ] Every task has test requirements
- [ ] Every task has effort estimate
- [ ] All dependencies are identified and valid (no circular dependencies)
- [ ] High-risk tasks are flagged with mitigation notes
- [ ] Tasks are grouped into logical milestones
- [ ] Critical path is identified
- [ ] Summary section is complete

---

**END OF TEMPLATE**
