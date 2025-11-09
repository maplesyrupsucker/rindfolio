# 🚀 Getting Started with DeFi Indexer Generator

Welcome! This guide will get you up and running in **under 5 minutes**.

## 📋 Prerequisites

Choose your path:

### Path 1: Standalone Script (Recommended for Testing)
- Python 3.10 or higher
- `pip` package manager
- Internet connection

### Path 2: Docker (Recommended for Production)
- Docker Desktop or Docker Engine
- Docker Compose
- 4GB+ RAM available

## ⚡ Quick Start (Standalone)

### Step 1: Install Dependencies

```bash
cd /Users/slavid/Documents/GitHub/rindfolio/defi-indexer-generator
pip install -r requirements.txt
```

Expected output:
```
Successfully installed requests-2.31.0 PyYAML-6.0.1 urllib3-2.0.0
```

### Step 2: Run Generator (Test Mode)

```bash
python generate_rindexer_yaml.py \
  --chains ethereum,polygon \
  --max-protocols 5 \
  --output ./my_first_indexer
```

This will:
- ✅ Discover 5 protocols from The Graph
- ✅ Fetch ABIs from Etherscan/Polygonscan
- ✅ Generate `rindexer.yaml` in `./my_first_indexer/`
- ⏱️ Takes ~30 seconds (first run)

### Step 3: Check Output

```bash
ls -lh my_first_indexer/
```

You should see:
```
rindexer.yaml       # Main config file
protocols.json      # Metadata
abis/               # Downloaded ABIs
```

### Step 4: View Generated Config

```bash
cat my_first_indexer/rindexer.yaml
```

You'll see a clean, minimal config with:
- Network configurations
- Contract addresses
- Event names to index
- ABI paths

**🎉 Congratulations! You've generated your first DeFi indexer config!**

---

## 🐳 Quick Start (Docker)

### Step 1: Set Up Environment

```bash
cd /Users/slavid/Documents/GitHub/rindfolio/defi-indexer-generator
cp env.example .env
```

### Step 2: (Optional) Add API Keys

Edit `.env` and add your API keys for better rate limits:

```bash
nano .env
```

Add:
```bash
ETHERSCAN_API_KEY=your_key_here
POLYGONSCAN_API_KEY=your_key_here
```

Get free keys:
- Etherscan: https://etherscan.io/apis
- Polygonscan: https://polygonscan.com/apis

### Step 3: Start All Services

```bash
docker-compose up -d
```

This starts:
- 🐘 PostgreSQL (database)
- 🔧 Generator (auto-runs once)
- 🚀 Rindexer (indexer)
- 🎮 GraphQL Playground (UI)

### Step 4: Watch Generator Logs

```bash
docker-compose logs -f generator
```

Wait for:
```
✨ GENERATION COMPLETE
🎯 Protocols: 48
📜 Contracts: 187
```

Press `Ctrl+C` to exit logs.

### Step 5: Access GraphQL Playground

Open in browser:
```bash
open http://localhost:4000
```

Or manually visit: http://localhost:4000

**🎉 You now have a full DeFi indexing stack running!**

---

## 🎯 What's Next?

### Option A: Customize Your Config

Edit the generator to add more protocols:

```bash
nano generate_rindexer_yaml.py
```

Find `TOP_DEFI_PROTOCOLS` and add:

```python
{
    "name": "my-protocol",
    "subgraph": "my-org/my-subgraph",
    "chains": ["ethereum", "polygon"]
}
```

### Option B: Generate for More Chains

```bash
python generate_rindexer_yaml.py \
  --chains ethereum,polygon,arbitrum,optimism,base \
  --max-protocols 50
```

### Option C: Use with Rindexer

```bash
cd rindexer_project
rindexer start
```

### Option D: Query Indexed Data

```bash
curl http://localhost:3001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ supplies { id user amount } }"}'
```

---

## 📚 Learn More

### Essential Reading

1. **README.md** — Complete documentation
2. **QUICKSTART.md** — 2-minute setup
3. **USAGE_EXAMPLES.md** — 29 real examples
4. **ARCHITECTURE.md** — How it works

### Common Tasks

#### Regenerate Config
```bash
python generate_rindexer_yaml.py
```

#### Clear Cache
```bash
rm -rf .cache/
```

#### View Protocols
```bash
cat rindexer_project/protocols.json | python -m json.tool
```

#### Check Docker Status
```bash
docker-compose ps
```

#### Restart Rindexer
```bash
docker-compose restart rindexer
```

---

## 🐛 Troubleshooting

### Problem: "No ABIs found"

**Cause:** Contracts might not be verified on block explorer.

**Solution:** 
1. Check if contract is verified on Etherscan
2. Add API key to `.env`
3. Try again in 1 minute (rate limit)

### Problem: "Rate limited"

**Cause:** Too many API calls without API key.

**Solution:**
1. Add API keys to `.env`
2. Reduce `--parallel` workers: `--parallel 2`
3. Wait 1 minute and retry

### Problem: "Subgraph not found"

