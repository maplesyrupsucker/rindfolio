# 📖 DeFi Indexer Generator - Complete Usage Guide

## 🎯 Quick Start (5 Minutes)

### Step 1: Setup

```bash
# Clone or navigate to the project
cd evm-balance-checker

# Run the setup script
chmod +x generate_indexer.sh
./generate_indexer.sh
```

### Step 2: Review Output

```bash
# Check generated config
cat rindexer.yaml

# Check cached ABIs
ls -la abis/
```

### Step 3: Start Indexing

```bash
# Start PostgreSQL (if using Docker)
docker-compose up -d postgres

# Start rindexer
rindexer start all
```

**That's it!** Your DeFi indexer is now running. 🎉

---

## 🔧 Detailed Setup

### Prerequisites

1. **Python 3.8+**
   ```bash
   python3 --version
   # Should show: Python 3.8.0 or higher
   ```

2. **pip (Python package manager)**
   ```bash
   pip3 --version
   ```

3. **rindexer (for running the indexer)**
   ```bash
   # Install rindexer
   cargo install rindexer
   
   # Or use Docker
   docker pull rindexer/rindexer:latest
   ```

4. **PostgreSQL (for data storage)**
   ```bash
   # Option A: Docker (recommended)
   docker-compose up -d postgres
   
   # Option B: Local installation
   brew install postgresql  # macOS
   sudo apt install postgresql  # Ubuntu
   ```

### Installation

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Set API keys
cp env.example .env
nano .env  # Add your Etherscan API key
source .env  # Load environment variables
```

---

## 🚀 Running the Generator

### Basic Usage

```bash
# Run with default settings
python3 defi_indexer_generator.py
```

### With API Key (Recommended)

```bash
# Set API key for higher rate limits
export ETHERSCAN_API_KEY="your_api_key_here"
python3 defi_indexer_generator.py
```

### Custom Configuration

```bash
# Custom output file
export OUTPUT_FILE="./my_custom_config.yaml"

# Custom cache directory
export CACHE_DIR="./my_abis"

# Custom cache duration (in seconds)
export CACHE_DURATION=3600  # 1 hour

# Run generator
python3 defi_indexer_generator.py
```

---

## 📊 Understanding the Output

### Generated Files

```
evm-balance-checker/
├── rindexer.yaml          # Main configuration file
├── abis/                  # Cached contract ABIs
│   ├── aave-v3_ethereum.json
│   ├── uniswap-v3_ethereum.json
│   ├── curve_ethereum.json
│   └── ...
└── defi_indexer_generator.py
```

### rindexer.yaml Structure

```yaml
name: defi_positions_indexer
description: Auto-generated DeFi positions indexer
project_type: no-code

# Network configurations
networks:
  ethereum:
    chain_id: 1
    rpc: https://eth.llamarpc.com
  arbitrum:
    chain_id: 42161
    rpc: https://arb1.arbitrum.io/rpc
  # ... more networks

# Storage configuration
storage:
  postgres:
    enabled: true
    drop_each_run: false

# Contract configurations
contracts:
  - name: Aave V3_ethereum
    details:
      - network: ethereum
        address: "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
        start_block: latest
    abi: ./abis/aave-v3_ethereum.json
    include_events:
      - Supply
      - Withdraw
      - Borrow
      - Repay
      - Liquidation
  # ... more contracts
