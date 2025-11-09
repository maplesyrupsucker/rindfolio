# 🚀 Rindfolio - Quick Reference Card

## 📦 Two Main Components

### 1. Multi-Chain Portfolio Tracker (Real-Time)
**Purpose**: Check balances and DeFi positions in real-time  
**Tech**: Flask + Web3.py + JavaScript  
**Port**: http://localhost:5001

```bash
# Start the tracker
./start.sh

# Or manually
source venv/bin/activate
python app.py
```

### 2. DeFi Indexer Generator (Historical)
**Purpose**: Auto-generate blockchain indexing configuration  
**Tech**: Python + YAML + Etherscan APIs  
**Output**: `rindexer.yaml` + cached ABIs

```bash
# Generate indexer config
./generate_indexer.sh

# Or manually
python3 defi_indexer_generator.py
```

---

## ⚡ Quick Commands

### Portfolio Tracker
```bash
# Start server
./start.sh

# Stop server
pkill -f "python app.py"

# View logs
tail -f nohup.out

# Check if running
ps aux | grep "python app.py"
```

### Indexer Generator
```bash
# Generate config
./generate_indexer.sh

# View generated config
cat rindexer.yaml

# View cached ABIs
ls -la abis/

# Clean cache
rm -rf abis/
```

### Both Components
```bash
# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip install --upgrade -r requirements.txt

# Check Python version
python3 --version
```

---

## 🌐 Supported Chains

| Chain | Chain ID | RPC |
|-------|----------|-----|
| Ethereum | 1 | eth.llamarpc.com |
| Arbitrum | 42161 | arb1.arbitrum.io/rpc |
| Polygon | 137 | polygon-rpc.com |
| Optimism | 10 | mainnet.optimism.io |
| Avalanche | 43114 | api.avax.network |
| BNB Chain | 56 | bsc-dataseed1.binance.org |

---

## 🎯 Supported DeFi Protocols

### Lending (2)
- **Aave V3** - 5 chains, 25+ tokens
- **Compound V3** - 3 chains

### DEX (4)
- **Uniswap V3** - 5 chains
- **Curve** - 5 chains
- **Balancer V2** - 3 chains
- **SushiSwap** - 5 chains

### Staking (1)
- **Lido** - Ethereum

### Vaults (1)
- **Yearn** - 3 chains

### Farming (1)
- **Convex** - Ethereum

### Perpetuals (1)
- **GMX** - Arbitrum, Avalanche

**Total**: 10 protocols, 28+ contracts

---

## 📁 File Structure

```
evm-balance-checker/
├── 🎨 FRONTEND
│   └── templates/index.html        # Web UI
│
├── 🔧 BACKEND
│   ├── app.py                      # Flask server
│   └── defi_indexer_generator.py   # Indexer generator
│
├── 📜 SCRIPTS
│   ├── start.sh                    # Start portfolio tracker
│   └── generate_indexer.sh         # Generate indexer config
│
├── 📚 DOCUMENTATION
│   ├── README.md                   # Main docs
│   ├── INDEXER_GENERATOR_README.md # Indexer docs
│   ├── USAGE_GUIDE.md              # Usage guide
│   ├── PROJECT_OVERVIEW.md         # Architecture
│   ├── QUICK_REFERENCE.md          # This file
│   └── env.example                 # Config template
│
├── 🗂️ DATA
│   ├── abis/                       # Cached ABIs
│   └── rindexer.yaml               # Generated config
│
└── ⚙️ CONFIG
    ├── requirements.txt            # Python deps
    ├── docker-compose.yml          # Docker setup
    └── .gitignore                  # Git ignore
```

---

## 🔑 Environment Variables

### Optional (Recommended)
```bash
# Blockchain Explorer API Keys
export ETHERSCAN_API_KEY="your_key"
export ARBISCAN_API_KEY="your_key"
export POLYGONSCAN_API_KEY="your_key"

# Custom RPC Endpoints
export ETH_RPC_URL="https://eth-mainnet.g.alchemy.com/v2/KEY"
export ARB_RPC_URL="https://arb-mainnet.g.alchemy.com/v2/KEY"

# Cache Configuration
export CACHE_DURATION=86400  # 24 hours
```

### Load from .env file
```bash
cp env.example .env
nano .env  # Edit file
source .env  # Load variables
```

---

## 🐛 Troubleshooting

### Portfolio Tracker Issues

**Port 5001 already in use**
```bash
# Find process
lsof -i :5001

# Kill process
kill -9 <PID>

# Or change port in app.py
app.run(port=5002)
```

**No balances showing**
```bash
# Check RPC connectivity
curl https://eth.llamarpc.com

# Check console logs (browser F12)
# Check server logs
tail -f nohup.out
```

**ENS not resolving**
```bash
# Check Ethereum RPC
# ENS only works on Ethereum mainnet
```

### Indexer Generator Issues

**Rate limit errors**
```bash
# Add API key
export ETHERSCAN_API_KEY="your_key"

# Or wait 1 minute
sleep 60 && ./generate_indexer.sh
```

**No events found**
```bash
# Check if contract is verified
curl "https://api.etherscan.io/api?module=contract&action=getabi&address=0xADDRESS"

# Manually add ABI to abis/ folder
```

**Connection timeout**
```bash
# Check internet
ping api.etherscan.io

# Try VPN if geo-restricted
```

---

## 📊 API Endpoints (Portfolio Tracker)

### Main UI
```
GET /
Returns: HTML page
```

