---
description: Create a session diary entry to document development progress, decisions, and handoff context
---

# /diary

This command creates a session diary entry to document development progress, decisions, and handoff context.

## Usage

```
/diary
```

Creates a new diary entry for the current date, or updates the existing entry if one already exists for today.

## Process

### 1. Determine File Path
- **File naming**: `/design-intent/diary/session-YYYY-MM-DD.md` (e.g., `/design-intent/diary/session-2024-01-15.md`)
- **Date format**: Use current date in YYYY-MM-DD format
- **Check existing**: If file already exists for today, update it instead of creating new

### 2. Gather Session Information
Before creating the entry, collect information about:
- **Session goals**: What was planned for this session
- **Accomplishments**: What was actually built or completed
- **Key decisions**: Important choices made during implementation
- **Current state**: Where the project stands now
- **Next priorities**: What should happen in the next session
- **Known issues**: Problems that aren't blocking but need attention

### 3. Create Diary Entry
Use the template from `/design-intent/diary/session-template.md`

### 4. Content Guidelines

#### What We Built Section
Focus on **concrete outcomes**:
- ✅ "Built gallery component with 3-card responsive layout"
- ✅ "Implemented user authentication flow with mock data"
- ❌ "Worked on some components"
- ❌ "Made progress on the frontend"

#### Key Implementation Details
Document **decisions and reasoning**:
- Why specific approaches were chosen
- What alternatives were considered
- How constitution principles were applied
- Trade-offs made for prototype goals

#### Current State
Be **specific about status**:
- What functionality works end-to-end
- What's partially implemented
- What's blocked or needs attention
- Any integration points established

#### Tomorrow's Priorities
Make priorities **actionable**:
- ✅ "Add loading states to gallery cards"
- ✅ "Implement search functionality for user dashboard"
- ❌ "Continue working on UI"
- ❌ "Fix various issues"

### 5. Update Existing Entry
If a diary entry already exists for today:
- **Append to accomplishments**: Add new items to "What We Built"
- **Update current state**: Reflect latest progress
- **Revise priorities**: Update based on what was completed
- **Add new decisions**: Document any additional key choices made

### 6. Output Confirmation
After creating/updating the diary entry:

```markdown
## Diary Entry Complete

**File**: `/design-intent/diary/session-[YYYY-MM-DD].md`
**Status**: [Created new / Updated existing]

### Session Summary
- **Accomplishments**: [X] items documented
- **Key Decisions**: [X] implementation choices recorded
- **Next Priorities**: [X] tasks identified for next session

### Handoff Ready
This entry provides context for:
- ✓ Current project state
- ✓ Recent decisions and trade-offs
- ✓ Next session priorities
- ✓ Known issues and considerations
```

## When to Use

### End of Session (Primary)
- User says "let's wrap up" or similar
- Natural stopping point reached
- Before committing major work

### Major Milestone
- Feature completion
- Significant architectural decision
- Integration point established

### Handoff Situations
- Switching context to different feature
- Long break between sessions expected
- Complex decisions that need documentation

### User Request
- User explicitly asks for documentation
- Project review or status check needed
- Planning next development phase

## Integration Points

### Session Continuity
- Next session starts by reading latest diary entry
- Provides context for where to resume work
- Maintains momentum across sessions

### Git Workflow
- Create diary entries before major commits
- Reference diary in commit messages if helpful
- Document decisions that affect architecture

### Design Intent Relationship
- Note any design patterns established
- Reference any `/document-design-intent` commands used
- Track custom components created

### Constitution Compliance
- Document how constitution principles were applied
- Note any trade-offs made for simplicity
- Record framework-first decisions

## Behavioral Notes

1. **Outcome-focused**: Document what was built, not how it was built
2. **Decision-focused**: Capture why choices were made, not just what was done
3. **Handoff-ready**: Write for someone else to continue the work
4. **Actionable**: Make priorities concrete and specific
5. **Honest**: Document both successes and known issues
6. **Pattern-aware**: Note design decisions that affect consistency
