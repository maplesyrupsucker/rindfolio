# 🌐 Rindfolio - Complete DeFi Portfolio Tracker

## 📋 Project Overview

**Rindfolio** is a comprehensive, production-ready system for tracking DeFi positions across multiple EVM chains. It consists of two main components:

1. **Multi-Chain Portfolio Tracker** - Real-time web UI for viewing balances and DeFi positions
2. **DeFi Indexer Generator** - Automated tool for generating blockchain indexing configurations

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Multi-Chain Portfolio Tracker (Flask + Web3)             │  │
│  │  • Real-time balance checking                             │  │
│  │  • DeFi position tracking (Aave, Uniswap, Curve, etc.)    │  │
│  │  • ENS resolution                                          │  │
│  │  • Light/Dark mode                                         │  │
│  │  • Interactive charts                                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   DATA LAYER                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  RPC Nodes (Ethereum, Arbitrum, Polygon, etc.)            │  │
│  │  • Direct blockchain queries                              │  │
│  │  • ERC20 token balances                                   │  │
│  │  • DeFi protocol positions                                │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  CoinGecko API                                            │  │
│  │  • Real-time token prices                                 │  │
│  │  • Token metadata                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  INDEXING LAYER (Optional)                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  DeFi Indexer Generator                                   │  │
│  │  • Auto-discovers DeFi protocols                          │  │
│  │  • Fetches contract ABIs                                  │  │
│  │  • Generates rindexer.yaml                                │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Rindexer (Rust-based indexer)                           │  │
│  │  • High-speed event indexing                              │  │
│  │  • PostgreSQL storage                                     │  │
│  │  • Historical data queries                                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Component 1: Multi-Chain Portfolio Tracker

### Features

✅ **Multi-Chain Support**
- Ethereum, Arbitrum One, Polygon, Avalanche, BNB Chain
- Parallel data fetching for fast performance
- Chain-specific filtering

✅ **Comprehensive DeFi Tracking**
- **Lending**: Aave V3, Compound V3, Venus, Radiant
- **DEX**: Uniswap V3, Curve, SushiSwap, Balancer
- **Staking**: Lido, Rocket Pool
- **Vaults**: Yearn Finance
- **Farming**: Convex Finance
- **Perpetuals**: GMX

✅ **User Experience**
- ENS domain resolution
- Real-time balance updates
- Loading indicators per chain
- Local storage caching (2-hour TTL)
- Saved address history
- Light/Dark mode with theme persistence

✅ **Data Visualization**
- Interactive pie charts (Chart.js)
- Portfolio distribution by token
- Portfolio distribution by chain
- DeFi distribution by protocol
- Animated chart transitions

✅ **Modern UI/UX**
- Responsive design
- Token icons (Trust Wallet assets)
- Chain icons (emoji-based)
- JetBrains Mono font for numbers
- Thousands separators for USD values
- Hover effects and smooth animations

### Tech Stack

- **Backend**: Flask (Python 3.8+)
- **Blockchain**: Web3.py
- **Frontend**: Vanilla JavaScript + HTML5 + CSS3
- **Charts**: Chart.js 4.4.0
- **Fonts**: Inter (UI), JetBrains Mono (numbers)
- **Icons**: Trust Wallet Assets, Unicode emojis

### Quick Start

```bash
cd evm-balance-checker
chmod +x start.sh
./start.sh

# Open browser to http://localhost:5001
```

### API Endpoints

```
GET  /                              # Main UI
GET  /api/check/<address>           # Check all chains
GET  /api/check-chain/<address>/<chain>  # Check specific chain
GET  /api/resolve-ens/<name>        # Resolve ENS domain
```

---

## 🎯 Component 2: DeFi Indexer Generator

### Features

✅ **Auto-Discovery**
- Predefined top 10 DeFi protocols
- Extensible protocol registry
- Multi-chain contract mapping

✅ **ABI Management**
- Auto-fetch from Etherscan/Arbiscan/Polygonscan
- 24-hour local caching
- Automatic retry on failure

✅ **Smart Event Filtering**
- Only indexes position-relevant events
- Ignores noise (Transfer, Approval, etc.)
- Customizable event lists per protocol

✅ **Production-Ready Output**
- Valid YAML configuration
- PostgreSQL storage setup
- Network configurations for 6 chains
- Start block optimization

### Supported Protocols

| Protocol | Chains | Events |
|----------|--------|--------|
| Aave V3 | 5 | Supply, Withdraw, Borrow, Repay, Liquidation |
| Compound V3 | 3 | Supply, Withdraw, SupplyCollateral |
| Uniswap V3 | 5 | Mint, Burn, Collect, IncreaseLiquidity |
| Curve | 5 | AddLiquidity, RemoveLiquidity, TokenExchange |
| Lido | 1 | Submitted, Transfer, TransferShares |
| Yearn | 3 | Deposit, Withdraw |
| Convex | 1 | Staked, Withdrawn, RewardPaid |
| Balancer V2 | 3 | PoolBalanceChanged, Swap |
| GMX | 2 | Stake, Unstake, AddLiquidity |
| SushiSwap | 5 | Mint, Burn, Swap |

