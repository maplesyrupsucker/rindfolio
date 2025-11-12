# Wallet Connection Setup Guide

This guide explains how to set up browser wallet and WalletConnect integration for the Multi-Chain Portfolio Tracker.

## Prerequisites

1. **Node.js and Bun** - Make sure you have Bun installed (we use Bun instead of npm)
2. **WalletConnect Project ID** - Get a free project ID from [WalletConnect Cloud](https://cloud.walletconnect.com/)

## Setup Steps

### 1. Install Dependencies

```bash
cd evm-balance-checker
bun install
```

### 2. Configure WalletConnect Project ID

Copy the `.env.example` file to `.env` (if you don't have one already):

```bash
cp env.example .env
```

Edit `.env` and add your WalletConnect project ID:

```bash
WALLETCONNECT_PROJECT_ID=your_project_id_here
```

**Note:** You can use the same WalletConnect project ID from the `7702-cleaner` project if you have one configured there.

### 3. Build React Components

Build the wallet connection React components:

```bash
bun run build
```

This will create the `static/` directory with the compiled JavaScript files.

### 4. Run the Flask Application

Start the Flask server as usual:

```bash
python app.py
```

Or if you're using a virtual environment:

```bash
source venv/bin/activate
python app.py
```

### 5. Access the Application

Open your browser and navigate to `http://localhost:5001` (or whatever port your Flask app uses).

## Features

### Browser Wallet Connection
- Click "Connect Browser Wallet" to connect MetaMask or other injected wallets
- Supports all major browser wallets (MetaMask, Coinbase Wallet, etc.)

### WalletConnect (Mobile Wallets)
- Click "Connect Mobile Wallet (WalletConnect)" to connect mobile wallets
- Scan QR code with your mobile wallet app
- Supports all WalletConnect-compatible wallets

### Auto-fill Address
- When a wallet is connected, the address input is automatically filled
- The portfolio check is automatically triggered
- You can still manually enter addresses or ENS names

### Disconnect
- Click "Disconnect" to disconnect your wallet
- The address input will be cleared

## Supported Chains

The wallet connection supports all chains tracked by the portfolio tracker:
- Ethereum (Mainnet)
- Arbitrum
- Polygon
- Avalanche
- BNB Chain
- Base
- Optimism

## Troubleshooting

### WalletConnect Not Showing
- Make sure `WALLETCONNECT_PROJECT_ID` is set in your `.env` file
- Restart the Flask server after adding the environment variable
- Check browser console for errors

### Build Errors
- Make sure all dependencies are installed: `bun install`
- Check that you're using Node.js 18+ and Bun

### Wallet Not Connecting
- Make sure your wallet extension is installed and unlocked
- For WalletConnect, make sure you're scanning the QR code with a compatible wallet
- Check browser console for connection errors

## Development

To run in development mode with hot reload:

```bash
bun run dev
```

This will start Vite dev server on port 5173. However, for full integration with Flask, you'll need to build the React components first.

## Architecture

- **React Components** (`src/`): Wallet connection UI components using wagmi
- **Providers** (`src/Providers.jsx`): Wagmi configuration with browser wallet and WalletConnect connectors
- **Main Entry** (`src/main.jsx`): Initializes React app and integrates with existing HTML
- **Flask Integration**: Flask serves the built React bundle and passes WalletConnect project ID to template

