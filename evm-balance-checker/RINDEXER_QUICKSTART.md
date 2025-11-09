# 🚀 Rindexer Auto-Generator - Quick Start

**Auto-generate production-ready `rindexer.yaml` from The Graph subgraphs in minutes!**

## 📋 What This Does

This system automatically:
1. ✅ Discovers DeFi protocols from The Graph subgraphs
2. ✅ Fetches contract ABIs from block explorers (Etherscan, Arbiscan, etc.)
3. ✅ Extracts critical events for position tracking
4. ✅ Generates a complete `rindexer.yaml` configuration
5. ✅ Creates comprehensive documentation

## ⚡ Quick Start (5 Minutes)

### Step 1: Run the Generator

```bash
# Make executable
chmod +x setup_indexer.sh

# Run (will create venv, install deps, generate config)
./setup_indexer.sh
```

### Step 2: Configure API Keys

```bash
# Copy example env file
cp env.example .env

# Edit and add your API keys
nano .env
```

Get free API keys (5 calls/sec):
- **Etherscan**: https://etherscan.io/apis
- **Arbiscan**: https://arbiscan.io/apis  
- **Polygonscan**: https://polygonscan.com/apis
- **Snowtrace**: https://snowtrace.io/apis
- **BscScan**: https://bscscan.com/apis

### Step 3: Review Generated Files

```bash
# Check the configuration
cat rindexer.yaml

# View cached ABIs
ls -la abis/

# Read documentation
cat README_INDEXER.md
```

### Step 4: Install & Run Rindexer

```bash
# Install Rust (if needed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install rindexer
cargo install rindexer

# Start indexing!
rindexer start
```

## 📊 What Gets Indexed

### Lending Protocols
- **Aave V3** (Ethereum, Arbitrum, Polygon, Avalanche)
  - 25+ aTokens tracked
  - Events: Supply, Withdraw, Borrow, Repay, Liquidation
  
- **Compound V3** (Ethereum, Arbitrum, Polygon)
  - cTokens tracked
  - Events: Supply, Withdraw, SupplyCollateral

### DEX / Liquidity
- **Uniswap V3** (Ethereum, Arbitrum, Polygon)
  - NFT position tracking
  - Events: Mint, Burn, IncreaseLiquidity, DecreaseLiquidity
  
- **Uniswap V2 / Forks** (Ethereum, Polygon, BSC)
  - LP token tracking
  - Events: Mint, Burn, Swap
  
- **Curve** (Ethereum, Arbitrum, Polygon)
  - Pool positions
  - Events: AddLiquidity, RemoveLiquidity
  
- **Balancer V2** (Ethereum, Arbitrum, Polygon)
  - Pool balances
  - Events: PoolBalanceChanged, Swap
  
- **SushiSwap** (Ethereum, Arbitrum, Polygon)
  - LP positions
  - Events: Mint, Burn, Swap

### Staking
- **Lido** (Ethereum)
  - stETH tracking
  - Events: Submitted, Transfer
  
- **Rocket Pool** (Ethereum)
  - rETH tracking
  - Events: Deposit, Burn

### Yield Aggregators
- **Yearn** (Ethereum, Arbitrum)
  - Vault positions
  - Events: Deposit, Withdraw
  
- **Convex** (Ethereum)
  - Staked positions
  - Events: Staked, Withdrawn, RewardPaid

### Perpetuals
- **GMX** (Arbitrum, Avalanche)
  - Position tracking
  - Events: IncreasePosition, DecreasePosition, Liquidate

## 🎯 Generated Files

```
evm-balance-checker/
├── rindexer.yaml              # Main configuration
├── abis/                      # Contract ABIs
│   ├── aave-v3_ethereum.json
│   ├── uniswap-v3_ethereum.json
│   └── ...
├── README_INDEXER.md          # Documentation
├── INDEXER_INTEGRATION_GUIDE.md  # Integration guide
├── defi_indexer_generator.py  # Generator script
├── graph_api_client.py        # The Graph API client
├── test_indexer_generator.py  # Test suite
└── setup_indexer.sh           # Setup script
```

## 🧪 Testing

Run the test suite to validate everything:

```bash
python3 test_indexer_generator.py
```

This checks:
- ✅ The Graph API connection
- ✅ ABI directory and files
- ✅ rindexer.yaml structure
- ✅ Protocol coverage
- ✅ Event coverage
- ✅ Chain coverage
- ✅ Environment configuration

## 🔧 Customization

### Add New Protocols

Edit `defi_indexer_generator.py`:

```python
DEFI_PROTOCOLS = {
    # Add your protocol
    'my-protocol': {
        'ethereum': 'protocol/subgraph-name',
        'arbitrum': 'protocol/subgraph-arbitrum',
        'category': 'lending',  # or 'dex', 'staking', etc.
        'events': ['Deposit', 'Withdraw', 'Claim']
    },
    # ... existing protocols
}
```

