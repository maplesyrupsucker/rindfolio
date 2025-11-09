#!/usr/bin/env python3
"""
Advanced DeFi Indexer Generator - Auto-discover protocols from The Graph
Uses The Graph Network subgraph to find top DeFi protocols dynamically
"""

import os
import json
import requests
import yaml
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict
import time
from pathlib import Path

# The Graph Network API
GRAPH_NETWORK_API = "https://api.thegraph.com/subgraphs/name/graphprotocol/graph-network-mainnet"

# DeFi Llama API for TVL data
DEFILLAMA_API = "https://api.llama.fi/protocols"

# Chain mapping for The Graph
GRAPH_CHAIN_MAPPING = {
    'mainnet': 'ethereum',
    'arbitrum-one': 'arbitrum',
    'matic': 'polygon',
    'avalanche': 'avalanche',
    'bsc': 'bsc'
}

# Event patterns by category
EVENT_PATTERNS = {
    'lending': {
        'supply': ['Supply', 'Deposit', 'Mint'],
        'borrow': ['Borrow'],
        'withdraw': ['Withdraw', 'Redeem'],
        'repay': ['Repay', 'RepayBorrow'],
        'liquidation': ['LiquidationCall', 'Liquidate']
    },
    'dex': {
        'liquidity': ['Mint', 'Burn', 'AddLiquidity', 'RemoveLiquidity'],
        'swap': ['Swap', 'TokenExchange'],
        'position': ['IncreaseLiquidity', 'DecreaseLiquidity', 'Collect']
    },
    'staking': {
        'stake': ['Stake', 'Staked', 'Deposit'],
        'unstake': ['Unstake', 'Unstaked', 'Withdraw'],
        'reward': ['RewardPaid', 'Claimed']
    },
    'vault': {
        'deposit': ['Deposit'],
        'withdraw': ['Withdraw'],
        'harvest': ['Harvest', 'StrategyReported']
    }
}

@dataclass
class SubgraphInfo:
    """Information about a subgraph from The Graph"""
    id: str
    name: str
    display_name: str
    network: str
    signal_amount: float
    query_count: int
    categories: List[str]

class TheGraphDiscovery:
    """Discover DeFi protocols from The Graph Network"""
    
    def __init__(self):
        self.session = requests.Session()
        self.subgraphs = []
        
    def query_graph_network(self, query: str) -> Dict:
        """Query The Graph Network subgraph"""
        try:
            response = self.session.post(
                GRAPH_NETWORK_API,
                json={'query': query},
                timeout=30
            )
            return response.json()
        except Exception as e:
            print(f"  ✗ Error querying The Graph: {e}")
            return {}
    
    def discover_defi_subgraphs(self, min_signal: float = 1000, limit: int = 50) -> List[SubgraphInfo]:
        """
        Discover top DeFi subgraphs by signal amount
        Signal amount is a proxy for quality/importance
        """
        print(f"\n{'='*60}")
        print("🔍 Discovering DeFi Subgraphs from The Graph Network")
        print(f"{'='*60}\n")
        
        # Query for top subgraphs with DeFi-related names
        query = """
        {
          subgraphs(
            first: %d,
            orderBy: signalAmount,
            orderDirection: desc,
            where: {
              active: true,
              signalAmount_gt: "%d"
            }
          ) {
            id
            metadata {
              displayName
              description
              categories
            }
            currentVersion {
              subgraphDeployment {
                network {
                  id
                }
                signalAmount
                queryFeesAmount
                stakedTokens
              }
            }
            versions {
              id
            }
          }
        }
        """ % (limit, int(min_signal))
        
        result = self.query_graph_network(query)
        
        if not result.get('data', {}).get('subgraphs'):
            print("  ⚠ No subgraphs found or API error")
            return []
        
        subgraphs = []
        defi_keywords = ['aave', 'uniswap', 'curve', 'compound', 'lido', 'balancer', 
                         'sushi', 'yearn', 'convex', 'gmx', 'pancake', 'trader']
        
        for sg in result['data']['subgraphs']:
            metadata = sg.get('metadata', {})
            display_name = metadata.get('displayName', '').lower()
            
            # Filter for DeFi protocols
            if any(keyword in display_name for keyword in defi_keywords):
                current_version = sg.get('currentVersion', {})
                deployment = current_version.get('subgraphDeployment', {})
                network = deployment.get('network', {}).get('id', 'unknown')
                
                subgraph_info = SubgraphInfo(
                    id=sg['id'],
                    name=sg['id'].split('/')[-1] if '/' in sg['id'] else sg['id'],
                    display_name=metadata.get('displayName', 'Unknown'),
                    network=GRAPH_CHAIN_MAPPING.get(network, network),
                    signal_amount=float(deployment.get('signalAmount', 0)) / 1e18,
                    query_count=int(deployment.get('queryFeesAmount', 0)),
                    categories=metadata.get('categories', [])
                )
                
                subgraphs.append(subgraph_info)
                print(f"  ✓ Found: {subgraph_info.display_name} on {subgraph_info.network}")
                print(f"    Signal: {subgraph_info.signal_amount:.2f} GRT")
        
        print(f"\n  Total DeFi subgraphs discovered: {len(subgraphs)}")
        return subgraphs
    
    def get_subgraph_schema(self, subgraph_id: str) -> Optional[Dict]:
        """
        Fetch subgraph schema to extract entity types and events
        Note: This requires querying the subgraph's metadata endpoint
        """
        # In production, you would query the subgraph's introspection endpoint
        # For now, we'll use pattern matching based on protocol category
        return None
    
    def infer_protocol_category(self, display_name: str, categories: List[str]) -> str:
        """Infer protocol category from name and metadata"""
        name_lower = display_name.lower()
        
        if any(x in name_lower for x in ['aave', 'compound', 'radiant']):
            return 'lending'
        elif any(x in name_lower for x in ['uniswap', 'curve', 'balancer', 'sushi', 'pancake']):
            return 'dex'
        elif any(x in name_lower for x in ['lido', 'rocket', 'stake']):
            return 'staking'
        elif any(x in name_lower for x in ['yearn', 'vault']):
            return 'vault'
        elif any(x in name_lower for x in ['convex', 'beefy']):
            return 'yield'
        elif any(x in name_lower for x in ['gmx', 'perp', 'perpetual']):
            return 'perp'
        
        return 'unknown'
    
    def get_critical_events_for_category(self, category: str) -> List[str]:
        """Get critical events based on protocol category"""
        if category not in EVENT_PATTERNS:
            return []
        
        events = []
        for event_list in EVENT_PATTERNS[category].values():
            events.extend(event_list)
        
        return list(set(events))  # Remove duplicates

