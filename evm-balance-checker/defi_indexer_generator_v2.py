#!/usr/bin/env python3
"""
DeFi Indexer Generator V2 - Enhanced with fallback ABIs
Auto-generate rindexer.yaml from The Graph subgraphs with built-in fallback ABIs
"""

import requests
import json
import os
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import yaml

# Configuration
OUTPUT_DIR = "./defi_indexer"
ABIS_DIR = f"{OUTPUT_DIR}/abis"
RINDEXER_CONFIG = f"{OUTPUT_DIR}/rindexer.yaml"

# Block Explorer APIs (free tier)
EXPLORERS = {
    'ethereum': {
        'api': 'https://api.etherscan.io/api',
        'key_env': 'ETHERSCAN_API_KEY',
        'chain_id': 1
    },
    'arbitrum': {
        'api': 'https://api.arbiscan.io/api',
        'key_env': 'ARBISCAN_API_KEY',
        'chain_id': 42161
    },
    'polygon': {
        'api': 'https://api.polygonscan.com/api',
        'key_env': 'POLYGONSCAN_API_KEY',
        'chain_id': 137
    },
    'avalanche': {
        'api': 'https://api.snowtrace.io/api',
        'key_env': 'SNOWTRACE_API_KEY',
        'chain_id': 43114
    },
    'bsc': {
        'api': 'https://api.bscscan.com/api',
        'key_env': 'BSCSCAN_API_KEY',
        'chain_id': 56
    },
    'optimism': {
        'api': 'https://api-optimistic.etherscan.io/api',
        'key_env': 'OPTIMISM_ETHERSCAN_API_KEY',
        'chain_id': 10
    },
    'base': {
        'api': 'https://api.basescan.org/api',
        'key_env': 'BASESCAN_API_KEY',
        'chain_id': 8453
    }
}

