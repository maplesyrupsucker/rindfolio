# DeFi Indexer Integration Guide

Complete guide for integrating the auto-generated rindexer configuration with your portfolio tracker.

## 🎯 Overview

This system automatically discovers DeFi protocols from The Graph subgraphs, fetches their ABIs from block explorers, and generates a production-ready `rindexer.yaml` configuration file.

## 📋 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     THE GRAPH SUBGRAPHS                      │
│  (Aave, Compound, Uniswap, Curve, Lido, Yearn, etc.)       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│            DEFI INDEXER GENERATOR (Python)                   │
│  • Discovers protocols and contracts                         │
│  • Fetches ABIs from Etherscan/Arbiscan/etc.               │
│  • Extracts relevant events (Supply, Mint, Stake, etc.)    │
│  • Generates rindexer.yaml                                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                  RINDEXER (Rust)                            │
│  • Indexes blockchain events in real-time                   │
│  • Stores in PostgreSQL                                     │
│  • Provides query interface                                 │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              PORTFOLIO TRACKER (Flask + Web UI)              │
│  • Queries indexed data for instant results                 │
│  • Displays positions, balances, history                    │
│  • Multi-chain support                                      │
└──────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Generate Indexer Configuration

```bash
# Make setup script executable
chmod +x setup_indexer.sh

# Run the generator
./setup_indexer.sh
```

This will:
- ✅ Create Python virtual environment
- ✅ Install dependencies (requests, pyyaml)
- ✅ Fetch ABIs from block explorers
- ✅ Generate `rindexer.yaml`
- ✅ Create `README_INDEXER.md`

### 2. Review Generated Files

```bash
# Check the configuration
cat rindexer.yaml

# View cached ABIs
ls -la abis/

# Read documentation
cat README_INDEXER.md
```

### 3. Install rindexer

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install rindexer
cargo install rindexer
```

### 4. Start Indexing

```bash
# Start the indexer
rindexer start

# Check status
rindexer status

# View logs
rindexer logs
```

## 📊 What Gets Indexed

### Lending Protocols
- **Aave V3** (Ethereum, Arbitrum, Polygon, Avalanche)
  - Events: `Supply`, `Withdraw`, `Borrow`, `Repay`, `LiquidationCall`
  - 25+ aTokens tracked across chains

- **Compound V3** (Ethereum, Arbitrum, Polygon)
  - Events: `Supply`, `Withdraw`, `SupplyCollateral`, `WithdrawCollateral`

### DEX / Liquidity
- **Uniswap V3** (Ethereum, Arbitrum, Polygon)
  - Events: `Mint`, `Burn`, `IncreaseLiquidity`, `DecreaseLiquidity`
  - NFT position tracking

- **Uniswap V2 / Forks** (Ethereum, Polygon, BSC)
  - Events: `Mint`, `Burn`, `Swap`
  - LP token tracking

- **Curve** (Ethereum, Arbitrum, Polygon)
  - Events: `AddLiquidity`, `RemoveLiquidity`, `RemoveLiquidityOne`

- **Balancer V2** (Ethereum, Arbitrum, Polygon)
  - Events: `PoolBalanceChanged`, `Swap`, `PoolCreated`

- **SushiSwap** (Ethereum, Arbitrum, Polygon)
  - Events: `Mint`, `Burn`, `Swap`

### Staking
- **Lido** (Ethereum)
  - Events: `Submitted`, `Transfer`, `Approval`
  - stETH tracking

- **Rocket Pool** (Ethereum)
  - Events: `Deposit`, `Burn`, `Transfer`
  - rETH tracking

### Yield Aggregators
- **Yearn** (Ethereum, Arbitrum)
  - Events: `Deposit`, `Withdraw`
  - Vault positions

- **Convex** (Ethereum)
  - Events: `Staked`, `Withdrawn`, `RewardPaid`

### Perpetuals
- **GMX** (Arbitrum, Avalanche)
  - Events: `IncreasePosition`, `DecreasePosition`, `LiquidatePosition`

## 🔧 Configuration

### Environment Variables

Copy `env.example` to `.env`:

```bash
cp env.example .env
```

Edit `.env` and add your API keys:

```bash
# Block Explorer API Keys (Required for ABI fetching)
ETHERSCAN_API_KEY=your_key_here
ARBISCAN_API_KEY=your_key_here
POLYGONSCAN_API_KEY=your_key_here
SNOWTRACE_API_KEY=your_key_here
BSCSCAN_API_KEY=your_key_here

