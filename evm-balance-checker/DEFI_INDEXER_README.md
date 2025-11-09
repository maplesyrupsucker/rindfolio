# DeFi Positions Indexer

Auto-generated configuration for tracking DeFi positions across multiple EVM chains.

## Overview

This indexer tracks critical DeFi events for:
- **Lending**: Aave V3, Compound V3
- **DEX**: Uniswap V3, Curve, Balancer
- **Staking**: Lido, Rocket Pool
- **Vaults**: Yearn
- **Farming**: Convex
- **Perpetuals**: GMX

## Supported Chains

- Ethereum (Mainnet)
- Arbitrum One
- Polygon
- Optimism
- Avalanche
- Base

## Events Tracked

### Lending Protocols
- `Supply` - User deposits assets
- `Withdraw` - User withdraws assets
- `Borrow` - User borrows assets
- `Repay` - User repays debt

### DEX / Liquidity
- `Mint` - Add liquidity
- `Burn` - Remove liquidity
- `AddLiquidity` - Add to pool
- `RemoveLiquidity` - Remove from pool

### Staking
- `Staked` - User stakes tokens
- `Withdrawn` - User unstakes tokens
- `Submitted` - Lido staking

## Setup

1. Install rindexer:
```bash
cargo install rindexer
```

2. Set environment variables:
```bash
export ETHEREUM_RPC_URL="your_ethereum_rpc"
export ARBITRUM_RPC_URL="your_arbitrum_rpc"
export POLYGON_RPC_URL="your_polygon_rpc"
# ... etc
```

3. Run the indexer:
```bash
rindexer start all
```

## Configuration

The `rindexer.yaml` file is auto-generated from The Graph subgraphs.

To regenerate:
```bash
python defi_indexer_generator.py
```

## Data Structure

Events are indexed with:
- User address
- Token/asset address
- Amount
- Timestamp
- Block number
- Transaction hash

## Querying Data

After indexing, query the database:

```sql
-- Get all user positions
SELECT * FROM supply_events WHERE user = '0x...';

-- Get total supplied by user
SELECT SUM(amount) FROM supply_events WHERE user = '0x...';
```

## Generated Files

- `rindexer.yaml` - Main configuration
- `abis/` - Contract ABIs
- `defi_indexer_cache/` - Cached data

## Maintenance

The indexer automatically:
- Fetches ABIs from blockchain explorers
- Caches subgraph metadata
- Validates event signatures
- Tracks from latest blocks

## License

MIT
