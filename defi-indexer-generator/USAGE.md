# 📖 Usage Guide

Complete guide to using the DeFi Indexer Generator.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Advanced Configuration](#advanced-configuration)
3. [Custom Protocols](#custom-protocols)
4. [API Keys Setup](#api-keys-setup)
5. [Troubleshooting](#troubleshooting)
6. [Production Deployment](#production-deployment)

---

## Basic Usage

### 1. Install Dependencies

```bash
cd defi-indexer-generator
pip install -r requirements.txt
```

### 2. Run Generator

```bash
python generate_rindexer.py
```

**Output:**
```
🚀 Generating rindexer.yaml configuration...

📦 Processing Aave V3 (lending)...
  🔗 Chain: ethereum
  Fetching ABI for 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2...
  ✅ ABI fetched successfully (142 items)
  💾 Saved ABI to ./abis/aave-v3_ethereum.json
  ✅ Added contract 0x87870Bca... with 5 events

✅ Generated rindexer.yaml

📊 Statistics:
  • Total Networks: 6
  • Total Contracts: 25
  • Total Events: 87
```

### 3. Review Output

```bash
# Check generated config
cat ../evm-balance-checker/rindexer.yaml

# List all ABIs
ls -la ../evm-balance-checker/abis/
```

---

## Advanced Configuration

### Using Custom RPC URLs

Edit `generate_rindexer.py`:

```python
CHAINS = {
    'ethereum': {
        'chain_id': 1,
        'rpc': 'https://your-custom-ethereum-rpc.com',
        'explorer_api': 'https://api.etherscan.io/api',
        'api_key': os.getenv('ETHERSCAN_API_KEY')
    }
}
```

### Using Environment Variables

Create `.env` file:

```bash
# Blockchain Explorer API Keys
ETHERSCAN_API_KEY=your_key_here
ARBISCAN_API_KEY=your_key_here
POLYGONSCAN_API_KEY=your_key_here

# Custom RPC URLs
ETH_RPC_URL=https://your-rpc.com
ARB_RPC_URL=https://your-arb-rpc.com
```

Load in script:

```python
from dotenv import load_dotenv
load_dotenv()

CHAINS = {
    'ethereum': {
        'rpc': os.getenv('ETH_RPC_URL', 'https://eth.llamarpc.com'),
        # ...
    }
}
```

### Filtering Protocols

Edit `generate_rindexer.py` to include only specific protocols:

```python
# Only generate for these protocols
PROTOCOLS_TO_INCLUDE = ['aave-v3', 'uniswap-v3', 'curve']

# In generate_rindexer_yaml():
for protocol_key, protocol_data in DEFI_PROTOCOLS.items():
    if protocol_key not in PROTOCOLS_TO_INCLUDE:
        continue
    # ... rest of logic
```

### Filtering Chains

```python
# Only generate for these chains
CHAINS_TO_INCLUDE = ['ethereum', 'arbitrum']

for chain, contracts in contracts_by_chain.items():
    if chain not in CHAINS_TO_INCLUDE:
        continue
    # ... rest of logic
```

---

## Custom Protocols

### Adding a New Protocol

1. **Define Protocol Configuration**

```python
DEFI_PROTOCOLS = {
    'my-protocol': {
        'name': 'My DeFi Protocol',
        'category': 'lending',  # or 'dex', 'staking', 'vault', etc.
        'events': ['Deposit', 'Withdraw', 'Borrow', 'Repay'],
        'subgraphs': {
            'ethereum': 'subgraph-id-here',
            'arbitrum': 'subgraph-id-here'
        }
    }
}
```

2. **Add Contract Addresses**

In `get_protocol_contracts()`:

```python
known_addresses = {
    'my-protocol': {
        'ethereum': ['0x1234...'],
        'arbitrum': ['0x5678...']
    }
}
```

3. **Run Generator**

```bash
python generate_rindexer.py
```

### Adding Custom Events

If your protocol uses unique events:

```python
# In generate_minimal_abi()
event_signatures = {
    'MyCustomEvent': 'event MyCustomEvent(address indexed user, uint256 amount)',
    # ... other events
}
```

---

## API Keys Setup

### Etherscan (Ethereum)

1. Go to https://etherscan.io/apis
2. Sign up for free account
3. Create API key
4. Add to `.env`:

```bash
ETHERSCAN_API_KEY=YourApiKeyHere
```

**Rate Limits:**
- Free: 5 calls/second
- Paid: Unlimited

### Other Chains

Same process for:
- **Arbiscan** (Arbitrum): https://arbiscan.io/apis
- **Polygonscan** (Polygon): https://polygonscan.com/apis
- **Snowtrace** (Avalanche): https://snowtrace.io/apis
- **Optimistic Etherscan** (Optimism): https://optimistic.etherscan.io/apis
- **Basescan** (Base): https://basescan.org/apis

**Pro Tip:** Most explorers accept the same API key across chains.

---

## Troubleshooting

### "ABI not found" Error

**Problem:** Explorer API can't find contract ABI

**Solutions:**

1. **Check if contract is verified:**
   ```bash
   # Visit explorer and search for contract address
   # Look for "Contract" tab with green checkmark
   ```

2. **Use fallback ABI:**
   ```python
   # Generator automatically creates minimal ABI
   # Check: ./abis/{protocol}_{chain}.json
   ```

3. **Manually add ABI:**
   ```bash
   # Download ABI from explorer
   # Save to: ./abis/my-protocol_ethereum.json
   ```

### Rate Limiting

**Problem:** "Max rate limit reached"

**Solutions:**

1. **Add API key:**
   ```bash
   export ETHERSCAN_API_KEY=your_key_here
   ```

2. **Increase delays:**
   ```python
   # In generate_rindexer.py
   time.sleep(0.5)  # Increase from 0.2 to 0.5
   ```

3. **Use paid API tier:**
   - Unlimited requests
   - Faster generation

### Missing Events in ABI

**Problem:** Required events not in fetched ABI

**Solutions:**

1. **Check event names:**
   ```python
   # Verify exact event name in protocol docs
   events = ['Supply', 'Withdraw']  # Case-sensitive!
   ```

2. **Use correct contract:**
   ```python
   # Some protocols have multiple contracts
   # Use the one that emits the events you need
   ```

3. **Add events manually:**
   ```python
   # In generate_minimal_abi()
   event_signatures['MyEvent'] = 'event MyEvent(...)'
   ```

### YAML Syntax Errors

**Problem:** Generated YAML has syntax errors

**Solutions:**

1. **Validate YAML:**
   ```bash
   python -c "import yaml; yaml.safe_load(open('rindexer.yaml'))"
   ```

2. **Check quotes:**
   ```yaml
   # Addresses must be quoted
   address: '0x1234...'  # ✅ Good
   address: 0x1234...    # ❌ Bad
   ```

3. **Check indentation:**
   ```yaml
   # Use 2 spaces, not tabs
   networks:
     ethereum:  # 2 spaces
       chain_id: 1  # 4 spaces
   ```

---

## Production Deployment

### 1. Optimize Configuration

**Use Paid RPCs:**
```python
CHAINS = {
    'ethereum': {
        'rpc': 'https://your-paid-rpc.com',  # Faster, more reliable
    }
}
```

**Set Start Blocks:**
```yaml
networks:
  ethereum:
    contracts:
      - name: Aave V3
        start_block: 16291127  # Aave V3 deployment block
```

**Adjust Batch Sizes:**
```yaml
networks:
  ethereum:
    batch_size: 10000  # Larger for faster chains
  arbitrum:
    batch_size: 50000  # Arbitrum is fast!
```

### 2. Monitor Indexing

```bash
# Start indexing
cd ../evm-balance-checker
rindexer start

# Monitor logs
tail -f logs/rindexer.log

# Check progress
rindexer status
```

### 3. Database Optimization

**PostgreSQL Configuration:**
```yaml
storage:
  postgres:
    enabled: true
    host: localhost
    port: 5432
    database: defi_indexer
    max_connections: 20
```

**Indexes:**
```sql
-- Add indexes for common queries
CREATE INDEX idx_user_address ON events(user_address);
CREATE INDEX idx_block_number ON events(block_number);
CREATE INDEX idx_protocol ON events(protocol);
```

### 4. Error Handling

**Retry Logic:**
```python
# In your indexer
max_retries = 3
retry_delay = 5  # seconds

for attempt in range(max_retries):
    try:
        # Fetch data
        break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
        else:
            raise
```

**Alerting:**
```python
# Send alerts on failures
import requests

def send_alert(message):
    requests.post('https://your-webhook.com', json={
        'text': f'🚨 Indexer Alert: {message}'
    })
```

### 5. Scaling

**Horizontal Scaling:**
```yaml
# Split by chain
indexer-1:  # Ethereum only
  networks: [ethereum]

indexer-2:  # L2s
  networks: [arbitrum, polygon, optimism]
```

**Vertical Scaling:**
```yaml
# Increase resources
resources:
  cpu: 4
  memory: 8GB
  disk: 500GB SSD
```

---

## Best Practices

### 1. Version Control

```bash
# Track generated configs
git add rindexer.yaml
git add abis/
git commit -m "Update indexer config"
```

### 2. Testing

```bash
# Test before production
python test_generator.py

# Validate YAML
rindexer validate rindexer.yaml
```

### 3. Documentation

```yaml
# Add comments to generated YAML
networks:
  ethereum:
    # Mainnet configuration
    # Updated: 2024-01-15
    chain_id: 1
```

### 4. Backups

```bash
# Backup database regularly
pg_dump defi_indexer > backup_$(date +%Y%m%d).sql

# Backup ABIs
tar -czf abis_backup.tar.gz abis/
```

### 5. Monitoring

- **Track indexing progress:** Block height, events indexed
- **Monitor performance:** Indexing speed, query latency
- **Alert on errors:** Failed RPC calls, missing events
- **Resource usage:** CPU, memory, disk space

---

## Examples

### Example 1: Ethereum Only

```python
# generate_ethereum_only.py
CHAINS_TO_INCLUDE = ['ethereum']
PROTOCOLS_TO_INCLUDE = ['aave-v3', 'uniswap-v3', 'lido']

# Run
python generate_ethereum_only.py
```

### Example 2: L2s Only

```python
# generate_l2s_only.py
CHAINS_TO_INCLUDE = ['arbitrum', 'polygon', 'optimism', 'base']
PROTOCOLS_TO_INCLUDE = ['aave-v3', 'uniswap-v3', 'gmx']

# Run
python generate_l2s_only.py
```

### Example 3: Lending Protocols Only

```python
# generate_lending_only.py
PROTOCOLS_TO_INCLUDE = [
    k for k, v in DEFI_PROTOCOLS.items() 
    if v['category'] == 'lending'
]

# Run
python generate_lending_only.py
```

---

## Next Steps

1. ✅ **Generate config:** `python generate_rindexer.py`
2. ✅ **Review output:** Check `rindexer.yaml` and `abis/`
3. ✅ **Test locally:** `rindexer start --dev`
4. ✅ **Deploy to production:** `rindexer start`
5. ✅ **Monitor:** Check logs and metrics
6. ✅ **Iterate:** Add more protocols as needed

---

**Need help?** Check:
- [README.md](README.md) - Overview and features
- [QUICKSTART.md](QUICKSTART.md) - Get started in 3 minutes
- [test_generator.py](test_generator.py) - Test suite examples

