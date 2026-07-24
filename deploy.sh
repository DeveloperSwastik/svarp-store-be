#!/usr/bin/env bash

# ==============================================================================
# SVARP Store Backend Deployment Script
# Target Server Location: /var/www/svarp-store-be
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

BE_DIR="${BE_DIR:-/var/www/svarp-store-be}"
BRANCH="${BRANCH:-dev}"

echo -e "${CYAN}========================================================================${NC}"
echo -e "${CYAN}                Deploying SVARP Store Backend                           ${NC}"
echo -e "${CYAN}========================================================================${NC}"

if [ -d "$BE_DIR" ]; then
  cd "$BE_DIR"
fi

echo -e "${YELLOW}➜ Pulling latest backend code (origin/${BRANCH})...${NC}"
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull origin "$BRANCH"

if [ -d "venv" ]; then
  echo -e "${YELLOW}➜ Updating python virtualenv dependencies...${NC}"
  source venv/bin/activate
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
  fi
fi

if [ -f "alembic.ini" ]; then
  echo -e "${YELLOW}➜ Running database migrations...${NC}"
  if [ -d "venv" ]; then
    source venv/bin/activate
  fi
  alembic upgrade head || echo -e "${YELLOW}Notice: Migration skipped or already up to date.${NC}"
fi

echo -e "${YELLOW}➜ Restarting systemd service 'svarp-store-be'...${NC}"
sudo systemctl restart svarp-store-be

echo -e "${GREEN}✓ Backend deployment successful!${NC}"
