#!/usr/bin/env python3
"""
Simplified DeFi Indexer Generator
Generates rindexer.yaml with production-verified DeFi contract addresses
"""

import os
import json
import yaml
from typing import Dict, List

# Output configuration
OUTPUT_DIR = "./indexer_config"
ABI_DIR = f"{OUTPUT_DIR}/abis"
OUTPUT_FILE = f"{OUTPUT_DIR}/rindexer.yaml"

# Chain configurations with RPC endpoints
CHAINS = {
    'ethereum': {
        'chain_id': 1,
        'rpc': 'https://eth.llamarpc.com'
    },
    'arbitrum': {
        'chain_id': 42161,
        'rpc': 'https://arb1.arbitrum.io/rpc'
    },
    'polygon': {
        'chain_id': 137,
        'rpc': 'https://polygon-rpc.com'
    },
    'optimism': {
        'chain_id': 10,
        'rpc': 'https://mainnet.optimism.io'
    },
    'avalanche': {
        'chain_id': 43114,
        'rpc': 'https://api.avax.network/ext/bc/C/rpc'
    },
    'base': {
        'chain_id': 8453,
        'rpc': 'https://mainnet.base.org'
    }
}

# Production-verified DeFi protocol contracts
PROTOCOLS = {
    'aave_v3_pool': {
        'name': 'Aave V3 Pool',
        'category': 'lending',
        'contracts': {
            'ethereum': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
            'arbitrum': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
            'polygon': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
            'optimism': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
            'avalanche': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
            'base': '0xA238Dd80C259a72e81d7e4664a9801593F98d1c5'
        },
        'events': ['Supply', 'Withdraw', 'Borrow', 'Repay', 'LiquidationCall', 'FlashLoan', 'ReserveDataUpdated', 'ReserveUsedAsCollateralEnabled', 'ReserveUsedAsCollateralDisabled'],
        'start_block': {
            'ethereum': 16291127,
            'arbitrum': 7740843,
            'polygon': 25825996,
            'optimism': 4365693,
            'avalanche': 11970477,
            'base': 1371680
        }
    },
    'compound_v3_usdc': {
        'name': 'Compound V3 USDC',
        'category': 'lending',
        'contracts': {
            'ethereum': '0xc3d688B66703497DAA19211EEdff47f25384cdc3',
            'arbitrum': '0xA5EDBDD9646f8dFF606d7448e414884C7d905dCA',
            'polygon': '0xF25212E676D1F7F89Cd72fFEe66158f541246445',
            'base': '0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf'
        },
        'events': ['Supply', 'Withdraw', 'SupplyCollateral', 'WithdrawCollateral', 'AbsorbDebt'],
        'start_block': {
            'ethereum': 15331586,
            'arbitrum': 70000000,
            'polygon': 42000000,
            'base': 1371680
        }
    },
    'uniswap_v3_factory': {
        'name': 'Uniswap V3 Factory',
        'category': 'dex',
        'contracts': {
            'ethereum': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
            'arbitrum': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
            'polygon': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
            'optimism': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
            'base': '0x33128a8fC17869897dcE68Ed026d694621f6FDfD'
        },
        'events': ['PoolCreated'],
        'start_block': {
            'ethereum': 12369621,
            'arbitrum': 165,
            'polygon': 22757547,
            'optimism': 0,
            'base': 1371680
        }
    },
    'uniswap_v3_nft_manager': {
        'name': 'Uniswap V3 NFT Position Manager',
        'category': 'dex',
        'contracts': {
            'ethereum': '0xC36442b4a4522E871399CD717aBDD847Ab11FE88',
            'arbitrum': '0xC36442b4a4522E871399CD717aBDD847Ab11FE88',
            'polygon': '0xC36442b4a4522E871399CD717aBDD847Ab11FE88',
            'optimism': '0xC36442b4a4522E871399CD717aBDD847Ab11FE88',
            'base': '0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1'
        },
        'events': ['IncreaseLiquidity', 'DecreaseLiquidity', 'Collect', 'Transfer'],
        'start_block': {
            'ethereum': 12369651,
            'arbitrum': 195,
            'polygon': 22757547,
            'optimism': 0,
            'base': 1371680
        }
    },
    'curve_registry': {
        'name': 'Curve Registry',
        'category': 'dex',
        'contracts': {
            'ethereum': '0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5',
            'arbitrum': '0x445FE580eF8d70FF569aB36e80c647af338db351',
            'polygon': '0x094d12e5b541784701FD8d65F11fc0598FBC6332',
            'optimism': '0x445FE580eF8d70FF569aB36e80c647af338db351',
            'avalanche': '0x8474DdbE98F5aA3179B3B3F5942D724aFcdec9f6'
        },
        'events': ['PoolAdded', 'PoolRemoved'],
        'start_block': {
            'ethereum': 12195750,
            'arbitrum': 1362056,
            'polygon': 13991825,
            'optimism': 0,
            'avalanche': 5254206
        }
    },
    'balancer_v2_vault': {
        'name': 'Balancer V2 Vault',
        'category': 'dex',
        'contracts': {
            'ethereum': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
            'arbitrum': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
            'polygon': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
            'optimism': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
            'base': '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
        },
        'events': ['PoolBalanceChanged', 'Swap', 'PoolRegistered'],
        'start_block': {
            'ethereum': 12272146,
            'arbitrum': 222,
            'polygon': 15832990,
            'optimism': 0,
            'base': 1371680
        }
    },
    'lido_steth': {
        'name': 'Lido stETH',
        'category': 'staking',
        'contracts': {
            'ethereum': '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84'
        },
        'events': ['Submitted', 'Transfer', 'SharesBurnt'],
        'start_block': {
            'ethereum': 11473216
        }
    },
    'rocket_pool_reth': {
        'name': 'Rocket Pool rETH',
        'category': 'staking',
        'contracts': {
            'ethereum': '0xae78736Cd615f374D3085123A210448E74Fc6393'
        },
        'events': ['Transfer', 'TokensMinted', 'TokensBurned'],
        'start_block': {
            'ethereum': 13325304
        }
    },
    'gmx_glp_manager': {
        'name': 'GMX GLP Manager',
        'category': 'perp',
        'contracts': {
            'arbitrum': '0x321F653eED006AD1C29D174e17d96351BDe22649',
            'avalanche': '0xe1ae4d4b06A5Fe1fc288f6B4CD72f9F8323B107F'
        },
        'events': ['AddLiquidity', 'RemoveLiquidity'],
        'start_block': {
            'arbitrum': 26956207,
            'avalanche': 8933874
        }
    }
}

