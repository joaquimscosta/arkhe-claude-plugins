# Workflow (Microlearn)

## 1) Intake & Clarify (≤3 Qs max if needed)
- Target platform(s)? (Shorts/Reels, Infographic, Micro-blog)
- Audience level? (Beginner/Intermediate/Advanced)
- Language(s)? (auto; default EN; can add KEA/PT)
- One-sentence outcome?

## 2) Plan
- Pick 1 concept only; define success in one sentence.
- Choose format(s); set duration/word cap.
- Outline using the template sections.

## 3) Draft
- Start with runnable code or visual anchor.
- Add one-sentence takeaway + CTA.
- For multi-output jobs, keep message consistent across assets.

## 4) Localize
- Generate EN → KEA → PT when requested.
- Adapt tone; keep tech terms consistent.

## 5) Package
- Create `video_script.md`, `infographic_brief.md`, `micro_blog.md` as needed.
- Add `seo.yaml` and `thumb_brief.md` for social/video.

## 6) Validate (optional)
- Run: `python3 scripts/validate_microlesson.py micro_blog.md video_script.md`
- Fix any missing sections or excessive length.

## 7) Deliver
- Provide a release note with: audience, language(s), format(s), topic, key takeaway.