# Fallback ABIs - Minimal event-only ABIs for common DeFi protocols
FALLBACK_ABIS = {
    'aave_v3_pool': [
        {"anonymous": False, "inputs": [{"indexed": True, "name": "reserve", "type": "address"}, {"indexed": False, "name": "user", "type": "address"}, {"indexed": True, "name": "onBehalfOf", "type": "address"}, {"indexed": False, "name": "amount", "type": "uint256"}, {"indexed": True, "name": "referralCode", "type": "uint16"}], "name": "Supply", "type": "event"},
        {"anonymous": False, "inputs": [{"indexed": True, "name": "reserve", "type": "address"}, {"indexed": True, "name": "user", "type": "address"}, {"indexed": True, "name": "to", "type": "address"}, {"indexed": False, "name": "amount", "type": "uint256"}], "name": "Withdraw", "type": "event"},
        {"anonymous": False, "inputs": [{"indexed": True, "name": "reserve", "type": "address"}, {"indexed": False, "name": "user", "type": "address"}, {"indexed": True, "name": "onBehalfOf", "type": "address"}, {"indexed": False, "name": "amount", "type": "uint256"}, {"indexed": False, "name": "interestRateMode", "type": "uint8"}, {"indexed": False, "name": "borrowRate", "type": "uint256"}, {"indexed": True, "name": "referralCode", "type": "uint16"}], "name": "Borrow", "type": "event"},
        {"anonymous": False, "inputs": [{"indexed": True, "name": "reserve", "type": "address"}, {"indexed": True, "name": "user", "type": "address"}, {"indexed": True, "name": "repayer", "type": "address"}, {"indexed": False, "name": "amount", "type": "uint256"}, {"indexed": False, "name": "useATokens", "type": "bool"}], "name": "Repay", "type": "event"},
        {"anonymous": False, "inputs": [{"indexed": True, "name": "collateralAsset", "type": "address"}, {"indexed": True, "name": "debtAsset", "type": "address"}, {"indexed": True, "name": "user", "type": "address"}, {"indexed": False, "name": "debtToCover", "type": "uint256"}, {"indexed": False, "name": "liquidatedCollateralAmount", "type": "uint256"}, {"indexed": False, "name": "liquidator", "type": "address"}, {"indexed": False, "name": "receiveAToken", "type": "bool"}], "name": "LiquidationCall", "type": "event"}
    ],
    'uniswap_v3_factory': [
        {"anonymous": False, "inputs": [{"indexed": True, "name": "token0", "type": "address"}, {"indexed": True, "name": "token1", "type": "address"}, {"indexed": True, "name": "fee", "type": "uint24"}, {"indexed": False, "name": "tickSpacing", "type": "int24"}, {"indexed": False, "name": "pool", "type": "address"}], "name": "PoolCreated", "type": "event"}
    ],
    'uniswap_v3_pool': [
        {"anonymous": False, "inputs": [{"indexed": False, "name": "sender", "type": "address"}, {"indexed": True, "name": "owner", "type": "address"}, {"indexed": True, "name": "tickLower", "type": "int24"}, {"indexed": True, "name": "tickUpper", "type": "int24"}, {"indexed": False, "name": "amount", "type": "uint128"}, {"indexed": False, "name": "amount0", "type": "uint256"}, {"indexed": False, "name": "amount1", "type": "uint256"}], "name": "Mint", "type": "event"},
        {"anonymous": False, "inputs": [{"indexed": True, "name": "owner", "type": "address"}, {"indexed": True, "name": "tickLower", "type": "int24"}, {"indexed": True, "name": "tickUpper", "type": "int24"}, {"indexed": False, "name": "amount", "type": "uint128"}, {"indexed": False, "name": "amount0", "type": "uint256"}, {"indexed": False, "name": "amount1", "type": "uint256"}], "name": "Burn", "type": "event"},
        {"anonymous": False, "inputs": [{"indexed": True, "name": "sender", "type": "address"}, {"indexed": True, "name": "recipient", "type": "address"}, {"indexed": False, "name": "amount0", "type": "int256"}, {"indexed": False, "name": "amount1", "type": "int256"}, {"indexed": False, "name": "sqrtPriceX96", "type": "uint160"}, {"indexed": False, "name": "liquidity", "type": "uint128"}, {"indexed": False, "name": "tick", "type": "int24"}], "name": "Swap", "type": "event"}
    ],
    'curve_pool': [
        {"anonymous": False, "inputs": [{"indexed": True, "name": "provider", "type": "address"}, {"indexed": False, "name": "token_amounts", "type": "uint256[2]"}, {"indexed": False, "name": "fees", "type": "uint256[2]"}, {"indexed": False, "name": "invariant", "type": "uint256"}, {"indexed": False, "name": "token_supply", "type": "uint256"}], "name": "AddLiquidity", "type": "event"},
        {"anonymous": False, "inputs": [{"indexed": True, "name": "provider", "type": "address"}, {"indexed": False, "name": "token_amounts", "type": "uint256[2]"}, {"indexed": False, "name": "fees", "type": "uint256[2]"}, {"indexed": False, "name": "token_supply", "type": "uint256"}], "name": "RemoveLiquidity", "type": "event"},
        {"anonymous": False, "inputs": [{"indexed": True, "name": "provider", "type": "address"}, {"indexed": False, "name": "token_amount", "type": "uint256"}, {"indexed": False, "name": "coin_amount", "type": "uint256"}, {"indexed": False, "name": "token_supply", "type": "uint256"}], "name": "RemoveLiquidityOne", "type": "event"},
        {"anonymous": False, "inputs": [{"indexed": True, "name": "buyer", "type": "address"}, {"indexed": False, "name": "sold_id", "type": "int128"}, {"indexed": False, "name": "tokens_sold", "type": "uint256"}, {"indexed": False, "name": "bought_id", "type": "int128"}, {"indexed": False, "name": "tokens_bought", "type": "uint256"}], "name": "TokenExchange", "type": "event"}
    ],
    'erc20': [
        {"anonymous": False, "inputs": [{"indexed": True, "name": "from", "type": "address"}, {"indexed": True, "name": "to", "type": "address"}, {"indexed": False, "name": "value", "type": "uint256"}], "name": "Transfer", "type": "event"},
        {"anonymous": False, "inputs": [{"indexed": True, "name": "owner", "type": "address"}, {"indexed": True, "name": "spender", "type": "address"}, {"indexed": False, "name": "value", "type": "uint256"}], "name": "Approval", "type": "event"}
    ]
}

