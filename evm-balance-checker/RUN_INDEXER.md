# Running the DeFi Indexer

## ✅ Quick Start - Using the Pre-configured Indexer

The easiest way to run the indexer is to use the pre-configured `defi_indexer` directory:

```bash
cd /Users/slavid/Documents/GitHub/rindfolio/evm-balance-checker/defi_indexer

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: defi_indexer_db
    environment:
      POSTGRES_USER: rindexer
      POSTGRES_PASSWORD: rindexer
      POSTGRES_DB: defi_indexer
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rindexer"]
      interval: 10s
      timeout: 5s
      retries: 5

  rindexer:
    image: ghcr.io/joshstevens19/rindexer:latest
    container_name: defi_indexer
    platform: linux/amd64
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - ETHEREUM_RPC_URL=https://eth.llamarpc.com
      - ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
      - POLYGON_RPC_URL=https://polygon-rpc.com
      - OPTIMISM_RPC_URL=https://mainnet.optimism.io
      - AVALANCHE_RPC_URL=https://api.avax.network/ext/bc/C/rpc
      - BASE_RPC_URL=https://mainnet.base.org
      - DATABASE_URL=postgresql://rindexer:rindexer@postgres:5432/defi_indexer
    volumes:
      - .:/workspace
    working_dir: /workspace
    command: ["start", "all"]
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# Start the indexer
docker compose up -d

# View logs
docker compose logs -f rindexer
```

## 📊 What's Being Indexed

The `defi_indexer` configuration tracks:

- **Aave V3** on Ethereum, Arbitrum, Polygon, Optimism, Base
- **Uniswap V3** on Ethereum, Arbitrum, Polygon, Optimism, Base  
- **Lido stETH** on Ethereum
- **Rocket Pool rETH** on Ethereum

## 🔌 Connect to Database

Once running, you can connect to the PostgreSQL database:

```bash
psql postgresql://rindexer:rindexer@localhost:5432/defi_indexer
```

## 🛑 Stop the Indexer

```bash
cd /Users/slavid/Documents/GitHub/rindfolio/evm-balance-checker/defi_indexer
docker compose down
```

## 🔄 Restart the Indexer

```bash
cd /Users/slavid/Documents/GitHub/rindfolio/evm-balance-checker/defi_indexer
docker compose restart rindexer
```

## 📝 View Logs

```bash
cd /Users/slavid/Documents/GitHub/rindfolio/evm-balance-checker/defi_indexer
docker compose logs -f rindexer
```

## 🔧 Troubleshooting

### Container keeps restarting

Check logs for errors:
```bash
docker compose logs rindexer --tail=100
```

### Can't connect to database

Ensure PostgreSQL is healthy:
```bash
docker compose ps
docker compose logs postgres
```

### Slow syncing

The indexer is using public RPCs which can be slow. For better performance, set your own RPC URLs in the docker-compose.yml environment section.

## 📈 Next Steps: Connect to Web Client

Once the indexer is running and has indexed some data, you can connect the web client (`app.py`) to query the PostgreSQL database instead of making direct RPC calls.

This will provide:
- ✅ Much faster queries
- ✅ Historical data
- ✅ Complex aggregations
- ✅ Lower RPC usage

See `CONNECT_WEB_CLIENT.md` for integration instructions.