**Cause:** Subgraph might be deprecated or moved.

**Solution:**
1. Check The Graph explorer: https://thegraph.com/explorer
2. Update subgraph name in `TOP_DEFI_PROTOCOLS`
3. Skip that protocol for now

### Problem: Docker won't start

**Cause:** Port conflicts or insufficient resources.

**Solution:**
1. Check if ports are available:
   ```bash
   lsof -i :5432  # PostgreSQL
   lsof -i :3001  # Rindexer
   lsof -i :4000  # GraphQL
   ```
2. Stop conflicting services
3. Ensure 4GB+ RAM available

### Problem: Generator takes too long

**Cause:** Many protocols, cold cache, slow network.

**Solution:**
1. Use fewer protocols: `--max-protocols 10`
2. Use more workers: `--parallel 10`
3. Second run will be much faster (cached)

---

## 💡 Pro Tips

### Tip 1: Start Small
Always test with `--max-protocols 5` first.

### Tip 2: Use Cache
Don't delete `.cache/` between runs — it makes regeneration instant.

### Tip 3: Monitor Logs
Use `docker-compose logs -f` to watch what's happening.

### Tip 4: Check Output Size
```bash
du -sh rindexer_project/
```

### Tip 5: Validate YAML
```bash
python -c "import yaml; yaml.safe_load(open('rindexer_project/rindexer.yaml'))"
```

---

## 🎓 Understanding the Output

### rindexer.yaml Structure

```yaml
name: defi_positions_indexer    # Project name
project_type: no-code            # No custom code needed
networks:                        # Chain configurations
  - name: ethereum
    chain_id: 1
    rpc: https://eth.llamarpc.com
storage:                         # Database config
  postgres:
    enabled: true
contracts:                       # Contracts to index
  - name: aave-v3_ethereum
    address: '0x87870...'
    abi_path: ./abis/aave-v3_ethereum.json
    events:                      # Events to track
      - Supply
      - Borrow
      - Withdraw
    network: ethereum
```

### protocols.json Structure

```json
{
  "generated_at": "2025-11-09T...",
  "chains": ["ethereum", "polygon"],
  "protocols": ["aave-v3", "compound-v3"],
  "contracts": [
    {
      "name": "aave-v3_ethereum",
      "address": "0x87870...",
      "chain": "ethereum",
      "protocol": "aave-v3",
      "events": ["Supply", "Borrow"],
      "abi_path": "./abis/aave-v3_ethereum.json"
    }
  ]
}
```

---

## 🚀 Production Deployment

### Step 1: Generate Full Config

```bash
python generate_rindexer_yaml.py \
  --chains ethereum,polygon,arbitrum,optimism,base \
  --max-protocols 100 \
  --output ./production
```

### Step 2: Add API Keys

```bash
cp env.example .env
nano .env  # Add all your API keys
```

### Step 3: Deploy with Docker

```bash
cd production
docker-compose up -d
```

### Step 4: Monitor

```bash
docker-compose logs -f rindexer
```

### Step 5: Set Up Monitoring

```bash
# Health check
curl http://localhost:3001/health

# Set up alerts (your monitoring tool)
```

---

## 📊 Expected Results

After running the generator, you should see:

```
======================================================================
✨ GENERATION COMPLETE
======================================================================
⏱️  Time: 120.45s
🎯 Protocols: 48
📜 Contracts: 187
🎪 Events indexed: 1,204
📦 ABIs cached: 92
======================================================================
```

This means:
- ✅ 48 DeFi protocols discovered
- ✅ 187 contracts configured
- ✅ 1,204 events will be indexed
- ✅ 92 ABIs downloaded and cached

---

## 🤝 Getting Help

### Documentation
- **README.md** — Full documentation
- **USAGE_EXAMPLES.md** — 29 examples
- **ARCHITECTURE.md** — System design

### Resources
- Rindexer Docs: https://github.com/joshstevens19/rindexer
- The Graph: https://thegraph.com/explorer
- Etherscan API: https://docs.etherscan.io/

### Common Questions

**Q: Do I need API keys?**  
A: No, but they help avoid rate limits.

**Q: How long does generation take?**  
A: 30s-3min depending on protocols and cache.

**Q: Can I add custom protocols?**  
A: Yes! Edit `TOP_DEFI_PROTOCOLS` in the script.

**Q: Does it work without Docker?**  
A: Yes! Use the standalone script.

**Q: How do I update the config?**  
A: Just run the generator again.

---

## ✅ Checklist

Before you start:
- [ ] Python 3.10+ installed (or Docker)
- [ ] Internet connection available
- [ ] 4GB+ RAM available (for Docker)
- [ ] Ports 3001, 4000, 5432 available (for Docker)

After generation:
- [ ] `rindexer.yaml` exists
- [ ] `protocols.json` exists
- [ ] `abis/` directory has files
- [ ] YAML validates (no syntax errors)
- [ ] Rindexer starts successfully (Docker)

---

**You're all set! Start indexing DeFi positions across the ecosystem. 🎉**

Need help? Check the documentation or open an issue!

