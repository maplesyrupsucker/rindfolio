#!/usr/bin/env python3
"""
Test script for DeFi Indexer Generator
Validates generated configuration and ABIs
"""

import os
import json
import yaml
from generate_rindexer import RindexerGenerator, DEFI_PROTOCOLS, CHAINS

def test_abi_generation():
    """Test minimal ABI generation"""
    print("🧪 Testing ABI generation...")
    
    generator = RindexerGenerator(output_dir="./test_output")
    
    events = ['Supply', 'Withdraw', 'Borrow', 'Repay']
    abi = generator.generate_minimal_abi(events)
    
    assert len(abi) == len(events), f"Expected {len(events)} events, got {len(abi)}"
    
    for event in abi:
        assert event['type'] == 'event', "Invalid event type"
        assert 'name' in event, "Event missing name"
    
    print("✅ ABI generation test passed")
    return True

def test_event_extraction():
    """Test event extraction from ABI"""
    print("🧪 Testing event extraction...")
    
    generator = RindexerGenerator(output_dir="./test_output")
    
    sample_abi = [
        {'type': 'function', 'name': 'deposit'},
        {'type': 'event', 'name': 'Deposit'},
        {'type': 'event', 'name': 'Withdraw'},
        {'type': 'function', 'name': 'withdraw'}
    ]
    
    events = generator.extract_events_from_abi(sample_abi)
    
    assert len(events) == 2, f"Expected 2 events, got {len(events)}"
    assert 'Deposit' in events, "Missing Deposit event"
    assert 'Withdraw' in events, "Missing Withdraw event"
    
    print("✅ Event extraction test passed")
    return True

def test_yaml_structure():
    """Test generated YAML structure"""
    print("🧪 Testing YAML structure...")
    
    generator = RindexerGenerator(output_dir="./test_output")
    
    # Create minimal config
    config = {
        'name': 'test_indexer',
        'networks': {
            'ethereum': {
                'chain_id': 1,
                'rpc': 'https://eth.llamarpc.com',
                'contracts': [
                    {
                        'name': 'TestContract',
                        'address': '0x1234567890123456789012345678901234567890',
                        'abi': './abis/test.json',
                        'events': ['Transfer']
                    }
                ]
            }
        }
    }
    
    # Save and reload
    filepath = generator.save_yaml(config, filename="test_config.yaml")
    
    with open(filepath, 'r') as f:
        loaded = yaml.safe_load(f)
    
    assert loaded['name'] == 'test_indexer', "Name mismatch"
    assert 'ethereum' in loaded['networks'], "Ethereum network missing"
    assert len(loaded['networks']['ethereum']['contracts']) == 1, "Contract count mismatch"
    
    print("✅ YAML structure test passed")
    
    # Cleanup
    os.remove(filepath)
    
    return True

def test_protocol_coverage():
    """Test protocol and chain coverage"""
    print("🧪 Testing protocol coverage...")
    
    total_protocols = len(DEFI_PROTOCOLS)
    total_chains = len(CHAINS)
    
    print(f"  📦 Protocols: {total_protocols}")
    print(f"  🌐 Chains: {total_chains}")
    
    # Count protocol-chain combinations
    combinations = 0
    for protocol_key, protocol_data in DEFI_PROTOCOLS.items():
        subgraphs = protocol_data.get('subgraphs', {})
        combinations += len(subgraphs)
        print(f"  • {protocol_data['name']}: {len(subgraphs)} chains")
    
    print(f"  🔗 Total combinations: {combinations}")
    
    assert total_protocols >= 10, "Should have at least 10 protocols"
    assert total_chains >= 5, "Should have at least 5 chains"
    assert combinations >= 20, "Should have at least 20 protocol-chain combinations"
    
    print("✅ Protocol coverage test passed")
    return True

def test_stats_generation():
    """Test statistics generation"""
    print("🧪 Testing statistics generation...")
    
    generator = RindexerGenerator(output_dir="./test_output")
    
    config = {
        'networks': {
            'ethereum': {
                'contracts': [
                    {'category': 'lending', 'events': ['Supply', 'Withdraw']},
                    {'category': 'dex', 'events': ['Swap', 'Mint']}
                ]
            },
            'arbitrum': {
                'contracts': [
                    {'category': 'lending', 'events': ['Borrow']}
                ]
            }
        }
    }
    
    stats = generator.generate_stats(config)
    
    assert stats['total_networks'] == 2, "Network count mismatch"
    assert stats['total_contracts'] == 3, "Contract count mismatch"
    assert stats['total_events'] == 5, "Event count mismatch"
    assert stats['contracts_by_network']['ethereum'] == 2, "Ethereum contract count mismatch"
    assert stats['protocols_by_category']['lending'] == 2, "Lending protocol count mismatch"
    
    print("✅ Statistics generation test passed")
    return True

def validate_chain_configs():
    """Validate chain configurations"""
    print("🧪 Validating chain configurations...")
    
    required_fields = ['chain_id', 'rpc', 'explorer_api', 'api_key']
    
    for chain_name, config in CHAINS.items():
        for field in required_fields:
            assert field in config, f"Chain {chain_name} missing {field}"
        
        assert isinstance(config['chain_id'], int), f"Chain {chain_name} has invalid chain_id"
        assert config['rpc'].startswith('http'), f"Chain {chain_name} has invalid RPC URL"
        
        print(f"  ✅ {chain_name}: Valid")
    
    print("✅ Chain configuration validation passed")
    return True

def validate_protocol_configs():
    """Validate protocol configurations"""
    print("🧪 Validating protocol configurations...")
    
    required_fields = ['name', 'category', 'events', 'subgraphs']
    valid_categories = ['lending', 'dex', 'staking', 'vault', 'yield', 'perp']
    
    for protocol_key, config in DEFI_PROTOCOLS.items():
        for field in required_fields:
            assert field in config, f"Protocol {protocol_key} missing {field}"
        
        assert config['category'] in valid_categories, f"Protocol {protocol_key} has invalid category"
        assert len(config['events']) > 0, f"Protocol {protocol_key} has no events"
        assert len(config['subgraphs']) > 0, f"Protocol {protocol_key} has no subgraphs"
        
        print(f"  ✅ {config['name']}: Valid ({config['category']})")
    
    print("✅ Protocol configuration validation passed")
    return True

def run_all_tests():
    """Run all tests"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         🧪 DeFi Indexer Generator - Test Suite                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("ABI Generation", test_abi_generation),
        ("Event Extraction", test_event_extraction),
        ("YAML Structure", test_yaml_structure),
        ("Protocol Coverage", test_protocol_coverage),
        ("Statistics Generation", test_stats_generation),
        ("Chain Configurations", validate_chain_configs),
        ("Protocol Configurations", validate_protocol_configs)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {test_name}")
            print('='*60)
            
            result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED\n")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED\n")
        
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} FAILED: {e}\n")
    
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║                      📊 TEST RESULTS                           ║
╚════════════════════════════════════════════════════════════════╝

Total Tests: {passed + failed}
✅ Passed: {passed}
❌ Failed: {failed}
Success Rate: {(passed / (passed + failed) * 100):.1f}%

{'🎉 ALL TESTS PASSED!' if failed == 0 else '⚠️  SOME TESTS FAILED'}
    """)
    
    # Cleanup test output directory
    if os.path.exists('./test_output'):
        import shutil
        shutil.rmtree('./test_output')
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