# Top DeFi protocols with known contracts and fallback ABI mappings
TOP_DEFI_PROTOCOLS = {
    'aave-v3': {
        'name': 'Aave V3',
        'category': 'lending',
        'abi_fallback': 'aave_v3_pool',
        'networks': {
            'ethereum': {
                'contracts': [
                    {'address': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2', 'name': 'Pool'}
                ],
                'events': ['Supply', 'Withdraw', 'Borrow', 'Repay', 'LiquidationCall']
            },
            'arbitrum': {
                'contracts': [
                    {'address': '0x794a61358D6845594F94dc1DB02A252b5b4814aD', 'name': 'Pool'}
                ],
                'events': ['Supply', 'Withdraw', 'Borrow', 'Repay']
            },
            'polygon': {
                'contracts': [
                    {'address': '0x794a61358D6845594F94dc1DB02A252b5b4814aD', 'name': 'Pool'}
                ],
                'events': ['Supply', 'Withdraw', 'Borrow', 'Repay']
            },
            'optimism': {
                'contracts': [
                    {'address': '0x794a61358D6845594F94dc1DB02A252b5b4814aD', 'name': 'Pool'}
                ],
                'events': ['Supply', 'Withdraw', 'Borrow', 'Repay']
            },
            'base': {
                'contracts': [
                    {'address': '0xA238Dd80C259a72e81d7e4664a9801593F98d1c5', 'name': 'Pool'}
                ],
                'events': ['Supply', 'Withdraw', 'Borrow', 'Repay']
            }
        }
    },
    'uniswap-v3': {
        'name': 'Uniswap V3',
        'category': 'dex',
        'abi_fallback': 'uniswap_v3_factory',
        'networks': {
            'ethereum': {
                'contracts': [
                    {'address': '0x1F98431c8aD98523631AE4a59f267346ea31F984', 'name': 'Factory'}
                ],
                'events': ['PoolCreated']
            },
            'arbitrum': {
                'contracts': [
                    {'address': '0x1F98431c8aD98523631AE4a59f267346ea31F984', 'name': 'Factory'}
                ],
                'events': ['PoolCreated']
            },
            'polygon': {
                'contracts': [
                    {'address': '0x1F98431c8aD98523631AE4a59f267346ea31F984', 'name': 'Factory'}
                ],
                'events': ['PoolCreated']
            },
            'optimism': {
                'contracts': [
                    {'address': '0x1F98431c8aD98523631AE4a59f267346ea31F984', 'name': 'Factory'}
                ],
                'events': ['PoolCreated']
            },
            'base': {
                'contracts': [
                    {'address': '0x33128a8fC17869897dcE68Ed026d694621f6FDfD', 'name': 'Factory'}
                ],
                'events': ['PoolCreated']
            }
        }
    },
    'compound-v3': {
        'name': 'Compound V3',
        'category': 'lending',
        'networks': {
            'ethereum': {
                'contracts': [
                    {'address': '0xc3d688B66703497DAA19211EEdff47f25384cdc3', 'name': 'cUSDCv3'}
                ],
                'events': ['Supply', 'Withdraw', 'SupplyCollateral', 'WithdrawCollateral']
            },
            'arbitrum': {
                'contracts': [
                    {'address': '0xA5EDBDD9646f8dFF606d7448e414884C7d905dCA', 'name': 'cUSDCv3'}
                ],
                'events': ['Supply', 'Withdraw']
            },
            'polygon': {
                'contracts': [
                    {'address': '0xF25212E676D1F7F89Cd72fFEe66158f541246445', 'name': 'cUSDCv3'}
                ],
                'events': ['Supply', 'Withdraw']
            },
            'base': {
                'contracts': [
                    {'address': '0xb125E6687d4313864e53df431d5425969c15Eb2F', 'name': 'cUSDCv3'}
                ],
                'events': ['Supply', 'Withdraw']
            }
        }
    },
    'lido': {
        'name': 'Lido',
        'category': 'staking',
        'abi_fallback': 'erc20',
        'networks': {
            'ethereum': {
                'contracts': [
                    {'address': '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84', 'name': 'stETH'}
                ],
                'events': ['Transfer']
            }
        }
    },
    'rocket-pool': {
        'name': 'Rocket Pool',
        'category': 'staking',
        'abi_fallback': 'erc20',
        'networks': {
            'ethereum': {
                'contracts': [
                    {'address': '0xae78736Cd615f374D3085123A210448E74Fc6393', 'name': 'rETH'}
                ],
                'events': ['Transfer']
            }
        }
    },
    'gmx': {
        'name': 'GMX',
        'category': 'perp',
        'networks': {
            'arbitrum': {
                'contracts': [
                    {'address': '0x489ee077994B6658eAfA855C308275EAd8097C4A', 'name': 'GLP Manager'}
                ],
                'events': ['AddLiquidity', 'RemoveLiquidity']
            },
            'avalanche': {
                'contracts': [
                    {'address': '0xe1ae4d4b06A5Fe1fc288f6B4CD72f9F8323B107F', 'name': 'GLP Manager'}
                ],
                'events': ['AddLiquidity', 'RemoveLiquidity']
            }
        }
    },
    'sushiswap': {
        'name': 'SushiSwap',
        'category': 'dex',
        'networks': {
            'ethereum': {
                'contracts': [
                    {'address': '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac', 'name': 'Factory'}
                ],
                'events': ['PairCreated']
            },
            'arbitrum': {
                'contracts': [
                    {'address': '0xc35DADB65012eC5796536bD9864eD8773aBc74C4', 'name': 'Factory'}
                ],
                'events': ['PairCreated']
            },
            'polygon': {
                'contracts': [
                    {'address': '0xc35DADB65012eC5796536bD9864eD8773aBc74C4', 'name': 'Factory'}
                ],
                'events': ['PairCreated']
            }
        }
    },
    'balancer-v2': {
        'name': 'Balancer V2',
        'category': 'dex',
        'networks': {
            'ethereum': {
                'contracts': [
                    {'address': '0xBA12222222228d8Ba445958a75a0704d566BF2C8', 'name': 'Vault'}
                ],
                'events': ['PoolBalanceChanged', 'Swap']
            },
            'arbitrum': {
                'contracts': [
                    {'address': '0xBA12222222228d8Ba445958a75a0704d566BF2C8', 'name': 'Vault'}
                ],
                'events': ['PoolBalanceChanged', 'Swap']
            },
            'polygon': {
                'contracts': [
                    {'address': '0xBA12222222228d8Ba445958a75a0704d566BF2C8', 'name': 'Vault'}
                ],
                'events': ['PoolBalanceChanged', 'Swap']
            }
        }
    }
}

class DefiIndexerGeneratorV2:
    def __init__(self, use_api_keys: bool = True):
        self.protocols = TOP_DEFI_PROTOCOLS
        self.abis_cache = {}
        self.rate_limit_delay = 0.2
        self.use_api_keys = use_api_keys
        self.stats = {
            'fetched_from_api': 0,
            'used_fallback': 0,
            'failed': 0
        }
        
        os.makedirs(ABIS_DIR, exist_ok=True)
        
    def fetch_abi_from_explorer(self, address: str, network: str) -> Optional[Dict]:
        """Fetch ABI from block explorer API"""
        if not self.use_api_keys:
            return None
            
        explorer = EXPLORERS.get(network)
        if not explorer:
            return None
            
        api_key = os.getenv(explorer['key_env'], '')
        if not api_key:
            return None
        
        cache_key = f"{network}_{address}"
        if cache_key in self.abis_cache:
            return self.abis_cache[cache_key]
        
        url = explorer['api']
        params = {
            'module': 'contract',
            'action': 'getabi',
            'address': address,
            'apikey': api_key
        }
        
        try:
            time.sleep(self.rate_limit_delay)
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == '1' and data.get('result'):
                abi = json.loads(data['result'])
                self.abis_cache[cache_key] = abi
                self.stats['fetched_from_api'] += 1
                return abi
                
        except Exception as e:
            pass
            
        return None
    
    def get_fallback_abi(self, protocol_id: str) -> Optional[List[Dict]]:
        """Get fallback ABI for protocol"""
        protocol_data = self.protocols.get(protocol_id, {})
        fallback_key = protocol_data.get('abi_fallback')
        
        if fallback_key and fallback_key in FALLBACK_ABIS:
            return FALLBACK_ABIS[fallback_key]
        
        return None
    
    def filter_events_from_abi(self, abi: List[Dict], required_events: List[str]) -> List[str]:
        """Extract only required events from ABI"""
        found_events = []
        
        for item in abi:
            if item.get('type') == 'event':
                event_name = item.get('name')
                if event_name in required_events:
                    found_events.append(event_name)
        
        return found_events
    
    def create_minimal_abi(self, abi: List[Dict], required_events: List[str]) -> List[Dict]:
        """Create minimal ABI with only required events"""
        minimal_abi = []
        
        for item in abi:
            if item.get('type') == 'event':
                event_name = item.get('name')
                if event_name in required_events:
                    minimal_abi.append(item)
        
        return minimal_abi
    
    def save_abi(self, abi: List[Dict], protocol: str, network: str, contract_name: str):
        """Save ABI to file"""
        safe_name = contract_name.replace(' ', '_').lower()
        filename = f"{ABIS_DIR}/{protocol}_{network}_{safe_name}.json"
        
        with open(filename, 'w') as f:
            json.dump(abi, f, indent=2)
        
        return filename
    
    def generate_rindexer_config(self) -> Dict:
        """Generate complete rindexer.yaml configuration"""
        config = {
            'name': 'defi_positions_indexer',
            'description': 'Auto-generated DeFi positions indexer with fallback ABIs',
            'project_type': 'no-code',
            'networks': [],
            'storage': {
                'postgres': {
                    'enabled': True
                }
            },
            'global_contracts': []
        }
        
        networks_data = defaultdict(lambda: {'contracts': []})
        
        print("\n🔍 Processing protocols...")
        
        for protocol_id, protocol_data in self.protocols.items():
            protocol_name = protocol_data['name']
            category = protocol_data['category']
            
            print(f"\n📦 {protocol_name} ({category})")
            
            for network, network_data in protocol_data['networks'].items():
                if network not in EXPLORERS:
                    continue
                
                contracts = network_data.get('contracts', [])
                events = network_data.get('events', [])
                
                for contract_info in contracts:
                    contract_addr = contract_info['address']
                    contract_name = contract_info['name']
                    
                    print(f"  📍 {network}: {contract_name} ({contract_addr[:10]}...)")
                    
                    # Try to fetch from API first
                    abi = self.fetch_abi_from_explorer(contract_addr, network)
                    source = "API"
                    
                    # Fall back to built-in ABI
                    if not abi:
                        abi = self.get_fallback_abi(protocol_id)
                        source = "Fallback"
                        if abi:
                            self.stats['used_fallback'] += 1
                    
                    if abi:
                        minimal_abi = self.create_minimal_abi(abi, events)
                        
                        if minimal_abi:
                            abi_path = self.save_abi(minimal_abi, protocol_id, network, contract_name)
                            found_events = self.filter_events_from_abi(abi, events)
                            
                            contract_config = {
                                'name': f"{protocol_id}_{network}_{contract_name.replace(' ', '_').lower()}",
                                'address': contract_addr,
                                'abi': abi_path.replace(f"{OUTPUT_DIR}/", "./"),
                                'events': found_events,
                                'start_block': 'latest'
                            }
                            
                            networks_data[network]['contracts'].append(contract_config)
                            
                            print(f"    ✅ [{source}] {len(found_events)} events: {', '.join(found_events)}")
                        else:
                            print(f"    ⚠️  No matching events in ABI")
                            self.stats['failed'] += 1
                    else:
                        print(f"    ❌ No ABI available")
                        self.stats['failed'] += 1
        
        # Build networks configuration
        for network, data in networks_data.items():
            if data['contracts']:
                explorer_info = EXPLORERS[network]
                network_config = {
                    'name': network,
                    'chain_id': explorer_info['chain_id'],
                    'rpc': f"${{{network.upper()}_RPC_URL}}",
                    'contracts': data['contracts']
                }
                config['networks'].append(network_config)
        
        return config
    
    def save_rindexer_yaml(self, config: Dict):
        """Save configuration to rindexer.yaml"""
        with open(RINDEXER_CONFIG, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, width=120)
        
        print(f"\n✅ Generated {RINDEXER_CONFIG}")
    
    def generate_env_template(self, networks: List[str]):
        """Generate .env.example"""
        env_file = f"{OUTPUT_DIR}/.env.example"
        
        lines = [
            "# Block Explorer API Keys (optional - fallback ABIs used if not provided)",
            ""
        ]
        
        for network in networks:
            if network in EXPLORERS:
                key_name = EXPLORERS[network]['key_env']
                lines.append(f"{key_name}=")
        
        lines.extend([
            "",
            "# RPC URLs (required)",
            ""
        ])
        
        rpc_defaults = {
            'ethereum': 'https://eth.llamarpc.com',
            'arbitrum': 'https://arb1.arbitrum.io/rpc',
            'polygon': 'https://polygon-rpc.com',
            'avalanche': 'https://api.avax.network/ext/bc/C/rpc',
            'bsc': 'https://bsc-dataseed1.binance.org',
            'optimism': 'https://mainnet.optimism.io',
            'base': 'https://mainnet.base.org'
        }
        
        for network in networks:
            rpc_url = rpc_defaults.get(network, 'https://your-rpc-url')
            lines.append(f"{network.upper()}_RPC_URL={rpc_url}")
        
        lines.extend([
            "",
            "# Database",
            "DATABASE_URL=postgresql://user:password@localhost:5432/defi_indexer"
        ])
        
        with open(env_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Generated {env_file}")
    
    def generate_readme(self, config: Dict):
        """Generate comprehensive README"""
        total_contracts = sum(len(n['contracts']) for n in config['networks'])
        
        readme = f"""# DeFi Positions Indexer

🚀 **Production-ready** auto-generated configuration for indexing DeFi positions across multiple chains using **rindexer**.

## ✨ Features

- ✅ **Works without API keys** - Built-in fallback ABIs for major protocols
- ✅ **Minimal ABIs** - Only position-tracking events (no bloat)
- ✅ **Multi-chain** - {len(config['networks'])} networks configured
- ✅ **Top protocols** - {len(self.protocols)} DeFi protocols indexed
- ✅ **{total_contracts} contracts** ready to index

## 📊 Indexed Protocols

{self._generate_protocol_table()}

## 🚀 Quick Start

### 1. Install rindexer

```bash
cargo install rindexer
```

### 2. Set up environment

```bash
cp .env.example .env
# Edit .env with your RPC URLs (API keys optional)
```

### 3. Run the indexer

```bash
cd {OUTPUT_DIR}
rindexer start all
```

## 📁 Structure

```
{OUTPUT_DIR}/
├── rindexer.yaml          # Main configuration
├── abis/                  # Minimal ABIs (events only)
│   ├── aave-v3_ethereum_pool.json
│   ├── uniswap-v3_ethereum_factory.json
│   └── ...
├── .env.example           # Environment template
└── README.md              # This file
```

## 🔧 Configuration Details

### Networks ({len(config['networks'])})
{self._generate_network_list(config['networks'])}

### Event Categories

**Lending** (Aave, Compound)
- `Supply`, `Withdraw`, `Borrow`, `Repay`, `LiquidationCall`

**DEX** (Uniswap, Balancer, SushiSwap)
- `PoolCreated`, `Mint`, `Burn`, `Swap`, `AddLiquidity`, `RemoveLiquidity`

**Staking** (Lido, Rocket Pool)
- `Transfer`, `Deposit`, `Withdraw`

**Perpetuals** (GMX)
- `AddLiquidity`, `RemoveLiquidity`, `IncreasePosition`, `DecreasePosition`

## 🔄 Regenerating

To regenerate with updated protocols or API keys:

```bash
# With API keys (fetches latest ABIs)
python defi_indexer_generator_v2.py

# Without API keys (uses fallback ABIs)
python defi_indexer_generator_v2.py --no-api-keys
```

## 📊 Generation Stats

- Fetched from API: {self.stats['fetched_from_api']}
- Used fallback ABIs: {self.stats['used_fallback']}
- Failed: {self.stats['failed']}

## 🎯 Use Cases

1. **Portfolio Tracking** - Index user positions across all protocols
2. **Analytics** - Track protocol TVL, volumes, and user activity
3. **Risk Monitoring** - Monitor liquidations and health factors
4. **Yield Farming** - Track LP positions and rewards
5. **Historical Analysis** - Query historical DeFi positions

## 📚 Resources

- [rindexer Documentation](https://rindexer.xyz)
- [The Graph Explorer](https://thegraph.com/explorer)
- [DeFi Llama](https://defillama.com)

## ⚠️ Notes

- **Start blocks** are set to `latest` - adjust for historical indexing
- **ABIs** are minimal (events only) to reduce size and improve performance
- **Fallback ABIs** ensure the indexer works even without block explorer API keys
- **Rate limits** apply to free-tier block explorer APIs (5 calls/sec)

## 🔐 API Keys (Optional)

While the indexer works without API keys using fallback ABIs, providing keys enables:
- Fetching latest ABIs with all event signatures
- Higher rate limits for ABI fetching
- Support for newly deployed contracts

Get free API keys:
- Etherscan: https://etherscan.io/apis
- Arbiscan: https://arbiscan.io/apis
- Polygonscan: https://polygonscan.com/apis
- Snowtrace: https://snowtrace.io/apis
- BscScan: https://bscscan.com/apis

---

Generated by **DeFi Indexer Generator V2**
"""
        
        with open(f"{OUTPUT_DIR}/README.md", 'w') as f:
            f.write(readme)
        
        print(f"✅ Generated {OUTPUT_DIR}/README.md")
    
    def _generate_protocol_table(self) -> str:
        """Generate markdown table of protocols"""
        lines = ["| Protocol | Category | Networks |", "|----------|----------|----------|"]
        
        for protocol_id, data in sorted(self.protocols.items()):
            name = data['name']
            category = data['category'].title()
            networks = ', '.join(sorted(data['networks'].keys()))
            lines.append(f"| {name} | {category} | {networks} |")
        
        return '\n'.join(lines)
    
    def _generate_network_list(self, networks: List[Dict]) -> str:
        """Generate markdown list of networks"""
        lines = []
        for net in networks:
            lines.append(f"- **{net['name'].title()}** (Chain ID: {net['chain_id']}) - {len(net['contracts'])} contracts")
        return '\n'.join(lines)
    
    def run(self):
        """Main execution"""
        print("=" * 70)
        print("🚀 DeFi Indexer Generator V2 (Enhanced)")
        print("=" * 70)
        print(f"\n📦 Protocols: {len(self.protocols)}")
        print(f"🌐 Networks: {len(EXPLORERS)}")
        print(f"📁 Output: {OUTPUT_DIR}")
        print(f"🔑 API Keys: {'Enabled' if self.use_api_keys else 'Disabled (using fallback ABIs)'}")
        
        config = self.generate_rindexer_config()
        self.save_rindexer_yaml(config)
        
        networks = [net['name'] for net in config['networks']]
        self.generate_env_template(networks)
        self.generate_readme(config)
        
        print("\n" + "=" * 70)
        print("✅ Generation Complete!")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"  - Networks: {len(config['networks'])}")
        print(f"  - Contracts: {sum(len(n['contracts']) for n in config['networks'])}")
        print(f"  - ABIs generated: {len(os.listdir(ABIS_DIR))}")
        print(f"\n📈 Stats:")
        print(f"  - Fetched from API: {self.stats['fetched_from_api']}")
        print(f"  - Used fallback: {self.stats['used_fallback']}")
        print(f"  - Failed: {self.stats['failed']}")
        print(f"\n🚀 Next steps:")
        print(f"  1. cd {OUTPUT_DIR}")
        print(f"  2. cp .env.example .env")
        print(f"  3. Edit .env with RPC URLs")
        print(f"  4. rindexer start all")
        print("\n" + "=" * 70)

if __name__ == "__main__":
    import sys
    use_api_keys = '--no-api-keys' not in sys.argv
    
    generator = DefiIndexerGeneratorV2(use_api_keys=use_api_keys)
    generator.run()

