# 🔍 EVM Balance Checker

A powerful EVM balance checker that displays an Ethereum address's balance, DeFi positions, and transaction history. Built with **Beads** for task management and **rindexer** for blockchain indexing.

## ✨ Features

- 💰 **Real-time Balance Checking** - Check ETH and ERC20 token balances
- 🏦 **DeFi Positions** - View token holdings and positions
- 📜 **Transaction History** - Browse recent transactions with block details
- 🎨 **Beautiful UI** - Modern, responsive web interface
- ⚡ **Fast Indexing** - Powered by rindexer for efficient blockchain data access
- 🔗 **Multi-chain Ready** - Easy to extend to other EVM chains

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Node.js (for rindexer)

### Installation

1. **Clone the repository**
```bash
cd /Users/slavid/Documents/GitHub/rindfolio/evm-balance-checker
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your RPC URLs if needed
```

4. **Start the database and indexer**
```bash
docker-compose up -d
```

Wait for the services to be healthy (about 30 seconds).

5. **Run the web application**
```bash
python app.py
```

6. **Open your browser**
```
http://localhost:5000
```

## 📖 Usage

1. Enter an Ethereum address in the search box
2. Click "Check Address" or press Enter
3. View:
   - Total portfolio value in USD
   - Token balances (ETH, USDC, USDT, DAI, WETH, etc.)
   - DeFi positions
   - Recent transaction history

### Example Addresses to Try

- Vitalik's address: `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045`
- USDC Treasury: `0x5414d89a8bF7E99d732BC52f3e6A3Ef461c0C078`

## 🏗️ Architecture

```
┌─────────────────┐
│   Web Browser   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Flask App      │ ◄── Web3.py ──► Ethereum RPC
│  (app.py)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   rindexer      │ ◄── Indexes blockchain data
│   (GraphQL)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
└─────────────────┘
```

## 🛠️ Technology Stack

- **Backend**: Python Flask, Web3.py
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Indexer**: rindexer (Rust-based EVM indexer)
- **Database**: PostgreSQL
- **Task Management**: Beads (bd)
- **Containerization**: Docker

## 🔧 Configuration

### Adding More Tokens

Edit `app.py` and add tokens to the `DEFI_PROTOCOLS` dictionary:

```python
DEFI_PROTOCOLS = {
    'YOUR_TOKEN': '0xYourTokenAddress',
    # ... more tokens
}
```

### Changing RPC Provider

Edit `.env`:
```bash
ETH_RPC_URL=https://your-rpc-provider.com
```

### Indexing More Contracts

Edit `rindexer.yaml` to add more contracts to index:

```yaml
contracts:
  - name: YourContract
    details:
      - network: ethereum
        address: "0xYourContractAddress"
        start_block: 1000000
    abi: ./abis/your-contract.json
    include_events:
      - YourEvent
```

## 📊 API Endpoints

### Check Address
```
GET /api/check/<address>
```

Returns:
```json
{
  "address": "0x...",
  "balances": [...],
  "total_value_usd": 12345.67,
  "transactions": [...],
  "defi_positions": [...],
  "timestamp": "2025-11-09T..."
}
```

### Health Check
```
GET /api/health
```

Returns:
```json
{
  "status": "ok",
  "web3_connected": true,
  "current_block": 18500000
}
```

## 🐛 Troubleshooting

### Docker services not starting
```bash
docker-compose down -v
docker-compose up -d
```

### Web3 connection issues
- Check your RPC URL in `.env`
- Try a different RPC provider (Infura, Alchemy, etc.)

### No transaction history showing
- Wait for rindexer to sync (check logs: `docker-compose logs -f rindexer`)
- The fallback method scans recent blocks directly from the blockchain

## 🔮 Future Enhancements

- [ ] Multi-chain support (Polygon, BSC, Arbitrum, etc.)
- [ ] NFT balance display
- [ ] Historical balance charts
- [ ] DeFi protocol integration (Aave, Compound, Uniswap positions)
- [ ] Export data to CSV
- [ ] Wallet tracking (save favorite addresses)
- [ ] Price alerts
- [ ] ENS name resolution

## 📝 Task Management with Beads

This project uses Beads for task tracking:

```bash
# View current tasks
bd list

# Check ready work
bd ready

# View task details
bd show <task-id>
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use this project for any purpose.

## 🙏 Acknowledgments

- [Beads](https://github.com/steveyegge/beads) - Task management for AI agents
- [rindexer](https://github.com/joshstevens19/rindexer) - Fast EVM indexer
- [Web3.py](https://github.com/ethereum/web3.py) - Python Ethereum library
- [Flask](https://flask.palletsprojects.com/) - Python web framework

---

Built with ❤️ using Beads and rindexer

