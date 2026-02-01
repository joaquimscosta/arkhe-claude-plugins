#!/bin/bash
# Ralph Wiggum Autonomous Development Loop
# =========================================
# Runs Claude Code in a continuous loop, each iteration with a fresh
# context window. Reads PROMPT.md and feeds it to Claude until all tasks
# are complete or max iterations is reached.
#
# Usage: ./ralph.sh [max_iterations]
# Example: ./ralph.sh 20

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
MAX_ITERATIONS=${1:-20}
COMPLETION_SIGNAL="RALPH_COMPLETE:"
PROMPT_FILE="PROMPT.md"
TASKSET_LINK=".ralph/current-taskset"
TASKS_FILE=".ralph/current-taskset/tasks.json"
ACTIVITY_LOG=".ralph/current-taskset/activity.log"

# Print banner
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}   Ralph Wiggum Autonomous Loop      ${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Verify required files exist
if [[ ! -f "$PROMPT_FILE" ]]; then
  echo -e "${RED}Error: $PROMPT_FILE not found${NC}"
  echo "Run /create-prd first to set up your project for Ralph."
  exit 1
fi

if [[ ! -L "$TASKSET_LINK" ]]; then
  echo -e "${RED}Error: No active task set${NC}"
  echo "Run /ralph taskset list to see available task sets."
  echo "Run /ralph taskset switch <name> to activate one."
  echo "Or run /create-prd to create a new project."
  exit 1
fi

if [[ ! -f "$TASKS_FILE" ]]; then
  echo -e "${RED}Error: $TASKS_FILE not found${NC}"
  echo "Current task set appears broken. Check .ralph/current-taskset symlink."
  exit 1
fi

# Create screenshots directory if it doesn't exist
mkdir -p screenshots

# Get current taskset name from symlink
CURRENT_TASKSET=$(basename "$(readlink "$TASKSET_LINK")")

# Display configuration
echo -e "Task set: ${GREEN}$CURRENT_TASKSET${NC}"
echo -e "Max iterations: ${GREEN}$MAX_ITERATIONS${NC}"
echo -e "Completion signal: ${GREEN}$COMPLETION_SIGNAL${NC}"
echo -e "Prompt file: ${CYAN}$PROMPT_FILE${NC}"
echo -e "Tasks file: ${CYAN}$TASKS_FILE${NC}"
echo ""
echo -e "${YELLOW}Starting in 3 seconds... Press Ctrl+C to abort${NC}"
sleep 3
echo ""

# Main loop
for ((i=1; i<=MAX_ITERATIONS; i++)); do
  echo -e "${BLUE}======================================${NC}"
  echo -e "${BLUE}   Iteration $i of $MAX_ITERATIONS${NC}"
  echo -e "${BLUE}   Task Set: $CURRENT_TASKSET${NC}"
  echo -e "${BLUE}======================================${NC}"
  echo ""

  # Run Claude with fresh context (read prompt file each time)
  # Using --output-format text for cleaner output
  result=$(claude -p "$(cat "$PROMPT_FILE")" --output-format text 2>&1) || true

  echo "$result"
  echo ""

  # Check for completion signal
  if echo "$result" | grep -q "$COMPLETION_SIGNAL"; then
    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}   RALPH COMPLETE!                   ${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo -e "Task set '${GREEN}$CURRENT_TASKSET${NC}' finished after ${GREEN}$i${NC} iteration(s)"
    echo ""
    echo "Next steps:"
    echo "  1. Review the completed work in your project"
    echo "  2. Check .ralph/current-taskset/activity.log for the full build log"
    echo "  3. Check .ralph/current-taskset/memories.md for learnings"
    echo "  4. Review screenshots/ for visual verification"
    echo "  5. Run your tests to verify everything works"
    echo ""
    echo "To work on another task set:"
    echo "  /ralph taskset new \"next-feature\""
    echo ""
    exit 0
  fi

  echo ""
  echo -e "${YELLOW}--- End of iteration $i ---${NC}"
  echo ""

  # Small delay between iterations to prevent hammering
  sleep 2
done

# Max iterations reached without completion
echo ""
echo -e "${RED}======================================${NC}"
echo -e "${RED}   MAX ITERATIONS REACHED            ${NC}"
echo -e "${RED}======================================${NC}"
echo ""
echo -e "Task set '${RED}$CURRENT_TASKSET${NC}' reached max iterations (${RED}$MAX_ITERATIONS${NC}) without completion."
echo ""
echo "Options:"
echo "  1. Run again with more iterations: ./ralph.sh 50"
echo "  2. Check .ralph/current-taskset/activity.log to see current progress"
echo "  3. Check .ralph/current-taskset/tasks.json to see remaining tasks"
echo "  4. Check .ralph/current-taskset/memories.md for any learnings"
echo "  5. Manually complete remaining tasks"
echo ""
exit 1
