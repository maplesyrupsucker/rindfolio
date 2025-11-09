# 📚 Usage Examples

## Basic Usage

### 1. Generate for Default Chains (Ethereum, Polygon, Arbitrum, Optimism, Base)

```bash
python generate_rindexer_yaml.py
```

**Output:**
```
======================================================================
🚀 DeFi Indexer Generator
======================================================================
📍 Chains: ethereum, polygon, arbitrum, optimism, base
📁 Output: ./rindexer_project
🔢 Max protocols: 50
======================================================================

🔍 Processing: aave-v3
   📊 Found 8 events in subgraph schema
   🔗 ethereum... ✅ 6 events
   🔗 polygon... ✅ 6 events
   🔗 arbitrum... ✅ 6 events

🔍 Processing: compound-v3
   📊 Found 4 events in subgraph schema
   🔗 ethereum... ✅ 2 events
   🔗 polygon... ✅ 2 events

... (48 more protocols)

======================================================================
📝 Generating rindexer.yaml...
======================================================================
✅ Generated: ./rindexer_project/rindexer.yaml
✅ Generated: ./rindexer_project/protocols.json

======================================================================
✨ GENERATION COMPLETE
======================================================================
⏱️  Time: 120.45s
🎯 Protocols: 48
📜 Contracts: 187
🎪 Events indexed: 1,204
📦 ABIs cached: 92
======================================================================

✅ Ready to use: ./rindexer_project/rindexer.yaml
💡 Next: cd rindexer_project && rindexer start
======================================================================
```

---

## Advanced Usage

### 2. Generate for Specific Chains

```bash
# Ethereum only
python generate_rindexer_yaml.py --chains ethereum

# Ethereum + Polygon
python generate_rindexer_yaml.py --chains ethereum,polygon

# All supported chains
python generate_rindexer_yaml.py --chains ethereum,polygon,arbitrum,optimism,base,avalanche,bsc
```

### 3. Limit Number of Protocols

```bash
# Top 10 protocols only (fast testing)
python generate_rindexer_yaml.py --max-protocols 10

# Top 5 protocols (very fast)
python generate_rindexer_yaml.py --max-protocols 5
```

### 4. Custom Output Directory

```bash
# Output to custom directory
python generate_rindexer_yaml.py --output ./my_indexer

# Output to absolute path
python generate_rindexer_yaml.py --output /Users/myuser/projects/defi_indexer
```

### 5. Parallel Processing

```bash
# Use 10 workers (faster, but more API calls)
python generate_rindexer_yaml.py --parallel 10

# Use 2 workers (slower, but safer for rate limits)
python generate_rindexer_yaml.py --parallel 2
```

### 6. Combined Options

```bash
# Fast test run
python generate_rindexer_yaml.py \
  --chains ethereum,polygon \
  --max-protocols 5 \
  --output ./test_run \
  --parallel 3

# Production run
python generate_rindexer_yaml.py \
  --chains ethereum,polygon,arbitrum,optimism,base \
  --max-protocols 100 \
  --output ./production_indexer \
  --parallel 10
```

---

## Docker Usage

### 7. Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View generator logs
docker-compose logs -f generator

# View rindexer logs
docker-compose logs -f rindexer

# Stop all services
docker-compose down
```

### 8. Regenerate Config

```bash
# Clear cache and regenerate
rm -rf .cache
docker-compose restart generator

# View new config
cat rindexer_project/rindexer.yaml
```

### 9. Custom Environment Variables

```bash
# Create .env file
cat > .env << EOF
ETHERSCAN_API_KEY=your_key_here
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your_key
EOF

# Restart with new config
docker-compose down
docker-compose up -d
```

---

## Working with Generated Output

### 10. Inspect Generated YAML

```bash
# View full config
cat rindexer_project/rindexer.yaml

# Count contracts
grep -c "^- name:" rindexer_project/rindexer.yaml

# List all protocols
cat rindexer_project/protocols.json | jq '.protocols | unique'

# List all chains
cat rindexer_project/protocols.json | jq '.chains'
```

### 11. Validate YAML Syntax

```bash
# Using Python
python -c "import yaml; yaml.safe_load(open('rindexer_project/rindexer.yaml'))"

# Using yq (if installed)
yq eval rindexer_project/rindexer.yaml
```

### 12. Inspect ABIs

```bash
# List all ABIs
ls -lh rindexer_project/abis/

# View specific ABI
cat rindexer_project/abis/aave-v3_ethereum.json | jq '.[] | select(.type == "event")'

# Count events in ABI
cat rindexer_project/abis/aave-v3_ethereum.json | jq '[.[] | select(.type == "event")] | length'
```

---

## Using with Rindexer

### 13. Start Rindexer

```bash
cd rindexer_project

# Start indexing
rindexer start

# Start with custom config
rindexer start --config rindexer.yaml
```

### 14. Query Indexed Data (GraphQL)

```bash
# Example: Query Aave supplies
curl http://localhost:3001/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ supplies(first: 10) { id user amount timestamp } }"
  }'

