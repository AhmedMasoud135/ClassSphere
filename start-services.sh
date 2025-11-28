#!/bin/bash

# ClassSphere - Start All Services Script

echo "🚀 Starting ClassSphere Services..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -d "summarize_quiz_generator" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the ClassSphere root directory"
    exit 1
fi

# Function to start backend
start_backend() {
    echo -e "${BLUE}📡 Starting Summarize Quiz Generator Backend...${NC}"
    cd summarize_quiz_generator
    
    # Activate virtual environment
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python -m venv venv
    fi
    
    source venv/Scripts/activate
    
    # Install dependencies if needed
    pip install -q -r requirements.txt
    
    # Start Flask server
    echo -e "${GREEN}✅ Backend starting on http://localhost:5001${NC}"
    python app.py &
    BACKEND_PID=$!
    
    cd ..
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}🎨 Starting Frontend...${NC}"
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing npm dependencies...${NC}"
        npm install
    fi
    
    # Start Next.js dev server
    echo -e "${GREEN}✅ Frontend starting on http://localhost:3000${NC}"
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
}

# Start services
start_backend
sleep 3
start_frontend

echo ""
echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo "📡 Backend API: http://localhost:5001"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
wait
