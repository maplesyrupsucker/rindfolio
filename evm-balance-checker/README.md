# 🔍 Multi-Chain Portfolio Tracker

A powerful multi-chain portfolio tracker that displays wallet balances, DeFi positions, and portfolio analytics across Ethereum, Arbitrum, Polygon, Avalanche, BNB Chain, and Base. Built with **React + Vite** frontend and **Flask** API backend.

## ✨ Features

- 💰 **Multi-Chain Balance Checking** - Check balances across 6+ EVM chains
- 🏦 **DeFi Positions** - View lending, borrowing, and liquidity positions
- 📊 **Interactive Charts** - Pie charts showing portfolio breakdown by token/chain and DeFi by protocol/chain
- 🔗 **Wallet Connection** - Connect via Browser Wallet (MetaMask) or WalletConnect QR
- 🎨 **Beautiful UI** - Modern, responsive React interface with dark/light theme
- 🖼️ **Token Icons** - Real token logos with fallback chain
- ⚡ **Fast API** - Flask backend with Web3.py for efficient blockchain queries
- 🔍 **ENS Support** - Resolve ENS names to addresses

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+ (or Bun)
- Docker & Docker Compose (optional, for rindexer)

### Installation

1. **Clone the repository**
```bash
cd evm-balance-checker
```

2. **Install Python dependencies (Backend)**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Install Node.js dependencies (Frontend)**
```bash
bun install
# or: npm install
```

4. **Set up environment variables**
```bash
# Create .env file with your RPC URLs
echo "RPC_URL=https://mainnet.infura.io/v3/YOUR_API_KEY" > .env
echo "VITE_RPC_URL=https://mainnet.infura.io/v3/YOUR_API_KEY" >> .env
```

5. **Start the application**

**Terminal 1 - Start Flask API Backend:**
```bash
source venv/bin/activate  # Activate virtual environment
python app.py
# Flask API runs on http://localhost:5001
```

**Terminal 2 - Start React Frontend:**
```bash
bun run dev
# or: npm run dev
# React app runs on http://localhost:5173
```

6. **Open your browser**
```
http://localhost:5173
```

The React frontend will automatically proxy API requests to Flask backend on port 5001.

### Development Mode

**Running Separately (Recommended for Development):**
- Flask API: `http://localhost:5001` (Terminal 1)
- React Dev Server: `http://localhost:5173` (Terminal 2)
- React proxies `/api/*` requests to Flask automatically

**Hot Module Replacement (HMR):**
- Changes to React components (`src/*.jsx`) will hot-reload automatically
- Changes to Flask API (`app.py`) require restarting Flask server
- Changes to CSS (`src/index.css`) will hot-reload automatically

### Production Build

**Build React frontend:**
```bash
bun run build
# or: npm run build
# Output: dist/ directory
```

**Serve Flask with static React build:**
```python
# Flask will serve static files from dist/ directory
# Update Flask routes if needed to serve index.html for all non-API routes
python app.py
```

## 📖 Usage

1. **Connect Wallet** (optional):
   - Click "🌐 Browser Wallet" to connect MetaMask or other browser wallets
   - Click "📱 WalletConnect" to scan QR code with mobile wallet
   - Or manually enter an Ethereum address or ENS name

2. **Check Address**:
   - Enter an Ethereum address or ENS name in the search box
   - Click "Check Address" or press Enter
   - Or click a wallet connection button to auto-fill your address

3. **View Results**:
   - **Portfolio Summary**: Total value, wallet tokens, DeFi positions
   - **Pie Charts**: Portfolio breakdown by token/chain, DeFi breakdown by protocol/chain
   - **Wallet Tokens**: All token balances with icons and USD values
   - **DeFi Positions**: Lending, borrowing, and liquidity positions

### Example Addresses to Try

- Vitalik's address: `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045`
- USDC Treasury: `0x5414d89a8bF7E99d732BC52f3e6A3Ef461c0C078`

## 🏗️ Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (localhost:5173)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  React + Vite   │ ◄── Frontend (Port 5173)
│  (Full UI)      │
└────────┬────────┘
         │ API Calls (/api/*)
         ▼
┌─────────────────┐
│  Flask API      │ ◄── Web3.py ──► Ethereum RPC
│  (Port 5001)    │
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

- **Backend**: Python Flask (API-only), Web3.py, flask-cors
- **Frontend**: React 18, Vite, Chart.js, Wagmi (WalletConnect)
- **Wallet Connection**: Browser Wallet (MetaMask) + WalletConnect QR
- **Charts**: Chart.js with react-chartjs-2
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
RPC_URL=https://mainnet.infura.io/v3/YOUR_API_KEY
VITE_RPC_URL=https://mainnet.infura.io/v3/YOUR_API_KEY
NEXT_PUBLIC_RPC_URL=https://mainnet.infura.io/v3/YOUR_API_KEY
```

- `RPC_URL`: Used by Flask backend
- `VITE_RPC_URL`: Used by React frontend (build-time)
- `NEXT_PUBLIC_RPC_URL`: Set in `index.html` for runtime access

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

Flask backend provides REST API endpoints (runs on port 5001):

### Check Address (All Chains)
```
GET /api/check/<address>
```

Returns:
```json
{
  "address": "0x...",
  "wallet_balances": [...],
  "defi_positions": [...],
  "total_value_usd": 12345.67,
  "wallet_value_usd": 10000.00,
  "defi_value_usd": 2345.67,
  "timestamp": "2025-11-09T..."
}
```

### Check Single Chain
```
GET /api/check-chain/<address>/<chain>
```

Where `<chain>` is: `ethereum`, `arbitrum`, `polygon`, `avalanche`, `bsc`, `base`

### Resolve ENS
```
GET /api/resolve-ens/<name>
```

Returns:
```json
{
  "name": "vitalik.eth",
  "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
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

### Flask API not starting
```bash
# Make sure flask-cors is installed
pip install flask-cors

# Check if port 5001 is available
lsof -ti:5001 | xargs kill -9  # Kill process on port 5001

# Start Flask
python app.py
```

### React frontend not connecting to API
- Make sure Flask is running on port 5001
- Check browser console for CORS errors
- Verify `vite.config.js` has proxy configured for `/api` → `http://localhost:5001`

### Wallet connection issues
- Make sure WalletConnect project ID is set in `index.html`
- For browser wallet: Install MetaMask or another Web3 wallet extension
- For WalletConnect: Check browser console for errors

### Charts not displaying
- Make sure `chart.js` and `react-chartjs-2` are installed: `bun install`
- Check browser console for Chart.js errors

### Token icons not loading
- Icons use fallback chain: Trust Wallet → CoinGecko → Cryptologos → Text
- Check browser network tab for failed image requests
- Icons are loaded from external CDNs

### Docker services not starting
```bash
docker-compose down -v
docker-compose up -d
```

### Web3 connection issues
- Check your RPC URL in `.env`
- Try a different RPC provider (Infura, Alchemy, etc.)
- Verify RPC endpoint is accessible

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