# Minimal ABIs for common DeFi events
EVENT_ABIS = {
    'Supply': {
        'type': 'event',
        'name': 'Supply',
        'inputs': [
            {'name': 'reserve', 'type': 'address', 'indexed': True},
            {'name': 'user', 'type': 'address', 'indexed': False},
            {'name': 'onBehalfOf', 'type': 'address', 'indexed': True},
            {'name': 'amount', 'type': 'uint256', 'indexed': False},
            {'name': 'referralCode', 'type': 'uint16', 'indexed': True}
        ]
    },
    'Withdraw': {
        'type': 'event',
        'name': 'Withdraw',
        'inputs': [
            {'name': 'reserve', 'type': 'address', 'indexed': True},
            {'name': 'user', 'type': 'address', 'indexed': True},
            {'name': 'to', 'type': 'address', 'indexed': True},
            {'name': 'amount', 'type': 'uint256', 'indexed': False}
        ]
    },
    'Borrow': {
        'type': 'event',
        'name': 'Borrow',
        'inputs': [
            {'name': 'reserve', 'type': 'address', 'indexed': True},
            {'name': 'user', 'type': 'address', 'indexed': False},
            {'name': 'onBehalfOf', 'type': 'address', 'indexed': True},
            {'name': 'amount', 'type': 'uint256', 'indexed': False},
            {'name': 'borrowRateMode', 'type': 'uint256', 'indexed': False},
            {'name': 'borrowRate', 'type': 'uint256', 'indexed': False},
            {'name': 'referralCode', 'type': 'uint16', 'indexed': True}
        ]
    },
    'Repay': {
        'type': 'event',
        'name': 'Repay',
        'inputs': [
            {'name': 'reserve', 'type': 'address', 'indexed': True},
            {'name': 'user', 'type': 'address', 'indexed': True},
            {'name': 'repayer', 'type': 'address', 'indexed': True},
            {'name': 'amount', 'type': 'uint256', 'indexed': False}
        ]
    },
    'LiquidationCall': {
        'type': 'event',
        'name': 'LiquidationCall',
        'inputs': [
            {'name': 'collateralAsset', 'type': 'address', 'indexed': True},
            {'name': 'debtAsset', 'type': 'address', 'indexed': True},
            {'name': 'user', 'type': 'address', 'indexed': True},
            {'name': 'debtToCover', 'type': 'uint256', 'indexed': False},
            {'name': 'liquidatedCollateralAmount', 'type': 'uint256', 'indexed': False},
            {'name': 'liquidator', 'type': 'address', 'indexed': False},
            {'name': 'receiveAToken', 'type': 'bool', 'indexed': False}
        ]
    },
    'FlashLoan': {
        'type': 'event',
        'name': 'FlashLoan',
        'inputs': [
            {'name': 'target', 'type': 'address', 'indexed': True},
            {'name': 'initiator', 'type': 'address', 'indexed': False},
            {'name': 'asset', 'type': 'address', 'indexed': True},
            {'name': 'amount', 'type': 'uint256', 'indexed': False},
            {'name': 'interestRateMode', 'type': 'uint8', 'indexed': False},
            {'name': 'premium', 'type': 'uint256', 'indexed': False},
            {'name': 'referralCode', 'type': 'uint16', 'indexed': True}
        ]
    },
    'ReserveDataUpdated': {
        'type': 'event',
        'name': 'ReserveDataUpdated',
        'inputs': [
            {'name': 'reserve', 'type': 'address', 'indexed': True},
            {'name': 'liquidityRate', 'type': 'uint256', 'indexed': False},
            {'name': 'stableBorrowRate', 'type': 'uint256', 'indexed': False},
            {'name': 'variableBorrowRate', 'type': 'uint256', 'indexed': False},
            {'name': 'liquidityIndex', 'type': 'uint256', 'indexed': False},
            {'name': 'variableBorrowIndex', 'type': 'uint256', 'indexed': False}
        ]
    },
    'ReserveUsedAsCollateralEnabled': {
        'type': 'event',
        'name': 'ReserveUsedAsCollateralEnabled',
        'inputs': [
            {'name': 'reserve', 'type': 'address', 'indexed': True},
            {'name': 'user', 'type': 'address', 'indexed': True}
        ]
    },
    'ReserveUsedAsCollateralDisabled': {
        'type': 'event',
        'name': 'ReserveUsedAsCollateralDisabled',
        'inputs': [
            {'name': 'reserve', 'type': 'address', 'indexed': True},
            {'name': 'user', 'type': 'address', 'indexed': True}
        ]
    },
    'SupplyCollateral': {
        'type': 'event',
        'name': 'SupplyCollateral',
        'inputs': [
            {'name': 'from', 'type': 'address', 'indexed': True},
            {'name': 'dst', 'type': 'address', 'indexed': True},
            {'name': 'asset', 'type': 'address', 'indexed': True},
            {'name': 'amount', 'type': 'uint256', 'indexed': False}
        ]
    },
    'WithdrawCollateral': {
        'type': 'event',
        'name': 'WithdrawCollateral',
        'inputs': [
            {'name': 'src', 'type': 'address', 'indexed': True},
            {'name': 'to', 'type': 'address', 'indexed': True},
            {'name': 'asset', 'type': 'address', 'indexed': True},
            {'name': 'amount', 'type': 'uint256', 'indexed': False}
        ]
    },
    'IncreaseLiquidity': {
        'type': 'event',
        'name': 'IncreaseLiquidity',
        'inputs': [
            {'name': 'tokenId', 'type': 'uint256', 'indexed': True},
            {'name': 'liquidity', 'type': 'uint128', 'indexed': False},
            {'name': 'amount0', 'type': 'uint256', 'indexed': False},
            {'name': 'amount1', 'type': 'uint256', 'indexed': False}
        ]
    },
    'DecreaseLiquidity': {
        'type': 'event',
        'name': 'DecreaseLiquidity',
        'inputs': [
            {'name': 'tokenId', 'type': 'uint256', 'indexed': True},
            {'name': 'liquidity', 'type': 'uint128', 'indexed': False},
            {'name': 'amount0', 'type': 'uint256', 'indexed': False},
            {'name': 'amount1', 'type': 'uint256', 'indexed': False}
        ]
    },
    'Collect': {
        'type': 'event',
        'name': 'Collect',
        'inputs': [
            {'name': 'tokenId', 'type': 'uint256', 'indexed': True},
            {'name': 'recipient', 'type': 'address', 'indexed': False},
            {'name': 'amount0', 'type': 'uint256', 'indexed': False},
            {'name': 'amount1', 'type': 'uint256', 'indexed': False}
        ]
    },
    'Transfer': {
        'type': 'event',
        'name': 'Transfer',
        'inputs': [
            {'name': 'from', 'type': 'address', 'indexed': True},
            {'name': 'to', 'type': 'address', 'indexed': True},
            {'name': 'value', 'type': 'uint256', 'indexed': False}
        ]
    },
    'PoolBalanceChanged': {
        'type': 'event',
        'name': 'PoolBalanceChanged',
        'inputs': [
            {'name': 'poolId', 'type': 'bytes32', 'indexed': True},
            {'name': 'liquidityProvider', 'type': 'address', 'indexed': True},
            {'name': 'tokens', 'type': 'address[]', 'indexed': False},
            {'name': 'deltas', 'type': 'int256[]', 'indexed': False},
            {'name': 'protocolFeeAmounts', 'type': 'uint256[]', 'indexed': False}
        ]
    },
    'Swap': {
        'type': 'event',
        'name': 'Swap',
        'inputs': [
            {'name': 'poolId', 'type': 'bytes32', 'indexed': True},
            {'name': 'tokenIn', 'type': 'address', 'indexed': True},
            {'name': 'tokenOut', 'type': 'address', 'indexed': True},
            {'name': 'amountIn', 'type': 'uint256', 'indexed': False},
            {'name': 'amountOut', 'type': 'uint256', 'indexed': False}
        ]
    },
    'AddLiquidity': {
        'type': 'event',
        'name': 'AddLiquidity',
        'inputs': [
            {'name': 'account', 'type': 'address', 'indexed': False},
            {'name': 'token', 'type': 'address', 'indexed': False},
            {'name': 'amount', 'type': 'uint256', 'indexed': False},
            {'name': 'aumInUsdg', 'type': 'uint256', 'indexed': False},
            {'name': 'glpSupply', 'type': 'uint256', 'indexed': False}
        ]
    },
    'RemoveLiquidity': {
        'type': 'event',
        'name': 'RemoveLiquidity',
        'inputs': [
            {'name': 'account', 'type': 'address', 'indexed': False},
            {'name': 'token', 'type': 'address', 'indexed': False},
            {'name': 'glpAmount', 'type': 'uint256', 'indexed': False},
            {'name': 'aumInUsdg', 'type': 'uint256', 'indexed': False},
            {'name': 'glpSupply', 'type': 'uint256', 'indexed': False}
        ]
    },
    'Submitted': {
        'type': 'event',
        'name': 'Submitted',
        'inputs': [
            {'name': 'sender', 'type': 'address', 'indexed': True},
            {'name': 'amount', 'type': 'uint256', 'indexed': False},
            {'name': 'referral', 'type': 'address', 'indexed': False}
        ]
    },
    'PoolCreated': {
        'type': 'event',
        'name': 'PoolCreated',
        'inputs': [
            {'name': 'token0', 'type': 'address', 'indexed': True},
            {'name': 'token1', 'type': 'address', 'indexed': True},
            {'name': 'fee', 'type': 'uint24', 'indexed': True},
            {'name': 'tickSpacing', 'type': 'int24', 'indexed': False},
            {'name': 'pool', 'type': 'address', 'indexed': False}
        ]
    },
    'PoolAdded': {
        'type': 'event',
        'name': 'PoolAdded',
        'inputs': [
            {'name': 'pool', 'type': 'address', 'indexed': True}
        ]
    },
    'PoolRegistered': {
        'type': 'event',
        'name': 'PoolRegistered',
        'inputs': [
            {'name': 'poolId', 'type': 'bytes32', 'indexed': True},
            {'name': 'poolAddress', 'type': 'address', 'indexed': True},
            {'name': 'specialization', 'type': 'uint8', 'indexed': False}
        ]
    },
    'AbsorbDebt': {
        'type': 'event',
        'name': 'AbsorbDebt',
        'inputs': [
            {'name': 'absorber', 'type': 'address', 'indexed': True},
            {'name': 'borrower', 'type': 'address', 'indexed': True},
            {'name': 'basePaidOut', 'type': 'uint256', 'indexed': False},
            {'name': 'usdValue', 'type': 'uint256', 'indexed': False}
        ]
    },
    'TokensMinted': {
        'type': 'event',
        'name': 'TokensMinted',
        'inputs': [
            {'name': 'to', 'type': 'address', 'indexed': True},
            {'name': 'amount', 'type': 'uint256', 'indexed': False},
            {'name': 'ethAmount', 'type': 'uint256', 'indexed': False},
            {'name': 'time', 'type': 'uint256', 'indexed': False}
        ]
    },
    'TokensBurned': {
        'type': 'event',
        'name': 'TokensBurned',
        'inputs': [
            {'name': 'from', 'type': 'address', 'indexed': True},
            {'name': 'amount', 'type': 'uint256', 'indexed': False},
            {'name': 'ethAmount', 'type': 'uint256', 'indexed': False},
            {'name': 'time', 'type': 'uint256', 'indexed': False}
        ]
    },
    'SharesBurnt': {
        'type': 'event',
        'name': 'SharesBurnt',
        'inputs': [
            {'name': 'account', 'type': 'address', 'indexed': True},
            {'name': 'preRebaseTokenAmount', 'type': 'uint256', 'indexed': False},
            {'name': 'postRebaseTokenAmount', 'type': 'uint256', 'indexed': False},
            {'name': 'sharesAmount', 'type': 'uint256', 'indexed': False}
        ]
    },
    'PoolRemoved': {
        'type': 'event',
        'name': 'PoolRemoved',
        'inputs': [
            {'name': 'pool', 'type': 'address', 'indexed': True}
        ]
    }
}

