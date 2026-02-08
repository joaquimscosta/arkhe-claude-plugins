# Ralph PRD Troubleshooting

## Common Issues

### Issue: Wizard interrupted mid-flow

**Symptoms:**
- Partial `.ralph/` directory created
- Missing files (tasks.json, prd.md, or config.json)

**Solution:**
```bash
# Check what was created
ls -la .ralph/current-taskset/

# If incomplete, remove and restart
rm -rf .ralph/ PROMPT.md ralph.sh
/create-prd
```

---

### Issue: Invalid or empty task set name

**Symptoms:**
- Error creating directory under `.ralph/tasksets/`
- Symlink `.ralph/current-taskset` points to non-existent directory

**Causes & Solutions:**

1. **Name contains special characters**
   - Use alphanumeric characters, hyphens, and underscores only
   - Example: `auth-feature`, `initial_setup`

2. **Name is empty**
   - Provide a name when prompted, or accept the default ("initial")

---

### Issue: Existing `.ralph/` directory conflicts

**Symptoms:**
- PRD creation fails or overwrites existing task sets
- Symlink already exists

**Solution:**
```bash
# Check existing state
ls -la .ralph/tasksets/

# To add a new task set without overwriting
/ralph taskset new "new-feature"

# To start completely fresh
rm -rf .ralph/ PROMPT.md ralph.sh
/create-prd
```

---

### Issue: Generated tasks too vague

**Symptoms:**
- Ralph loop fails to complete tasks
- Tasks like "implement the feature" without specific steps

**Causes & Solutions:**

1. **Vague feature descriptions during wizard**
   - Be specific: "User login with email/password and JWT tokens" instead of "authentication"
   - Include tech stack details and constraints

2. **Fix after generation**
   ```bash
   # Edit tasks directly
   vi .ralph/current-taskset/tasks.json

   # Add specific steps to each task
   # Break large tasks into smaller ones (prefix: setup-, feat-, test-)
   ```

---

### Issue: Generated tasks too granular

**Symptoms:**
- 50+ tasks generated for a simple project
- Tasks overlap or duplicate each other

**Solution:**
```bash
# Review and consolidate tasks
cat .ralph/current-taskset/tasks.json | jq '.tasks | length'

# Edit to merge related tasks
vi .ralph/current-taskset/tasks.json

# Aim for 10-25 tasks for most projects
```

---

### Issue: ralph.sh not generated or not executable

**Symptoms:**
- `bash: ralph.sh: No such file or directory`
- `bash: ralph.sh: Permission denied`

**Solution:**
```bash
# If missing, re-run PRD creation
/create-prd

# If permission issue
chmod +x ralph.sh
```

---

### Issue: PROMPT.md missing or incorrect

**Symptoms:**
- Ralph loop doesn't know what to do
- Generic behavior instead of project-specific

**Solution:**
```bash
# Check if PROMPT.md exists and has content
ls -la PROMPT.md
wc -l PROMPT.md

# If missing or empty, re-run PRD creation
/create-prd
```

---

## Debugging Tips

### Verify Complete Setup

```bash
# All required files should exist
ls -la PROMPT.md ralph.sh
ls -la .ralph/current-taskset/tasks.json
ls -la .ralph/current-taskset/prd.md
ls -la .ralph/current-taskset/config.json
ls -la .ralph/current-taskset/memories.md
ls -la .ralph/current-taskset/activity.log
```

### Inspect Generated Tasks

```bash
# Pretty print tasks
cat .ralph/current-taskset/tasks.json | jq '.'

# Count tasks by category
cat .ralph/current-taskset/tasks.json | jq '[.tasks[].category] | group_by(.) | map({(.[0]): length}) | add'
```

### Review PRD Content

```bash
# Check the generated PRD
cat .ralph/current-taskset/prd.md
```

---

## Getting Help

If you're still stuck:

1. Verify all required files exist (see checklist above)
2. Check that tasks.json is valid JSON: `cat .ralph/current-taskset/tasks.json | jq .`
3. Re-run `/create-prd` for a fresh start
4. Review [EXAMPLES.md](EXAMPLES.md) for expected output format
5. Review [WORKFLOW.md](WORKFLOW.md) for the expected creation flow
