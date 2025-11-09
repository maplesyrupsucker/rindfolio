# 🏗️ Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                     DeFi Indexer Generator                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   1. Protocol Discovery (The Graph)     │
        │   • Query subgraph registry             │
        │   • Extract event schemas               │
        │   • Map to on-chain events              │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   2. ABI Fetching (Block Explorers)     │
        │   • Etherscan / Polygonscan APIs        │
        │   • Download verified ABIs              │
        │   • Extract event signatures            │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   3. Event Filtering (Critical Only)    │
        │   • Supply, Deposit, Mint               │
        │   • Borrow, Withdraw, Repay             │
        │   • Swap, AddLiquidity, Stake           │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   4. YAML Generation (Minimal Config)   │
        │   • One contract per protocol/chain     │
        │   • Only discovered events              │
        │   • No duplicates or bloat              │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   5. Output (Ready to Index)            │
        │   • rindexer.yaml                       │
        │   • abis/*.json                         │
        │   • protocols.json                      │
        └─────────────────────────────────────────┘
```

## Components

### 1. Generator Script (`generate_rindexer_yaml.py`)

**Responsibilities:**
- Orchestrate entire generation process
- Parallel processing of protocols
- Caching and rate limiting
- Error handling and retries

**Key Functions:**
- `fetch_subgraph_schema()` — Query The Graph
- `extract_events_from_schema()` — Parse GraphQL schema
- `fetch_abi_from_explorer()` — Download ABIs
- `generate_rindexer_yaml()` — Create config

### 2. The Graph Integration

**How It Works:**
1. Query hosted service: `https://api.thegraph.com/subgraphs/name/{org}/{name}`
2. Use GraphQL introspection to get schema
3. Extract event types from schema
4. Map to on-chain event signatures

**Example Query:**
```graphql
{
  __schema {
    types {
      name
      kind
      fields {
        name
        type { name }
      }
    }
  }
}
```

### 3. Block Explorer Integration

**Supported Explorers:**
- Etherscan (Ethereum)
- Polygonscan (Polygon)
- Arbiscan (Arbitrum)
- Optimism Etherscan (Optimism)
- Basescan (Base)
- Snowtrace (Avalanche)
- BSCScan (BNB Chain)

**API Endpoint:**
```
GET /api?module=contract&action=getabi&address={address}&apikey={key}
```

**Rate Limits:**
- Free tier: 5 calls/sec
- With API key: 5 calls/sec (higher daily limit)

### 4. Event Filtering

**Critical Events (Position Tracking):**

| Category | Events |
|----------|--------|
| Lending | Supply, Deposit, Mint, Borrow, Withdraw, Redeem, Repay, Liquidate |
| DEX/LP | Swap, AddLiquidity, RemoveLiquidity, Burn, Collect |
| Staking | Stake, Unstake, Claim, RewardPaid |
| Transfers | Transfer |

**Why These Events?**
- Reconstruct user positions
- Track deposits/withdrawals
- Calculate balances
- Monitor liquidations

### 5. Caching Strategy

**Cache Layers:**
1. **Subgraph schemas** (24h) — Rarely change
2. **ABIs** (24h) — Immutable once verified
3. **API responses** (24h) — Reduce rate limiting

**Cache Location:**
```
.cache/
├── subgraph_schema_aave_protocol-v3.json
├── abi_ethereum_0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2.json
└── ...
```

## Data Flow

```
User Input (--chains, --max-protocols)
    │
    ▼
Load TOP_DEFI_PROTOCOLS list
    │
    ▼
For each protocol (parallel):
    │
    ├─▶ Fetch subgraph schema (The Graph)
    │       │
    │       ▼
    │   Extract event names
    │       │
    │       ▼
    ├─▶ For each chain:
    │       │
    │       ├─▶ Get contract address (hardcoded/subgraph)
    │       │
    │       ├─▶ Fetch ABI (block explorer)
    │       │
    │       ├─▶ Extract events from ABI
    │       │
    │       ├─▶ Filter critical events
    │       │
    │       └─▶ Save ABI to ./abis/
    │
    └─▶ Collect all contracts
            │
            ▼
Generate rindexer.yaml
    │
    ├─▶ networks: [chain configs]
    ├─▶ storage: {postgres: true}
    └─▶ contracts: [contract configs]
            │
            ▼
Save outputs:
    ├─▶ rindexer.yaml
    ├─▶ protocols.json
    └─▶ abis/*.json
```

## Docker Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose                            │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Postgres    │   │   Generator   │   │   Rindexer    │
│   (Database)  │   │   (Python)    │   │   (Rust)      │
│               │   │               │   │               │
│   Port: 5432  │   │   Runs once   │   │   Port: 3001  │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        │                     ▼                     │
        │           ┌───────────────┐              │
        │           │  Volumes:     │              │
        │           │  • .cache     │              │
        │           │  • output     │              │
        │           └───────────────┘              │
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                    ┌───────────────┐
                    │   GraphQL     │
                    │   Playground  │
                    │   Port: 4000  │
                    └───────────────┘
```

## Performance Characteristics

### Time Complexity

| Operation | Cold Cache | Warm Cache |
|-----------|------------|------------|
| Subgraph schema fetch | O(n) | O(1) |
| ABI fetch | O(n × m) | O(1) |
| YAML generation | O(n × m) | O(n × m) |

Where:
- n = number of protocols
- m = number of chains

### Space Complexity

| Component | Size |
|-----------|------|
| Subgraph schema | ~50 KB each |
| ABI | ~10-100 KB each |
| Cache total | ~5-50 MB |
| Generated YAML | ~10-100 KB |

### Parallelization

- **Default workers:** 5
- **Max workers:** 20 (rate limit constraint)
- **Speedup:** ~3-4x with 5 workers

## Error Handling

### Retry Strategy

```python
Retry(
    total=3,              # 3 retries
    backoff_factor=1,     # 1s, 2s, 4s delays
    status_forcelist=[429, 500, 502, 503, 504]
)
```

### Fallback Mechanisms

1. **Subgraph not found** → Skip protocol, log warning
2. **ABI not verified** → Skip contract, log warning
3. **Rate limited** → Wait and retry (exponential backoff)
4. **Network error** → Retry up to 3 times

## Security Considerations

### API Keys
- Stored in `.env` (not committed)
- Optional (works without)
- Never logged or exposed

### RPC URLs
- Public RPCs by default
- User can override with private RPCs
- No sensitive data in logs

### Contract Addresses
- Verified on block explorers
- Cross-referenced with The Graph
- Checksummed format

## Extensibility

### Adding New Protocols

```python
TOP_DEFI_PROTOCOLS.append({
    "name": "my-protocol",
    "subgraph": "my-org/my-subgraph",
    "chains": ["ethereum", "polygon"]
})
```

### Adding New Chains

```python
CHAIN_IDS["my-chain"] = 12345
DEFAULT_RPCS["my-chain"] = "https://rpc.my-chain.com"
BLOCK_EXPLORERS["my-chain"] = {
    "api": "https://api.my-chain-scan.com/api",
    "key_env": "MY_CHAIN_API_KEY",
    "default_key": "YourApiKeyToken"
}
```

### Adding New Events

```python
CRITICAL_EVENTS.add("MyCustomEvent")
```

## Testing Strategy

### Unit Tests
- Test event extraction
- Test ABI parsing
- Test YAML generation

### Integration Tests
- Test with real APIs (rate-limited)
- Test with cached data
- Test error scenarios

### End-to-End Tests
- Generate full config
- Validate YAML syntax
- Test with rindexer

## Monitoring & Observability

### Logs
- Protocol processing status
- API call success/failure
- Cache hit/miss rates
- Generation summary

### Metrics
- Total protocols processed
- Total contracts discovered
- Total events indexed
- Generation time

### Debugging
- Verbose logging available
- Cache inspection tools
- YAML validation

## Future Improvements

1. **Auto-update protocol list** from The Graph registry
2. **Smart contract address discovery** from subgraphs
3. **Event signature verification** against on-chain data
4. **Multi-version support** (e.g., Aave V2 + V3)
5. **Custom event filters** per protocol
6. **GraphQL schema validation**
7. **Automated testing** of generated configs

---

**Built for scale, optimized for speed, designed for DeFi. 🚀**
