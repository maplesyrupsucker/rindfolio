# 🚀 Quick Start Guide

Get your EVM Balance Checker running in 5 minutes!

## Prerequisites

- ✅ Docker Desktop installed and running
- ✅ Python 3.9 or higher
- ✅ 2GB free disk space

## Installation Steps

### 1. Navigate to the project
```bash
cd /Users/slavid/Documents/GitHub/rindfolio/evm-balance-checker
```

### 2. Run the startup script
```bash
./start.sh
```

That's it! The script will:
- Create a Python virtual environment
- Install all dependencies
- Start PostgreSQL database
- Start rindexer for blockchain indexing
- Launch the web application

### 3. Open your browser
```
http://localhost:5000
```

## What You Can Do

### Check Any Ethereum Address

Try these example addresses:

**Vitalik Buterin's Address:**
```
0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

**USDC Treasury:**
```
0x5414d89a8bF7E99d732BC52f3e6A3Ef461c0C078
```

### View Information

The app displays:
- 💰 **Total Portfolio Value** - Sum of all assets in USD
- 💎 **Token Balances** - ETH, USDC, USDT, DAI, WETH, WBTC, AAVE, UNI, LINK
- 🏦 **DeFi Positions** - Token holdings and their USD values
- 📜 **Transaction History** - Recent transactions with block numbers

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Install Python dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Docker services
```bash
docker-compose up -d
```

### 3. Run the application
```bash
python app.py
```

## Stopping the Application

Press `Ctrl+C` in the terminal to stop the Flask server.

To stop Docker services:
```bash
docker-compose down
```

To stop and remove all data:
```bash
docker-compose down -v
```

## Troubleshooting

### Docker not running
```bash
# Start Docker Desktop, then try again
./start.sh
```

### Port already in use
If port 5000 or 3001 is already in use:

**Option 1:** Stop the conflicting service

**Option 2:** Edit `docker-compose.yml` and `app.py` to use different ports

### Can't connect to Ethereum
- Check your internet connection
- The app uses public RPC endpoints which may have rate limits
- For better performance, get a free API key from:
  - [Infura](https://infura.io/)
  - [Alchemy](https://www.alchemy.com/)
  - [QuickNode](https://www.quicknode.com/)

Then update `.env`:
```bash
ETH_RPC_URL=https://mainnet.infura.io/v3/YOUR_API_KEY
```

### Rindexer not indexing
Check the logs:
```bash
docker-compose logs -f rindexer
```

Restart the service:
```bash
docker-compose restart rindexer
```

## API Usage

You can also use the API directly:

```bash
# Check an address
curl http://localhost:5000/api/check/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# Health check
curl http://localhost:5000/api/health
```

## Using Beads for Task Management

This project uses Beads for tracking development tasks:

```bash
# View all tasks
bd list

# Check what's ready to work on
bd ready

# Show task details
bd show <task-id>
```

## Next Steps

- 📖 Read the full [README.md](README.md) for detailed documentation
- 🔧 Customize token list in `app.py`
- 🌐 Add more chains in `rindexer.yaml`
- 🎨 Modify the UI in `templates/index.html`

## Need Help?

- Check the [README.md](README.md) for detailed documentation
- Review [rindexer documentation](https://rindexer.xyz/)
- Check [Beads documentation](https://github.com/steveyegge/beads)

---

Happy balance checking! 🎉

