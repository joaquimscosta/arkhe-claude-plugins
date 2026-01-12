---
description: Guided feature development with codebase exploration, architecture design, and quality review
argument-hint: <feature description>
---

# Feature Development

You are helping a developer implement a new feature. Follow a systematic approach: understand the request, explore the codebase deeply, clarify ambiguities, design architecture, implement, and review.

## Core Principles

- **Ask clarifying questions early**: Identify ambiguities before designing, not after
- **Understand before acting**: Read and comprehend existing code patterns first
- **Read files identified by agents**: After agents complete, read key files to build deep context
- **Use TodoWrite**: Track all progress throughout every phase
- **Simple and elegant**: Prioritize readable, maintainable, architecturally sound code

---

## Phase 1: Discovery

**Goal**: Understand what needs to be built

Initial request: $ARGUMENTS

**Actions**:
1. Create todo list with all 7 phases
2. If feature is unclear, ask user for:
   - What problem are they solving?
   - What should the feature do?
   - Any constraints or requirements?
3. Summarize understanding and confirm with user

---

## Phase 2: Codebase Exploration

**Goal**: Understand relevant existing code and patterns

**Actions**:
1. Launch 2-3 `code-explorer` agents in parallel. Each agent should:
   - Trace through the code comprehensively
   - Focus on different aspects (similar features, architecture, patterns)
   - Return a list of 5-10 key files to read

   **Example agent prompts**:
   - "Find features similar to [feature] and trace their implementation comprehensively"
   - "Map the architecture and abstractions for [feature area]"
   - "Identify UI patterns, testing approaches, or extension points relevant to [feature]"

2. Read all key files identified by agents to build deep understanding
3. Present comprehensive summary of findings and patterns discovered

---

## Phase 3: Clarifying Questions

**Goal**: Fill in gaps and resolve all ambiguities before designing

**CRITICAL**: This is one of the most important phases. DO NOT SKIP.

**Actions**:
1. Review codebase findings and original feature request
2. Identify underspecified aspects:
   - Edge cases and error handling
   - Integration points and scope boundaries
   - Design preferences and backward compatibility
   - Performance and security needs
3. **Present all questions to user in a clear, organized list**
4. **Wait for answers before proceeding to architecture design**

If the user says "whatever you think is best", provide your recommendation and get explicit confirmation.

---

## Phase 4: Architecture Design

**Goal**: Design implementation approach with clear trade-offs

**Actions**:
1. Launch 2-3 `code-architect` agents in parallel with different focuses:
   - Minimal changes (smallest change, maximum reuse)
   - Clean architecture (maintainability, elegant abstractions)
   - Pragmatic balance (speed + quality)

2. Review all approaches and form your opinion on which fits best
3. Present to user:
   - Brief summary of each approach
   - Trade-offs comparison
   - **Your recommendation with reasoning**
   - Concrete implementation differences
4. **Ask user which approach they prefer**

---

## Phase 5: Implementation

**Goal**: Build the feature

**DO NOT START WITHOUT USER APPROVAL**

**Actions**:
1. Wait for explicit user approval of chosen architecture
2. Read all relevant files identified in previous phases
3. Implement following chosen architecture
4. Follow codebase conventions strictly
5. Write clean, well-documented code
6. Update todos as you progress

---

## Phase 6: Quality Review

**Goal**: Ensure code is correct, clean, and follows conventions

**Actions**:
1. Launch 2-3 `code-reviewer` agents in parallel with different focuses:
   - Simplicity, DRY, elegance
   - Bugs, logic errors, functional correctness
   - Project conventions and abstractions

2. Consolidate findings and identify highest severity issues
3. **Present findings to user and ask what they want to do**:
   - Fix now
   - Fix later
   - Proceed as-is
4. Address issues based on user decision

---

## Phase 7: Summary

**Goal**: Document what was accomplished

**Actions**:
1. Mark all todos complete
2. Summarize:
   - What was built
   - Key decisions made
   - Files modified
   - Suggested next steps

---

## Guidelines

- Each phase should complete before moving to the next
- User checkpoints exist at phases 3, 4, 5, and 6 - respect them
- Agents have access to WebSearch and can research externally when helpful
- The goal is thorough, high-quality feature development - don't rush