### Tech Stack

- **Language**: Python 3.8+
- **Config Format**: YAML
- **APIs**: Etherscan, Arbiscan, Polygonscan, etc.
- **Caching**: Local filesystem (24-hour TTL)
- **Concurrency**: ThreadPoolExecutor for parallel ABI fetching

### Quick Start

```bash
cd evm-balance-checker
chmod +x generate_indexer.sh
./generate_indexer.sh

# Review generated files
cat rindexer.yaml
ls -la abis/

# Start indexing
rindexer start all
```

---

## 📊 Data Flow

### Real-Time Portfolio Tracking

```
User Input (Address/ENS)
    ↓
ENS Resolution (if needed)
    ↓
Parallel Chain Queries
    ├─→ Ethereum RPC
    ├─→ Arbitrum RPC
    ├─→ Polygon RPC
    ├─→ Avalanche RPC
    └─→ BSC RPC
    ↓
For Each Chain:
    ├─→ Native Balance (ETH, MATIC, etc.)
    ├─→ ERC20 Balances (USDC, USDT, etc.)
    └─→ DeFi Positions (Aave, Uniswap, etc.)
    ↓
Price Lookup (CoinGecko)
    ↓
USD Value Calculation
    ↓
Cache in LocalStorage (2h TTL)
    ↓
Render UI (Charts, Tables, Stats)
```

### Historical Indexing

```
DeFi Indexer Generator
    ↓
Protocol Discovery
    ├─→ Aave V3
    ├─→ Uniswap V3
    ├─→ Curve
    └─→ ... (10 protocols)
    ↓
For Each Protocol:
    ├─→ Fetch ABI (Etherscan API)
    ├─→ Extract Events
    └─→ Cache Locally (24h TTL)
    ↓
Generate rindexer.yaml
    ↓
Rindexer Execution
    ├─→ Connect to RPC Nodes
    ├─→ Subscribe to Events
    ├─→ Parse Event Logs
    └─→ Store in PostgreSQL
    ↓
Historical Data Available
```

---

## 🚀 Deployment Options

### Option 1: Local Development

```bash
# Portfolio Tracker
cd evm-balance-checker
./start.sh
# Access: http://localhost:5001

# Indexer Generator
./generate_indexer.sh
# Output: rindexer.yaml + abis/
```

### Option 2: Docker

```bash
# Start all services
docker-compose up -d

# Services:
# - Portfolio Tracker: http://localhost:5001
# - PostgreSQL: localhost:5432
# - Rindexer: Background process
```

### Option 3: Production (Cloud)

```bash
# Deploy to AWS/GCP/Azure
# - Portfolio Tracker: ECS/Cloud Run/App Service
# - PostgreSQL: RDS/Cloud SQL/Azure Database
# - Rindexer: ECS/Cloud Run/Container Instances

# Example: AWS ECS
aws ecs create-service \
  --cluster rindfolio \
  --service-name portfolio-tracker \
  --task-definition portfolio-tracker:1 \
  --desired-count 2
```

---

## 📁 Project Structure

```
evm-balance-checker/
├── app.py                          # Flask backend
├── templates/
│   └── index.html                  # Web UI
├── abis/
│   ├── erc20.json                  # Standard ERC20 ABI
│   └── [generated ABIs]            # Auto-generated protocol ABIs
├── defi_indexer_generator.py       # Indexer generator
├── generate_indexer.sh             # Setup script
├── start.sh                        # Portfolio tracker start script
├── requirements.txt                # Python dependencies
├── docker-compose.yml              # Docker orchestration
├── rindexer.yaml                   # Generated indexer config
├── README.md                       # Main documentation
├── INDEXER_GENERATOR_README.md     # Indexer docs
├── USAGE_GUIDE.md                  # Detailed usage guide
├── PROJECT_OVERVIEW.md             # This file
├── FEATURES.md                     # Feature list
├── QUICKSTART.md                   # Quick start guide
├── DEMO.md                         # Demo walkthrough
├── RUNNING.md                      # Runtime instructions
└── env.example                     # Environment variables template
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Blockchain Explorer API Keys
ETHERSCAN_API_KEY=your_key_here
ARBISCAN_API_KEY=your_key_here
POLYGONSCAN_API_KEY=your_key_here

# RPC Endpoints (optional, defaults provided)
ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
ARB_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY

# Cache Configuration
CACHE_DURATION=86400  # 24 hours
ICON_CACHE_DURATION=5184000  # 60 days

# Database (for indexer)
DATABASE_URL=postgresql://user:pass@localhost:5432/rindexer
```

### Customization

