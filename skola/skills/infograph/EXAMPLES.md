# Examples

This file provides ready-to-run examples showing how to generate and improve infographics using both **Gemini** and **Nano Banana** engines.

---

## 🧠 Example 1 — Algorithm Breakdown

**Goal:** Visualize the key steps of *Dijkstra’s Algorithm* in a clean, structured infographic.

### Brief
- **Topic:** Dijkstra’s Algorithm (Single-Source Shortest Path)
- **Audience:** Intermediate Computer Science students
- **Type:** Algorithm Breakdown
- **Takeaway:** Greedy relaxation builds a shortest-path tree from the source node.

### Steps
1. **Problem:** Weighted graph, non-negative edges (why it matters)  
2. **Intuition:** Priority queue frontier, relaxation of edges  
3. **Pseudocode:** Numbered lines, clean monospaced font  
4. **Complexity:** O((V + E) log V)  
5. **Edge Cases:** Disconnected nodes, negative edges (unsupported)

### Render (Structured Mode)

#### Option A — Gemini (structured, layout-accurate)
```bash
uv run scripts/generate_infograph.py \
  --engine gemini \
  --mode structured \
  --layout-file layouts/dijkstra.json \
  --output-dir ./output
````

#### Option B — Nano Banana (aesthetic, styled)

```bash
uv run scripts/generate_infograph.py \
  --engine nanobanana \
  --mode structured \
  --layout-file layouts/dijkstra.json \
  --output-dir ./output
```

**Result**

* Gemini → precise diagram (`dijkstra_0_<timestamp>.png`)
* Nano Banana → prompt file (`dijkstra_<timestamp>_nanobanana_prompt.txt`) for styled rendering

---

## 🏗️ Example 2 — Architecture Snapshot

**Goal:** Illustrate a cloud-native microservices architecture.

### Brief

* **Topic:** Cloud Microservices System Overview
* **Audience:** DevOps engineers and software architects
* **Type:** Architecture Snapshot
* **Takeaway:** Show client → gateway → service → database flow clearly.

### Key Regions

1. **Clients:** Browser and mobile app icons
2. **Edge:** API Gateway (auth, rate limit)
3. **Services:** User, Payment, and Notification services
4. **Data Layer:** PostgreSQL + Redis cache
5. **Observability:** Logs, metrics, tracing flow

### Render

#### Gemini (structured)

```bash
uv run scripts/generate_infograph.py \
  --engine gemini \
  --mode structured \
  --layout-file layouts/microservices.json \
  --output-dir ./output
```

#### Nano Banana (styled)

```bash
uv run scripts/generate_infograph.py \
  --engine nanobanana \
  --mode structured \
  --layout-file layouts/microservices.json \
  --output-dir ./output
```

**Result**

* Gemini → precise, label-consistent diagram
* Nano Banana → creative, branded visual version

---

## 🔁 Example 3 — Improve Existing Infographic

**Scenario:** You have an outdated infographic that lacks accessibility contrast and clear hierarchy.

### Input

A JSON layout file (`layouts/old_algorithm.json`) with verbose labels and poor spacing.

### Workflow

1. Run **Audit** using `08_Checklist.md`
2. Identify issues: overcrowding, weak contrast, redundant arrows
3. Revise layout and re-render using Gemini or Nano Banana

### Command

#### Gemini (precise re-render)
```bash
uv run scripts/generate_infograph.py \
  --engine gemini \
  --mode structured \
  --layout-file layouts/old_algorithm_revised.json \
  --output-dir ./output
```

#### Nano Banana (styled re-render)
```bash
uv run scripts/generate_infograph.py \
  --engine nanobanana \
  --mode structured \
  --layout-file layouts/old_algorithm_revised.json \
  --output-dir ./output
```

---

## 🎨 Example 4 — Nano Banana SAE-ALD Prompt Generation

**Goal:** Demonstrate how Nano Banana converts structured JSON layouts into natural-language SAE-ALD prompts.

### Scenario

You have a structured layout (`layouts/cloud_microservices.json`) and want to generate a styled, aesthetic infographic using Nano Banana's SAE-ALD (Subject–Action–Environment–Art Style–Lighting–Details) approach.

### Command

```bash
uv run scripts/generate_infograph.py \
  --engine nanobanana \
  --mode structured \
  --layout-file layouts/cloud_microservices.json \
  --output-dir ./output
```

### Generated Prompt Example

The system automatically converts your structured JSON into this natural-language prompt:

```text
A modern minimalist infographic style with soft colors, crisp icons, and readable typography depiction of an educational infographic titled 'Cloud Microservices System Overview', illustrating key concepts such as Clients, API Gateway, Services, Databases, set in a clean, flat vector layout with balanced spacing and neutral background, illuminated by even diffuse lighting with subtle shadows for clarity. The design emphasizes consistent iconography, clear hierarchy, and smooth flow between panels. no extra text beyond labels; no watermarks or signatures; avoid clutter; icons appear natural and proportional.
```

### Output

* **Prompt file:** `cloud_microservices_<timestamp>_nanobanana_prompt.txt`
* **Usage:** Copy this prompt to Nano Banana (Gemini 2.5 Flash Image) for creative rendering

### Why SAE-ALD?

- **Subject:** Defines what the infographic depicts
- **Action:** Describes the key concepts being illustrated
- **Environment:** Sets the visual context (layout, background)
- **Art Style:** Specifies the design aesthetic
- **Lighting:** Defines the illumination approach
- **Details:** Emphasizes design priorities

This structured approach ensures consistent, high-quality styled renders without manual prompt engineering.

---

## 🧩 Dual-Engine Workflow Summary

| Stage                        | Engine         | Purpose                     | Output                    |
| ---------------------------- | -------------- | --------------------------- | ------------------------- |
| **Plan & Wireframe**         | Claude (Skill) | Generate layout and content | `layout.json`             |
| **Technical Render**         | Gemini         | Precise structured diagram  | `*_image.png`             |
| **Styled Render (Optional)** | Nano Banana    | Polished, aesthetic version | `*_nanobanana_prompt.txt` |

---

> 💡 **Tip:** Run Gemini first for structure → then Nano Banana for design.
> This two-pass workflow ensures both accuracy and aesthetics with minimal rework.

```