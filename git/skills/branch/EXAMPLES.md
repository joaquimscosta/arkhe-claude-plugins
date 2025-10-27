# Git Branch Creation: Examples

This document provides real-world examples of branch creation with the `creating-branch` skill.

For quick start instructions, see [SKILL.md](SKILL.md).
For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).

---

## Example 1: Feature Branch (New Functionality)

### Scenario
Adding a new user authentication system to the application.

### Command
```bash
/create-branch add user authentication system
```

### Execution

**Step 1: Parse Description**
```
Input: "add user authentication system"
```

**Step 2: Detect Type**
```
Keyword found: "add"
Type detected: feat
```

**Step 3: Extract Keywords**
```
Remove stopwords: "add"
Meaningful words: ["user", "authentication", "system"]
Selected: "user", "authentication" (first 2)
Keywords: user-authentication
```

**Step 4: Find Next Number**
```
Existing branches: feat/001-profile, feat/002-dashboard
Max number: 002
Next number: 003
```

**Step 5: Create Branch**
```
Branch name: feat/003-user-authentication
Command: git checkout -b feat/003-user-authentication
```

### Output
```
✅ Branch created: feat/003-user-authentication
```

### Typical Usage
```bash
# Create branch
/create-branch add user authentication system

# Make changes
vim src/auth/authenticator.js

# Commit
git add .
git commit -m "feat: implement user authentication"

# Push
git push -u origin feat/003-user-authentication
```

---

## Example 2: Bug Fix Branch

### Scenario
Fixing a null pointer exception in the login service.

### Command
```bash
/create-branch fix null pointer in login service
```

### Execution

**Step 1: Parse**
```
Input: "fix null pointer in login service"
```

**Step 2: Detect Type**
```
Keyword found: "fix"
Type detected: fix
```

**Step 3: Extract Keywords**
```
Remove stopwords: "fix", "in"
Meaningful words: ["null", "pointer", "login", "service"]
Selected: "null", "pointer" (first 2)
Keywords: null-pointer
```

**Step 4: Find Next Number**
```
Existing branches: feat/003-user-authentication
Max number: 003
Next number: 004
```

**Step 5: Create Branch**
```
Branch name: fix/004-null-pointer
Command: git checkout -b fix/004-null-pointer
```

### Output
```
✅ Branch created: fix/004-null-pointer
```

---

## Example 3: Refactoring Branch

### Scenario
Refactoring the authentication service to improve code quality.

### Command
```bash
/create-branch refactor authentication service
```

### Execution

**Detection**:
```
Keyword: "refactor"
Type: refactor
Keywords: authentication-service
Number: 005
```

**Result**:
```
Branch: refactor/005-authentication-service
```

### Output
```
✅ Branch created: refactor/005-authentication-service
```

---

## Example 4: Documentation Branch

### Scenario
Adding documentation for API endpoints.

### Command
```bash
/create-branch document api endpoints
```

### Execution

**Detection**:
```
Keyword: "document"
Type: docs
Keywords: api-endpoints
Number: 006
```

**Result**:
```
Branch: docs/006-api-endpoints
```

### Output
```
✅ Branch created: docs/006-api-endpoints
```

---

## Example 5: Chore Branch

### Scenario
Removing deprecated code from the codebase.

### Command
```bash
/create-branch remove deprecated code
```

### Execution

**Detection**:
```
Keyword: "remove"
Type: chore
Keywords: deprecated-code
Number: 007
```

**Result**:
```
Branch: chore/007-deprecated-code
```

### Output
```
✅ Branch created: chore/007-deprecated-code
```

---

## Example 6: Default to Feature Type

### Scenario
No explicit type keyword in description.

### Command
```bash
/create-branch dashboard improvements
```

### Execution

**Detection**:
```
No keyword found
Default type: feat
Keywords: dashboard-improvements
Number: 008
```

**Result**:
```
Branch: feat/008-dashboard-improvements
```

### Output
```
✅ Branch created: feat/008-dashboard-improvements
```

---

## Example 7: Long Description (Keyword Limiting)

### Scenario
Very detailed description with many words.

