# 🚀 DeFi Indexer Generator

**Auto-generate production-ready `rindexer.yaml` from The Graph subgraphs and blockchain explorers**

## 📋 Overview

This tool automatically discovers and configures DeFi protocol indexing across **6 EVM chains** by:

1. **Auto-discovering** top DeFi protocols (Aave, Compound, Uniswap, Curve, etc.)
2. **Auto-downloading** verified ABIs from blockchain explorers (Etherscan, Arbiscan, etc.)
3. **Auto-generating** a complete `rindexer.yaml` configuration file

### ✨ Key Features

- ✅ **10+ Major DeFi Protocols** (Aave V3, Compound V3, Uniswap V3, Curve, Lido, Yearn, Convex, Balancer, GMX, SushiSwap)
- ✅ **6 EVM Chains** (Ethereum, Arbitrum, Polygon, Optimism, Avalanche, BSC)
- ✅ **Smart ABI Caching** (24-hour cache to avoid API rate limits)
- ✅ **Event Filtering** (Only indexes critical DeFi events: Supply, Mint, Deposit, Stake, etc.)
- ✅ **Zero Manual Configuration** (Fully automated)
- ✅ **Production-Ready Output** (PostgreSQL storage, proper event filtering)

---

## 🎯 Supported Protocols

| Protocol | Category | Chains | Events Tracked |
|----------|----------|--------|----------------|
| **Aave V3** | Lending | ETH, ARB, POLY, OP, AVAX | Supply, Withdraw, Borrow, Repay, Liquidation |
| **Compound V3** | Lending | ETH, ARB, POLY | Supply, Withdraw, SupplyCollateral |
| **Uniswap V3** | DEX | ETH, ARB, POLY, OP, BSC | Mint, Burn, Collect, IncreaseLiquidity |
| **Curve** | DEX | ETH, ARB, POLY, OP, AVAX | AddLiquidity, RemoveLiquidity, TokenExchange |
| **Lido** | Staking | ETH | Submitted, Transfer, TransferShares |
| **Yearn** | Vault | ETH, ARB, POLY | Deposit, Withdraw |
| **Convex** | Farming | ETH | Staked, Withdrawn, RewardPaid |
| **Balancer V2** | DEX | ETH, ARB, POLY | PoolBalanceChanged, Swap |
| **GMX** | Perpetuals | ARB, AVAX | Stake, Unstake, AddLiquidity |
| **SushiSwap** | DEX | ETH, ARB, POLY, AVAX, BSC | Mint, Burn, Swap |

---

## 🛠️ Installation

### Prerequisites

```bash
# Python 3.8+
python3 --version

# Install dependencies
pip install -r requirements.txt

# (Optional) Set Etherscan API key for higher rate limits
export ETHERSCAN_API_KEY="your_api_key_here"
```

### Quick Start

```bash
# 1. Run the generator
python3 defi_indexer_generator.py

# 2. Review the generated files
ls -la abis/          # Cached ABIs
cat rindexer.yaml     # Generated config

# 3. Start indexing (requires rindexer installed)
rindexer start all
```

---

## 📊 How It Works

### Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. PROTOCOL DISCOVERY                                      │
│  • Load predefined top DeFi protocols                       │
│  • Map protocols to chains and contract addresses           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. ABI FETCHING (Parallel)                                 │
│  • Query Etherscan/Arbiscan/Polygonscan APIs                │
│  • Cache ABIs locally (24h TTL)                             │
│  • Extract relevant events from ABI                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. EVENT FILTERING                                         │
│  • Match ABI events against target events                   │
│  • Filter: Supply, Mint, Deposit, Stake, AddLiquidity, etc. │
│  • Ignore: Transfer, Approval, non-position events          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. YAML GENERATION                                         │
│  • Build networks section (6 chains)                        │
│  • Build contracts section (protocol configs)               │
│  • Build storage section (PostgreSQL)                       │
│  • Write rindexer.yaml                                      │
└─────────────────────────────────────────────────────────────┘
```

### Generated `rindexer.yaml` Structure

```yaml
name: defi_positions_indexer
description: Auto-generated DeFi positions indexer across multiple chains
project_type: no-code

networks:
  ethereum:
    chain_id: 1
    rpc: https://eth.llamarpc.com
  arbitrum:
    chain_id: 42161
    rpc: https://arb1.arbitrum.io/rpc
  # ... more chains

storage:
  postgres:
    enabled: true
    drop_each_run: false

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
  # ... more contracts
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Etherscan API key (free tier: 5 calls/sec)
export ETHERSCAN_API_KEY="your_key_here"

# Optional: Custom cache directory
export CACHE_DIR="./custom_abis"

