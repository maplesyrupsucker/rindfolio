#!/usr/bin/env python3
"""
Demo script - Test the DeFi Indexer Generator without API keys
Generates a sample rindexer.yaml with mock data
"""

import json
import yaml
from pathlib import Path

def create_mock_abi(protocol: str, events: list) -> dict:
    """Create a mock ABI with specified events"""
    abi = []
    for event in events:
        abi.append({
            "type": "event",
            "name": event,
            "inputs": [
                {"name": "user", "type": "address", "indexed": True},
                {"name": "amount", "type": "uint256", "indexed": False}
            ],
            "anonymous": False
        })
    return abi

def generate_demo_config():
    """Generate a demo rindexer.yaml without API calls"""
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     🎬 DeFi Indexer Generator - DEMO MODE 🎬                  ║
║                                                                ║
║  Generating sample config without API keys                    ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Create abis directory
    abis_dir = Path('./abis')
    abis_dir.mkdir(exist_ok=True)
    
    # Demo protocols
    protocols = {
        'aave-v3': {
            'name': 'Aave V3',
            'category': 'lending',
            'events': ['Supply', 'Borrow', 'Withdraw', 'Repay', 'LiquidationCall'],
            'contracts': {
                'ethereum': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
                'arbitrum': '0x794a61358D6845594F94dc1DB02A252b5b4814aD'
            }
        },
        'uniswap-v3': {
            'name': 'Uniswap V3',
            'category': 'dex',
            'events': ['Mint', 'Burn', 'Collect', 'IncreaseLiquidity', 'DecreaseLiquidity'],
            'contracts': {
                'ethereum': '0xC36442b4a4522E871399CD717aBDD847Ab11FE88',
                'arbitrum': '0xC36442b4a4522E871399CD717aBDD847Ab11FE88'
            }
        },
        'lido': {
            'name': 'Lido',
            'category': 'staking',
            'events': ['Submitted', 'Transfer', 'SharesBurnt'],
            'contracts': {
                'ethereum': '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84'
            }
        }
    }
    
    # Generate mock ABIs
    print("\n📝 Generating mock ABIs...\n")
    for protocol_id, protocol in protocols.items():
        for chain, address in protocol['contracts'].items():
            abi = create_mock_abi(protocol_id, protocol['events'])
            abi_filename = f"{protocol_id}_{chain}.json"
            abi_path = abis_dir / abi_filename
            
            with open(abi_path, 'w') as f:
                json.dump(abi, f, indent=2)
            
            print(f"  ✓ Created {abi_filename} with {len(abi)} events")
    
    # Build rindexer config
    print("\n🔨 Building rindexer.yaml...\n")
    
    config = {
        'name': 'defi_positions_indexer',
        'description': 'Auto-generated DeFi positions indexer (DEMO)',
        'project_type': 'no-code',
        'networks': {
            'ethereum': {
                'chain_id': 1,
                'rpc': 'https://eth.llamarpc.com'
            },
            'arbitrum': {
                'chain_id': 42161,
                'rpc': 'https://arb1.arbitrum.io/rpc'
            }
        },
        'contracts': []
    }
    
    # Add contracts
    for protocol_id, protocol in protocols.items():
        for chain, address in protocol['contracts'].items():
            config['contracts'].append({
                'name': f"{protocol_id}_{chain}",
                'network': chain,
                'address': address,
                'abi': f"./abis/{protocol_id}_{chain}.json",
                'events': protocol['events'],
                'metadata': {
                    'protocol': protocol['name'],
                    'category': protocol['category']
                }
            })
    
    # Write YAML
    with open('rindexer.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    # Print summary
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     ✅ DEMO GENERATION COMPLETE ✅                            ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

📊 Summary:
  • Output: rindexer.yaml
  • Chains: {len(config['networks'])}
  • Contracts: {len(config['contracts'])}
  • Protocols: {len(protocols)}

📁 Files Created:
  • rindexer.yaml (main config)
  • abis/*.json ({len(config['contracts'])} files)

🎯 Next Steps:
  1. Review rindexer.yaml
  2. Get API keys for production use
  3. Run: python generate_rindexer.py

💡 This is a DEMO with mock ABIs. For production:
  • Add API keys to .env
  • Run generate_rindexer.py for real ABIs
  • Customize protocols in DEFI_PROTOCOLS

╚════════════════════════════════════════════════════════════════╝
    """)

if __name__ == '__main__':
    generate_demo_config()

