# 🚀 DeFi Indexer Generator

**Auto-generate production-ready `rindexer.yaml` configurations from The Graph subgraphs**

A complete, bloat-free system that automatically discovers DeFi protocols, downloads their ABIs, and generates minimal indexing configurations for tracking user positions across 5+ EVM chains.

---

## ✨ Features

### 🎯 Core Capabilities
- **Auto-Discovery**: Leverages The Graph subgraphs to identify top DeFi protocols
- **Smart ABI Management**: Downloads and caches ABIs from block explorers (Etherscan, Arbiscan, etc.)
- **Minimal Configuration**: Generates lean `rindexer.yaml` with only critical events
- **Multi-Chain Support**: Ethereum, Arbitrum, Polygon, Avalanche, BNB Chain
- **Production-Ready**: Caching, rate limiting, error handling, and comprehensive logging

### 📊 Supported DeFi Categories
- **Lending**: Aave V3, Compound V3
- **DEX**: Uniswap V3, Curve, Balancer V2, SushiSwap
- **Staking**: Lido
- **Vaults**: Yearn Finance
- **Yield Aggregators**: Convex Finance
- **Perpetuals**: GMX

### 🔍 Critical Events Tracked
- **Lending**: Supply, Borrow, Withdraw, Repay, LiquidationCall
- **DEX**: Mint, Burn, Swap, AddLiquidity, RemoveLiquidity
- **Staking**: Stake, Unstake, Deposit, Withdraw
- **Vaults**: Deposit, Withdraw, Transfer

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd defi-indexer-generator
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file:
```bash
cp .env.example .env
```