### Command
```bash
/create-branch add comprehensive user authentication system with OAuth2 and JWT tokens
```

### Execution

**Detection**:
```
Keyword: "add"
Type: feat
Meaningful words: ["comprehensive", "user", "authentication", "system", "with", "OAuth2", "and", "JWT", "tokens"]
Selected: "user", "authentication" (first 2 meaningful words, skipping "comprehensive")
Keywords: user-authentication
Number: 009
```

**Result**:
```
Branch: feat/009-user-authentication
```

### Output
```
✅ Branch created: feat/009-user-authentication
```

**Note**: The script automatically limits to 2-3 keywords to keep branch names short and readable.

---

## Example 8: Multiple Type Keywords

### Scenario
Description contains multiple type keywords.

### Command
```bash
/create-branch fix and improve login validation
```

### Execution

**Detection**:
```
Keywords found: "fix" (first), "improve" (second)
Type: fix (first keyword takes priority)
Meaningful words: ["and", "improve", "login", "validation"]
Remove: "and", "improve" (stopwords + type keyword)
Selected: "login", "validation"
Keywords: login-validation
Number: 010
```

**Result**:
```
Branch: fix/010-login-validation
```

### Output
```
✅ Branch created: fix/010-login-validation
```

**Note**: First detected type keyword determines branch type.

---

## Example 9: With Feature Directory

### Scenario
Branch creation with `FEATURE_DIR` configured.

### Configuration
```bash
export FEATURE_DIR=".claude/specs"
```

### Command
```bash
/create-branch add payment gateway integration
```

### Execution

**Detection**:
```
Type: feat
Keywords: payment-gateway
Number: 011
Branch: feat/011-payment-gateway
```

**Feature Directory Creation**:
```bash
mkdir -p .claude/specs/feat-011-payment-gateway/
```

### Output
```
✅ Branch created: feat/011-payment-gateway
📁 Feature directory: .claude/specs/feat-011-payment-gateway/
```

### Directory Structure
```
.claude/specs/
└── feat-011-payment-gateway/
    ├── spec.md            # Feature specification
    ├── design.md          # Design decisions
    └── notes.md           # Implementation notes
```

---

## Example 10: Sequential Numbering Across Types

### Scenario
Multiple branches of different types.

### Commands
```bash
/create-branch add user profile
→ feat/001-user-profile

/create-branch fix login bug
→ fix/002-login-bug

/create-branch add dashboard
→ feat/003-dashboard

/create-branch refactor auth
→ refactor/004-auth
```

### Result
```
All branches share sequential numbering:
- feat/001-user-profile
- fix/002-login-bug
- feat/003-dashboard
- refactor/004-auth
```

**Note**: Numbers are global across all branch types, not per-type.

---

## Example 11: Type Detection Keywords

### Complete Keyword Reference

**feat (Feature)**:
```bash
/create-branch add notification system
→ feat/001-notification-system

/create-branch create admin dashboard
→ feat/002-admin-dashboard

/create-branch implement search functionality
→ feat/003-search-functionality

/create-branch new reporting feature
→ feat/004-reporting-feature

/create-branch update user interface
→ feat/005-user-interface

/create-branch improve performance
→ feat/006-performance
```

**fix (Bug Fix)**:
```bash
/create-branch fix crash on startup
→ fix/007-crash-startup

/create-branch bug in payment processing
→ fix/008-payment-processing

/create-branch resolve memory leak
→ fix/009-memory-leak

/create-branch correct validation logic
→ fix/010-validation-logic

/create-branch repair broken link
→ fix/011-broken-link
```

**refactor (Code Refactoring)**:
```bash
/create-branch refactor database layer
→ refactor/012-database-layer

/create-branch rename user model
→ refactor/013-user-model

/create-branch reorganize component structure
→ refactor/014-component-structure
```

**chore (Maintenance)**:
```bash
/create-branch remove old migrations
→ chore/015-old-migrations

/create-branch delete unused files
→ chore/016-unused-files

/create-branch clean up dependencies
→ chore/017-dependencies

/create-branch cleanup test fixtures
→ chore/018-test-fixtures
```

