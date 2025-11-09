# ⚡ Quick Start Guide

Get up and running in **2 minutes**.

## 🚀 Fastest Way (Standalone)

```bash
# 1. Install dependencies
pip install requests PyYAML

# 2. Run generator
python generate_rindexer_yaml.py

# 3. Done! Check output
ls rindexer_project/
```

## 🐳 Docker Way (Full Stack)

```bash
# 1. Start everything
docker-compose up -d

# 2. Wait ~2 minutes for generation
docker-compose logs -f generator

# 3. Access GraphQL playground
open http://localhost:4000
```

## 📝 What You Get

```
rindexer_project/
├── rindexer.yaml          # Ready-to-use config
├── protocols.json         # Discovered protocols
└── abis/                  # All ABIs (auto-downloaded)
    ├── aave-v3_ethereum.json
    ├── uniswap-v3_polygon.json
    └── ...
```

## 🎯 Next Steps

### Use with Rindexer

```bash
cd rindexer_project
rindexer start
```

### Query GraphQL

```bash
curl http://localhost:3001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ supplies { id user amount } }"}'
```

### Customize

```bash
# Generate for specific chains
python generate_rindexer_yaml.py --chains ethereum,polygon

# Limit protocols
python generate_rindexer_yaml.py --max-protocols 10

# Change output directory
python generate_rindexer_yaml.py --output ./my_indexer
```

## 🔑 Optional: Add API Keys

For better rate limits:

```bash
# Copy template
cp env.example .env

# Edit with your keys
nano .env

# Run with keys
docker-compose up -d
```

## 💡 Pro Tips

1. **First run takes ~2-3 minutes** (downloading ABIs)
2. **Second run takes ~10 seconds** (everything cached)
3. **Use `--parallel 10`** for faster generation
4. **Check logs** if something fails: `docker-compose logs generator`

## ❓ Troubleshooting

**Generator stuck?**
```bash
docker-compose logs generator
```

**Rindexer not starting?**
```bash
# Check if Postgres is ready
docker-compose logs postgres
```

**Need to regenerate?**
```bash
# Clear cache and restart
rm -rf .cache
docker-compose restart generator
```

---

**That's it! You're indexing DeFi positions across 5 chains. 🎉**