**Add New Protocol**:
```python
# In defi_indexer_generator.py
DEFI_PROTOCOLS['new-protocol'] = {
    'name': 'New Protocol',
    'category': 'lending',
    'events': ['Deposit', 'Withdraw'],
    'contracts': {
        'ethereum': ['0xContractAddress']
    }
}
```

**Add New Chain**:
```python
# In defi_indexer_generator.py
CHAINS['new-chain'] = {
    'chain_id': 1234,
    'rpc': 'https://rpc.newchain.com',
    'explorer_api': 'https://api.newscan.com/api',
    'graph_network': 'new-chain'
}
```

---

## 📈 Performance

### Portfolio Tracker

- **Initial Load**: ~2-5 seconds (5 chains in parallel)
- **Cached Load**: <500ms (from localStorage)
- **ENS Resolution**: ~1 second
- **Price Updates**: ~500ms (CoinGecko API)

### Indexer Generator

- **First Run**: ~30-60 seconds (fetching ABIs)
- **Cached Run**: ~2-5 seconds (using cached ABIs)
- **Protocols Indexed**: 10
- **Contracts Indexed**: ~28 across 6 chains

### Rindexer (Historical)

- **Sync Speed**: ~1000-5000 blocks/second
- **Storage**: PostgreSQL (optimized for time-series)
- **Query Speed**: <100ms for most queries

---

## 🔐 Security

### Best Practices

✅ **API Keys**
- Never commit to git
- Use environment variables
- Rotate regularly

✅ **RPC Endpoints**
- Use authenticated endpoints in production
- Implement rate limiting
- Monitor usage

✅ **Database**
- Strong passwords
- SSL/TLS connections
- Regular backups

✅ **Frontend**
- Input validation
- XSS prevention
- CORS configuration

---

## 📚 Documentation

### User Guides

- **[README.md](README.md)** - Main project documentation
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Comprehensive usage instructions
- **[DEMO.md](DEMO.md)** - Feature walkthrough

### Technical Docs

- **[INDEXER_GENERATOR_README.md](INDEXER_GENERATOR_README.md)** - Indexer generator details
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Technical architecture
- **[FEATURES.md](FEATURES.md)** - Feature list and roadmap

### Operations

- **[RUNNING.md](RUNNING.md)** - Server management
- **[docker-compose.yml](docker-compose.yml)** - Container orchestration

---

## 🛣️ Roadmap

### Phase 1: Core Features ✅ (Completed)
- [x] Multi-chain balance checking
- [x] DeFi position tracking (10 protocols)
- [x] Real-time price data
- [x] ENS resolution
- [x] Light/Dark mode
- [x] Interactive charts
- [x] Local storage caching
- [x] Auto-indexer generator

### Phase 2: Enhanced Tracking (In Progress)
- [ ] Health factor for lending positions
- [ ] Impermanent loss calculation
- [ ] Yield tracking over time
- [ ] Transaction history
- [ ] Gas cost analysis

### Phase 3: Advanced Features (Planned)
- [ ] Portfolio analytics
- [ ] Risk assessment
- [ ] Automated rebalancing suggestions
- [ ] Multi-wallet support
- [ ] Mobile app (React Native)

### Phase 4: Enterprise (Future)
- [ ] API for third-party integrations
- [ ] White-label solution
- [ ] Advanced reporting
- [ ] Compliance tools
- [ ] Team collaboration features

---

## 🤝 Contributing

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### Areas for Contribution

- 🔧 **Add New Protocols** - Integrate more DeFi protocols
- 🌍 **Add New Chains** - Support more EVM chains
- 🎨 **UI/UX Improvements** - Enhance the interface
- 📊 **Analytics Features** - Build new visualizations
- 📝 **Documentation** - Improve guides and tutorials
- 🐛 **Bug Fixes** - Report and fix issues

---

## 📞 Support

### Getting Help

- **Documentation**: Read the guides in this repository
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

### Reporting Bugs

Please include:
1. Description of the issue
2. Steps to reproduce
3. Expected vs actual behavior
4. Environment details (OS, Python version, etc.)
5. Relevant logs or screenshots

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

### Technologies

- **Rindexer** - High-performance EVM indexing
- **The Graph** - Decentralized indexing protocol
- **Web3.py** - Python Ethereum library
- **Flask** - Lightweight web framework
- **Chart.js** - Beautiful charts
- **Trust Wallet** - Token icon assets

### DeFi Protocols

- Aave, Compound, Uniswap, Curve, Lido, Yearn, Convex, Balancer, GMX, SushiSwap

### Community

- Ethereum developer community
- DeFi protocol teams
- Open source contributors

---

## 📊 Project Stats

- **Lines of Code**: ~5,000+
- **Supported Chains**: 6
- **Supported Protocols**: 10+
- **Token Support**: 50+ common tokens
- **API Integrations**: 3 (RPC, CoinGecko, Etherscan)
- **Documentation Pages**: 10+

---

**Built with ❤️ for the DeFi community**

*Making DeFi portfolio tracking simple, fast, and accessible to everyone.*

