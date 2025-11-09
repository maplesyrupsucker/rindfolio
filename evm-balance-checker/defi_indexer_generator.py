#!/usr/bin/env python3
"""
DeFi Indexer Generator - Auto-generate rindexer.yaml from The Graph subgraphs
Discovers top DeFi protocols, fetches ABIs, and generates minimal indexing config
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
GRAPH_API_URL = "https://api.thegraph.com/subgraphs/name"
GRAPH_GATEWAY_URL = "https://gateway.thegraph.com/api"
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
    }
}

# Top DeFi protocols with known subgraph IDs
TOP_DEFI_PROTOCOLS = {
    'aave-v3': {
        'name': 'Aave V3',
        'category': 'lending',
        'networks': {
            'ethereum': {
                'subgraph': 'aave/protocol-v3',
                'contracts': ['0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'],  # Pool
                'events': ['Supply', 'Withdraw', 'Borrow', 'Repay', 'LiquidationCall']
            },
            'arbitrum': {
                'subgraph': 'aave/protocol-v3-arbitrum',
                'contracts': ['0x794a61358D6845594F94dc1DB02A252b5b4814aD'],
                'events': ['Supply', 'Withdraw', 'Borrow', 'Repay']
            },
            'polygon': {
                'subgraph': 'aave/protocol-v3-polygon',
                'contracts': ['0x794a61358D6845594F94dc1DB02A252b5b4814aD'],
                'events': ['Supply', 'Withdraw', 'Borrow', 'Repay']
            }
        }
    },
    'uniswap-v3': {
        'name': 'Uniswap V3',
        'category': 'dex',
        'networks': {
            'ethereum': {
                'subgraph': 'uniswap/uniswap-v3',
                'contracts': ['0x1F98431c8aD98523631AE4a59f267346ea31F984'],  # Factory
                'events': ['PoolCreated', 'Mint', 'Burn', 'Swap', 'Collect']
            },
            'arbitrum': {
                'subgraph': 'ianlapham/uniswap-arbitrum-one',
                'contracts': ['0x1F98431c8aD98523631AE4a59f267346ea31F984'],
                'events': ['PoolCreated', 'Mint', 'Burn']
            },
            'polygon': {
                'subgraph': 'ianlapham/uniswap-v3-polygon',
                'contracts': ['0x1F98431c8aD98523631AE4a59f267346ea31F984'],
                'events': ['PoolCreated', 'Mint', 'Burn']
            }
        }
    },
    'curve': {
        'name': 'Curve Finance',
        'category': 'dex',
        'networks': {
            'ethereum': {
                'subgraph': 'messari/curve-finance-ethereum',
                'contracts': ['0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5'],  # Registry
                'events': ['AddLiquidity', 'RemoveLiquidity', 'RemoveLiquidityOne', 'TokenExchange']
            },
            'polygon': {
                'subgraph': 'messari/curve-finance-polygon',
                'contracts': ['0x47bB542B9dE58b970bA50c9dae444DDB4c16751a'],
                'events': ['AddLiquidity', 'RemoveLiquidity']
            }
        }
    },
    'lido': {
        'name': 'Lido',
        'category': 'staking',
        'networks': {
            'ethereum': {
                'subgraph': 'lido/lido',
                'contracts': ['0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84'],  # stETH
                'events': ['Submitted', 'Transfer', 'SharesBurnt']
            }
        }
    },
    'compound-v3': {
        'name': 'Compound V3',
        'category': 'lending',
        'networks': {
            'ethereum': {
                'subgraph': 'messari/compound-v3-ethereum',
                'contracts': ['0xc3d688B66703497DAA19211EEdff47f25384cdc3'],  # cUSDCv3
                'events': ['Supply', 'Withdraw', 'SupplyCollateral', 'WithdrawCollateral']
            },
            'arbitrum': {
                'subgraph': 'messari/compound-v3-arbitrum',
                'contracts': ['0xA5EDBDD9646f8dFF606d7448e414884C7d905dCA'],
                'events': ['Supply', 'Withdraw']
            }
        }
    },
    'yearn': {
        'name': 'Yearn Finance',
        'category': 'vault',
        'networks': {
            'ethereum': {
                'subgraph': 'yearn/yearn-vaults-v2-mainnet',
                'contracts': ['0x50c1a2eA0a861A967D9d0FFE2AE4012c2E053804'],  # Registry
                'events': ['Deposit', 'Withdraw', 'Transfer']
            }
        }
    },
    'gmx': {
        'name': 'GMX',
        'category': 'perp',
        'networks': {
            'arbitrum': {
                'subgraph': 'gmx-io/gmx-stats',
                'contracts': ['0x489ee077994B6658eAfA855C308275EAd8097C4A'],  # GLP Manager
                'events': ['AddLiquidity', 'RemoveLiquidity', 'IncreasePosition', 'DecreasePosition']
            },
            'avalanche': {
                'subgraph': 'gmx-io/gmx-avalanche-stats',
                'contracts': ['0xe1ae4d4b06A5Fe1fc288f6B4CD72f9F8323B107F'],
                'events': ['AddLiquidity', 'RemoveLiquidity']
            }
        }
    },
    'convex': {
        'name': 'Convex Finance',
        'category': 'yield',
        'networks': {
            'ethereum': {
                'subgraph': 'convex-community/convex',
                'contracts': ['0xF403C135812408BFbE8713b5A23a04b3D48AAE31'],  # Booster
                'events': ['Deposited', 'Withdrawn', 'Staked']
            }
        }
    },
    'balancer-v2': {
        'name': 'Balancer V2',
        'category': 'dex',
        'networks': {
            'ethereum': {
                'subgraph': 'balancer-labs/balancer-v2',
                'contracts': ['0xBA12222222228d8Ba445958a75a0704d566BF2C8'],  # Vault
                'events': ['PoolBalanceChanged', 'Swap', 'InternalBalanceChanged']
            },
            'arbitrum': {
                'subgraph': 'balancer-labs/balancer-arbitrum-v2',
                'contracts': ['0xBA12222222228d8Ba445958a75a0704d566BF2C8'],
                'events': ['PoolBalanceChanged', 'Swap']
            },
            'polygon': {
                'subgraph': 'balancer-labs/balancer-polygon-v2',
                'contracts': ['0xBA12222222228d8Ba445958a75a0704d566BF2C8'],
                'events': ['PoolBalanceChanged', 'Swap']
            }
        }
    },
    'sushiswap': {
        'name': 'SushiSwap',
        'category': 'dex',
        'networks': {
            'ethereum': {
                'subgraph': 'sushi-v2/sushiswap-ethereum',
                'contracts': ['0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac'],  # Factory
                'events': ['PairCreated', 'Mint', 'Burn', 'Swap']
            },
            'arbitrum': {
                'subgraph': 'sushiswap/exchange-arbitrum',
                'contracts': ['0xc35DADB65012eC5796536bD9864eD8773aBc74C4'],
                'events': ['PairCreated', 'Mint', 'Burn']
            },
            'polygon': {
                'subgraph': 'sushiswap/matic-exchange',
                'contracts': ['0xc35DADB65012eC5796536bD9864eD8773aBc74C4'],
                'events': ['PairCreated', 'Mint', 'Burn']
            }
        }
    },
    'rocket-pool': {
        'name': 'Rocket Pool',
        'category': 'staking',
        'networks': {
            'ethereum': {
                'subgraph': 'rocket-pool/rocketpool',
                'contracts': ['0xae78736Cd615f374D3085123A210448E74Fc6393'],  # rETH
                'events': ['Transfer', 'TokensMinted', 'TokensBurned']
            }
        }
    },
    'frax': {
        'name': 'Frax Finance',
        'category': 'stablecoin',
        'networks': {
            'ethereum': {
                'subgraph': 'frax-finance/frax',
                'contracts': ['0xac3E018457B222d93114458476f3E3416Abbe38F'],  # sfrxETH
                'events': ['Deposit', 'Withdraw', 'Transfer']
            }
        }
    }
}

# Critical events for position tracking
POSITION_EVENTS = {
    'lending': ['Supply', 'Deposit', 'Mint', 'Withdraw', 'Redeem', 'Borrow', 'Repay', 'LiquidationCall'],
    'dex': ['Mint', 'Burn', 'AddLiquidity', 'RemoveLiquidity', 'PairCreated', 'PoolCreated'],
    'staking': ['Stake', 'Unstake', 'Deposit', 'Withdraw', 'Submitted', 'Transfer'],
    'vault': ['Deposit', 'Withdraw', 'Transfer'],
    'yield': ['Deposited', 'Withdrawn', 'Staked', 'Claimed'],
    'perp': ['IncreasePosition', 'DecreasePosition', 'AddLiquidity', 'RemoveLiquidity']
}

@dataclass
class ContractConfig:
    name: str
    address: str
    abi_path: str
    events: List[str]
    start_block: Optional[int] = None

@dataclass
class NetworkConfig:
    name: str
    chain_id: int
    rpc_url: str
    contracts: List[ContractConfig]

class DefiIndexerGenerator:
    def __init__(self):
        self.protocols = TOP_DEFI_PROTOCOLS
        self.abis_cache = {}
        self.rate_limit_delay = 0.2  # 200ms between API calls
        
        # Create output directories
        os.makedirs(ABIS_DIR, exist_ok=True)
        
    def fetch_abi_from_explorer(self, address: str, network: str) -> Optional[Dict]:
        """Fetch ABI from block explorer API"""
        explorer = EXPLORERS.get(network)
        if not explorer:
            print(f"⚠️  No explorer configured for {network}")
            return None
            
        api_key = os.getenv(explorer['key_env'], '')
        if not api_key:
            print(f"⚠️  No API key for {network} (set {explorer['key_env']})")
            # Try without API key (limited rate)
            api_key = ''
        
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
                print(f"✅ Fetched ABI for {address[:10]}... on {network}")
                return abi
            else:
                print(f"❌ Failed to fetch ABI for {address} on {network}: {data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching ABI for {address} on {network}: {e}")
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
    
    def save_abi(self, abi: List[Dict], protocol: str, network: str, contract_addr: str):
        """Save ABI to file"""
        filename = f"{ABIS_DIR}/{protocol}_{network}_{contract_addr[:10]}.json"
        
        with open(filename, 'w') as f:
            json.dump(abi, f, indent=2)
        
        return filename
    
    def generate_rindexer_config(self) -> Dict:
        """Generate complete rindexer.yaml configuration"""
        config = {
            'name': 'defi_positions_indexer',
            'description': 'Auto-generated DeFi positions indexer from The Graph subgraphs',
            'project_type': 'no-code',
            'networks': [],
            'storage': {
                'postgres': {
                    'enabled': True
                }
            },
            'global_contracts': []
        }
        
        # Group by network
        networks_data = defaultdict(lambda: {
            'contracts': [],
            'rpc_url': ''
        })
        
        print("\n🔍 Processing protocols...")
        
        for protocol_id, protocol_data in self.protocols.items():
            protocol_name = protocol_data['name']
            category = protocol_data['category']
            
            print(f"\n📦 Processing {protocol_name} ({category})")
            
            for network, network_data in protocol_data['networks'].items():
                if network not in EXPLORERS:
                    continue
                
                contracts = network_data.get('contracts', [])
                events = network_data.get('events', POSITION_EVENTS.get(category, []))
                
                for contract_addr in contracts:
                    print(f"  📍 {network}: {contract_addr[:10]}...")
                    
                    # Fetch ABI
                    abi = self.fetch_abi_from_explorer(contract_addr, network)
                    
                    if abi:
                        # Create minimal ABI with only required events
                        minimal_abi = self.create_minimal_abi(abi, events)
                        
                        if minimal_abi:
                            # Save ABI
                            abi_path = self.save_abi(minimal_abi, protocol_id, network, contract_addr)
                            found_events = self.filter_events_from_abi(abi, events)
                            
                            # Add to network contracts
                            contract_config = {
                                'name': f"{protocol_id}_{network}",
                                'address': contract_addr,
                                'abi': abi_path.replace(f"{OUTPUT_DIR}/", "./"),
                                'events': found_events,
                                'start_block': 'latest'
                            }
                            
                            networks_data[network]['contracts'].append(contract_config)
                            
                            print(f"    ✅ Added {len(found_events)} events: {', '.join(found_events)}")
                        else:
                            print(f"    ⚠️  No matching events found in ABI")
                    else:
                        print(f"    ⚠️  Could not fetch ABI, skipping")
        
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
        """Generate .env.example with required variables"""
        env_file = f"{OUTPUT_DIR}/.env.example"
        
        lines = [
            "# Block Explorer API Keys (optional but recommended)",
            ""
        ]
        
        for network in networks:
            if network in EXPLORERS:
                key_name = EXPLORERS[network]['key_env']
                lines.append(f"{key_name}=your_api_key_here")
        
        lines.extend([
            "",
            "# RPC URLs",
            ""
        ])
        
        rpc_defaults = {
            'ethereum': 'https://eth.llamarpc.com',
            'arbitrum': 'https://arb1.arbitrum.io/rpc',
            'polygon': 'https://polygon-rpc.com',
            'avalanche': 'https://api.avax.network/ext/bc/C/rpc',
            'bsc': 'https://bsc-dataseed1.binance.org',
            'optimism': 'https://mainnet.optimism.io'
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
    
    def generate_readme(self):
        """Generate README with usage instructions"""
        readme = f"""# DeFi Positions Indexer

