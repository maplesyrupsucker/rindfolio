# ⚡ Quick Reference Card

## 🚀 Quick Start

```bash
# 1. Try the demo (no API keys)
python3 demo_simple.py

# 2. Generate with real ABIs
export ETHERSCAN_API_KEY=your_key_here
python3 generate_rindexer.py

# 3. Review output
cat demo_rindexer.yaml
ls abis/
```

## 📦 What It Does

**Input:** Protocol definitions + Chain configs  
**Process:** Fetch ABIs → Extract events → Generate YAML  
**Output:** `rindexer.yaml` + `abis/` directory

## 🌐 Supported Chains

| Chain | Chain ID | RPC |
|-------|----------|-----|
| Ethereum | 1 | eth.llamarpc.com |
| Arbitrum | 42161 | arb1.arbitrum.io |
| Polygon | 137 | polygon-rpc.com |
| Optimism | 10 | mainnet.optimism.io |
| Avalanche | 43114 | api.avax.network |
| Base | 8453 | mainnet.base.org |

## 📊 Protocols

### Lending
- Aave V3 (6 chains)
- Compound V3 (3 chains)

### DEX
- Uniswap V3 (5 chains)
- Curve (4 chains)
- Balancer V2 (3 chains)

### Staking
- Lido (Ethereum)
- Rocket Pool (Ethereum)

### Vaults
- Yearn (2 chains)
- Convex (Ethereum)

### Perps
- GMX (Arbitrum, Avalanche)

## 🔧 Common Tasks

### Add a Protocol

```python
# In generate_rindexer.py
DEFI_PROTOCOLS['my-protocol'] = {
    'name': 'My Protocol',
    'category': 'lending',
    'events': ['Deposit', 'Withdraw'],
    'contracts': {
        'ethereum': '0x...'
    }
}
```

### Add a Chain

```python
# In generate_rindexer.py
CHAINS['new-chain'] = {
    'chain_id': 12345,
    'rpc': 'https://rpc.new-chain.com',
    'explorer_api': 'https://api.explorer.com/api',
    'api_key': os.getenv('EXPLORER_API_KEY')
}
```

### Filter Protocols

```python
# Only generate for specific protocols
PROTOCOLS_TO_INCLUDE = ['aave-v3', 'uniswap-v3']

for protocol_key, protocol_data in DEFI_PROTOCOLS.items():
    if protocol_key not in PROTOCOLS_TO_INCLUDE:
        continue
    # ... rest of logic
```

### Filter Chains

```python
# Only generate for specific chains
CHAINS_TO_INCLUDE = ['ethereum', 'arbitrum']

for chain, contracts in contracts_by_chain.items():
    if chain not in CHAINS_TO_INCLUDE:
        continue
    # ... rest of logic
```

## 🔑 API Keys

### Get Free API Keys

1. **Etherscan**: https://etherscan.io/apis
2. **Arbiscan**: https://arbiscan.io/apis
3. **Polygonscan**: https://polygonscan.com/apis
4. **Snowtrace**: https://snowtrace.io/apis

### Set API Keys

```bash
# Option 1: Environment variables
export ETHERSCAN_API_KEY=your_key_here

# Option 2: .env file
echo "ETHERSCAN_API_KEY=your_key_here" > .env
```

### Rate Limits

- **Free**: 5 calls/second
- **Paid**: Unlimited
- **Script delay**: 200ms between calls

## 📁 Output Files

```
evm-balance-checker/
├── rindexer.yaml              # Main config (or demo_rindexer.yaml)
└── abis/
    ├── erc20.json             # Standard ERC20
    ├── aave-v3_ethereum.json  # Aave V3 on Ethereum
    ├── uniswap-v3_ethereum.json
    └── ...                    # More ABIs
```

## 🎯 Key Events

### Lending
- `Supply`, `Withdraw`, `Borrow`, `Repay`, `LiquidationCall`

### DEX
- `Mint`, `Burn`, `Swap`, `AddLiquidity`, `RemoveLiquidity`

### Staking
- `Stake`, `Unstake`, `Submitted`, `Withdrawal`

### Vaults
- `Deposit`, `Withdraw`, `RewardPaid`

## 🐛 Troubleshooting

### "ABI not found"
```bash
# Add API key
export ETHERSCAN_API_KEY=your_key_here

# Or script will generate minimal ABI automatically
```

### "Rate limited"
```bash
# Add API key for unlimited requests
export ETHERSCAN_API_KEY=your_key_here

# Or increase delay in script
time.sleep(0.5)  # Change from 0.2 to 0.5
```

### "YAML syntax error"
```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('rindexer.yaml'))"

# Check quotes on addresses
address: '0x...'  # ✅ Good
address: 0x...    # ❌ Bad
```

## 📊 Statistics

**Typical Generation:**
- ⏱️ Time: 30-60 seconds (with API calls)
- 📦 Contracts: 25+ across all chains
- 🎯 Events: 87+ position-tracking events
- 📁 Files: 1 YAML + 25+ ABI JSON files

## 🔗 Resources

- **Main README**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Full Guide**: [USAGE.md](USAGE.md)
- **Technical**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

## 💡 Pro Tips

1. **Cache ABIs**: Run once, ABIs are cached locally
2. **Start Small**: Test with 1-2 protocols first
3. **Use Demo**: Try `demo_simple.py` before full generation
4. **Check Output**: Always review generated YAML
5. **API Keys**: Free tier is usually sufficient

## 🎯 Next Steps

1. ✅ Run demo: `python3 demo_simple.py`
2. ✅ Add API key: `export ETHERSCAN_API_KEY=...`
3. ✅ Generate: `python3 generate_rindexer.py`
4. ✅ Review: `cat rindexer.yaml`
5. ✅ Use: `rindexer start`

---

**Need more help?** See full documentation in [README.md](README.md)