Then regenerate:

```bash
./setup_indexer.sh
```

### Add Custom Contracts

Add specific contract addresses:

```python
def query_subgraph_contracts(self, subgraph_name: str, chain: str) -> List[str]:
    known_contracts = {
        'my-protocol': {
            'ethereum': ['0x...', '0x...'],
            'arbitrum': ['0x...'],
        }
    }
    # ... rest of function
```

### Customize Events

Modify events per protocol:

```python
DEFI_PROTOCOLS = {
    'aave-v3': {
        'ethereum': 'aave/protocol-v3',
        'category': 'lending',
        'events': ['Supply', 'Withdraw', 'Borrow', 'Repay', 'LiquidationCall']
        # Add or remove events as needed
    }
}
```

## 🔌 Integration with Portfolio Tracker

### Option 1: Direct Database Queries

```python
import psycopg2

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Get user's positions
cursor.execute("""
    SELECT * FROM aave_v3_ethereum_supply 
    WHERE user = %s 
    ORDER BY block_number DESC
""", (user_address,))

positions = cursor.fetchall()
```

### Option 2: Hybrid Approach (Recommended)

```python
def get_user_positions(address: str, chain: str):
    # 1. Query indexed historical events
    events = query_indexed_events(address, chain)
    
    # 2. Calculate positions from events
    positions = calculate_positions(events)
    
    # 3. Verify with live RPC for current balance
    for pos in positions:
        pos['balance'] = get_live_balance(pos['contract'], address)
    
    return positions
```

### Option 3: API Layer

```python
@app.route('/api/positions/<address>')
def get_positions(address):
    indexed = get_indexed_positions(address)
    live = get_live_balances(address)
    return jsonify(merge_positions(indexed, live))
```

## 📈 Performance Comparison

### Without Indexer (Current)
- ❌ 50+ RPC calls per address
- ❌ 5-10 seconds response time
- ❌ Rate limited by RPC providers
- ❌ No historical data

### With Indexer
- ✅ 1 database query + few RPC calls
- ✅ <1 second response time
- ✅ No rate limits
- ✅ Full historical data
- ✅ Infinite scalability

## 🐛 Troubleshooting

### "No ABI found"
**Solution**: Check API keys in `.env`

```bash
# Test your API key
curl "https://api.etherscan.io/api?module=contract&action=getabi&address=0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2&apikey=YOUR_KEY"
```

### "Rate limit exceeded"
**Solution**: Add delays or upgrade API tier

```python
# In defi_indexer_generator.py
time.sleep(0.5)  # Increase delay
```

### "Database connection failed"
**Solution**: Ensure PostgreSQL is running

```bash
# macOS
brew services start postgresql

# Create database
createdb defi_positions
```

### "Events not indexing"
**Solution**: Check rindexer logs

```bash
rindexer logs --follow
```

## 📚 Documentation

- **README_INDEXER.md** - Complete indexer documentation
- **INDEXER_INTEGRATION_GUIDE.md** - Integration guide with code examples
- **rindexer docs** - https://github.com/joshstevens19/rindexer

## 🎯 Next Steps

1. ✅ Generate configuration: `./setup_indexer.sh`
2. ✅ Configure API keys in `.env`
3. ✅ Install rindexer: `cargo install rindexer`
4. ✅ Start indexing: `rindexer start`
5. ⏳ Wait for initial sync (can take hours)
6. ✅ Integrate with portfolio tracker
7. ✅ Deploy to production

## 💡 Pro Tips

1. **Start with recent blocks**: Set `start_block` in `rindexer.yaml` to sync faster
2. **Use multiple databases**: Separate DBs per chain for better performance
3. **Cache aggressively**: Cache indexed data for 1+ hours
4. **Batch queries**: Query multiple protocols at once
5. **Monitor sync status**: Display progress in UI

## 🚀 Production Deployment

Use Docker Compose for production:

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

  rindexer:
    image: rindexer:latest
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/defi_positions
    volumes:
      - ./rindexer.yaml:/app/rindexer.yaml
      - ./abis:/app/abis

  portfolio_tracker:
    build: .
    depends_on:
      - postgres
      - rindexer
    ports:
      - "5001:5001"

volumes:
  postgres_data:
```

## 🎉 Success Metrics

After setup, you should have:
- ✅ `rindexer.yaml` with 20+ contracts
- ✅ 50+ ABIs cached in `./abis/`
- ✅ 5+ chains configured
- ✅ 100+ events tracked
- ✅ Full documentation generated

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Docs**: Check README_INDEXER.md and INDEXER_INTEGRATION_GUIDE.md
- **Rindexer**: https://github.com/joshstevens19/rindexer

---

**Ready to index?** Run `./setup_indexer.sh` now! 🚀