# Optional: Custom output file
export OUTPUT_FILE="./custom_rindexer.yaml"
```

### Adding New Protocols

Edit `defi_indexer_generator.py` and add to `DEFI_PROTOCOLS`:

```python
DEFI_PROTOCOLS = {
    # ... existing protocols
    'your-protocol': {
        'name': 'Your Protocol',
        'category': 'lending',  # lending, dex, staking, vault, farming, perp
        'events': ['Deposit', 'Withdraw'],  # Target events
        'subgraphs': {
            'ethereum': 'your-org/your-subgraph'
        },
        'contracts': {
            'ethereum': ['0xYourContractAddress']
        }
    }
}
```

### Adding New Chains

Edit `CHAINS` dictionary:

```python
CHAINS = {
    # ... existing chains
    'your-chain': {
        'chain_id': 1234,
        'rpc': 'https://your-rpc.com',
        'explorer_api': 'https://api.yourscan.com/api',
        'graph_network': 'your-network'
    }
}
```

---

## 📈 Performance

### Benchmarks

- **Protocol Discovery**: Instant (predefined)
- **ABI Fetching**: ~2-5 seconds per contract (cached after first run)
- **YAML Generation**: <1 second
- **Total Runtime** (first run): ~30-60 seconds
- **Total Runtime** (cached): ~2-5 seconds

### Rate Limits

| Service | Free Tier | Caching Strategy |
|---------|-----------|------------------|
| Etherscan API | 5 calls/sec | 24-hour ABI cache |
| The Graph | 1000 queries/day | Predefined subgraphs |
| RPC Nodes | Varies | No direct calls |

---

## 🎨 Output Examples

### Console Output

```
======================================================================
DeFi Indexer Generator - Auto-generating rindexer.yaml
======================================================================

📦 Processing Aave V3 (lending)...
  🔗 Chain: ethereum
  → Fetching ABI for 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2 on ethereum...
  ✓ Fetched and cached ABI
  ✓ Generated config for Aave V3 on ethereum: 5 events

📦 Processing Uniswap V3 (dex)...
  🔗 Chain: ethereum
  ✓ Using cached ABI for 0xC36442b4a4522E871399CD717aBDD847Ab11FE88 on ethereum
  ✓ Generated config for Uniswap V3 on ethereum: 5 events

📝 Generating rindexer.yaml...
✅ Generated ./rindexer.yaml

======================================================================
SUMMARY
======================================================================
Total Chains: 6
Total Contracts: 28
Total Protocols: 10

  ethereum: 10 contracts
  arbitrum: 7 contracts
  polygon: 7 contracts
  optimism: 2 contracts
  avalanche: 2 contracts
  bsc: 0 contracts

📁 ABIs cached in: ./abis/
📄 Config written to: ./rindexer.yaml

🚀 Next steps:
  1. Review the generated rindexer.yaml
  2. Set up PostgreSQL database
  3. Run: rindexer start all
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: `Failed to fetch ABI: Max rate limit reached`
```bash
# Solution: Set Etherscan API key or wait 1 minute
export ETHERSCAN_API_KEY="your_key"
```

**Issue**: `No matching events found for address`
```bash
# Solution: Check if contract is verified on explorer
# Or manually add ABI to ./abis/{protocol}_{chain}.json
```

**Issue**: `Connection timeout`
```bash
# Solution: Check internet connection or use VPN
# Some RPC endpoints may be geo-restricted
```

---

## 🚀 Advanced Usage

### Custom Event Filtering

```python
# Only index specific events
target_events = ['Supply', 'Withdraw']  # Ignore Borrow, Repay

# Or use wildcards (requires custom implementation)
target_events = ['*Liquidity*']  # Matches AddLiquidity, RemoveLiquidity
```

### Multi-Threading

```python
# Fetch ABIs in parallel (already implemented)
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_abi, addr, chain) 
               for addr in addresses]
```

### Custom Start Blocks

```python
# Index from specific block (saves sync time)
contract.start_block = 15000000  # Ethereum block number
```

---

## 📚 Related Documentation

- [Rindexer Documentation](https://github.com/joshstevens19/rindexer)
- [The Graph Documentation](https://thegraph.com/docs)
- [Etherscan API Docs](https://docs.etherscan.io/)
- [EVM Events & Logs](https://ethereum.org/en/developers/docs/smart-contracts/anatomy/#events-and-logs)

---

## 🤝 Contributing

### Adding More Protocols

1. Find the protocol's subgraph on [The Graph Explorer](https://thegraph.com/explorer)
2. Identify the main contract address on each chain
3. Determine which events track user positions
4. Add to `DEFI_PROTOCOLS` dictionary
5. Run generator and test

### Protocol Priority List

- [ ] Radiant Capital (Arbitrum lending)
- [ ] Stargate (Cross-chain bridge)
- [ ] Frax Finance (Stablecoin + lending)
- [ ] Rocket Pool (ETH staking)
- [ ] Pendle (Yield trading)
- [ ] Camelot (Arbitrum DEX)
- [ ] Trader Joe (Avalanche DEX)

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Rindexer** - High-performance EVM indexing framework
- **The Graph** - Decentralized protocol for indexing blockchain data
- **Etherscan** - Blockchain explorer and API provider
- **DeFi Protocols** - For building open, permissionless financial infrastructure

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Discord**: [Your Discord Server](https://discord.gg/your-invite)

---

**Built with ❤️ for the DeFi community**