class DeFiLlamaIntegration:
    """Get protocol data from DeFi Llama"""
    
    def __init__(self):
        self.session = requests.Session()
        self.protocols = {}
        
    def fetch_top_protocols(self, min_tvl: float = 100_000_000, limit: int = 50) -> Dict:
        """Fetch top protocols by TVL"""
        print(f"\n{'='*60}")
        print("💰 Fetching Protocol Data from DeFi Llama")
        print(f"{'='*60}\n")
        
        try:
            response = self.session.get(DEFILLAMA_API, timeout=30)
            protocols = response.json()
            
            # Filter and sort by TVL
            top_protocols = [
                p for p in protocols 
                if p.get('tvl', 0) >= min_tvl and p.get('category') in ['Dexes', 'Lending', 'Liquid Staking', 'Yield']
            ]
            top_protocols.sort(key=lambda x: x.get('tvl', 0), reverse=True)
            top_protocols = top_protocols[:limit]
            
            for p in top_protocols:
                name = p.get('name', 'Unknown')
                tvl = p.get('tvl', 0)
                category = p.get('category', 'Unknown')
                chains = p.get('chains', [])
                
                self.protocols[name.lower()] = {
                    'name': name,
                    'tvl': tvl,
                    'category': category,
                    'chains': chains
                }
                
                print(f"  ✓ {name}: ${tvl/1e9:.2f}B TVL ({category})")
            
            print(f"\n  Total protocols: {len(self.protocols)}")
            return self.protocols
            
        except Exception as e:
            print(f"  ✗ Error fetching DeFi Llama data: {e}")
            return {}
    
    def match_protocol(self, subgraph_name: str) -> Optional[Dict]:
        """Match subgraph to DeFi Llama protocol"""
        name_lower = subgraph_name.lower()
        
        # Direct match
        if name_lower in self.protocols:
            return self.protocols[name_lower]
        
        # Partial match
        for protocol_name, protocol_data in self.protocols.items():
            if protocol_name in name_lower or name_lower in protocol_name:
                return protocol_data
        
        return None

class AdvancedRindexerGenerator:
    """Generate rindexer.yaml using auto-discovered protocols"""
    
    def __init__(self):
        self.graph_discovery = TheGraphDiscovery()
        self.defillama = DeFiLlamaIntegration()
        self.contracts_by_chain = defaultdict(list)
        
    def generate_from_discovery(self, output_path: str = 'rindexer_advanced.yaml'):
        """Generate rindexer.yaml from discovered protocols"""
        
        print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     🚀 Advanced DeFi Indexer Generator 🚀                     ║