### Check All Chains
```
GET /api/check/<address>
Returns: JSON with balances from all chains
Example: /api/check/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

### Check Single Chain
```
GET /api/check-chain/<address>/<chain>
Returns: JSON with balances from specific chain
Example: /api/check-chain/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb/ethereum
```

### Resolve ENS
```
GET /api/resolve-ens/<name>
Returns: JSON with Ethereum address
Example: /api/resolve-ens/vitalik.eth
```

---

## 🎨 UI Features

### Portfolio Tracker
- ✅ Real-time balance updates
- ✅ ENS domain support
- ✅ Light/Dark mode toggle
- ✅ Interactive pie charts
- ✅ Chain filtering
- ✅ Loading indicators
- ✅ Local storage caching
- ✅ Saved address history
- ✅ Token icons (Trust Wallet)
- ✅ Chain icons (emojis)
- ✅ Thousands separators
- ✅ JetBrains Mono font for numbers

### Chart Toggles
- 📊 Portfolio by Token
- 🌐 Portfolio by Chain
- 🏦 DeFi by Protocol

---

## 🚀 Performance

### Portfolio Tracker
- Initial load: 2-5 seconds (parallel)
- Cached load: <500ms
- ENS resolution: ~1 second
- Price updates: ~500ms

### Indexer Generator
- First run: 30-60 seconds
- Cached run: 2-5 seconds
- Protocols: 10
- Contracts: ~28

---

## 📚 Documentation Index

| Document | Purpose | Audience |
|----------|---------|----------|
| **README.md** | Main project docs | Everyone |
| **QUICK_REFERENCE.md** | Quick commands | Developers |
| **QUICKSTART.md** | 5-min setup | New users |
| **USAGE_GUIDE.md** | Detailed guide | Power users |
| **INDEXER_GENERATOR_README.md** | Indexer docs | Indexer users |
| **PROJECT_OVERVIEW.md** | Architecture | Architects |
| **FEATURES.md** | Feature list | Product managers |
| **DEMO.md** | Walkthrough | Demos |
| **RUNNING.md** | Server ops | DevOps |

---

## 🔗 Useful Links

### Documentation
- [Rindexer](https://github.com/joshstevens19/rindexer)
- [The Graph](https://thegraph.com/explorer)
- [Web3.py](https://web3py.readthedocs.io/)
- [Flask](https://flask.palletsprojects.com/)

### APIs
- [Etherscan API](https://docs.etherscan.io/)
- [CoinGecko API](https://www.coingecko.com/en/api)
- [Trust Wallet Assets](https://github.com/trustwallet/assets)

### Tools
- [ABI Decoder](https://abi.hashex.org/)
- [4byte Directory](https://www.4byte.directory/)
- [Ethereum Unit Converter](https://eth-converter.com/)

---

## 💡 Pro Tips

### Speed Up Development
```bash
# Use cached ABIs (commit to git)
git add abis/
git commit -m "Cache ABIs"

# Use local RPC nodes (faster)
export ETH_RPC_URL="http://localhost:8545"

# Increase cache duration
export CACHE_DURATION=604800  # 7 days
```

### Production Deployment
```bash
# Use managed RPC (Alchemy, Infura)
# Use managed PostgreSQL (RDS, Cloud SQL)
# Set up monitoring (Prometheus, Datadog)
# Enable SSL/TLS
# Use secrets manager for API keys
```

### Debugging
```bash
# Enable debug mode (Flask)
export FLASK_DEBUG=1

# Verbose logging
export LOG_LEVEL=DEBUG

# Check browser console (F12)
# Check server logs (tail -f nohup.out)
```

---

## 🎯 Common Tasks

### Add New Protocol
1. Edit `defi_indexer_generator.py`
2. Add to `DEFI_PROTOCOLS` dict
3. Run `./generate_indexer.sh`
4. Review `rindexer.yaml`

### Add New Chain
1. Edit `defi_indexer_generator.py`
2. Add to `CHAINS` dict
3. Add protocol contracts for that chain
4. Run `./generate_indexer.sh`

### Update Token List
1. Edit `app.py`
2. Add to `TOKENS_BY_CHAIN` dict
3. Restart server: `pkill -f "python app.py" && ./start.sh`

### Clear Cache
```bash
# Clear ABI cache
rm -rf abis/

# Clear browser cache
# Open DevTools (F12) → Application → Local Storage → Clear

# Clear both
rm -rf abis/ && echo "localStorage.clear()" | pbcopy
# Then paste in browser console
```

---

## 📞 Getting Help

### Check Documentation
1. Read relevant docs (see index above)
2. Check troubleshooting sections
3. Review examples

### Debug Yourself
1. Check console logs (browser F12)
2. Check server logs (`tail -f nohup.out`)
3. Test API endpoints (`curl http://localhost:5001/api/check/ADDRESS`)

### Ask for Help
1. Search existing issues
2. Create new issue with:
   - Description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Logs/screenshots

---

## ✅ Checklist

### First-Time Setup
- [ ] Clone repository
- [ ] Install Python 3.8+
- [ ] Run `pip install -r requirements.txt`
- [ ] (Optional) Set API keys in `.env`
- [ ] Test portfolio tracker: `./start.sh`
- [ ] Test indexer generator: `./generate_indexer.sh`

### Before Production
- [ ] Set all API keys
- [ ] Use managed RPC endpoints
- [ ] Set up PostgreSQL
- [ ] Configure monitoring
- [ ] Enable SSL/TLS
- [ ] Set up backups
- [ ] Test thoroughly
- [ ] Document deployment

---

**🚀 Happy Building!**

For more details, see the full documentation in the respective README files.

