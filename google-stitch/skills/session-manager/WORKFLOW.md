# Stitch Session Manager — Workflow

## 1. Initialize Session (`session:new`)
1. Validate project identifier (slugify to `kebab-case`).
2. Create `.claude/sessions/<project>/` if missing.
3. Bootstrap structure:
   ```
   session.json        # metadata + running index
   screen-log/         # individual prompt files
   summary.md          # empty until export
   ```
4. Write `session.json` template:
   ```json
   {
     "session_name": "<project>",
     "created_at": "<ISO8601>",
     "style_guide": null,
     "prompts": []
   }
   ```

## 2. Add Screen / Prompt (`session:add`)
1. Parse user brief (screen name + intent).
2. Read latest `session.json` to capture style cues (`style_guide` or aggregated attributes).
3. Call `authoring-stitch-prompts` with payload:
   ```json
   {
     "screen": "<user screen name>",
     "brief": "<user description>",
     "style_context": "<derived cues>"
   }
   ```
4. Receive optimized prompt.
5. Persist file `screen-log/<slug>-###.json`:
   ```json
   {
     "id": "<slug>-###",
     "name": "<Screen Name>",
     "type": "screen",
     "timestamp": "<ISO8601>",
     "prompt": "<optimized prompt>",
     "source_brief": "<raw user text>"
   }
   ```
6. Append reference to `session.json.prompts`.

## 3. List / Summarize (`session:list`, `session:summary`)
1. Load `session.json`.
2. For `session:list`, format ordered bullets with name, version, timestamp, status.
3. For `session:summary`:
   - Aggregate style cues (color words, typography, layout).
   - Detect missing flow steps (login → dashboard → settings) using heuristics from logged names.
   - Output:
     ```
     Session: <name>
     Screens: <comma-separated>
     Style cues: <palettes/typography>
     Recommendations: <gaps or next screens>
     ```

## 4. Reuse Style (`session:style`)
1. Collect palette + tone descriptors from previous prompts (simple frequency count or manual review).
2. Present summary back to the user.
3. Attach the same summary when routing future briefs to `authoring-stitch-prompts`.

## 5. Export Session (`session:export`)
1. Read `session.json` and all `screen-log/*.json`.
2. Build `summary.md`:
   ```markdown
   # <Project> — Stitch Session Summary

   **Total Screens:** <count>
   **Design Style:** <derived cues>
   **Created:** <date string>

   ## Screens
   1. <Name> (v1) – <timestamp>
   ...

   ## Notes
   <observations + recommendations>
   ```
3. Confirm file path for user and mark session as closed by adding `closed_at` inside `session.json`.

## 6. Continue Existing Session
1. Detect `.claude/sessions/<project>/session.json`.
2. Load metadata, confirm last updated timestamp.
3. Resume at step 2 above for additional screens or summaries.