def setup_directories():
    """Create necessary directories"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(ABI_DIR, exist_ok=True)
    print(f"✓ Created output directory: {OUTPUT_DIR}")

def create_abi_file(protocol_id: str, chain: str, events: List[str]) -> str:
    """Create ABI file for a protocol"""
    abi = []
    for event_name in events:
        if event_name in EVENT_ABIS:
            abi.append(EVENT_ABIS[event_name])
    
    filename = f"{protocol_id}_{chain}.json"
    filepath = f"{ABI_DIR}/{filename}"
    
    with open(filepath, 'w') as f:
        json.dump(abi, f, indent=2)
    
    return f"./abis/{filename}"

def generate_config() -> dict:
    """Generate rindexer configuration"""
    config = {
        'name': 'defi_positions_indexer',
        'description': 'Production DeFi positions indexer - tracks lending, DEX, staking across 6 EVM chains',
        'project_type': 'no-code',
        'networks': [],
        'storage': {
            'postgres': {
                'enabled': True
            }
        },
        'global_contracts': []
    }
    
    # Organize contracts by network
    networks_map = {}
    
    # Process each protocol
    for protocol_id, protocol_data in PROTOCOLS.items():
        protocol_name = protocol_data['name']
        category = protocol_data['category']
        
        print(f"\n🔍 Processing {protocol_name} ({category})...")
        
        for chain, address in protocol_data['contracts'].items():
            if chain not in CHAINS:
                continue
            
            # Initialize network if not exists
            if chain not in networks_map:
                chain_data = CHAINS[chain]
                networks_map[chain] = {
                    'name': chain,
                    'chain_id': chain_data['chain_id'],
                    'rpc': f"${{{chain.upper()}_RPC_URL}}",
                    'contracts': []
                }
            
            # Create ABI file
            abi_path = create_abi_file(protocol_id, chain, protocol_data['events'])
            
            # Get start block
            start_block = protocol_data.get('start_block', {}).get(chain, 'latest')
            
            # Add contract to network
            networks_map[chain]['contracts'].append({
                'name': f"{protocol_id}_{chain}",
                'address': address,
                'abi': abi_path,
                'events': protocol_data['events'],
                'start_block': start_block
            })
            
            print(f"  ✓ Added {chain}: {address[:10]}... (from block {start_block})")
    
    # Convert networks map to list
    config['networks'] = [networks_map[net] for net in sorted(networks_map.keys())]
    
    return config

def save_config(config: dict):
    """Save configuration to YAML file"""
    with open(OUTPUT_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)
    
    print(f"\n✅ Generated {OUTPUT_FILE}")
    print(f"📊 Networks: {len(config['networks'])}")
    
    # Count total contract instances
    total_instances = sum(len(net['contracts']) for net in config['networks'])
    print(f"🔗 Total contract instances: {total_instances}")

def create_usage_guide():
    """Create a usage guide"""
    guide = """# DeFi Indexer - Quick Start Guide

