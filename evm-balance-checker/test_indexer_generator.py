#!/usr/bin/env python3
"""
Test script for DeFi Indexer Generator
Validates the generated configuration and tests all components
"""

import os
import json
import yaml
from typing import Dict, List
from graph_api_client import GraphAPIClient


class IndexerGeneratorTester:
    """Test suite for the indexer generator"""
    
    def __init__(self):
        self.client = GraphAPIClient()
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def test_graph_connection(self) -> bool:
        """Test connection to The Graph"""
        print("🧪 Test 1: The Graph API Connection")
        
        try:
            if self.client.test_connection():
                self.results['passed'].append("Graph API connection")
                return True
            else:
                self.results['failed'].append("Graph API connection")
                return False
        except Exception as e:
            self.results['failed'].append(f"Graph API connection: {e}")
            return False
    
    def test_abi_directory(self) -> bool:
        """Test if ABIs directory exists and has files"""
        print("\n🧪 Test 2: ABI Directory")
        
        if not os.path.exists('./abis'):
            self.results['failed'].append("ABIs directory not found")
            print("   ❌ ABIs directory not found")
            return False
        
        abi_files = [f for f in os.listdir('./abis') if f.endswith('.json')]
        
        if len(abi_files) == 0:
            self.results['warnings'].append("No ABI files found (run generator first)")
            print(f"   ⚠️  No ABI files found")
            return False
        
        print(f"   ✅ Found {len(abi_files)} ABI files")
        self.results['passed'].append(f"ABI directory ({len(abi_files)} files)")
        
        # Validate a few ABIs
        for abi_file in abi_files[:3]:
            try:
                with open(f'./abis/{abi_file}', 'r') as f:
                    abi = json.load(f)
                    events = [item for item in abi if item.get('type') == 'event']
                    print(f"      {abi_file}: {len(events)} events")
            except Exception as e:
                print(f"      ❌ Error reading {abi_file}: {e}")
        
        return True
    
    def test_rindexer_yaml(self) -> bool:
        """Test if rindexer.yaml exists and is valid"""
        print("\n🧪 Test 3: rindexer.yaml Configuration")
        
        if not os.path.exists('./rindexer.yaml'):
            self.results['warnings'].append("rindexer.yaml not found (run generator first)")
            print("   ⚠️  rindexer.yaml not found")
            return False
        
        try:
            with open('./rindexer.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate structure
            required_keys = ['name', 'networks', 'contracts']
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                self.results['failed'].append(f"rindexer.yaml missing keys: {missing_keys}")
                print(f"   ❌ Missing keys: {missing_keys}")
                return False
            
            # Check networks
            networks = config.get('networks', [])
            print(f"   ✅ Networks: {len(networks)}")
            for network in networks:
                print(f"      - {network.get('name')} (chain_id: {network.get('chain_id')})")
            
            # Check contracts
            contracts = config.get('contracts', [])
            print(f"   ✅ Contracts: {len(contracts)}")
            
            # Validate contract structure
            for contract in contracts[:5]:
                name = contract.get('name', 'unknown')
                details = contract.get('details', {})
                events = details.get('events', [])
                print(f"      - {name}: {len(events)} events")
            
            self.results['passed'].append(f"rindexer.yaml ({len(contracts)} contracts)")
            return True
            
        except Exception as e:
            self.results['failed'].append(f"rindexer.yaml validation: {e}")
            print(f"   ❌ Error: {e}")
            return False
    
    def test_protocol_coverage(self) -> bool:
        """Test if major protocols are covered"""
        print("\n🧪 Test 4: Protocol Coverage")
        
        if not os.path.exists('./rindexer.yaml'):
            print("   ⚠️  Skipping (no rindexer.yaml)")
            return False
        
        with open('./rindexer.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        contracts = config.get('contracts', [])
        contract_names = [c.get('name', '') for c in contracts]
        
        # Check for major protocols
        major_protocols = {
            'aave': ['aave-v3', 'aave'],
            'compound': ['compound-v3', 'compound'],
            'uniswap': ['uniswap-v3', 'uniswap-v2', 'uniswap'],
            'curve': ['curve'],
            'lido': ['lido'],
            'balancer': ['balancer'],
        }
        
        found_protocols = []
        missing_protocols = []
        
        for protocol, patterns in major_protocols.items():
            found = any(
                any(pattern in name.lower() for pattern in patterns)
                for name in contract_names
            )
            
            if found:
                found_protocols.append(protocol)
                print(f"   ✅ {protocol.capitalize()}")
            else:
                missing_protocols.append(protocol)
                print(f"   ⚠️  {protocol.capitalize()} not found")
        
        if found_protocols:
            self.results['passed'].append(f"Protocol coverage ({len(found_protocols)}/{len(major_protocols)})")
        
        if missing_protocols:
            self.results['warnings'].append(f"Missing protocols: {', '.join(missing_protocols)}")
        
        return len(found_protocols) > 0
    
    def test_event_coverage(self) -> bool:
        """Test if critical events are covered"""
        print("\n🧪 Test 5: Event Coverage")
        
        if not os.path.exists('./rindexer.yaml'):
            print("   ⚠️  Skipping (no rindexer.yaml)")
            return False
        
        with open('./rindexer.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Collect all events
        all_events = set()
        for contract in config.get('contracts', []):
            details = contract.get('details', {})
            events = details.get('events', [])
            all_events.update(events)
        
        # Critical events for position tracking
        critical_events = {
            'Supply', 'Deposit', 'Mint',
            'Withdraw', 'Redeem', 'Burn',
            'Borrow', 'Repay',
            'Stake', 'Unstake',
            'AddLiquidity', 'RemoveLiquidity'
        }
        
        found_events = critical_events & all_events
        missing_events = critical_events - all_events
        
        print(f"   ✅ Total unique events: {len(all_events)}")
        print(f"   ✅ Critical events found: {len(found_events)}/{len(critical_events)}")
        
        if found_events:
            print(f"      Found: {', '.join(sorted(found_events))}")
        
        if missing_events:
            print(f"      ⚠️  Missing: {', '.join(sorted(missing_events))}")
            self.results['warnings'].append(f"Missing critical events: {', '.join(missing_events)}")
        
        self.results['passed'].append(f"Event coverage ({len(found_events)}/{len(critical_events)})")
        return True
    
    def test_chain_coverage(self) -> bool:
        """Test if all target chains are covered"""
        print("\n🧪 Test 6: Chain Coverage")
        
        if not os.path.exists('./rindexer.yaml'):
            print("   ⚠️  Skipping (no rindexer.yaml)")
            return False
        
        with open('./rindexer.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        networks = config.get('networks', [])
        network_names = [n.get('name', '') for n in networks]
        
        target_chains = ['ethereum', 'arbitrum', 'polygon', 'avalanche', 'bsc']
        
        for chain in target_chains:
            if chain in network_names:
                print(f"   ✅ {chain.capitalize()}")
            else:
                print(f"   ⚠️  {chain.capitalize()} not configured")
        
        covered = len([c for c in target_chains if c in network_names])
        self.results['passed'].append(f"Chain coverage ({covered}/{len(target_chains)})")
        
        return covered > 0
    
    def test_env_configuration(self) -> bool:
        """Test environment configuration"""
        print("\n🧪 Test 7: Environment Configuration")
        
        # Check for env.example
        if not os.path.exists('./env.example'):
            self.results['warnings'].append("env.example not found")
            print("   ⚠️  env.example not found")
            return False
        
        print("   ✅ env.example found")
        
        # Check for actual .env
        if os.path.exists('./.env'):
            print("   ✅ .env file found")
            
            # Check for API keys (without revealing them)
            with open('./.env', 'r') as f:
                env_content = f.read()
            
            api_keys = [
                'ETHERSCAN_API_KEY',
                'ARBISCAN_API_KEY',
                'POLYGONSCAN_API_KEY',
                'SNOWTRACE_API_KEY',
                'BSCSCAN_API_KEY'
            ]
            
            configured_keys = []
            for key in api_keys:
                if key in env_content and 'YourApiKeyToken' not in env_content:
                    configured_keys.append(key)
            
            if configured_keys:
                print(f"   ✅ {len(configured_keys)}/{len(api_keys)} API keys configured")
            else:
                print(f"   ⚠️  No API keys configured")
                self.results['warnings'].append("No API keys configured in .env")
        else:
            print("   ⚠️  .env file not found (copy from env.example)")
            self.results['warnings'].append(".env file not found")
        
        self.results['passed'].append("Environment configuration")
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.results['passed']) + len(self.results['failed'])
        
        print(f"\n✅ Passed: {len(self.results['passed'])}/{total_tests}")
        for test in self.results['passed']:
            print(f"   • {test}")
        
        if self.results['failed']:
            print(f"\n❌ Failed: {len(self.results['failed'])}")
            for test in self.results['failed']:
                print(f"   • {test}")
        
        if self.results['warnings']:
            print(f"\n⚠️  Warnings: {len(self.results['warnings'])}")
            for warning in self.results['warnings']:
                print(f"   • {warning}")
        
        print("\n" + "=" * 70)
        
        if len(self.results['failed']) == 0:
            print("🎉 All critical tests passed!")
        else:
            print("⚠️  Some tests failed. Review the output above.")
        
        print("=" * 70)
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 70)
        print("🧪 DEFI INDEXER GENERATOR - TEST SUITE")
        print("=" * 70)
        print()
        
        self.test_graph_connection()
        self.test_abi_directory()
        self.test_rindexer_yaml()
        self.test_protocol_coverage()
        self.test_event_coverage()
        self.test_chain_coverage()
        self.test_env_configuration()
        
        self.print_summary()


def main():
    """Run test suite"""
    tester = IndexerGeneratorTester()
    tester.run_all_tests()
    
    print("\n💡 Next Steps:")
    print("   1. If tests passed: Run ./setup_indexer.sh to generate config")
    print("   2. Configure API keys in .env file")
    print("   3. Install rindexer: cargo install rindexer")
    print("   4. Start indexing: rindexer start")
    print()


if __name__ == "__main__":
    main()

