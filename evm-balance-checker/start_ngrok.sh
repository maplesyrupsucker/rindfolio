#!/bin/bash

# ngrok Tunnel Starter for EVM Balance Checker
# Usage: ./start_ngrok.sh [your-authtoken]

echo "🌍 Starting ngrok tunnel for EVM Balance Checker..."
echo ""

# Check if authtoken is provided as argument
if [ ! -z "$1" ]; then
    echo "📝 Configuring ngrok with provided authtoken..."
    ngrok config add-authtoken "$1"
fi

# Check if Flask server is running
if ! curl -s http://localhost:5001 > /dev/null; then
    echo "⚠️  Flask server is not running on port 5001!"
    echo "   Starting Flask server..."
    cd "$(dirname "$0")"
    source venv/bin/activate
    nohup python3 app.py > /tmp/flask_server.log 2>&1 &
    sleep 5
fi

echo "✅ Flask server is running on http://localhost:5001"
echo ""
echo "🚀 Starting ngrok tunnel..."
echo ""

# Start ngrok in the background
nohup ngrok http 5001 --log=stdout > /tmp/ngrok.log 2>&1 &

# Wait for ngrok to start
sleep 3

# Try to get the public URL
for i in {1..10}; do
    PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    if tunnels:
        print(tunnels[0]['public_url'])
except:
    pass
" 2>/dev/null)
    
    if [ ! -z "$PUBLIC_URL" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "✨ ngrok tunnel is LIVE!"
        echo ""
        echo "🌐 Public URL: $PUBLIC_URL"
        echo ""
        echo "📱 Access your portfolio from anywhere:"
        echo "   $PUBLIC_URL"
        echo ""
        echo "🔍 ngrok Dashboard: http://localhost:4040"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "💡 To stop ngrok: pkill ngrok"
        echo "💡 To stop Flask: pkill -f 'python.*app.py'"
        echo ""
        exit 0
    fi
    
    sleep 1
done

# If we get here, ngrok didn't start properly
echo "❌ Failed to start ngrok tunnel"
echo ""
echo "📋 Troubleshooting:"
echo "   1. Check if you have an ngrok account: https://dashboard.ngrok.com/signup"
echo "   2. Get your authtoken: https://dashboard.ngrok.com/get-started/your-authtoken"
echo "   3. Run: ngrok config add-authtoken YOUR_TOKEN"
echo "   4. Try again: ./start_ngrok.sh"
echo ""
echo "📄 Check logs:"
echo "   ngrok: tail -f /tmp/ngrok.log"
echo "   Flask: tail -f /tmp/flask_server.log"
echo ""

exit 1