Auto-generated configuration for indexing DeFi positions across multiple chains using rindexer.

## 📊 Indexed Protocols

{self._generate_protocol_list()}

## 🚀 Quick Start

### 1. Install rindexer

```bash
cargo install rindexer
```

### 2. Set up environment

```bash
cp .env.example .env
# Edit .env with your API keys and RPC URLs
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
├── .env.example           # Environment template
└── README.md              # This file
```

## 🔧 Configuration

The `rindexer.yaml` file contains:
- **Networks**: {', '.join([n for n in EXPLORERS.keys()])}
- **Protocols**: {len(self.protocols)} DeFi protocols
- **Events**: Only critical position-tracking events (no bloat)

## 📝 Tracked Events

### Lending (Aave, Compound)
- Supply, Withdraw, Borrow, Repay, LiquidationCall

### DEX (Uniswap, Curve, Balancer, SushiSwap)
- Mint, Burn, AddLiquidity, RemoveLiquidity, Swap

### Staking (Lido, Rocket Pool)
- Stake, Unstake, Deposit, Withdraw, Transfer

### Vaults (Yearn)
- Deposit, Withdraw, Transfer

### Yield (Convex)
- Deposited, Withdrawn, Staked, Claimed

## 🔄 Regenerating

To regenerate with updated protocols:

