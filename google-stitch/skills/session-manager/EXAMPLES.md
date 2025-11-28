# Stitch Session Manager — Examples

## Example 1 — Start New Session
**User:** `Start a new Stitch session for Mobile Banking app.`  
**Skill actions:**
1. Slugify to `mobile-banking`.
2. Create `.claude/sessions/mobile-banking/`.
3. Write baseline `session.json`.
4. Reply:
   > Initialized Stitch session **Mobile Banking**. Use “Add a new screen…” to begin logging prompts.

## Example 2 — Add Screen with Optimized Prompt
**User:**  
```
Add a new screen called Dashboard with this brief:
- Show recent transactions
- Spending donut chart
- Quick actions card
Use same style as existing session.
```
**Skill actions:**
1. Fetch palette + tone from session logs (e.g., deep blue, rounded, sans-serif).
2. Call `authoring-stitch-prompts` with extracted cues.
3. Save `screen-log/dashboard-001.json`.
4. Reply:
   ```
   Logged screen dashboard-001.
   Ready-to-use Stitch prompt:
   Design a responsive banking dashboard...
   ```

## Example 3 — Session Summary
**User:** `Summarize my current Stitch session.`  
**Skill reply:**
```
Session: Mobile Banking
Screens: login-001, dashboard-001
Style cues: deep blue palette, rounded cards, sans-serif type, soft gradients
Recommendations: Add transactions detail screen to complete money flow.
Summary exported to .claude/sessions/mobile-banking/summary.md
```

## Example 4 — Export & Close
**User:** `End this Stitch session and export summary.`  
**Skill actions:**
1. Compile totals + notes.
2. Write summary file and add `closed_at`.
3. Reply with file path and reminder to reinstall Skill if editing prompts again.
