#!/bin/bash

# Setup script for DeFi Indexer Generator
# This script installs dependencies and runs the generator

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║    🚀 DeFi Indexer Generator Setup                            ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install required packages
echo ""
echo "📦 Installing dependencies..."
pip install requests pyyaml > /dev/null 2>&1
echo "✅ Dependencies installed"

# Check for .env file
echo ""
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "📝 IMPORTANT: Edit .env and add your API keys!"
    echo "   Get free keys from:"
    echo "   - Etherscan: https://etherscan.io/apis"
    echo "   - Arbiscan: https://arbiscan.io/apis"
    echo "   - Polygonscan: https://polygonscan.com/apis"
    echo "   - Snowtrace: https://snowtrace.io/apis"
    echo "   - BscScan: https://bscscan.com/apis"
    echo ""
else
    echo "✅ Found existing .env file"
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create abis directory
mkdir -p abis

# Run the generator
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║    🎯 Running DeFi Indexer Generator                          ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

python3 defi_indexer_generator.py

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║    ✨ Setup Complete!                                         ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Generated files:"
echo "   - rindexer.yaml (main configuration)"
echo "   - README_INDEXER.md (documentation)"
echo "   - abis/*.json (contract ABIs)"
echo ""
echo "🎯 Next steps:"
echo "   1. Review rindexer.yaml"
echo "   2. Install rindexer: cargo install rindexer"
echo "   3. Start indexing: rindexer start"
echo ""
echo "💡 To regenerate config:"
echo "   ./setup_indexer.sh"
echo ""