║                                                                ║
║  Auto-discovering protocols from The Graph & DeFi Llama       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
        """)
        
        # Step 1: Fetch top protocols from DeFi Llama
        protocols = self.defillama.fetch_top_protocols(min_tvl=100_000_000, limit=30)
        
        # Step 2: Discover subgraphs from The Graph
        subgraphs = self.graph_discovery.discover_defi_subgraphs(min_signal=1000, limit=50)
        
        # Step 3: Match and enrich
        print(f"\n{'='*60}")
        print("🔗 Matching Subgraphs with Protocol Data")
        print(f"{'='*60}\n")
        
        matched_protocols = []
        for subgraph in subgraphs:
            protocol_data = self.defillama.match_protocol(subgraph.display_name)
            
            if protocol_data:
                category = self.graph_discovery.infer_protocol_category(
                    subgraph.display_name, 
                    subgraph.categories
                )
                
                events = self.graph_discovery.get_critical_events_for_category(category)
                
                matched_protocols.append({
                    'name': subgraph.display_name,
                    'subgraph_id': subgraph.id,
                    'network': subgraph.network,
                    'category': category,
                    'events': events,
                    'tvl': protocol_data['tvl'],
                    'signal': subgraph.signal_amount
                })
                
                print(f"  ✓ Matched: {subgraph.display_name}")
                print(f"    Category: {category}, TVL: ${protocol_data['tvl']/1e9:.2f}B")
                print(f"    Events: {', '.join(events[:3])}...")
        
        # Step 4: Generate YAML
        print(f"\n{'='*60}")
        print("📝 Generating rindexer.yaml")
        print(f"{'='*60}\n")
        
        config = {
            'name': 'defi_positions_indexer_advanced',
            'description': 'Auto-generated from The Graph Network & DeFi Llama',
            'project_type': 'no-code',
            'networks': {},
            'contracts': []
        }
        
        # Add networks
        networks_used = set()
        for protocol in matched_protocols:
            networks_used.add(protocol['network'])
        
        chain_configs = {
            'ethereum': {'chain_id': 1, 'rpc': 'https://eth.llamarpc.com'},
            'arbitrum': {'chain_id': 42161, 'rpc': 'https://arb1.arbitrum.io/rpc'},
            'polygon': {'chain_id': 137, 'rpc': 'https://polygon-rpc.com'},
            'avalanche': {'chain_id': 43114, 'rpc': 'https://api.avax.network/ext/bc/C/rpc'},
            'bsc': {'chain_id': 56, 'rpc': 'https://bsc-dataseed1.binance.org'}
        }
        
        for network in networks_used:
            if network in chain_configs:
                config['networks'][network] = chain_configs[network]
        
        # Add contracts (note: we don't have actual contract addresses from subgraph metadata)
        # In production, you would query each subgraph's schema to extract contract addresses
        for protocol in matched_protocols:
            config['contracts'].append({
                'name': protocol['name'].lower().replace(' ', '-'),
                'network': protocol['network'],
                'subgraph_id': protocol['subgraph_id'],
                'events': protocol['events'],
                'metadata': {
                    'protocol': protocol['name'],
                    'category': protocol['category'],
                    'tvl': protocol['tvl'],
                    'signal': protocol['signal']
                },
                'note': 'Contract addresses need to be extracted from subgraph schema'
            })
        
        # Write YAML
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        # Print summary
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     ✅ ADVANCED GENERATION COMPLETE ✅                        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

📊 Summary:
  • Output: {output_path}
  • Protocols Discovered: {len(matched_protocols)}
  • Chains: {len(config['networks'])}
  • Total TVL: ${sum(p['tvl'] for p in matched_protocols)/1e9:.2f}B

📁 Top Protocols by TVL:
        """)
        
        for protocol in sorted(matched_protocols, key=lambda x: x['tvl'], reverse=True)[:10]:
            print(f"  • {protocol['name']}: ${protocol['tvl']/1e9:.2f}B ({protocol['category']})")
        
        print(f"""
💡 Next Steps:
  1. Review {output_path}
  2. Extract contract addresses from subgraph schemas
  3. Download ABIs using generate_rindexer.py
  4. Start indexing!

⚠️  Note: This is a discovery tool. Contract addresses need to be
   extracted from each subgraph's schema or documentation.

╚════════════════════════════════════════════════════════════════╝
        """)

def main():
    """Main execution"""
    generator = AdvancedRindexerGenerator()
    generator.generate_from_discovery()

if __name__ == '__main__':
    main()

