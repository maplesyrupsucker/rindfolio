# 🔗 Integration Guide - DeFi Indexer Generator

Complete guide for integrating the auto-generated `rindexer.yaml` with your project.

---

## 📋 Table of Contents

1. [Quick Integration](#quick-integration)
2. [With Existing Rindexer Project](#with-existing-rindexer-project)
3. [With Portfolio Tracker](#with-portfolio-tracker)
4. [Custom Integration](#custom-integration)
5. [Production Deployment](#production-deployment)

---

## ⚡ Quick Integration

### Step 1: Generate Configuration

```bash
cd defi-indexer-generator
python3 generate_rindexer.py
```

**Output**:
- `rindexer.yaml` - Indexer configuration
- `abis/*.json` - Contract ABIs

### Step 2: Copy to Rindexer Project

```bash
# Copy config
cp rindexer.yaml ../your-rindexer-project/

# Copy ABIs
cp -r abis ../your-rindexer-project/

# Navigate to project
cd ../your-rindexer-project
```

### Step 3: Start Indexing

```bash
# Install rindexer (if not already)
cargo install rindexer

# Initialize database
rindexer init

# Start indexing
rindexer start
```

**Done!** Your indexer is now tracking DeFi positions across multiple chains.

---

## 🔧 With Existing Rindexer Project

### Merge Configurations

If you already have a `rindexer.yaml`:

```bash
# Backup existing config
cp rindexer.yaml rindexer.yaml.backup

# Merge manually or use this script:
python3 merge_configs.py rindexer.yaml.backup rindexer.yaml
```

**merge_configs.py**:

```python
#!/usr/bin/env python3
import yaml
import sys

def merge_configs(existing_path, new_path, output_path='rindexer_merged.yaml'):
    with open(existing_path) as f:
        existing = yaml.safe_load(f)
    
    with open(new_path) as f:
        new = yaml.safe_load(f)
    
    # Merge networks
    existing['networks'].update(new['networks'])
    
    # Merge contracts (avoid duplicates)
    existing_names = {c['name'] for c in existing['contracts']}
    for contract in new['contracts']:
        if contract['name'] not in existing_names:
            existing['contracts'].append(contract)
    
    # Write merged config
    with open(output_path, 'w') as f:
        yaml.dump(existing, f, default_flow_style=False, sort_keys=False)
    
    print(f"✓ Merged config written to {output_path}")
    print(f"  Networks: {len(existing['networks'])}")
    print(f"  Contracts: {len(existing['contracts'])}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 merge_configs.py existing.yaml new.yaml")
        sys.exit(1)
    
    merge_configs(sys.argv[1], sys.argv[2])
```

---

## 📊 With Portfolio Tracker

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Portfolio Tracker (Flask)                 │
│  - User queries address                                     │
│  - Fetches balances via RPC                                 │
│  - Queries indexed data from PostgreSQL                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   PostgreSQL Database                       │
│  - Indexed DeFi events                                      │
│  - Historical positions                                     │
│  - Transaction history                                      │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                   Rindexer (Background)                     │
│  - Indexes events from rindexer.yaml                        │
│  - Writes to PostgreSQL                                     │
│  - Runs continuously                                        │
└─────────────────────────────────────────────────────────────┘
```

### Step 1: Setup Database

```bash
# Start PostgreSQL (if using Docker)
docker run -d \
  --name defi-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=defi_indexer \
  -p 5432:5432 \
  postgres:15
```

### Step 2: Configure Rindexer

Edit `rindexer.yaml` to add database connection:

```yaml
name: defi_positions_indexer
description: Auto-generated DeFi positions indexer
project_type: no-code

# Add database config
storage:
  postgres:
    enabled: true
    connection_string: "postgresql://postgres:password@localhost:5432/defi_indexer"

networks:
  # ... (generated networks)

contracts:
  # ... (generated contracts)
```

### Step 3: Start Rindexer

```bash
rindexer start
```

### Step 4: Query from Portfolio Tracker

Update `app.py` to query indexed data:

```python
import psycopg2

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="defi_indexer",
        user="postgres",
        password="password"
    )

# Query indexed DeFi positions
def get_indexed_positions(address: str, chain: str) -> List[Dict]:
    """Get DeFi positions from indexed data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Example: Query Aave supply events
    query = """
        SELECT 
            contract_address,
            event_name,
            user_address,
            amount,
            block_number,
            timestamp
        FROM events
        WHERE 
            user_address = %s 
            AND network = %s
            AND event_name IN ('Supply', 'Deposit')
        ORDER BY block_number DESC
        LIMIT 100
    """
    
    cursor.execute(query, (address.lower(), chain))
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return [
        {
            'contract': row[0],
            'event': row[1],
            'user': row[2],
            'amount': row[3],
            'block': row[4],
            'timestamp': row[5]
        }
        for row in results
    ]

# Add to /api/check-chain endpoint
@app.route('/api/check-chain/<address>/<chain>')
def check_chain(address, chain):
    # ... existing code ...
    
    # Add indexed positions
    indexed_positions = get_indexed_positions(address, chain)
    
    return jsonify({
        'wallet_balances': wallet_balances,
        'defi_positions': defi_positions,
        'indexed_positions': indexed_positions  # New!
    })
```

### Step 5: Display in Frontend

Update `index.html` to show historical data:

```javascript
function displayIndexedPositions(positions) {
    const container = document.getElementById('history-section');
    
    let html = '<h2>📜 Historical Positions</h2>';
    
    positions.forEach(pos => {
        html += `
            <div class="history-card">
                <div class="history-event">${pos.event}</div>
                <div class="history-amount">${formatAmount(pos.amount)}</div>
                <div class="history-time">${formatTimestamp(pos.timestamp)}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}
```

---

## 🎛️ Custom Integration

### Using as a Library

```python
from generate_rindexer import RindexerGenerator, DEFI_PROTOCOLS

# Create generator
generator = RindexerGenerator()

# Add custom protocol
DEFI_PROTOCOLS['my-protocol'] = {
    'name': 'My Protocol',
    'category': 'lending',
    'critical_events': ['Deposit', 'Withdraw'],
    'contracts': {
        'ethereum': ['0x...']
    }
}

# Generate
generator.generate_yaml('custom_rindexer.yaml')
```

### Programmatic Access

```python
from generate_rindexer import ABIDownloader

# Download specific ABI
downloader = ABIDownloader()
abi = downloader.get_abi('0x...', 'ethereum')

# Extract events
events = downloader.extract_events(abi, ['Transfer', 'Approval'])
```

---

## 🚀 Production Deployment

### Docker Compose Setup

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: defi_indexer
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  rindexer:
    image: rindexer/rindexer:latest
    depends_on:
      - postgres
    volumes:
      - ./rindexer.yaml:/app/rindexer.yaml
      - ./abis:/app/abis
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres:5432/defi_indexer
      ETH_RPC_URL: ${ETH_RPC_URL}
      ARB_RPC_URL: ${ARB_RPC_URL}
      POLYGON_RPC_URL: ${POLYGON_RPC_URL}
    restart: unless-stopped

  portfolio-tracker:
    build: ../evm-balance-checker
    depends_on:
      - postgres
    ports:
      - "5001:5001"
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres:5432/defi_indexer
      ETH_RPC_URL: ${ETH_RPC_URL}
      ARB_RPC_URL: ${ARB_RPC_URL}
      POLYGON_RPC_URL: ${POLYGON_RPC_URL}
    restart: unless-stopped

volumes:
  postgres_data:
```

**.env**:

```bash
# Database
DB_PASSWORD=your_secure_password

# RPC URLs (use Alchemy, Infura, or public RPCs)
ETH_RPC_URL=https://eth.llamarpc.com
ARB_RPC_URL=https://arb1.arbitrum.io/rpc
POLYGON_RPC_URL=https://polygon-rpc.com
AVAX_RPC_URL=https://api.avax.network/ext/bc/C/rpc
BSC_RPC_URL=https://bsc-dataseed1.binance.org

# Block Explorer API Keys
ETHERSCAN_API_KEY=your_key
ARBISCAN_API_KEY=your_key
POLYGONSCAN_API_KEY=your_key
SNOWTRACE_API_KEY=your_key
BSCSCAN_API_KEY=your_key
```

### Start Production Stack

```bash
# Generate config
python3 generate_rindexer.py

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f rindexer

# Access portfolio tracker
open http://localhost:5001
```

### Monitoring

```bash
# Check indexing progress
docker-compose exec postgres psql -U postgres -d defi_indexer -c "
  SELECT 
    network, 
    COUNT(*) as event_count,
    MAX(block_number) as latest_block
  FROM events
  GROUP BY network;
"

# Check database size
docker-compose exec postgres psql -U postgres -d defi_indexer -c "
  SELECT pg_size_pretty(pg_database_size('defi_indexer'));
"
```

---

## 🔍 Troubleshooting

### Rindexer Not Starting

**Issue**: `Error: Failed to connect to database`

**Fix**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string
docker-compose exec rindexer env | grep DATABASE_URL
```

### Slow Indexing

**Issue**: Indexing is taking too long

**Fix**:
```yaml
# Add to rindexer.yaml
performance:
  batch_size: 1000
  parallel_requests: 10
  cache_size: 10000
```

### Missing Events

**Issue**: Some events are not being indexed

**Fix**:
1. Check ABI includes the event
2. Verify contract address is correct
3. Check start block is not too recent

```bash
# Verify ABI
cat abis/aave-v3_ethereum.json | jq '.[] | select(.name=="Supply")'

# Check contract on Etherscan
open https://etherscan.io/address/0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2#events
```

---

## 📚 Resources

- [Rindexer Documentation](https://github.com/joshstevens19/rindexer)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [The Graph Docs](https://thegraph.com/docs/)

---

**Ready for production deployment!** 🚀