# Database (Required for rindexer)
DATABASE_URL=postgresql://postgres:password@localhost:5432/defi_positions
```

### Get Free API Keys

1. **Etherscan**: https://etherscan.io/apis
2. **Arbiscan**: https://arbiscan.io/apis
3. **Polygonscan**: https://polygonscan.com/apis
4. **Snowtrace**: https://snowtrace.io/apis
5. **BscScan**: https://bscscan.com/apis

All provide free tier with 5 calls/second.

## 🔌 Integration with Portfolio Tracker

### Option 1: Direct Database Queries

Query indexed data directly from PostgreSQL:

```python
import psycopg2

# Connect to rindexer database
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Get user's Aave positions
cursor.execute("""
    SELECT * FROM aave_v3_ethereum_supply 
    WHERE user = %s 
    ORDER BY block_number DESC
""", (user_address,))

positions = cursor.fetchall()
```

### Option 2: Hybrid Approach (Recommended)

Use rindexer for historical data, live RPC for current state:

```python
def get_user_defi_positions(address: str, chain: str):
    """Get DeFi positions using hybrid approach"""
    
    # 1. Query indexed historical events
    historical_events = query_indexed_events(address, chain)
    
    # 2. Calculate current positions from events
    positions = calculate_positions_from_events(historical_events)
    
    # 3. Verify with live RPC call for current balance
    for position in positions:
        current_balance = get_live_balance(
            position['contract'], 
            address, 
            chain
        )
        position['balance'] = current_balance
    
    return positions

def query_indexed_events(address: str, chain: str):
    """Query rindexer database for user events"""
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    # Get all relevant events for user
    cursor.execute("""
        SELECT event_name, contract_address, block_number, 
               transaction_hash, data, timestamp
        FROM events
        WHERE user_address = %s 
          AND chain = %s
        ORDER BY block_number ASC
    """, (address, chain))
    
    return cursor.fetchall()
```

### Option 3: API Layer

Create a unified API that combines both sources:

```python
@app.route('/api/positions/<address>')
def get_positions(address):
    """Unified endpoint for all positions"""
    
    # Get indexed historical data
    indexed_data = get_indexed_positions(address)
    
    # Get live balances
    live_balances = get_live_balances(address)
    
    # Merge and enrich
    positions = merge_positions(indexed_data, live_balances)
    
    return jsonify(positions)
```

## 📈 Performance Benefits

### Without Indexer (Current)
- ❌ 50+ RPC calls per address check
- ❌ 5-10 seconds response time
- ❌ Rate limited by RPC providers
- ❌ No historical data
- ❌ Expensive to scale

### With Indexer
- ✅ 1 database query + few RPC calls
- ✅ <1 second response time
- ✅ No rate limits
- ✅ Full historical data
- ✅ Scales infinitely

## 🎨 UI Integration

### Display Indexed History

```javascript
// Fetch position history
async function fetchPositionHistory(address, protocol) {
    const response = await fetch(
        `/api/history/${address}/${protocol}`
    );
    const history = await response.json();
    
    // Display timeline
    displayTimeline(history);
}