```bash
python defi_indexer_generator.py
```

## 📚 Resources

- [rindexer Documentation](https://rindexer.xyz)
- [The Graph Explorer](https://thegraph.com/explorer)
- [Block Explorer APIs](https://docs.etherscan.io/api-endpoints)

## ⚠️ Notes

- Start blocks are set to 'latest' - adjust for historical indexing
- ABIs are minimal (events only) to reduce size
- Rate limits apply to free-tier block explorer APIs
- Some protocols may require additional configuration

Generated by DeFi Indexer Generator
"""
        
        with open(f"{OUTPUT_DIR}/README.md", 'w') as f:
            f.write(readme)
        
        print(f"✅ Generated {OUTPUT_DIR}/README.md")
    
    def _generate_protocol_list(self) -> str:
        """Generate markdown list of protocols"""
        lines = []
        
        by_category = defaultdict(list)
        for protocol_id, data in self.protocols.items():
            by_category[data['category']].append(data['name'])
        
        for category, protocols in sorted(by_category.items()):
            lines.append(f"### {category.title()}")
            for protocol in sorted(protocols):
                lines.append(f"- {protocol}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def run(self):
        """Main execution"""
        print("=" * 70)
        print("🚀 DeFi Indexer Generator")
        print("=" * 70)
        print(f"\n📦 Protocols to process: {len(self.protocols)}")
        print(f"🌐 Networks: {', '.join(EXPLORERS.keys())}")
        print(f"📁 Output directory: {OUTPUT_DIR}")
        
        # Generate configuration
        config = self.generate_rindexer_config()
        
        # Save rindexer.yaml
        self.save_rindexer_yaml(config)
        
        # Generate supporting files
        networks = [net['name'] for net in config['networks']]
        self.generate_env_template(networks)
        self.generate_readme()
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ Generation Complete!")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"  - Networks configured: {len(config['networks'])}")
        print(f"  - Total contracts: {sum(len(n['contracts']) for n in config['networks'])}")
        print(f"  - ABIs generated: {len(os.listdir(ABIS_DIR))}")
        print(f"\n📁 Output: {OUTPUT_DIR}/")
        print(f"\n🚀 Next steps:")
        print(f"  1. cd {OUTPUT_DIR}")
        print(f"  2. cp .env.example .env")
        print(f"  3. Edit .env with your API keys")
        print(f"  4. rindexer start all")
        print("\n" + "=" * 70)

if __name__ == "__main__":
    generator = DefiIndexerGenerator()
    generator.run()