Get **free** API keys from:
- [Etherscan](https://etherscan.io/apis) → `ETHERSCAN_API_KEY`
- [Arbiscan](https://arbiscan.io/apis) → `ARBISCAN_API_KEY`
- [Polygonscan](https://polygonscan.com/apis) → `POLYGONSCAN_API_KEY`
- [Snowtrace](https://snowtrace.io/apis) → `SNOWTRACE_API_KEY`
- [BscScan](https://bscscan.com/apis) → `BSCSCAN_API_KEY`

Edit `.env` with your keys:
```bash
ETHERSCAN_API_KEY=ABC123...
ARBISCAN_API_KEY=DEF456...
# ... etc
```

### 3. Generate Configuration

```bash
python generate_rindexer.py
```

This will:
1. ✅ Download ABIs for all configured protocols
2. ✅ Extract critical events from each ABI
3. ✅ Generate minimal ABIs (only required events)
4. ✅ Create `rindexer.yaml` with complete configuration
5. ✅ Cache everything in `./abis/` for reuse

### 4. Use with Rindexer

```bash
# Copy generated config to your rindexer project
cp rindexer.yaml ../your-rindexer-project/
cp -r abis ../your-rindexer-project/

# Start indexing
cd ../your-rindexer-project
rindexer start
```

---

## 📁 Output Structure

After running the generator:

```
defi-indexer-generator/
├── rindexer.yaml          # ← Generated indexer config
├── abis/                  # ← Cached ABIs
│   ├── aave-v3_ethereum.json
│   ├── uniswap-v3_arbitrum.json
│   ├── curve_ethereum.json
│   └── ... (minimal, event-only ABIs)
├── generate_rindexer.py   # Main script
├── requirements.txt
├── .env                   # Your API keys
└── README.md
```

---

## 🎛️ Configuration

### Adding New Protocols

Edit `DEFI_PROTOCOLS` in `generate_rindexer.py`:

```python
DEFI_PROTOCOLS = {
    'your-protocol': {
        'name': 'Your Protocol Name',
        'category': 'lending',  # lending, dex, staking, vault, yield, perp
        'subgraph_ids': {
            'ethereum': 'Qm...',  # Optional: for documentation
        },
        'critical_events': ['Deposit', 'Withdraw'],  # Events to track
        'contracts': {
            'ethereum': ['0x...'],  # Contract addresses
            'arbitrum': ['0x...'],
        }
    }
}
```

### Customizing Chains

Edit `CHAINS` in `generate_rindexer.py`:

```python
CHAINS = {
    'your-chain': {
        'chain_id': 1234,
        'rpc': 'https://your-rpc-url.com',
        'explorer_api': 'https://api.yourscan.io/api',
        'api_key': YOUR_API_KEY,
        'graph_network': 'your-network'
    }
}
```

---

## 🔧 Advanced Usage

### Cache Management

ABIs are cached in `./abis/` to avoid redundant API calls:
- **Cached files**: `{chain}_{address}.json` (full ABI)
- **Minimal files**: `{protocol}_{chain}.json` (events only)

To refresh cache:
```bash
rm -rf abis/
python generate_rindexer.py
```

### Rate Limiting

The script includes automatic rate limiting:
- 0.2s delay between API calls
- Respects free tier limits (5 calls/sec)

For higher throughput, upgrade to paid API keys.

### Custom Event Selection

To track additional events, modify `critical_events` in protocol config:

```python
'critical_events': [
    'Supply', 'Borrow',      # Core events
    'FlashLoan', 'Swap'      # Additional events
]
```

---

## 📊 Sample Output

### Generated `rindexer.yaml`

```yaml
name: defi_positions_indexer
description: Auto-generated DeFi positions indexer from The Graph subgraphs
project_type: no-code

networks:
  ethereum:
    chain_id: 1
    rpc: https://eth.llamarpc.com
  arbitrum:
    chain_id: 42161
    rpc: https://arb1.arbitrum.io/rpc

contracts:
  - name: aave-v3_ethereum
    network: ethereum
    address: '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'
    abi: ./abis/aave-v3_ethereum.json
    events:
      - Supply
      - Borrow
      - Withdraw
      - Repay
      - LiquidationCall
    metadata:
      protocol: Aave V3
      category: lending
```

### Console Output

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     🚀 DeFi Indexer Generator - Production System 🚀          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

============================================================
Processing: Aave V3 (lending)
============================================================

  Chain: ethereum
  ⟳ Fetching ABI for 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2...
  ✓ Downloaded and cached ABI
  ✓ Created minimal ABI with 5 events

============================================================
✓ GENERATION COMPLETE
============================================================

Output: rindexer.yaml
Chains: 5
Contracts: 23

Breakdown by chain:
  ethereum: 8 contracts
  arbitrum: 6 contracts
  polygon: 5 contracts
  avalanche: 2 contracts
  bsc: 2 contracts

Breakdown by category:
  lending: 6 contracts
  dex: 10 contracts
  staking: 1 contract
  vault: 2 contracts
  yield: 2 contracts
  perp: 2 contracts
```

---

## 🎯 Use Cases

### 1. Portfolio Tracking
Index all user DeFi positions across chains for a unified dashboard.

### 2. Risk Monitoring
Track liquidation events and health factors for lending protocols.

### 3. Yield Optimization
Monitor APYs and positions across vaults and farms.

### 4. Analytics Platform
Build comprehensive DeFi analytics with historical position data.

---

## 🛠️ Troubleshooting

### "Failed to fetch ABI"
- **Cause**: Invalid API key or rate limit exceeded
- **Fix**: Check your `.env` file and wait 1 minute before retrying

### "No matching events found"
- **Cause**: Contract ABI doesn't contain specified events
- **Fix**: Verify contract address and event names in `DEFI_PROTOCOLS`

### "Unknown chain"
- **Cause**: Chain not configured in `CHAINS`
- **Fix**: Add chain configuration or remove from protocol config

---

## 📈 Roadmap

### Phase 1 (Current)
- ✅ Manual protocol configuration
- ✅ ABI auto-download and caching
- ✅ Minimal YAML generation
- ✅ Multi-chain support

### Phase 2 (Planned)
- 🔄 Auto-discovery via The Graph Network subgraph
- 🔄 Dynamic protocol detection by TVL
- 🔄 Event signature inference from subgraph schemas
- 🔄 Automatic start block detection

### Phase 3 (Future)
- 📋 Web UI for protocol selection
- 📋 Real-time subgraph monitoring
- 📋 Custom event filtering rules
- 📋 Integration with DeFi Llama API

---

## 🤝 Contributing

Want to add more protocols? Submit a PR with:
1. Protocol config in `DEFI_PROTOCOLS`
2. Contract addresses for supported chains
3. Critical events list

---

## 📄 License

MIT License - feel free to use in your projects!

---

## 🔗 Resources

- [Rindexer Docs](https://github.com/joshstevens19/rindexer)
- [The Graph](https://thegraph.com/explorer)
- [Etherscan API](https://docs.etherscan.io/)
- [DeFi Llama](https://defillama.com/)

---

**Built with ❤️ for the DeFi community**