```

---

## 🎨 Customization

### Adding a New Protocol

1. **Find the protocol's contract address**
   - Check the protocol's documentation
   - Look on Etherscan/blockchain explorer

2. **Identify key events**
   - What events track user positions?
   - Examples: `Deposit`, `Mint`, `Stake`, `AddLiquidity`

3. **Add to `defi_indexer_generator.py`**

```python
DEFI_PROTOCOLS = {
    # ... existing protocols
    
    'radiant-capital': {
        'name': 'Radiant Capital',
        'category': 'lending',
        'events': ['Supply', 'Withdraw', 'Borrow', 'Repay'],
        'subgraphs': {
            'arbitrum': 'radiant-community/radiant-v2'
        },
        'contracts': {
            'arbitrum': ['0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1']
        }
    }
}
```

4. **Re-run the generator**

```bash
python3 defi_indexer_generator.py
```

### Adding a New Chain

1. **Add chain configuration**

```python
CHAINS = {
    # ... existing chains
    
    'base': {
        'chain_id': 8453,
        'rpc': 'https://mainnet.base.org',
        'explorer_api': 'https://api.basescan.org/api',
        'graph_network': 'base'
    }
}
```

2. **Add protocol contracts for that chain**

```python
'aave-v3': {
    # ... existing config
    'contracts': {
        # ... existing chains
        'base': ['0xContractAddressOnBase']
    }
}
```

3. **Re-run the generator**

### Filtering Events

To only index specific events, modify the `events` list:

```python
# Only track deposits and withdrawals
'events': ['Deposit', 'Withdraw']

# Track all liquidity events
'events': ['AddLiquidity', 'RemoveLiquidity', 'RemoveLiquidityOne']
```

---

## 🔍 Monitoring & Debugging

### Check Generator Output

```bash
# Run with verbose output
python3 defi_indexer_generator.py 2>&1 | tee generator.log

# Check for errors
grep "✗" generator.log

# Check success count
grep "✓" generator.log | wc -l
```

### Verify ABIs

```bash
# List all cached ABIs
ls -lh abis/

# Check a specific ABI
cat abis/aave-v3_ethereum.json | jq '.[] | select(.type=="event") | .name'
```

### Test Generated Config

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('rindexer.yaml'))"

# Pretty print config
cat rindexer.yaml | yq .
```

### Check Indexer Status

```bash
# Start indexer in foreground (for debugging)
rindexer start all

# Check logs
tail -f ~/.rindexer/logs/indexer.log

# Check database
psql -h localhost -U postgres -d rindexer -c "SELECT * FROM events LIMIT 10;"
```

---

## 🐛 Troubleshooting

### Issue: Rate Limit Errors

**Symptom**: `Max rate limit reached` or `429 Too Many Requests`

**Solution**:
```bash
# Option 1: Add API key
export ETHERSCAN_API_KEY="your_key"

# Option 2: Wait 1 minute (free tier resets)
sleep 60 && python3 defi_indexer_generator.py

# Option 3: Use cached ABIs (if available)
# Just re-run - cached ABIs are used automatically
python3 defi_indexer_generator.py
```

### Issue: No Events Found

**Symptom**: `No matching events found for address`

**Possible Causes**:
1. Contract not verified on explorer
2. Wrong contract address
3. Event names don't match ABI

**Solution**:
```bash
# Check if contract is verified
curl "https://api.etherscan.io/api?module=contract&action=getabi&address=0xYourAddress"

# Manually inspect ABI
cat abis/protocol_chain.json | jq '.[] | select(.type=="event")'

# Update event names in DEFI_PROTOCOLS
```

### Issue: Connection Timeout

**Symptom**: `Connection timeout` or `Failed to connect`

**Solution**:
```bash
# Check internet connection
ping -c 3 api.etherscan.io

# Try different RPC endpoint
export ETH_RPC_URL="https://eth.llamarpc.com"

# Use VPN if geo-restricted
```

### Issue: Invalid YAML

**Symptom**: `yaml.scanner.ScannerError`

**Solution**:
```bash
# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('rindexer.yaml'))"

# Check for special characters in addresses
grep -E "[^a-zA-Z0-9_\-\.]" rindexer.yaml

# Re-generate with clean data
rm rindexer.yaml
python3 defi_indexer_generator.py
```

---

## 📈 Performance Optimization

### Speed Up Generation

```bash
# Use cached ABIs (24-hour default)
# No action needed - automatic

# Reduce cache duration for testing
export CACHE_DURATION=3600  # 1 hour

# Increase for production
export CACHE_DURATION=604800  # 7 days
```

### Reduce API Calls

```bash
# Pre-download ABIs for all protocols
python3 defi_indexer_generator.py

# Commit ABIs to git (optional)
git add abis/
git commit -m "Add cached ABIs"

# Future runs use cached ABIs
python3 defi_indexer_generator.py  # Fast!
```