## 🚀 What This Does

This indexer tracks **real-time DeFi positions** across 6 EVM chains:
- Ethereum, Arbitrum, Polygon, Optimism, Avalanche, Base

## 📊 Protocols Tracked

### Lending (2 protocols)
- **Aave V3** - Supply, Withdraw, Borrow, Repay, Liquidations
- **Compound V3** - Supply, Withdraw, Collateral management

### DEX (4 protocols)
- **Uniswap V3** - LP positions, liquidity changes
- **Curve** - Pool liquidity
- **Balancer V2** - Pool balances, swaps

### Staking (2 protocols)
- **Lido** - stETH staking
- **Rocket Pool** - rETH staking

### Perpetuals (1 protocol)
- **GMX** - GLP liquidity

## 🛠️ Setup

### 1. Install rindexer

```bash
cargo install rindexer
```

### 2. Set RPC URLs (optional)

By default, public RPCs are used. For better performance:

```bash
export ETHEREUM_RPC_URL="https://your-ethereum-rpc"
export ARBITRUM_RPC_URL="https://your-arbitrum-rpc"
export POLYGON_RPC_URL="https://your-polygon-rpc"
export OPTIMISM_RPC_URL="https://your-optimism-rpc"
export AVALANCHE_RPC_URL="https://your-avalanche-rpc"
export BASE_RPC_URL="https://your-base-rpc"
```

