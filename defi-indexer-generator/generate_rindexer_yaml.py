#!/usr/bin/env python3
"""
DeFi Indexer Generator - Auto-generate rindexer.yaml from The Graph subgraphs
Discovers top DeFi protocols, fetches ABIs, and creates minimal indexing config.
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ============================================================================
# CONFIGURATION
# ============================================================================

# The Graph API endpoints
GRAPH_HOSTED_API = "https://api.thegraph.com/subgraphs/name"
GRAPH_DECENTRALIZED_GATEWAY = "https://gateway.thegraph.com/api"

# Block explorer APIs (free tier)
BLOCK_EXPLORERS = {
    "ethereum": {
        "api": "https://api.etherscan.io/api",
        "key_env": "ETHERSCAN_API_KEY",
        "default_key": "YourApiKeyToken"  # Free tier works without key
    },
    "polygon": {
        "api": "https://api.polygonscan.com/api",
        "key_env": "POLYGONSCAN_API_KEY",
        "default_key": "YourApiKeyToken"
    },
    "arbitrum": {
        "api": "https://api.arbiscan.io/api",
        "key_env": "ARBISCAN_API_KEY",
        "default_key": "YourApiKeyToken"
    },
    "optimism": {
        "api": "https://api-optimistic.etherscan.io/api",
        "key_env": "OPTIMISM_ETHERSCAN_API_KEY",
        "default_key": "YourApiKeyToken"
    },
    "base": {
        "api": "https://api.basescan.org/api",
        "key_env": "BASESCAN_API_KEY",
        "default_key": "YourApiKeyToken"
    },
    "avalanche": {
        "api": "https://api.snowtrace.io/api",
        "key_env": "SNOWTRACE_API_KEY",
        "default_key": "YourApiKeyToken"
    },
    "bsc": {
        "api": "https://api.bscscan.com/api",
        "key_env": "BSCSCAN_API_KEY",
        "default_key": "YourApiKeyToken"
    }
}

# Chain ID mapping
CHAIN_IDS = {
    "ethereum": 1,
    "polygon": 137,
    "arbitrum": 42161,
    "optimism": 10,
    "base": 8453,
    "avalanche": 43114,
    "bsc": 56
}

# Public RPC endpoints (free tier)
DEFAULT_RPCS = {
    "ethereum": "https://eth.llamarpc.com",
    "polygon": "https://polygon-rpc.com",
    "arbitrum": "https://arb1.arbitrum.io/rpc",
    "optimism": "https://mainnet.optimism.io",
    "base": "https://mainnet.base.org",
    "avalanche": "https://api.avax.network/ext/bc/C/rpc",
    "bsc": "https://bsc-dataseed.binance.org"
}

# Top DeFi protocols by TVL (manually curated list of known subgraphs)
TOP_DEFI_PROTOCOLS = [
    # Lending
    {"name": "aave-v3", "subgraph": "aave/protocol-v3", "chains": ["ethereum", "polygon", "arbitrum", "optimism", "base"]},
    {"name": "aave-v2", "subgraph": "aave/protocol-v2", "chains": ["ethereum", "polygon"]},
    {"name": "compound-v3", "subgraph": "compound-finance/compound-v3", "chains": ["ethereum", "polygon", "arbitrum", "base"]},
    {"name": "compound-v2", "subgraph": "graphprotocol/compound-v2", "chains": ["ethereum"]},
    
    # DEXes
    {"name": "uniswap-v3", "subgraph": "uniswap/uniswap-v3", "chains": ["ethereum", "polygon", "arbitrum", "optimism", "base"]},
    {"name": "uniswap-v2", "subgraph": "uniswap/uniswap-v2", "chains": ["ethereum"]},
    {"name": "curve", "subgraph": "messari/curve-finance-ethereum", "chains": ["ethereum", "polygon", "arbitrum", "optimism"]},
    {"name": "balancer-v2", "subgraph": "balancer-labs/balancer-v2", "chains": ["ethereum", "polygon", "arbitrum", "optimism", "base"]},
    {"name": "sushiswap", "subgraph": "sushi-labs/sushiswap", "chains": ["ethereum", "polygon", "arbitrum", "optimism", "base"]},
    {"name": "pancakeswap", "subgraph": "pancakeswap/exchange-v3", "chains": ["bsc", "ethereum"]},
    
    # Liquid Staking
    {"name": "lido", "subgraph": "lidofinance/lido", "chains": ["ethereum"]},
    {"name": "rocket-pool", "subgraph": "rocket-pool/rocketpool", "chains": ["ethereum"]},
    
    # Derivatives & Perps
    {"name": "gmx", "subgraph": "gmx-io/gmx-stats", "chains": ["arbitrum", "avalanche"]},
    {"name": "synthetix", "subgraph": "synthetix/synthetix", "chains": ["ethereum", "optimism"]},
    
    # Yield Aggregators
    {"name": "yearn-v2", "subgraph": "yearn/yearn-vaults-v2", "chains": ["ethereum"]},
    {"name": "convex", "subgraph": "convex-community/convex", "chains": ["ethereum"]},
    
    # Stablecoins
    {"name": "frax", "subgraph": "frax-finance/frax", "chains": ["ethereum"]},
    {"name": "maker", "subgraph": "protofire/makerdao", "chains": ["ethereum"]},
]

# Critical DeFi events to index (position-tracking events)
CRITICAL_EVENTS = {
    # Lending/Borrowing
    "Supply", "Deposit", "Mint", "Borrow", "Withdraw", "Redeem", "Repay", "Liquidate",
    # DEX/LP
    "Swap", "AddLiquidity", "RemoveLiquidity", "Burn", "Collect",
    # Staking
    "Stake", "Unstake", "Claim", "RewardPaid",
    # Transfers (for position tracking)
    "Transfer",
}

# Cache settings
CACHE_DIR = Path(".cache")
CACHE_DURATION = timedelta(hours=24)


# ============================================================================
# HTTP SESSION WITH RETRY
# ============================================================================

def create_session() -> requests.Session:
    """Create requests session with retry logic"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