# Example: Query Uniswap swaps
curl http://localhost:3001/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ swaps(first: 10, orderBy: timestamp, orderDirection: desc) { id from to amount0 amount1 } }"
  }'
```

### 15. Access GraphQL Playground

```bash
# Open in browser
open http://localhost:4000

# Or use curl
curl http://localhost:4000
```

---

## Caching & Performance

### 16. View Cache Statistics

```bash
# List cached files
ls -lh .cache/

# Count cached items
ls .cache/ | wc -l

# Check cache size
du -sh .cache/
```

### 17. Clear Cache

```bash
# Clear all cache
rm -rf .cache/

# Clear specific protocol cache
rm .cache/subgraph_schema_aave_protocol-v3.json

# Clear ABI cache only
rm .cache/abi_*.json
```

### 18. Benchmark Performance

```bash
# Cold run (no cache)
rm -rf .cache/
time python generate_rindexer_yaml.py --max-protocols 10

# Warm run (with cache)
time python generate_rindexer_yaml.py --max-protocols 10
```

---

## Debugging & Troubleshooting

### 19. Verbose Output

```bash
# Add debug logging (modify script to enable)
python generate_rindexer_yaml.py --max-protocols 5 2>&1 | tee generation.log

# View errors only
python generate_rindexer_yaml.py 2>&1 | grep "⚠️\|❌"
```

### 20. Test Single Protocol

```bash
# Edit script to process only one protocol
python -c "
from generate_rindexer_yaml import *
protocol = {'name': 'aave-v3', 'subgraph': 'aave/protocol-v3', 'chains': ['ethereum']}
contracts = process_protocol(protocol, ['ethereum'], Path('./test'))
print(f'Found {len(contracts)} contracts')
"
```

### 21. Verify Contract Addresses

```bash
# Check if contract is verified on Etherscan
curl "https://api.etherscan.io/api?module=contract&action=getabi&address=0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2&apikey=YourApiKeyToken"

# Check contract on multiple explorers
for chain in ethereum polygon arbitrum; do
  echo "Checking $chain..."
  # Add appropriate API calls
done
```

---

## Integration Examples

### 22. Use in CI/CD Pipeline

```yaml
# .github/workflows/generate-indexer.yml
name: Generate Indexer Config

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate config
        env:
          ETHERSCAN_API_KEY: ${{ secrets.ETHERSCAN_API_KEY }}
        run: |
          python generate_rindexer_yaml.py \
            --chains ethereum,polygon,arbitrum \
            --output ./indexer
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: indexer-config
          path: indexer/
```

### 23. Automated Testing

```bash
# Test script
#!/bin/bash
set -e

echo "Testing generator..."

# Generate config
python generate_rindexer_yaml.py \
  --chains ethereum \
  --max-protocols 3 \
  --output ./test_output

# Validate YAML
python -c "import yaml; yaml.safe_load(open('test_output/rindexer.yaml'))"

# Check output files exist
test -f test_output/rindexer.yaml
test -f test_output/protocols.json
test -d test_output/abis

echo "✅ All tests passed!"
```

### 24. Monitoring & Alerts

```bash
# Monitor generation time
start=$(date +%s)
python generate_rindexer_yaml.py
end=$(date +%s)
duration=$((end - start))

if [ $duration -gt 300 ]; then
  echo "⚠️  Generation took ${duration}s (>5min)"
  # Send alert
fi
```

---

## Production Deployment

### 25. Production Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/defi-indexer-generator.git
cd defi-indexer-generator

# 2. Set up environment
cp env.example .env
nano .env  # Add your API keys

# 3. Generate config
python generate_rindexer_yaml.py \
  --chains ethereum,polygon,arbitrum,optimism,base \
  --max-protocols 100 \
  --output ./production

# 4. Deploy with Docker
cd production
docker-compose up -d

# 5. Monitor
docker-compose logs -f
```

### 26. Update Existing Deployment

```bash
# 1. Regenerate config
python generate_rindexer_yaml.py --output ./production

# 2. Restart rindexer
cd production
docker-compose restart rindexer

# 3. Verify
curl http://localhost:3001/health
```

---

## Tips & Best Practices

### 27. Optimize for Speed

```bash
# Use cached data
# Don't delete .cache/ between runs

# Use more workers
python generate_rindexer_yaml.py --parallel 10

# Limit protocols for testing
python generate_rindexer_yaml.py --max-protocols 5
```

### 28. Optimize for Reliability

```bash
# Use fewer workers (avoid rate limits)
python generate_rindexer_yaml.py --parallel 2

# Add API keys to .env
export ETHERSCAN_API_KEY=your_key

# Test with small subset first
python generate_rindexer_yaml.py --max-protocols 3
```

### 29. Regular Maintenance

```bash
# Weekly: Regenerate config (new protocols)
python generate_rindexer_yaml.py

# Monthly: Clear cache (fresh data)
rm -rf .cache/
python generate_rindexer_yaml.py

# Daily: Check rindexer health
curl http://localhost:3001/health
```

---

**More examples coming soon! 🚀**