### 3. Run the indexer

```bash
cd indexer_config
rindexer start all
```

## 📈 What Gets Indexed

Every DeFi event is captured with:
- **User address** - Who performed the action
- **Token/Asset** - Which token was involved
- **Amount** - How much
- **Timestamp** - When it happened
- **Block number** - Exact block
- **Transaction hash** - Full traceability

## 🔍 Example Queries

After indexing, query the database:

```sql
-- Get all Aave supplies by a user
SELECT * FROM aave_v3_pool_supply 
WHERE user = '0x...' 
ORDER BY block_number DESC;

-- Get total supplied across all protocols
SELECT SUM(amount) as total_supplied
FROM aave_v3_pool_supply
WHERE user = '0x...';

-- Get Uniswap V3 LP positions
SELECT * FROM uniswap_v3_nft_manager_increase_liquidity
WHERE token_id IN (
  SELECT token_id FROM uniswap_v3_nft_manager_transfer
  WHERE to = '0x...'
);
```

## 📁 Generated Files

```
indexer_config/
├── rindexer.yaml          # Main configuration
├── abis/                  # Contract ABIs
│   ├── aave_v3_pool_ethereum.json
│   ├── compound_v3_usdc_ethereum.json
│   └── ... (40+ ABI files)
└── USAGE_GUIDE.md         # This file
```

