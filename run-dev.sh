#!/bin/bash
# RR Engine Development Server Launcher
# Starts both the geometry API and frontend dev servers

set -e

echo "=================================="
echo "RR Engine Development Environment"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Start geometry API server
echo -e "${BLUE}Starting Geometry API on port 8001...${NC}"
cd "$SCRIPT_DIR/geometry"
source .venv/bin/activate
python api.py &
GEOMETRY_PID=$!
echo "Geometry API PID: $GEOMETRY_PID"

# Wait for geometry API to be ready
sleep 2

# Start frontend dev server
echo -e "${BLUE}Starting Frontend on port 3000...${NC}"
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo -e "${GREEN}=================================="
echo "Servers running!"
echo "=================================="
echo ""
echo "Frontend:     http://localhost:3000"
echo "Geometry API: http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop all servers"
echo -e "==================================${NC}"

# Trap Ctrl+C and kill both processes
trap "echo 'Shutting down...'; kill $GEOMETRY_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Wait for either process to exit
wait
