#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log()  { echo -e "${GREEN}[hexen]${NC} $1"; }
info() { echo -e "${CYAN}[hexen]${NC} $1"; }
err()  { echo -e "${RED}[hexen]${NC} $1" >&2; }

# ─── Check prerequisites ────────────────────────────

check_cmd() {
  if ! command -v "$1" &>/dev/null; then
    err "Missing: $1 — install it first"
    exit 1
  fi
}

check_cmd python3
check_cmd node
check_cmd npm

PYTHON=$(command -v python3)
NODE=$(command -v node)

log "Python: $($PYTHON --version 2>&1)"
log "Node:   $($NODE --version)"

# ─── Install Python packages ────────────────────────

log "Installing Python dependencies..."
$PYTHON -m pip install -e "$ROOT" --quiet 2>/dev/null || {
  info "pip not available, trying ensurepip..."
  $PYTHON -m ensurepip --quiet 2>/dev/null
  $PYTHON -m pip install -e "$ROOT" --quiet
}
log "Python packages installed ✓"

# ─── Install Node packages ──────────────────────────

log "Installing frontend dependencies..."
cd "$ROOT/frontend"
npm install --silent 2>/dev/null || npm install
log "Node packages installed ✓"

# ─── Start servers ──────────────────────────────────

cleanup() {
  log "Shutting down..."
  [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null
  [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null
  wait 2>/dev/null
  log "All servers stopped."
}
trap cleanup EXIT INT TERM

log ""
log "═══════════════════════════════════════════"
log "  ${BOLD}Hexen${NC} — starting servers..."
log "═══════════════════════════════════════════"
log ""

# Start backend API server
BACKEND_PORT="${BACKEND_PORT:-8000}"
log "Starting backend API on http://localhost:${BACKEND_PORT} ..."
$PYTHON "$ROOT/backend_server.py" "$BACKEND_PORT" &
BACKEND_PID=$!
info "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
for i in $(seq 1 15); do
  if curl -s "http://localhost:${BACKEND_PORT}/health" >/dev/null 2>&1; then
    log "Backend ready ✓"
    break
  fi
  sleep 1
done

# Start Astro frontend dev server
FRONTEND_PORT="${FRONTEND_PORT:-4321}"
log "Starting frontend on http://localhost:${FRONTEND_PORT} ..."
npm run dev --prefix "$ROOT/frontend" &
FRONTEND_PID=$!
info "Frontend PID: $FRONTEND_PID"

# Wait for frontend to be ready
for i in $(seq 1 30); do
  if curl -s "http://localhost:${FRONTEND_PORT}" >/dev/null 2>&1; then
    log "Frontend ready ✓"
    break
  fi
  sleep 1
done

log ""
log "═══════════════════════════════════════════"
log "  ${BOLD}Hexen${NC} is running!"
log ""
log "  Frontend:  http://localhost:${FRONTEND_PORT}"
log "  Backend:   http://localhost:${BACKEND_PORT}"
log ""
log "  API Endpoints:"
log "    /movie?action=popular"
log "    /movie/550"
log "    /movie/550/credits"
log "    /movie/550/videos"
log "    /movie/550/images"
log "    /movie/550/reviews"
log "    /tv?action=popular"
log "    /tv/1399"
log "    /tv/1399/credits"
log "    /person/128"
log "    /search?q=fight+club"
log "    /discover/movie"
log "    /trending/movie/day"
log "    /genre/movie"
log "    /health"
log ""
log "  Pages:"
log "    Landing:  http://localhost:${FRONTEND_PORT}/"
log "    Home:     http://localhost:${FRONTEND_PORT}/home"
log "    Movies:   http://localhost:${FRONTEND_PORT}/movies"
log "    TV Shows: http://localhost:${FRONTEND_PORT}/tv"
log "    Discover: http://localhost:${FRONTEND_PORT}/discover"
log "    Search:   http://localhost:${FRONTEND_PORT}/search"
log ""
log "  Press Ctrl+C to stop all servers"
log "═══════════════════════════════════════════"

wait