### Parallel Processing

Already implemented! The generator uses `ThreadPoolExecutor` for parallel ABI fetching.

---

## 🎯 Production Deployment

### Step 1: Prepare Environment

```bash
# Create production .env
cp env.example .env
nano .env  # Add all API keys

# Set production RPC endpoints (Alchemy, Infura, etc.)
ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
ARB_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY
```

### Step 2: Generate Config

```bash
# Load environment
source .env

# Generate production config
python3 defi_indexer_generator.py

# Verify output
cat rindexer.yaml
```

### Step 3: Setup Database

```bash
# Option A: Docker (recommended)
docker-compose up -d postgres

# Option B: Managed PostgreSQL (AWS RDS, etc.)
# Update connection string in rindexer.yaml
```

### Step 4: Deploy Indexer

```bash
# Option A: Docker
docker-compose up -d rindexer

# Option B: Systemd service
sudo systemctl start rindexer
sudo systemctl enable rindexer

# Option C: Kubernetes
kubectl apply -f k8s/rindexer-deployment.yaml
```

### Step 5: Monitor

```bash
# Check logs
docker logs -f rindexer

# Check database
psql -h localhost -U postgres -d rindexer -c "SELECT COUNT(*) FROM events;"

# Setup alerts (optional)
# - Prometheus + Grafana
# - Datadog
# - CloudWatch
```

---

## 🔐 Security Best Practices

### API Keys

```bash
# Never commit API keys
echo ".env" >> .gitignore

# Use environment variables
export ETHERSCAN_API_KEY="key"

# Or use secrets manager (AWS, GCP, etc.)
aws secretsmanager get-secret-value --secret-id etherscan-api-key
```

### RPC Endpoints

```bash
# Use authenticated endpoints in production
ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY

# Avoid public endpoints (rate limits, reliability issues)
# ❌ https://eth.llamarpc.com
# ✅ https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
```

### Database

```bash
# Use strong passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Enable SSL
POSTGRES_SSL_MODE=require

# Restrict network access
# Only allow indexer to connect
```

---

## 📚 Additional Resources

### Documentation

- [Rindexer Docs](https://github.com/joshstevens19/rindexer)
- [The Graph Explorer](https://thegraph.com/explorer)
- [Etherscan API](https://docs.etherscan.io/)

### Community

- [Rindexer Discord](https://discord.gg/rindexer)
- [The Graph Discord](https://discord.gg/thegraph)
- [Ethereum Stack Exchange](https://ethereum.stackexchange.com/)

### Tools

- [ABI Decoder](https://abi.hashex.org/)
- [Event Signature Database](https://www.4byte.directory/)
- [Contract Diff Checker](https://www.diffchecker.com/)

---

## 💡 Tips & Tricks

### Tip 1: Incremental Indexing

```yaml
# Start from specific block (faster initial sync)
start_block: 15000000  # Ethereum block number
```

### Tip 2: Event Filtering

```yaml
# Only index events with specific parameters
include_events:
  - name: Supply
    filter:
      user: "0xYourAddress"  # Only your transactions
```

### Tip 3: Multi-Environment Setup

```bash
# Development
export OUTPUT_FILE="rindexer.dev.yaml"
python3 defi_indexer_generator.py

# Production
export OUTPUT_FILE="rindexer.prod.yaml"
python3 defi_indexer_generator.py
```

### Tip 4: Backup ABIs

```bash
# Backup cached ABIs
tar -czf abis_backup_$(date +%Y%m%d).tar.gz abis/

# Restore from backup
tar -xzf abis_backup_20250109.tar.gz
```

---

## 🎓 Learning Path

### Beginner

1. Run the generator with default settings
2. Explore the generated `rindexer.yaml`
3. Start indexing one protocol (e.g., Aave)
4. Query the database

### Intermediate

1. Add a new protocol
2. Customize event filtering
3. Add a new chain
4. Setup monitoring

### Advanced

1. Integrate with your application
2. Build custom analytics
3. Optimize for high-throughput
4. Contribute to the project

---

**Happy Indexing! 🚀**

For questions or issues, please open a GitHub issue or join our Discord community.