**docs (Documentation)**:
```bash
/create-branch docs for setup process
→ docs/019-setup-process

/create-branch document deployment guide
→ docs/020-deployment-guide

/create-branch documentation for api
→ docs/021-api
```

---

## Example 12: Edge Cases

### Empty or Very Short Descriptions

**One Word**:
```bash
/create-branch authentication
→ feat/001-authentication  # Default type: feat
```

**Two Words**:
```bash
/create-branch fix login
→ fix/002-login
```

**Generic Terms**:
```bash
/create-branch update things
→ feat/003-update-things  # Keeps "update" as keyword since no other meaningful words
```

### Special Characters

**With Punctuation**:
```bash
/create-branch add user's profile page
→ feat/004-user-profile  # Removes apostrophes and special chars
```

**With Numbers**:
```bash
/create-branch add OAuth2 authentication
→ feat/005-oauth-authentication  # Numbers in words are handled
```

---

## Example 13: Real-World Project Workflow

### Scenario: Building a Blog Platform

**Phase 1: Core Features**
```bash
/create-branch add post model
→ feat/001-post-model

/create-branch add user authentication
→ feat/002-user-authentication

/create-branch add comment system
→ feat/003-comment-system
```

**Phase 2: Bug Fixes**
```bash
/create-branch fix post save error
→ fix/004-post-save

/create-branch fix comment validation
→ fix/005-comment-validation
```

**Phase 3: Improvements**
```bash
/create-branch refactor post repository
→ refactor/006-post-repository

/create-branch improve comment performance
→ feat/007-comment-performance
```

**Phase 4: Documentation**
```bash
/create-branch document api endpoints
→ docs/008-api-endpoints
```

**Result**: Clean, sequential branch history across entire project lifecycle.

---

## Common Patterns

### REST API Development
```bash
/create-branch add user endpoints
→ feat/001-user-endpoints

/create-branch add post endpoints
→ feat/002-post-endpoints

/create-branch fix authentication middleware
→ fix/003-authentication-middleware

/create-branch document rest api
→ docs/004-rest-api
```

### Frontend Development
```bash
/create-branch add login component
→ feat/001-login-component

/create-branch add dashboard layout
→ feat/002-dashboard-layout

/create-branch fix responsive design
→ fix/003-responsive-design

/create-branch refactor component structure
→ refactor/004-component-structure
```

### Database Work
```bash
/create-branch add user migration
→ feat/001-user-migration

/create-branch fix foreign key constraint
→ fix/002-foreign-key

/create-branch refactor database schema
→ refactor/003-database-schema
```

---

## Tips for Effective Branch Names

### ✅ Good Practices

1. **Use action verbs**:
   - `/create-branch add payment integration` ✅
   - `/create-branch payment integration` ⚠️ (works but less clear)

2. **Be specific**:
   - `/create-branch fix null pointer in auth` ✅
   - `/create-branch fix bug` ❌ (too vague)

3. **Use conventional keywords**:
   - `/create-branch add user auth` ✅ (detected as feat)
   - `/create-branch implement user auth` ✅ (detected as feat)
   - `/create-branch user auth` ⚠️ (defaults to feat)

4. **Keep descriptions concise**:
   - The script uses first 2-3 meaningful words
   - Longer descriptions are automatically shortened

### ❌ Avoid

1. **Too vague**:
   - `/create-branch work on feature` ❌
   - `/create-branch updates` ❌

2. **Too long** (will be shortened anyway):
   - `/create-branch add comprehensive user authentication system with OAuth2 JWT tokens and refresh token support`
   - Result: `feat/001-user-authentication` (only first 2 meaningful words kept)

3. **Non-descriptive**:
   - `/create-branch temp` ❌
   - `/create-branch test` ❌

---

## Summary

The `creating-branch` skill automatically:
- ✅ Detects branch type from natural language
- ✅ Extracts meaningful keywords
- ✅ Generates short, readable names
- ✅ Maintains sequential numbering
- ✅ Creates consistent branch names

**Result**: Professional, discoverable branch names that align with conventional commits.

For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

*Last Updated: 2025-10-27*
