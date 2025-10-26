# Troubleshooting Guide

Complete error handling reference for the Udemy Course Extractor.

## Table of Contents

- [Authentication Errors](#authentication-errors)
- [Course Access Errors](#course-access-errors)
- [API Errors](#api-errors)
- [Content Extraction Errors](#content-extraction-errors)
- [Resource Download Errors](#resource-download-errors)
- [Network Errors](#network-errors)
- [Python Version Errors](#python-version-errors)

---

## Authentication Errors

### Error: "Authentication failed" or 401 Unauthorized

**Symptoms:**
```
✗ Authentication failed
ERROR: 401 Unauthorized
```

**Causes:**
- Cookies have expired (typically expire after ~24 hours)
- Invalid `access_token` or `client_id` in `cookies.json`
- Logged out from Udemy in the browser
- Using cookies from wrong Udemy site (e.g., udemy.com vs risesmart.udemy.com)

**Solutions:**

1. **Refresh cookies** from browser DevTools:
   ```bash
   # 1. Log into Udemy in browser (correct site!)
   # 2. Open DevTools (F12) → Application → Cookies
   # 3. Find and copy:
   #    - access_token
   #    - client_id
   # 4. Update cookies.json
   ```

2. **Verify cookies format**:
   ```json
   {
     "access_token": "your-token-here",
     "client_id": "your-client-id-here"
   }
   ```

3. **Check you're using the correct Udemy site**:
   - If course is on `risesmart.udemy.com`, extract cookies from there
   - Don't use `udemy.com` cookies for `risesmart.udemy.com` courses

### Error: "No cookies found" or "cookies.json not found"

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'cookies.json'
```

**Solution:**

Create `cookies.json` in `udemy-research/` directory:
```bash
cd udemy-research
touch cookies.json
# Edit file and add your cookies
```

---

## Course Access Errors

### Error: "Could not find course with slug"

**Symptoms:**
```
✗ Could not find course with slug: data-structures-and-algorithms-java
```

**Causes:**
- Course is not in your enrolled courses list
- You're not logged in with the account that enrolled in the course
- Course URL slug doesn't match any enrolled course

**Solutions:**

1. **Verify enrollment**:
   - Go to Udemy → "My Courses"
   - Ensure the course appears in your list
   - If not, enroll in the course first

2. **Check authentication**:
   - Verify cookies are from the same account
   - Log out and log back into Udemy
   - Refresh cookies

3. **Try numeric course ID instead**:
   ```bash
   # Extract course ID from URL or browser
   python3 extract.py "https://SITE.udemy.com/course/4218796/"
   ```

### Error: "Course not found" or 404

**Symptoms:**
```
ERROR: 404 Not Found - Course {id} not found
```

**Causes:**
- Course has been deleted or made private
- Course ID is incorrect
- Access has been revoked

**Solution:**
- Verify course URL is correct
- Check if course is still accessible in browser
- Try re-enrolling in the course

---

## API Errors

### Error: "API endpoints changed"

**Symptoms:**
```
⚠️ Documented endpoint failed, attempting discovery...
✗ Could not discover working API endpoints
```

**Causes:**
- Udemy updated their API
- Endpoint patterns have changed
- Authentication headers changed

**Solutions:**

1. **Re-run API discovery**:
   ```bash
   # Use analyze_content_types.py to test endpoints
   python3 scripts/tools/analyze_content_types.py "COURSE_URL" output.json
   ```

2. **Check for new endpoint patterns**:
   - Look at network tab in browser DevTools
   - Find requests to `/api-2.0/`
   - Update `api_client.py` with new patterns

3. **Update API.md**:
   - Document new endpoint patterns
   - Include working examples

### Error: "Rate limited" or 429 Too Many Requests

**Symptoms:**
```
ERROR: 429 Too Many Requests
Please slow down your requests
```

**Solution:**

The script includes built-in rate limiting (0.5s between requests), but if you still hit limits:

1. **Increase delay** in `extract.py:extract.py:382`:
   ```python
   time.sleep(1.0)  # Increase from 0.5 to 1.0 seconds
   ```

2. **Extract in batches**:
   ```bash
   # Extract first 50 lectures, then pause, then continue
   # (Manual intervention required)
   ```

---

## Content Extraction Errors

### Error: "No transcripts found"

**Symptoms:**
```
[001] ⚠️  Lecture Title - No extractable content
```

**Causes:**
- Lecture genuinely has no captions/transcripts
- Lecture is a quiz or coding exercise (no video)
- Caption endpoint has changed
- Video hasn't been processed yet

**Solutions:**

1. **Check in browser**:
   - Open lecture in Udemy
   - Look for CC (closed captions) button
   - If no CC button, lecture truly has no transcripts

2. **Check lecture type**:
   - Quizzes don't have transcripts (use `--content-types quiz` instead)
   - Coding exercises may not have transcripts
   - Articles don't have transcripts (use `--content-types article` instead)

3. **Verify caption endpoint**:
   - Check `api_client.py` for caption URL pattern
   - May need to update endpoint

### Error: "Article extraction failed - 'NoneType' object has no attribute 'get'"

**Symptoms:**
```
ERROR: Lecture 12345 (Title): Resource extraction failed - 'NoneType' object has no attribute 'get'
```

**Causes:**
- Article HTML is missing or malformed
- API returned incomplete data
- Unexpected article structure

**Solutions:**

1. **Check API response**:
   ```python
   # In api_client.py, add debug logging:
   print(f"Article data: {lecture.get('asset', {})}")
   ```

2. **Fallback to raw HTML**:
   - ArticleExtractor saves raw HTML if markdown conversion fails
   - Check `articles/` directory for `.html` fallback files

3. **Report as partial success**:
   - Script continues with other lectures
   - Check extraction statistics at end

### Error: "No resources found" (but visible in UI)

**Symptoms:**
```
Statistics:
  Resources: 0

# But Playwright/browser shows downloadable files
```

**Causes:**
- **BUG FIXED 2025-10-18**: `supplementary_assets` was being discarded during parsing
- Using old version before bug fix

**Solution:**

1. **Verify you have the latest version**:
   ```bash
   # Check api_client.py line 353 includes:
   'supplementary_assets': item.get('supplementary_assets', [])
   ```

2. **Re-run extraction**:
   ```bash
   python3 extract.py "COURSE_URL" --content-types resource
   ```

3. **Verify resources are detected**:
   ```bash
   # Run content analysis
   python3 scripts/tools/analyze_content_types.py "COURSE_URL" analysis.json
   # Check: "Lectures with Downloadable Resources: X"
   ```

---

## Resource Download Errors

### Error: "Resource download failed - File too large"

**Symptoms:**
```
⊘ Skipped large-file.zip - exceeds limit (250MB > 100MB)
```

**Cause:**
- File exceeds `--max-resource-size` limit (default: 100MB)

**Solutions:**

1. **Increase size limit**:
   ```bash
   python3 extract.py "COURSE_URL" --max-resource-size 500
   ```

2. **Download specific resources manually**:
   - Check `resources/XXX-resources.md` catalog
   - Contains URLs for manual download

3. **Skip resource downloading**:
   ```bash
   python3 extract.py "COURSE_URL" --no-download-resources
   # Creates catalogs without downloading files
   ```

### Error: "Download failed - Network timeout"

**Symptoms:**
```
ERROR: Failed to download resource.pdf - timeout
✗ X files failed to download
```

**Solutions:**

1. **Re-run extraction** (will skip already downloaded files):
   ```bash
   python3 extract.py "COURSE_URL" --content-types resource
   ```

2. **Check network connection**:
   - Verify internet connectivity
   - Try downloading a single resource manually

3. **Use manual download URLs**:
   - Check resource catalog markdown files
   - Download failed files manually

### Error: "Permission denied" when saving resources

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: 'resources/file.pdf'
```

**Solutions:**

1. **Check directory permissions**:
   ```bash
   ls -la udemy-research/course-name/resources/
   chmod 755 udemy-research/course-name/resources/
   ```

2. **Check disk space**:
   ```bash
   df -h
   ```

3. **Run with correct user**:
   - Don't run as root unless necessary
   - Ensure user has write permissions

---

## Network Errors

### Error: "Connection refused" or "Network unreachable"

**Symptoms:**
```
ConnectionRefusedError: [Errno 61] Connection refused
```

**Causes:**
- No internet connection
- Firewall blocking requests
- Proxy configuration issues

**Solutions:**

1. **Check internet**:
   ```bash
   ping google.com
   curl https://www.udemy.com
   ```

2. **Check firewall**:
   - Ensure Python can make outbound HTTPS connections
   - Add exception if needed

3. **Proxy configuration** (if behind corporate firewall):
   ```bash
   export HTTP_PROXY="http://proxy:port"
   export HTTPS_PROXY="http://proxy:port"
   python3 extract.py "COURSE_URL"
   ```

### Error: "SSL Certificate verification failed"

**Symptoms:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Causes:**
- System certificates out of date
- Corporate proxy intercepting SSL
- Python SSL module not configured

**Solutions:**

1. **Update certificates**:
   ```bash
   # macOS
   /Applications/Python\ 3.x/Install\ Certificates.command

   # Linux
   sudo apt-get install ca-certificates
   ```

2. **If behind corporate proxy**, install proxy certificate:
   ```bash
   export REQUESTS_CA_BUNDLE=/path/to/proxy-cert.pem
   ```

---

## Python Version Errors

### Error: "SyntaxError: invalid syntax"

**Symptoms:**
```
  File "extract.py", line 15
    def parse_course_url(url: str) -> dict:
                          ^
SyntaxError: invalid syntax
```

**Cause:**
- Running with Python 2.x instead of Python 3.8+
- Type hints not supported in Python 2

**Solutions:**

1. **Use `python3` command**:
   ```bash
   python3 extract.py "COURSE_URL"
   # NOT: python extract.py
   ```

2. **Verify Python version**:
   ```bash
   python3 --version
   # Should show: Python 3.8.x or higher
   ```

3. **Make script executable** (uses shebang `#!/usr/bin/env python3`):
   ```bash
   chmod +x extract.py
   ./extract.py "COURSE_URL"
   ```

### Error: "ModuleNotFoundError"

**Symptoms:**
```
ModuleNotFoundError: No module named 'some_module'
```

**Cause:**
- Should not happen! Script uses only standard library

**Solution:**

If you see this error, you may have:
1. Modified the script to use external packages
2. Corrupted Python installation

**Fix:**
```bash
# Reinstall Python 3.8+
# Verify standard library is intact:
python3 -c "import urllib.request, json, re; print('OK')"
```

---

## Getting Help

If issues persist:

1. **Check recent changes**:
   - See `IMPLEMENTATION_SUMMARY.md` for recent updates
   - Check `../../../udemy-research/FUTURE_EXTRACTORS_ROADMAP.md` for known issues

2. **Enable debug logging**:
   ```python
   # In extract.py, change logging level:
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Run content analysis**:
   ```bash
   python3 scripts/tools/analyze_content_types.py "COURSE_URL" debug-analysis.json
   # Check output for API response details
   ```

4. **Check API documentation**:
   - See `../../../udemy-research/API.md` for endpoint details
   - May need to update endpoints if Udemy changed their API

---

## Quick Reference

| Error | Quick Fix |
|-------|-----------|
| Authentication failed | Refresh cookies from browser |
| Course not found | Verify enrollment, check URL |
| No transcripts | Check if lecture has captions in UI |
| No resources (but visible in UI) | Verify `supplementary_assets` parsing (bug fix 2025-10-18) |
| Python syntax error | Use `python3` command |
| Rate limited | Increase delay in extract.py |
| Download failed | Re-run (skips completed), or use `--no-download-resources` |
| Network timeout | Check connection, try again |
