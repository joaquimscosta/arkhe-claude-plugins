# Troubleshooting

**Gemini auth**
- Ensure `GEMINI_API_KEY` is set in environment.

**Missing output**
- Check `--output-dir` permissions; default `./output/`.

**Structured JSON errors**
- Validate keys: `title`, `canvas{width,height}`, `regions[*]{id,type,x,y,w,h,(text|bullets|code|label)}`.
- Unknown types fallback to “panel” with text.

**Skill not triggering**
- Description must include specific triggers; keep concise and third-person :contentReference[oaicite:17]{index=17}:contentReference[oaicite:18]{index=18}.

**Oversized SKILL.md**
- Move long content into `references/` per progressive disclosure best practice :contentReference[oaicite:19]{index=19}.

