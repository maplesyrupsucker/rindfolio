#!/usr/bin/env python3
"""
Simple Demo of DeFi Indexer Generator
Shows basic functionality without requiring API keys
"""

import os
import json
import yaml
from pathlib import Path

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     🔥 DeFi Indexer Generator - Simple Demo                   ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")

# Define a simple protocol configuration
DEMO_PROTOCOLS = {
    'aave-v3': {
        'name': 'Aave V3',
        'category': 'lending',
        'events': ['Supply', 'Withdraw', 'Borrow', 'Repay', 'LiquidationCall'],
        'contracts': {
            'ethereum': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
            'arbitrum': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
            'polygon': '0x794a61358D6845594F94dc1DB02A252b5b4814aD'
        }
    },
    'uniswap-v3': {
        'name': 'Uniswap V3',
        'category': 'dex',
        'events': ['Mint', 'Burn', 'Swap', 'IncreaseLiquidity', 'DecreaseLiquidity'],
        'contracts': {
            'ethereum': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
            'arbitrum': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
            'polygon': '0x1F98431c8aD98523631AE4a59f267346ea31F984'
        }
    },
    'curve': {
        'name': 'Curve Finance',
        'category': 'dex',
        'events': ['AddLiquidity', 'RemoveLiquidity', 'TokenExchange'],
        'contracts': {
            'ethereum': '0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5',
            'arbitrum': '0x445FE580eF8d70FF569aB36e80c647af338db351',
            'polygon': '0x094d12e5b541784701FD8d65F11fc0598FBC6332'
        }
    }
}

DEMO_CHAINS = {
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
    }
}

def generate_demo_config():
    """Generate a demo rindexer configuration"""
    
    print("🚀 Generating demo configuration...\n")
    
    networks = {}
    stats = {
        'total_contracts': 0,
        'total_events': 0,
        'contracts_by_chain': {},
        'protocols_by_category': {}
    }
    
    for protocol_id, protocol_data in DEMO_PROTOCOLS.items():
        print(f"📦 Processing {protocol_data['name']} ({protocol_data['category']})...")
        
        for chain, address in protocol_data['contracts'].items():
            if chain not in DEMO_CHAINS:
                continue
            
            # Initialize network if not exists
            if chain not in networks:
                networks[chain] = {
                    'chain_id': DEMO_CHAINS[chain]['chain_id'],
                    'rpc': DEMO_CHAINS[chain]['rpc'],
                    'contracts': []
                }
                stats['contracts_by_chain'][chain] = 0
            
            # Add contract
            networks[chain]['contracts'].append({
                'name': f"{protocol_data['name']}_{chain}",
                'address': address,
                'abi': f"./abis/{protocol_id}_{chain}.json",
                'category': protocol_data['category'],
                'events': protocol_data['events']
            })
            
            # Update stats
            stats['total_contracts'] += 1
            stats['contracts_by_chain'][chain] += 1
            stats['total_events'] += len(protocol_data['events'])
            
            category = protocol_data['category']
            stats['protocols_by_category'][category] = stats['protocols_by_category'].get(category, 0) + 1
            
            print(f"  ✅ Added {chain}: {address[:10]}... with {len(protocol_data['events'])} events")
    
    # Build final config
    config = {
        'name': 'defi_positions_indexer',
        'description': 'Auto-generated DeFi positions indexer (Demo)',
        'project_type': 'no-code',
        'networks': networks,
        'storage': {
            'postgres': {
                'enabled': True
            }
        },
        'global_contracts': [
            {
                'name': 'ERC20',
                'abi': './abis/erc20.json'
            }
        ]
    }
    
    return config, stats

def save_config(config, filename='demo_rindexer.yaml'):
    """Save configuration to YAML file"""
    
    output_dir = Path(__file__).parent
    filepath = output_dir / filename
    
    with open(filepath, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)
    
    print(f"\n✅ Generated {filepath}")
    return filepath

def print_stats(stats):
    """Print generation statistics"""
    
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║                     📊 GENERATION COMPLETE                     ║
╚════════════════════════════════════════════════════════════════╝

📈 Statistics:
  • Total Networks: {len(stats['contracts_by_chain'])}
  • Total Contracts: {stats['total_contracts']}
  • Total Events: {stats['total_events']}

🌐 Contracts by Network:""")
    
    for network, count in stats['contracts_by_chain'].items():
        print(f"  • {network}: {count} contracts")
    
    print(f"\n📦 Protocols by Category:")
    for category, count in stats['protocols_by_category'].items():
        print(f"  • {category}: {count} contracts")

def create_demo_abi():
    """Create a demo ERC20 ABI file"""
    
    erc20_abi = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "from", "type": "address"},
                {"indexed": True, "name": "to", "type": "address"},
                {"indexed": False, "name": "value", "type": "uint256"}
            ],
            "name": "Transfer",
            "type": "event"
        }
    ]
    
    abis_dir = Path(__file__).parent / 'abis'
    abis_dir.mkdir(exist_ok=True)
    
    abi_path = abis_dir / 'erc20.json'
    with open(abi_path, 'w') as f:
        json.dump(erc20_abi, f, indent=2)
    
    print(f"\n📝 Created demo ERC20 ABI: {abi_path}")

def main():
    """Main demo function"""
    
    # Generate configuration
    config, stats = generate_demo_config()
    
    # Save to file
    filepath = save_config(config)
    
    # Create demo ABI
    create_demo_abi()
    
    # Print statistics
    print_stats(stats)
    
    print(f"""
📁 Output Files:
  • Configuration: {filepath}
  • ABIs Directory: ./abis/
  
🚀 Next Steps:
  1. Review the generated demo_rindexer.yaml
  2. To generate with real ABIs, use: python generate_rindexer.py
  3. Set ETHERSCAN_API_KEY for ABI fetching
  4. Run: rindexer start

💡 This demo shows the structure without requiring API keys!
    """)

if __name__ == "__main__":
    main()