// Display timeline of events
function displayTimeline(events) {
    const timeline = document.getElementById('timeline');
    
    events.forEach(event => {
        const item = document.createElement('div');
        item.className = 'timeline-item';
        item.innerHTML = `
            <div class="timeline-date">${formatDate(event.timestamp)}</div>
            <div class="timeline-event">
                <span class="event-type">${event.event_name}</span>
                <span class="event-amount">${formatAmount(event.amount)}</span>
                <a href="${getExplorerLink(event.tx_hash)}" target="_blank">
                    View TX ↗
                </a>
            </div>
        `;
        timeline.appendChild(item);
    });
}
```

### Show Position Changes

```javascript
// Calculate position changes over time
function calculatePositionChanges(events) {
    const changes = [];
    let currentBalance = 0;
    
    events.forEach(event => {
        if (event.event_name === 'Supply' || event.event_name === 'Deposit') {
            currentBalance += event.amount;
        } else if (event.event_name === 'Withdraw') {
            currentBalance -= event.amount;
        }
        
        changes.push({
            timestamp: event.timestamp,
            balance: currentBalance,
            event: event.event_name
        });
    });
    
    return changes;
}

// Display chart
function displayPositionChart(changes) {
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: changes.map(c => formatDate(c.timestamp)),
            datasets: [{
                label: 'Position Size',
                data: changes.map(c => c.balance),
                borderColor: '#8B5CF6',
                fill: true
            }]
        }
    });
}
```

## 🔄 Updating Configuration

To add new protocols or update existing ones:

1. **Edit `defi_indexer_generator.py`**:

```python
DEFI_PROTOCOLS = {
    # Add new protocol
    'new-protocol': {
        'ethereum': 'protocol/subgraph-name',
        'arbitrum': 'protocol/subgraph-arbitrum',
        'category': 'lending',  # or 'dex', 'staking', etc.
        'events': ['Deposit', 'Withdraw']
    },
    # ... existing protocols
}
```

2. **Regenerate configuration**:

```bash
./setup_indexer.sh
```

3. **Restart rindexer**:

```bash
rindexer restart
```

## 🐛 Troubleshooting

### Issue: "No ABI found"

**Solution**: Check API keys in `.env` file

```bash
# Test API key
curl "https://api.etherscan.io/api?module=contract&action=getabi&address=0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2&apikey=YOUR_KEY"
```

### Issue: "Rate limit exceeded"

**Solution**: Add delays or upgrade to paid tier

```python
# In defi_indexer_generator.py
time.sleep(0.5)  # Increase delay between requests
```

### Issue: "Database connection failed"

**Solution**: Ensure PostgreSQL is running

```bash
# Start PostgreSQL
brew services start postgresql

# Create database
createdb defi_positions
```

### Issue: "Events not indexing"

**Solution**: Check rindexer logs

```bash
rindexer logs --follow
```

## 📚 Additional Resources

- **rindexer Documentation**: https://github.com/joshstevens19/rindexer
- **The Graph Explorer**: https://thegraph.com/explorer
- **Etherscan API Docs**: https://docs.etherscan.io/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

## 🎯 Next Steps

1. ✅ Generate `rindexer.yaml`
2. ✅ Install and start rindexer
3. ⏳ Wait for initial sync (can take hours for full history)
4. ✅ Integrate with portfolio tracker
5. ✅ Add UI for historical data
6. ✅ Deploy to production

## 💡 Pro Tips

1. **Start with recent blocks**: Configure `start_block` in `rindexer.yaml` to sync faster
2. **Use multiple databases**: Separate databases per chain for better performance
3. **Cache aggressively**: Cache indexed data for 1+ hours
4. **Batch queries**: Query multiple protocols at once
5. **Monitor sync status**: Display sync progress in UI

## 🚀 Production Deployment

### Docker Compose Setup

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: defi_positions
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  rindexer:
    image: rindexer:latest
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/defi_positions
    volumes:
      - ./rindexer.yaml:/app/rindexer.yaml
      - ./abis:/app/abis
    command: rindexer start

  portfolio_tracker:
    build: .
    depends_on:
      - postgres
      - rindexer
    ports:
      - "5001:5001"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/defi_positions

volumes:
  postgres_data:
```

### Monitoring

```bash
# Check sync status
rindexer status

# Monitor database size
psql -c "SELECT pg_size_pretty(pg_database_size('defi_positions'));"

# View recent events
psql -c "SELECT * FROM events ORDER BY block_number DESC LIMIT 10;"
```

---

**Need help?** Open an issue or check the documentation!