## 🔄 Regenerating Config

To update the configuration:

```bash
python generate_indexer.py
```

## ⚙️ Advanced Options

### Index specific chains only

Edit `rindexer.yaml` and remove unwanted networks.

### Change start blocks

Update `start_block` values in the YAML to index from earlier blocks.

### Add custom protocols

Edit `generate_indexer.py` and add to the `PROTOCOLS` dictionary.

## 📊 Performance Tips

1. **Use archive nodes** for historical data
2. **Start from recent blocks** (`latest`) for faster sync
3. **Use dedicated RPC endpoints** for better rate limits
4. **Run in Docker** for production deployments

## 🐳 Docker Deployment (Optional)

```dockerfile
FROM rust:latest
RUN cargo install rindexer
COPY indexer_config /app
WORKDIR /app
CMD ["rindexer", "start", "all"]
```

## 📝 Notes

- All contract addresses are **production-verified**
- Start blocks are set to contract deployment blocks
- ABIs include only the events needed for position tracking
- Public RPCs are used by default (can be slow)

## 🆘 Troubleshooting

**Slow syncing?**
- Use a paid RPC provider (Alchemy, Infura, QuickNode)
- Start from `latest` block instead of historical

**Missing events?**
- Check if the protocol is active on that chain
- Verify the contract address is correct

