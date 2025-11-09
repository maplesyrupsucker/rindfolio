#!/usr/bin/env python3
"""
The Graph API Client - Query subgraphs to discover protocols and contracts
"""

import requests
import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SubgraphInfo:
    """Information about a subgraph"""
    id: str
    name: str
    display_name: str
    description: str
    network: str
    contracts: List[str]
    events: List[str]


class GraphAPIClient:
    """Client for querying The Graph API"""
    
    # The Graph's decentralized network endpoint
    GRAPH_NETWORK_URL = "https://api.thegraph.com/subgraphs/name/graphprotocol/graph-network-mainnet"
    
    # Hosted service endpoint (being deprecated but still useful)
    HOSTED_SERVICE_URL = "https://api.thegraph.com/index-node/graphql"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
        })
    
    def query_subgraph(self, subgraph_name: str, query: str) -> Optional[Dict]:
        """Query a specific subgraph"""
        url = f"https://api.thegraph.com/subgraphs/name/{subgraph_name}"
        
        try:
            response = self.session.post(
                url,
                json={'query': query},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error querying {subgraph_name}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception querying {subgraph_name}: {e}")
            return None
    
    def get_protocol_contracts(self, subgraph_name: str, protocol_type: str) -> List[str]:
        """Get contract addresses from a subgraph"""
        
        # Different protocols have different schemas
        queries = {
            'aave': '''
            {
                pools(first: 100) {
                    id
                }
            }
            ''',
            'compound': '''
            {
                markets(first: 100) {
                    id
                }
            }
            ''',
            'uniswap': '''
            {
                factories(first: 10) {
                    id
                }
                pools(first: 100) {
                    id
                }
            }
            ''',
            'curve': '''
            {
                pools(first: 100) {
                    id
                    address
                }
            }
            ''',
            'balancer': '''
            {
                pools(first: 100) {
                    id
                    address
                }
            }
            ''',
            'yearn': '''
            {
                vaults(first: 100) {
                    id
                }
            }
            ''',
            'lido': '''
            {
                totalRewards(first: 1) {
                    id
                }
            }
            ''',
            'sushiswap': '''
            {
                factories(first: 10) {
                    id
                }
            }
            '''
        }
        
        query = queries.get(protocol_type, queries['uniswap'])
        result = self.query_subgraph(subgraph_name, query)
        
        if not result or 'data' not in result:
            return []
        
        # Extract addresses from response
        addresses = []
        data = result['data']
        
        for key in data:
            if isinstance(data[key], list):
                for item in data[key]:
                    if 'id' in item:
                        addresses.append(item['id'])
                    elif 'address' in item:
                        addresses.append(item['address'])
        
        return addresses
    
    def get_aave_v3_contracts(self, chain: str) -> Dict[str, str]:
        """Get Aave V3 contract addresses for a chain"""
        
        # Aave V3 Pool addresses (verified)
        pools = {
            'ethereum': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
            'arbitrum': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
            'polygon': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
            'avalanche': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
        }
        
        # Query subgraph for aTokens
        subgraph_names = {
            'ethereum': 'aave/protocol-v3',
            'arbitrum': 'aave/protocol-v3-arbitrum',
            'polygon': 'aave/protocol-v3-polygon',
            'avalanche': 'aave/protocol-v3-avalanche',
        }
        
        subgraph = subgraph_names.get(chain)
        if not subgraph:
            return {}
        
        query = '''
        {
            reserves(first: 100) {
                id
                name
                symbol
                aToken {
                    id
                }
            }
        }
        '''
        
        result = self.query_subgraph(subgraph, query)
        
        contracts = {
            'pool': pools.get(chain, '')
        }
        
        if result and 'data' in result and 'reserves' in result['data']:
            for reserve in result['data']['reserves']:
                if reserve.get('aToken'):
                    symbol = reserve.get('symbol', 'UNKNOWN')
                    contracts[f"aToken_{symbol}"] = reserve['aToken']['id']
        
        return contracts
    
    def get_uniswap_v3_contracts(self, chain: str) -> Dict[str, str]:
        """Get Uniswap V3 contract addresses"""
        
        # Core contracts
        contracts = {
            'ethereum': {
                'factory': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
                'position_manager': '0xC36442b4a4522E871399CD717aBDD847Ab11FE88',
                'router': '0xE592427A0AEce92De3Edee1F18E0157C05861564'
            },
            'arbitrum': {
                'factory': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
                'position_manager': '0xC36442b4a4522E871399CD717aBDD847Ab11FE88',
                'router': '0xE592427A0AEce92De3Edee1F18E0157C05861564'
            },
            'polygon': {
                'factory': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
                'position_manager': '0xC36442b4a4522E871399CD717aBDD847Ab11FE88',
                'router': '0xE592427A0AEce92De3Edee1F18E0157C05861564'
            }
        }
        
        return contracts.get(chain, {})
    
    def get_compound_v3_contracts(self, chain: str) -> Dict[str, str]:
        """Get Compound V3 contract addresses"""
        
        contracts = {
            'ethereum': {
                'cUSDCv3': '0xc3d688B66703497DAA19211EEdff47f25384cdc3',
                'cWETHv3': '0xA17581A9E3356d9A858b789D68B4d866e593aE94',
            },
            'arbitrum': {
                'cUSDCv3': '0xA5EDBDD9646f8dFF606d7448e414884C7d905dCA',
                'cUSDC.ev3': '0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf',
            },
            'polygon': {
                'cUSDCv3': '0xF25212E676D1F7F89Cd72fFEe66158f541246445',
            }
        }
        
        return contracts.get(chain, {})
    
    def get_curve_contracts(self, chain: str) -> List[str]:
        """Get Curve pool addresses"""
        
        # Major Curve pools
        pools = {
            'ethereum': [
                '0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7',  # 3pool
                '0xDC24316b9AE028F1497c275EB9192a3Ea0f67022',  # stETH
                '0xD51a44d3FaE010294C616388b506AcdA1bfAAE46',  # tricrypto2
            ],
            'arbitrum': [
                '0x7f90122BF0700F9E7e1F688fe926940E8839F353',  # 2pool
                '0x960ea3e3C7FB317332d990873d354E18d7645590',  # tricrypto
            ],
            'polygon': [
                '0x445FE580eF8d70FF569aB36e80c647af338db351',  # aave pool
                '0x92577943c7aC4accb35288aB2CC84D75feC330aF',  # atricrypto3
            ]
        }
        
        return pools.get(chain, [])
    
    def test_connection(self) -> bool:
        """Test connection to The Graph"""
        query = '''
        {
            _meta {
                block {
                    number
                }
            }
        }
        '''
        
        result = self.query_subgraph('uniswap/uniswap-v3', query)
        
        if result and 'data' in result:
            print("✅ Successfully connected to The Graph")
            return True
        else:
            print("❌ Failed to connect to The Graph")
            return False


def main():
    """Test the Graph API client"""
    print("🧪 Testing The Graph API Client\n")
    
    client = GraphAPIClient()
    
    # Test connection
    print("1️⃣ Testing connection...")
    client.test_connection()
    print()
    
    # Test Aave V3
    print("2️⃣ Fetching Aave V3 contracts...")
    for chain in ['ethereum', 'arbitrum', 'polygon']:
        contracts = client.get_aave_v3_contracts(chain)
        print(f"   {chain}: {len(contracts)} contracts")
        if contracts:
            print(f"      Pool: {contracts.get('pool', 'N/A')}")
    print()
    
    # Test Uniswap V3
    print("3️⃣ Fetching Uniswap V3 contracts...")
    for chain in ['ethereum', 'arbitrum', 'polygon']:
        contracts = client.get_uniswap_v3_contracts(chain)
        print(f"   {chain}: {len(contracts)} contracts")
        if contracts:
            print(f"      Factory: {contracts.get('factory', 'N/A')}")
    print()
    
    # Test Compound V3
    print("4️⃣ Fetching Compound V3 contracts...")
    for chain in ['ethereum', 'arbitrum', 'polygon']:
        contracts = client.get_compound_v3_contracts(chain)
        print(f"   {chain}: {len(contracts)} contracts")
    print()
    
    # Test Curve
    print("5️⃣ Fetching Curve contracts...")
    for chain in ['ethereum', 'arbitrum', 'polygon']:
        pools = client.get_curve_contracts(chain)
        print(f"   {chain}: {len(pools)} pools")
    print()
    
    print("✅ All tests complete!")


if __name__ == "__main__":
    main()

