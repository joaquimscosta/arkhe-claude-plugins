# Troubleshooting

Common issues and solutions for the Design Intent Specialist skill.

---

## Issue: No Design Intent Directory Found

### Symptoms

```
Error: Cannot find /design-intent/patterns/ directory
```

### Cause

Project hasn't been initialized with `/setup` command.

### Solution

Run the setup command to create the design intent structure:

```
/setup
```

This creates:
- `/design-intent/memory/` - Constitution and team roles
- `/design-intent/specs/` - Feature specifications
- `/design-intent/patterns/` - Design patterns
- `/design-intent/diary/` - Session documentation

### Workaround

If you don't want to use the full design-intent structure, you can proceed without patterns. The skill will note:

```
No existing design intent patterns found. Will establish new patterns based on this implementation.
```

---

## Issue: MCP Server Not Available

### Symptoms

- Figma URL provided but can't extract design data
- `fluent-pilot` queries fail

### Cause

MCP servers not configured in project.

### Solution

The skill works without MCPs - they're optional enhancements.

**For Figma integration**, configure in `.mcp.json`:
```json
{
  "mcpServers": {
    "figma-dev-mode-mcp-server": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-figma-dev-mode"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "your-token"
      }
    }
  }
}
```

**For Fluent UI guidance**:
```json
{
  "mcpServers": {
    "fluent-pilot": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-fluent-pilot"]
    }
  }
}
```

### Workaround

Without MCPs:
- Provide screenshots instead of Figma URLs
- Manually describe Fluent UI components to use
- The skill can still create accurate implementations

---

## Issue: Pattern Conflict Not Resolved

### Symptoms

- Implementation doesn't match expected pattern
- User wasn't asked about conflict

### Cause

Conflict detection might have missed the pattern, or user guidance wasn't properly incorporated.

### Solution

1. **Re-check patterns manually**
   ```
   Check /design-intent/patterns/ for [pattern-name].md
   ```

2. **Explicitly state the conflict**
   ```
   "This implementation uses 8px padding, but our card-spacing pattern
   specifies 12px. Should I update this to match the pattern?"
   ```

3. **After resolution, update implementation**

### Prevention

Always verify pattern check completed before implementation:
```
Existing patterns to consider:
- [list should appear here]
```

If list is empty or missing patterns you know exist, check file paths.

---

## Issue: Custom Component Not Documented

### Symptoms

- Created a custom component but no documentation header
- Later can't find why component was created

### Cause

Forgot to add documentation header during implementation.

### Solution

Add the standard documentation header:

```tsx
/**
 * CUSTOM COMPONENT: ComponentName
 * Base: @fluentui/react-components/BaseComponent
 * Reason: [Why standard component wasn't sufficient]
 * Created: YYYY-MM-DD
 */
```

### Prevention

The skill should automatically add this header when creating custom components. If it doesn't, remind:

```
"Please add the standard custom component documentation header."
```

---

## Issue: Responsive Behavior Missing

### Symptoms

- Implementation looks good on desktop
- Breaks on mobile viewports

### Cause

Responsive breakpoints not considered during implementation.

### Solution

1. **Check constitution Article III** - Responsive Design Mandate

2. **Add breakpoint handling**:
   ```tsx
   // Standard breakpoints
   // Mobile: < 768px
   // Desktop: >= 768px

   @media (max-width: 767px) {
     // Mobile styles
   }
   ```

3. **Common responsive patterns**:
   - Sidebar collapses to hamburger menu
   - Grid columns reduce (3 → 2 → 1)
   - Stack horizontal layouts vertically
   - Reduce padding/margins

### Prevention

For each section, explicitly note responsive behavior:
```
### Responsiveness
- < 768px: [mobile behavior]
- ≥ 768px: [desktop behavior]
```

---

## Issue: Wrong Component Selected

### Symptoms

- Used custom component when Fluent UI had one
- Used wrong Fluent UI component variant

### Cause

Didn't check framework components first (Article II violation).

### Solution

1. **Check Fluent UI first**
   - Query `fluent-pilot` MCP if available
   - Check react.fluentui.dev documentation

2. **If custom still needed**, document why:
   ```tsx
   /**
    * CUSTOM COMPONENT: CustomSelect
    * Base: @fluentui/react-components/Dropdown
    * Reason: Needed async search with debounce, Dropdown doesn't support
    */
   ```

### Prevention

Follow component selection priority:
1. Existing project components
2. Fluent UI components
3. Custom components (document reason)

---

## Issue: Visual Fidelity vs Pattern Conflict

### Symptoms

- User wants exact visual match to reference
- Existing patterns dictate different values

### Cause

Unclear guidance on which takes precedence.

### Solution

**Default behavior**: Implement reference faithfully, then flag conflict.

Ask user:
```
This design uses [reference value], but our pattern specifies [pattern value].

Options:
1. Follow reference (creates exception)
2. Use pattern (adapts design)
3. Update pattern (makes reference the new standard)

Which approach?
```

### Philosophy

- Visual fidelity is primary goal
- Patterns exist for consistency
- User decides when to break patterns
- Document exceptions

---

## Issue: Session Context Lost

### Symptoms

- New Claude session doesn't know about previous patterns
- Re-implementing things already decided

### Cause

Design intent patterns weren't documented, or diary entry wasn't created.

### Solution

1. **Check for diary entries**
   ```
   /design-intent/diary/session-YYYY-MM-DD.md
   ```

2. **Check for patterns**
   ```
   /design-intent/patterns/
   ```

3. **If missing, recreate from code**
   - Review implemented components
   - Extract patterns for documentation
   - Run `/save-patterns`

### Prevention

- Always run `/diary` at end of session
- Run `/save-patterns` after successful implementations
- Commit pattern files to git

---

## Issue: Skill Not Auto-Invoking

### Symptoms

- Provided Figma URL but skill didn't activate
- Asked to implement UI but got generic response

### Cause

Context didn't trigger skill invocation.

### Solution

Use explicit triggers:
- `/design [reference]` - Explicit command
- "Implement this UI from the screenshot"
- "Create React components matching this Figma design"

### Trigger Keywords

The skill responds to:
- Figma URLs
- Screenshots/design images attached
- "implement this UI"
- "implement this design"
- "create components from this"
- "match this visual reference"

---

## Getting Help

If issues persist:

1. Check constitution at `/design-intent/memory/constitution.md`
2. Review existing patterns in `/design-intent/patterns/`
3. Create a diary entry documenting the issue
4. Consider running `/save-patterns` to capture what's working
