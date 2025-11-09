#!/usr/bin/env python3
"""
Update app.py with all discovered Aave V3 tokens
"""
import json
import re

# Read discovered tokens
with open('aave_tokens_discovered.json') as f:
    data = json.load(f)

tokens = data['tokens']
prices_needed = data['prices_needed']

# Read current app.py
with open('app.py') as f:
    app_content = f.read()

# CoinGecko price mappings
coingecko_mappings = {
    'AAVE': 'aave',
    'AGEUR': 'ageur',
    'ARB': 'arbitrum',
    'BAL': 'balancer',
    'BTCB': 'bitcoin',
    'CAKE': 'pancakeswap-token',
    'CBETH': 'coinbase-wrapped-staked-eth',
    'CRV': 'curve-dao-token',
    'DAI': 'dai',
    'DPI': 'defipulse-index',
    'ETH': 'ethereum',
    'EURS': 'stasis-eurs',
    'FDUSD': 'first-digital-usd',
    'FRAX': 'frax',
    'GHST': 'aavegotchi',
    'JEUR': 'jarvis-synthetic-euro',
    'LDO': 'lido-dao',
    'LINK': 'chainlink',
    'LUSD': 'liquity-usd',
    'MAI': 'mimatic',
    'MATICX': 'stader-maticx',
    'MKR': 'maker',
    'RETH': 'rocket-pool-eth',
    'SAVAX': 'benqi-liquid-staked-avax',
    'SNX': 'havven',
    'STMATIC': 'lido-staked-matic',
    'SUSHI': 'sushi',
    'TBTC': 'bitcoin',
    'UNI': 'uniswap',
    'USDC': 'usd-coin',
    'USDCN': 'usd-coin',
    'USDCE': 'usd-coin',
    'USDT': 'tether',
    'WAVAX': 'avalanche-2',
    'WBNB': 'binancecoin',
    'WBTC': 'wrapped-bitcoin',
    'WETH': 'ethereum',
    'WETHE': 'ethereum',
    'WMATIC': 'matic-network',
    'WSTETH': 'wrapped-steth',
}

# Generate new Aave sections for each chain
def generate_aave_section(chain_name, chain_data):
    lines = []
    lines.append(f"        # Aave V3 aTokens (Supply/Lend positions)")
    lines.append(f"        'aave': {{")
    for token_name, address in sorted(chain_data['aave'].items()):
        lines.append(f"            '{token_name}': '{address}',")
    lines.append(f"        }},")
    lines.append(f"        # Aave V3 Variable Debt Tokens (Borrow positions)")
    lines.append(f"        'aave_debt': {{")
    for token_name, address in sorted(chain_data['aave_debt'].items()):
        lines.append(f"            '{token_name}': '{address}',")
    lines.append(f"        }},")
    return '\n'.join(lines)

# For each chain, replace the Aave sections
for chain in ['ethereum', 'arbitrum', 'polygon', 'avalanche', 'bsc']:
    if chain in tokens:
        new_aave_section = generate_aave_section(chain, tokens[chain])
        
        # Pattern to match Aave section for this chain
        # Match from "# Aave V3 aTokens" to the next protocol or end of chain
        pattern = rf"(    '{chain}': \{{[\s\S]*?)(        # Aave V3.*?'aave_debt': \{{[\s\S]*?\}},)([\s\S]*?)(        # [A-Z]|\    \}})"
        
        def replacer(match):
            return match.group(1) + new_aave_section + '\n' + match.group(4)
        
        app_content = re.sub(pattern, replacer, app_content)

# Update price mappings
# Find the symbol_to_coingecko dictionary
price_pattern = r"(symbol_to_coingecko = \{)([\s\S]*?)(\n    \})"

def update_prices(match):
    # Generate new price mapping
    lines = [match.group(1)]
    for symbol in sorted(coingecko_mappings.keys()):
        coingecko_id = coingecko_mappings[symbol]
        lines.append(f"\n        '{symbol}': '{coingecko_id}',")
    lines.append(match.group(3))
    return ''.join(lines)

app_content = re.sub(price_pattern, update_prices, app_content)

# Write updated content
with open('app.py', 'w') as f:
    f.write(app_content)

print("✅ app.py updated successfully!")
print(f"📊 Added {sum(len(chain_data['aave']) for chain_data in tokens.values())} supply tokens")
print(f"📊 Added {sum(len(chain_data['aave_debt']) for chain_data in tokens.values())} debt tokens")
print(f"💰 Added {len(coingecko_mappings)} price mappings")