SESSION = create_session()


# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

def get_cache_path(key: str) -> Path:
    """Get cache file path for a key"""
    CACHE_DIR.mkdir(exist_ok=True)
    safe_key = key.replace("/", "_").replace(":", "_")
    return CACHE_DIR / f"{safe_key}.json"


def get_cached(key: str) -> Optional[dict]:
    """Get cached data if not expired"""
    cache_path = get_cache_path(key)
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, "r") as f:
            data = json.load(f)
        
        cached_time = datetime.fromisoformat(data["timestamp"])
        if datetime.now() - cached_time < CACHE_DURATION:
            return data["content"]
    except Exception as e:
        print(f"⚠️  Cache read error for {key}: {e}")
    
    return None


def set_cached(key: str, content: dict):
    """Cache data with timestamp"""
    cache_path = get_cache_path(key)
    try:
        with open(cache_path, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "content": content
            }, f, indent=2)
    except Exception as e:
        print(f"⚠️  Cache write error for {key}: {e}")


# ============================================================================
# THE GRAPH SUBGRAPH DISCOVERY
# ============================================================================

def fetch_subgraph_schema(subgraph_name: str) -> Optional[Dict]:
    """Fetch subgraph schema from The Graph"""
    cache_key = f"subgraph_schema_{subgraph_name}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    # Try hosted service first
    url = f"{GRAPH_HOSTED_API}/{subgraph_name}"
    
    # GraphQL introspection query to get schema
    query = """
    {
        _meta {
            deployment
            hasIndexingErrors
        }
    }
    """
    
    try:
        response = SESSION.post(url, json={"query": query}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                # Fetch full schema
                schema_query = """
                {
                    __schema {
                        types {
                            name
                            kind
                            fields {
                                name
                                type {
                                    name
                                    kind
                                }
                            }
                        }
                    }
                }
                """
                schema_response = SESSION.post(url, json={"query": schema_query}, timeout=10)
                if schema_response.status_code == 200:
                    schema_data = schema_response.json()
                    if "data" in schema_data:
                        set_cached(cache_key, schema_data["data"])
                        return schema_data["data"]
    except Exception as e:
        print(f"⚠️  Error fetching subgraph {subgraph_name}: {e}")
    
    return None


def extract_events_from_schema(schema: Dict) -> Set[str]:
    """Extract event names from subgraph schema"""
    events = set()
    
    if not schema or "__schema" not in schema:
        return events
    
    types = schema["__schema"].get("types", [])
    
    for type_def in types:
        type_name = type_def.get("name", "")
        
        # Look for event-like types (usually end with Event or have event-like names)
        if any(keyword in type_name.lower() for keyword in ["event", "transaction", "action"]):
            # Extract the base name (remove Event suffix)
            event_name = type_name.replace("Event", "").replace("Transaction", "")
            if event_name and event_name[0].isupper():
                events.add(event_name)
        
        # Also check fields that might represent events
        fields = type_def.get("fields", [])
        for field in fields:
            field_name = field.get("name", "")
            # Common event field patterns
            if any(keyword in field_name.lower() for keyword in CRITICAL_EVENTS):
                # Normalize to PascalCase
                normalized = "".join(word.capitalize() for word in field_name.split("_"))
                if normalized in CRITICAL_EVENTS:
                    events.add(normalized)
    
    return events


def discover_protocol_contracts(protocol: Dict, chain: str) -> List[Dict]:
    """Discover contract addresses for a protocol on a specific chain"""
    # For now, we'll use a hardcoded mapping of known contract addresses
    # In production, this would query the subgraph for contract addresses
    
    contracts = []
    
    # Hardcoded addresses for major protocols (production would fetch from subgraph)
    known_addresses = {
        "aave-v3": {
            "ethereum": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",  # Pool
            "polygon": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "arbitrum": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "optimism": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "base": "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5",
        },
        "compound-v3": {
            "ethereum": "0xc3d688B66703497DAA19211EEdff47f25384cdc3",  # cUSDCv3
            "polygon": "0xF25212E676D1F7F89Cd72fFEe66158f541246445",
            "arbitrum": "0xA5EDBDD9646f8dFF606d7448e414884C7d905dCA",
            "base": "0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf",
        },
        "uniswap-v3": {
            "ethereum": "0x1F98431c8aD98523631AE4a59f267346ea31F984",  # Factory
            "polygon": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
            "arbitrum": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
            "optimism": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
            "base": "0x33128a8fC17869897dcE68Ed026d694621f6FDfD",
        },
        "curve": {
            "ethereum": "0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5",  # Registry
            "polygon": "0x094d12e5b541784701FD8d65F11fc0598FBC6332",
            "arbitrum": "0x445FE580eF8d70FF569aB36e80c647af338db351",
        },
        "lido": {
            "ethereum": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",  # stETH
        },
        "gmx": {
            "arbitrum": "0x489ee077994B6658eAfA855C308275EAd8097C4A",  # Vault
            "avalanche": "0x9ab2De34A33fB459b538c43f251eB825645e8595",
        },
    }
    
    protocol_name = protocol["name"]
    if protocol_name in known_addresses and chain in known_addresses[protocol_name]:
        address = known_addresses[protocol_name][chain]
        contracts.append({
            "name": f"{protocol_name}_{chain}",
            "address": address,
            "chain": chain,
            "protocol": protocol_name
        })
    
    return contracts


# ============================================================================
# ABI FETCHING FROM BLOCK EXPLORERS
# ============================================================================

def fetch_abi_from_explorer(address: str, chain: str) -> Optional[List]:
    """Fetch verified contract ABI from block explorer"""
    cache_key = f"abi_{chain}_{address}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    if chain not in BLOCK_EXPLORERS:
        print(f"⚠️  No block explorer configured for {chain}")
        return None
    
    explorer = BLOCK_EXPLORERS[chain]
    api_key = os.getenv(explorer["key_env"], explorer["default_key"])
    
    params = {
        "module": "contract",
        "action": "getabi",
        "address": address,
        "apikey": api_key
    }
    
    try:
        response = SESSION.get(explorer["api"], params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "1" and data.get("result"):
                abi = json.loads(data["result"])
                set_cached(cache_key, abi)
                return abi
            else:
                print(f"⚠️  ABI not found for {address} on {chain}: {data.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"⚠️  Error fetching ABI for {address} on {chain}: {e}")
    
    return None


def extract_events_from_abi(abi: List) -> Set[str]:
    """Extract event names from ABI"""
    events = set()
    
    for item in abi:
        if item.get("type") == "event":
            event_name = item.get("name")
            if event_name and event_name in CRITICAL_EVENTS:
                events.add(event_name)
    
    return events


def save_abi(abi: List, protocol: str, chain: str, output_dir: Path):
    """Save ABI to file"""
    abi_dir = output_dir / "abis"
    abi_dir.mkdir(parents=True, exist_ok=True)
    
    abi_path = abi_dir / f"{protocol}_{chain}.json"
    with open(abi_path, "w") as f:
        json.dump(abi, f, indent=2)
    
    return f"./abis/{protocol}_{chain}.json"


# ============================================================================
# RINDEXER YAML GENERATION
# ============================================================================

def generate_rindexer_yaml(contracts: List[Dict], chains: List[str], output_dir: Path) -> Dict:
    """Generate rindexer.yaml configuration"""
    
    # Build networks configuration
    networks = []
    for chain in chains:
        rpc_url = os.getenv(f"{chain.upper()}_RPC_URL", DEFAULT_RPCS.get(chain))
        networks.append({
            "name": chain,
            "chain_id": CHAIN_IDS.get(chain, 1),
            "rpc": rpc_url
        })
    
    # Build contracts configuration
    contract_configs = []
    for contract in contracts:
        if contract.get("events") and contract.get("abi_path"):
            contract_configs.append({
                "name": contract["name"],
                "address": contract["address"],
                "abi_path": contract["abi_path"],
                "events": sorted(list(contract["events"])),
                "network": contract["chain"]
            })
    
    # Build final YAML structure
    config = {
        "name": "defi_positions_indexer",
        "project_type": "no-code",
        "networks": networks,
        "storage": {
            "postgres": {
                "enabled": True
            }
        },
        "contracts": contract_configs
    }
    
    return config


def save_yaml(config: Dict, output_dir: Path):
    """Save YAML configuration to file"""
    yaml_path = output_dir / "rindexer.yaml"
    
    with open(yaml_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)
    
    print(f"✅ Generated: {yaml_path}")
    return yaml_path


# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def process_protocol(protocol: Dict, chains: List[str], output_dir: Path) -> List[Dict]:
    """Process a single protocol across multiple chains"""
    protocol_name = protocol["name"]
    print(f"\n🔍 Processing: {protocol_name}")
    
    contracts = []
    
    # Fetch subgraph schema
    schema = fetch_subgraph_schema(protocol["subgraph"])
    subgraph_events = extract_events_from_schema(schema) if schema else set()
    
    if subgraph_events:
        print(f"   📊 Found {len(subgraph_events)} events in subgraph schema")
    
    # Process each chain
    for chain in chains:
        if chain not in protocol.get("chains", []):
            continue
        
        print(f"   🔗 {chain}...", end=" ")
        
        # Discover contracts
        chain_contracts = discover_protocol_contracts(protocol, chain)
        
        for contract in chain_contracts:
            # Fetch ABI
            abi = fetch_abi_from_explorer(contract["address"], chain)
            
            if not abi:
                print(f"❌ No ABI")
                continue
            
            # Extract events from ABI
            abi_events = extract_events_from_abi(abi)
            
            # Use subgraph events if available, otherwise use ABI events
            events = subgraph_events & CRITICAL_EVENTS if subgraph_events else abi_events
            
            if not events:
                print(f"⚠️  No critical events")
                continue
            
            # Save ABI
            abi_path = save_abi(abi, protocol_name, chain, output_dir)
            
            # Add to contracts list
            contract["events"] = events
            contract["abi_path"] = abi_path
            contracts.append(contract)
            
            print(f"✅ {len(events)} events")
    
    return contracts


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Auto-generate rindexer.yaml from The Graph subgraphs"
    )
    parser.add_argument(
        "--chains",
        type=str,
        default="ethereum,polygon,arbitrum,optimism,base",
        help="Comma-separated list of chains to index"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./rindexer_project",
        help="Output directory for generated files"
    )
    parser.add_argument(
        "--max-protocols",
        type=int,
        default=50,
        help="Maximum number of protocols to process"
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=5,
        help="Number of parallel workers"
    )
    
    args = parser.parse_args()
    
    # Parse chains
    chains = [c.strip() for c in args.chains.split(",")]
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("🚀 DeFi Indexer Generator")
    print("=" * 70)
    print(f"📍 Chains: {', '.join(chains)}")
    print(f"📁 Output: {output_dir}")
    print(f"🔢 Max protocols: {args.max_protocols}")
    print("=" * 70)
    
    start_time = time.time()
    
    # Process protocols in parallel
    all_contracts = []
    protocols_to_process = TOP_DEFI_PROTOCOLS[:args.max_protocols]
    
    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        futures = {
            executor.submit(process_protocol, protocol, chains, output_dir): protocol
            for protocol in protocols_to_process
        }
        
        for future in as_completed(futures):
            protocol = futures[future]
            try:
                contracts = future.result()
                all_contracts.extend(contracts)
            except Exception as e:
                print(f"❌ Error processing {protocol['name']}: {e}")
    
    # Generate YAML
    print("\n" + "=" * 70)
    print("📝 Generating rindexer.yaml...")
    print("=" * 70)
    
    config = generate_rindexer_yaml(all_contracts, chains, output_dir)
    yaml_path = save_yaml(config, output_dir)
    
    # Save protocols metadata
    protocols_path = output_dir / "protocols.json"
    with open(protocols_path, "w") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "chains": chains,
            "protocols": [c["protocol"] for c in all_contracts],
            "contracts": all_contracts
        }, f, indent=2)
    
    print(f"✅ Generated: {protocols_path}")
    
    # Print summary
    elapsed = time.time() - start_time
    total_events = sum(len(c.get("events", [])) for c in all_contracts)
    unique_protocols = len(set(c["protocol"] for c in all_contracts))
    unique_abis = len(set(c["abi_path"] for c in all_contracts))
    
    print("\n" + "=" * 70)
    print("✨ GENERATION COMPLETE")
    print("=" * 70)
    print(f"⏱️  Time: {elapsed:.2f}s")
    print(f"🎯 Protocols: {unique_protocols}")
    print(f"📜 Contracts: {len(all_contracts)}")
    print(f"🎪 Events indexed: {total_events:,}")
    print(f"📦 ABIs cached: {unique_abis}")
    print("=" * 70)
    print(f"\n✅ Ready to use: {yaml_path}")
    print(f"💡 Next: cd {output_dir} && rindexer start")
    print("=" * 70)


if __name__ == "__main__":
    main()

