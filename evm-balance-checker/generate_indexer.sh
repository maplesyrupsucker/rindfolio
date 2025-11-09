#!/bin/bash

# DeFi Indexer Generator - Quick Start Script
# This script sets up and runs the auto-generator for rindexer.yaml

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║       🚀 DeFi Indexer Generator - Auto Setup                  ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "📥 Activating virtual environment and installing dependencies..."
source venv/bin/activate

# Install/upgrade dependencies
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Check for Etherscan API key
if [ -z "$ETHERSCAN_API_KEY" ]; then
    echo "⚠️  ETHERSCAN_API_KEY not set (using free tier with rate limits)"
    echo "   To set it: export ETHERSCAN_API_KEY='your_key_here'"
else
    echo "✅ ETHERSCAN_API_KEY found"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🚀 Running DeFi Indexer Generator..."
echo "════════════════════════════════════════════════════════════════"
echo ""

# Run the generator
python3 defi_indexer_generator.py

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✨ GENERATION COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📁 Generated files:"
echo "   • rindexer.yaml - Main configuration file"
echo "   • abis/ - Cached contract ABIs"
echo ""
echo "🔍 Quick review:"
echo "   cat rindexer.yaml"
echo "   ls -la abis/"
echo ""
echo "🚀 Next steps:"
echo "   1. Review rindexer.yaml"
echo "   2. Set up PostgreSQL: docker-compose up -d postgres"
echo "   3. Start indexing: rindexer start all"
echo ""
echo "📚 Documentation: INDEXER_GENERATOR_README.md"
echo ""

