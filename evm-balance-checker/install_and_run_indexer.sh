#!/bin/bash

set -e

echo "========================================"
echo "🚀 DeFi Indexer - Install & Run"
echo "========================================"
echo ""

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "📦 Rust/Cargo not found. Installing..."
    echo ""
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
    echo ""
    echo "✅ Rust installed successfully"
else
    echo "✅ Rust/Cargo already installed"
fi

echo ""
echo "📦 Installing rindexer..."
cargo install rindexer

echo ""
echo "✅ rindexer installed successfully"
echo ""

# Start PostgreSQL if not running
if ! docker ps | grep -q defi_indexer_db; then
    echo "🐘 Starting PostgreSQL..."
    docker run -d \
      --name defi_indexer_db \
      -e POSTGRES_USER=rindexer \
      -e POSTGRES_PASSWORD=rindexer \
      -e POSTGRES_DB=defi_indexer \
      -p 5432:5432 \
      postgres:15-alpine
    
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 10
    echo "✅ PostgreSQL is running"
else
    echo "✅ PostgreSQL already running"
fi

echo ""
echo "🔧 Setting up environment..."

# Export environment variables
export ETHEREUM_RPC_URL=https://eth.llamarpc.com
export ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
export POLYGON_RPC_URL=https://polygon-rpc.com
export OPTIMISM_RPC_URL=https://mainnet.optimism.io
export AVALANCHE_RPC_URL=https://api.avax.network/ext/bc/C/rpc
export BASE_RPC_URL=https://mainnet.base.org
export DATABASE_URL=postgresql://rindexer:rindexer@localhost:5432/defi_indexer

echo "✅ Environment configured"
echo ""
echo "========================================"
echo "🚀 Starting rindexer..."
echo "========================================"
echo ""
echo "📍 Working directory: $(pwd)/indexer_config"
echo "📊 Indexing 34 contracts across 6 chains"
echo "⏳ This will run continuously. Press Ctrl+C to stop."
echo ""

cd indexer_config
rindexer start all

