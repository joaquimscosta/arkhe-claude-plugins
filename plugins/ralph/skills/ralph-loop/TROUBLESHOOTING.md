# Ralph Loop Troubleshooting

## Common Issues

### Issue: Loop exits immediately without doing anything

**Symptoms:**
- Script exits with error code 1
- No iterations are executed

**Causes & Solutions:**

1. **Missing PROMPT.md**
   ```bash
   # Check if file exists
   ls -la PROMPT.md

   # Solution: Run /create-prd first
   /create-prd
   ```

2. **Missing .ralph/current-taskset symlink or tasks.json**
   ```bash
   # Check if symlink and file exist
   ls -la .ralph/current-taskset
   ls -la .ralph/current-taskset/tasks.json

   # Solution: Run /create-prd first
   /create-prd
   ```

3. **ralph.sh not executable**
   ```bash
   # Make executable
   chmod +x ralph.sh
   ```

---

### Issue: Loop completes on first iteration

**Symptoms:**
- Outputs "RALPH_COMPLETE:" immediately
- No work was done

**Cause:** All tasks already have `passes: true`

**Solution:**
```bash
# Check task status
cat .ralph/current-taskset/tasks.json | jq '.tasks[] | {id, passes}'

# Reset tasks if needed
# Edit .ralph/current-taskset/tasks.json and set passes: false
```

---

### Issue: Loop never completes (hits max iterations)

**Symptoms:**
- Reaches max iterations without "RALPH_COMPLETE:"
- Same task keeps failing

**Causes & Solutions:**

1. **Task too vague**
   - Edit `.ralph/current-taskset/tasks.json`
   - Add more specific steps
   - Break large task into smaller ones

2. **Verification always fails**
   ```bash
   # Check what's failing
   npm run lint
   npm run typecheck
   npm run test

   # Fix underlying issues manually if needed
   ```

3. **Task impossible to complete**
   - Review the task requirements
   - Consider if it's achievable
   - Modify or remove problematic task

---

### Issue: Tasks not being marked as complete

**Symptoms:**
- Work is done in each iteration
- But tasks stay `passes: false`

**Cause:** Claude not updating tasks.json properly

**Solution:**
```bash
# Manually verify the task.json format is correct
cat .ralph/current-taskset/tasks.json | jq .

# Check activity log for errors
tail -n 50 .ralph/current-taskset/activity.log
```

---

### Issue: No commits being created

**Symptoms:**
- Work is done
- But git log shows no new commits

**Causes & Solutions:**

1. **Not a git repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Git configuration issues**
   ```bash
   git config user.name "Your Name"
   git config user.email "your@email.com"
   ```

---

### Issue: Context seems to carry over

**Symptoms:**
- Later iterations reference things from earlier iterations
- Behavior changes unpredictably

**Cause:** This shouldn't happen with the external bash loop.

**Solution:**
1. Verify you're using `ralph.sh` (not running Claude directly)
2. Check that PROMPT.md doesn't have accumulated content
3. Restart the loop fresh

---

### Issue: Activity log getting corrupted

**Symptoms:**
- Malformed entries in activity.log
- JSON parse errors

**Solution:**
```bash
# Backup current log
cp .ralph/current-taskset/activity.log .ralph/current-taskset/activity.log.bak

# Clear and start fresh
echo "" > .ralph/current-taskset/activity.log
```

---

## Debugging Tips

### Verbose Mode

Run a single iteration manually to see what's happening:

```bash
claude -p "$(cat PROMPT.md)" --output-format text
```

### Check Task State

```bash
# Pretty print tasks
cat .ralph/current-taskset/tasks.json | jq '.'

# Show only incomplete tasks
cat .ralph/current-taskset/tasks.json | jq '.tasks[] | select(.passes == false)'

# Count complete vs incomplete
echo "Complete: $(cat .ralph/current-taskset/tasks.json | jq '[.tasks[] | select(.passes == true)] | length')"
echo "Incomplete: $(cat .ralph/current-taskset/tasks.json | jq '[.tasks[] | select(.passes == false)] | length')"
```

### Review Activity

```bash
# Last iteration only
tail -n 15 .ralph/current-taskset/activity.log

# Search for failures
grep -A 5 "STATUS: FAIL" .ralph/current-taskset/activity.log

# Search for specific task
grep -A 10 "TASK: feat-001" .ralph/current-taskset/activity.log
```

### Git History

```bash
# See commits made by Ralph
git log --oneline -10

# See changes in last commit
git show --stat HEAD
```

---

## Recovery Procedures

### Reset a Single Task

```bash
# Edit tasks.json and set specific task to passes: false
# Then run the loop again
./ralph.sh 5
```

### Reset All Tasks

```bash
# Set all tasks back to incomplete
cat .ralph/current-taskset/tasks.json | jq '.tasks[].passes = false | .tasks[].iteration_completed = null' > /tmp/tasks.json
mv /tmp/tasks.json .ralph/current-taskset/tasks.json
```

### Start Fresh

```bash
# Remove all Ralph state
rm -rf .ralph/
rm -f PROMPT.md ralph.sh

# Run PRD creation again
/create-prd
```

---

## Getting Help

If you're still stuck:

1. Check the activity log for specific error messages
2. Run a single iteration manually to observe behavior
3. Review the PROMPT.md to ensure instructions are clear
4. Verify tasks.json has valid JSON format
