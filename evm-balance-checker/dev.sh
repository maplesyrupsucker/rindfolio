#!/bin/bash

echo "🚀 Starting Development Mode..."
echo ""
echo "This will start:"
echo "  • Flask server (backend) on http://localhost:5001"
echo "  • Vite dev server (React hot reload) on http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start Vite dev server in background
echo "⚛️  Starting Vite dev server..."
bun run dev &
VITE_PID=$!

# Wait a moment for Vite to start
sleep 2

# Start Flask server
echo "🐍 Starting Flask server..."
python3 app.py &
FLASK_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $VITE_PID 2>/dev/null
    kill $FLASK_PID 2>/dev/null
    exit
}

# Trap Ctrl+C
trap cleanup INT TERM

# Wait for both processes
wait

