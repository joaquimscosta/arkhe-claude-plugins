# Developer Tools

Tools for plugin developers and contributors working on the Arkhe Claude Plugins.

---

## Udemy API Inspector

**Location:** `udemy-research/scripts/api-inspector.js`
**Type:** Development/Research Tool
**Language:** Node.js (Playwright)

### Purpose

The API Inspector is a browser automation tool that helps document Udemy's API endpoints by monitoring network requests while you navigate through a course. This tool was used during the development of the `extract` skill to discover and document API patterns.

### Use Cases

- **API Endpoint Discovery**: Find new or undocumented API endpoints
- **Request/Response Analysis**: Capture authentication headers, request patterns, and response structures
- **Debugging**: Understand how the Udemy platform communicates with its backend
- **Documentation**: Generate reference data for API client development

### Requirements

```bash
# Install dependencies
cd udemy-research
npm install
```

**Dependencies:**
- Node.js 14+
- Playwright (for browser automation)
- dotenv (for environment variables)

### Configuration

Create a `.env` file in `udemy-research/`:

```env
UDEMY_USERNAME=your-email@example.com
UDEMY_PASSWORD=your-password
```

**Security Note:** The `.env` file is gitignored. Never commit credentials.

### Usage

```bash
# Basic usage
node scripts/api-inspector.js "https://SITE.udemy.com/course/course-name/"

# Specify custom output file
node scripts/api-inspector.js "https://SITE.udemy.com/course/course-name/" "./my-api-logs.json"
```

### How It Works

1. **Launches Browser**: Opens Playwright-controlled Chromium (visible, not headless)
2. **Captures Requests**: Monitors all network requests/responses
3. **Filters API Calls**: Focuses on Udemy API endpoints and JSON responses
4. **User Interaction**: Allows you to navigate the course manually
5. **Logs Data**: Records URLs, headers, methods, and response bodies
6. **Saves Output**: Generates JSON file with all captured data

### Workflow

1. Run the script with a course URL
2. Browser opens and navigates to the course
3. If needed, login manually or script attempts auto-login
4. Navigate through the course:
   - Click on lectures
   - Expand sections
   - Open transcripts
   - Download resources
5. Press Enter when done inspecting
6. Script saves all captured requests to JSON

### Output Format

```json
{
  "metadata": {
    "courseUrl": "https://...",
    "timestamp": "2025-10-19T...",
    "totalRequests": 156,
    "apiPatternsFound": [
      "/api-2.0/courses/{id}/",
      "/api-2.0/courses/{id}/cached-subscriber-curriculum-items",
      "/api-2.0/asset/{id}/captions"
    ]
  },
  "requests": [
    {
      "timestamp": "...",
      "method": "GET",
      "url": "...",
      "headers": {...},
      "status": 200,
      "responseBody": {...}
    }
  ],
  "summary": {
    "apiPatterns": [...],
    "authHeaders": ["authorization", "cookie"]
  }
}
```

### Analysis

After capturing API data:

1. **Review Output**: Open the JSON file
2. **Identify Patterns**: Look for common endpoint structures
3. **Document APIs**: Add findings to `UDEMY_PLATFORM_REFERENCE.md`
4. **Update Client**: Enhance `api_client.py` with new endpoints
5. **Test Integration**: Verify new endpoints work in extraction scripts

### Not Suitable For

❌ **End-user usage** - This is a development tool
❌ **Production extraction** - Use the `extract` skill instead
❌ **Automated testing** - Requires manual interaction
❌ **Plugin distribution** - Stays in research directory

### Related Documentation

- [Udemy Platform Reference](../udemy-research/UDEMY_PLATFORM_REFERENCE.md) - API documentation derived from inspector data
- [API Client](../arkhe-claude-plugins/skola/skills/extract-udemy/scripts/api_client.py) - Production API client implementation
- [Research Notes](../udemy-research/RESEARCH.md) - Original API research findings

---

## Contributing New Tools

Have a useful development tool? Consider adding it:

1. **Document clearly**: Explain purpose, usage, and requirements
2. **Keep separate**: Development tools stay in `udemy-research/` or appropriate research directory
3. **Update this file**: Add your tool to this documentation
4. **Share learnings**: Document insights in relevant reference files

---

## See Also

- [Agent Skills Overview](./AGENT_SKILLS_OVERVIEW.md) - Understanding skill architecture
- [Skill Development Best Practices](./SKILL_DEVELOPMENT_BEST_PRACTICES.md) - Creating production skills
- [Plugin Documentation Index](./README.md) - All developer resources