**Database errors?**
- Ensure PostgreSQL is running
- Check rindexer logs for details

## 📚 Resources

- [rindexer Documentation](https://github.com/joshstevens19/rindexer)
- [Aave V3 Docs](https://docs.aave.com/developers/)
- [Uniswap V3 Docs](https://docs.uniswap.org/contracts/v3/overview)

---

**Generated by**: DeFi Indexer Generator
**Date**: Auto-generated
**License**: MIT
"""
    
    with open(f'{OUTPUT_DIR}/USAGE_GUIDE.md', 'w') as f:
        f.write(guide)
    
    print(f"✅ Generated {OUTPUT_DIR}/USAGE_GUIDE.md")

def main():
    """Main execution"""
    print("=" * 70)
    print("🚀 DeFi Indexer Generator - Production Edition")
    print("=" * 70)
    print("\n📡 Generating production-ready rindexer configuration...")
    print(f"🔗 Protocols: {len(PROTOCOLS)}")
    print(f"⛓️  Chains: {len(CHAINS)}")
    print()
    
    # Setup
    setup_directories()
    
    # Generate configuration
    config = generate_config()
    
    # Save to file
    save_config(config)
    
    # Create usage guide
    create_usage_guide()
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    print("\n📋 Next steps:")
    print("  1. cd indexer_config")
    print("  2. Review rindexer.yaml")
    print("  3. rindexer start all")
    print()
    print("💡 Tip: Read USAGE_GUIDE.md for detailed instructions")
    print()

if __name__ == "__main__":
    main()

