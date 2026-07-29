#!/usr/bin/env bash
set -e

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${HOME}/.gemini/config/plugins"

echo -e "${BLUE}=== Arkhe Plugins Installer for Antigravity CLI (agy) ===${NC}\n"

# 1. Build shims to ensure everything is up to date
if [ -f "${REPO_DIR}/scripts/build-shims.sh" ]; then
  echo -e "${YELLOW}Building latest extension shims...${NC}"
  bash "${REPO_DIR}/scripts/build-shims.sh" > /dev/null 2>&1 || true
fi

# 2. Create plugins target directory
mkdir -p "${TARGET_DIR}"

# 3. Determine plugins to install
REQUESTED_PLUGINS=("$@")
PLUGINS_TO_INSTALL=()

if [ ${#REQUESTED_PLUGINS[@]} -eq 0 ]; then
  for p in "${REPO_DIR}/.gemini-extensions"/*; do
    if [ -d "$p" ]; then
      PLUGINS_TO_INSTALL+=("$(basename "$p")")
    fi
  done
else
  PLUGINS_TO_INSTALL=("${REQUESTED_PLUGINS[@]}")
fi

# Ensure 'core' is installed first if present in the list
HAS_CORE=false
OTHER_PLUGINS=()
for p in "${PLUGINS_TO_INSTALL[@]}"; do
  if [ "$p" == "core" ]; then
    HAS_CORE=true
  else
    OTHER_PLUGINS+=("$p")
  fi
done

FINAL_PLUGINS=()
if [ "$HAS_CORE" = true ]; then
  FINAL_PLUGINS+=("core")
fi
FINAL_PLUGINS+=("${OTHER_PLUGINS[@]}")

# 4. Install symlinks
INSTALLED_COUNT=0
for plugin in "${FINAL_PLUGINS[@]}"; do
  [ -z "$plugin" ] && continue

  SRC="${REPO_DIR}/.gemini-extensions/${plugin}"
  DEST="${TARGET_DIR}/${plugin}"

  if [ ! -d "$SRC" ]; then
    echo -e "${RED}✘ Plugin '$plugin' not found in .gemini-extensions/${NC}"
    continue
  fi

  rm -rf "$DEST"
  ln -s "$SRC" "$DEST"
  echo -e "${GREEN}✔ Installed plugin:${NC} $plugin"
  INSTALLED_COUNT=$((INSTALLED_COUNT + 1))
done

echo -e "\n${BLUE}=== Summary ===${NC}"
echo -e "Installed ${GREEN}${INSTALLED_COUNT}${NC} plugins into ${TARGET_DIR}"

# 5. Validate with agy CLI if installed
if command -v agy >/dev/null 2>&1; then
  echo -e "\n${YELLOW}Validating installed core plugin with agy...${NC}"
  agy plugin validate "${TARGET_DIR}/core" || true
fi

echo -e "\n${GREEN}Done! Restart agy or start a new session to use your installed plugins.${NC}"
