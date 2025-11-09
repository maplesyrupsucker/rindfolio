#!/usr/bin/env python3
"""
Discover all Aave V3 tokens across all supported chains
"""
from web3 import Web3
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Aave V3 Pool addresses per chain
AAVE_V3_POOLS = {
    'ethereum': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
    'arbitrum': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
    'polygon': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
    'avalanche': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
    'bsc': '0x6807dc923806fE8Fd134338EABCA509979a7e0cB',
}

# RPC URLs
RPC_URLS = {
    'ethereum': os.getenv('ETHEREUM_RPC_URL', 'https://eth.llamarpc.com'),
    'arbitrum': os.getenv('ARB_RPC_URL', 'https://arb1.arbitrum.io/rpc'),
    'polygon': os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com'),
    'avalanche': os.getenv('AVAX_RPC_URL', 'https://api.avax.network/ext/bc/C/rpc'),
    'bsc': os.getenv('BSC_RPC_URL', 'https://bsc-dataseed1.binance.org'),
}

# Common tokens to check on each chain
COMMON_TOKENS = {
    'ethereum': {
        'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
        'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
        'AAVE': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
        'LINK': '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        'CBETH': '0xBe9895146f7AF43049ca1c1AE358B0541Ea49704',
        'RETH': '0xae78736Cd615f374D3085123A210448E74Fc6393',
        'tBTC': '0x18084fbA666a33d37592fA2633fD49a74DD93a88',
        'LUSD': '0x5f98805A4E8be255a32880FDeC7F6728C6568bA0',
        'CRV': '0xD533a949740bb3306d119CC777fa900bA034cd52',
        'LDO': '0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32',
        'BAL': '0xba100000625a3754423978a60c9317c58a424e3D',
        'UNI': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
        'SNX': '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F',
        'MKR': '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',
    },
    'arbitrum': {
        'USDC': '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
        'USDC.e': '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        'USDT': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
        'DAI': '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
        'WETH': '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
        'WBTC': '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
        'ARB': '0x912CE59144191C1204E64559FE8253a0e49E6548',
        'LINK': '0xf97f4df75117a78c1A5a0DBb814Af92458539FB4',
        'AAVE': '0xba5DdD1f9d7F570dc94a51479a000E3BCE967196',
        'EURS': '0xD22a58f79e9481D1a88e00c343885A588b34b68B',
        'wstETH': '0x5979D7b546E38E414F7E9822514be443A4800529',
        'rETH': '0xEC70Dcb4A1EFa46b8F2D97C310C9c4790ba5ffA8',
        'LUSD': '0x93b346b6BC2548dA6A1E7d98E9a421B42541425b',
    },
    'polygon': {
        'USDC': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
        'USDC.e': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
        'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
        'DAI': '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',
        'WETH': '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
        'WBTC': '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6',
        'WMATIC': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
        'AAVE': '0xD6DF932A45C0f255f85145f286eA0b292B21C90B',
        'LINK': '0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39',
        'CRV': '0x172370d5Cd63279eFa6d502DAB29171933a610AF',
        'BAL': '0x9a71012B13CA4d3D0Cdc72A177DF3ef03b0E76A3',
        'GHST': '0x385Eeac5cB85A38A9a07A70c73e0a3271CfB54A7',
        'SUSHI': '0x0b3F868E0BE5597D5DB7fEB59E1CADBb0fdDa50a',
        'jEUR': '0x4e3Decbb3645551B8A19f0eA1678079FCB33fB4c',
        'agEUR': '0xE0B52e49357Fd4DAf2c15e02058DCE6BC0057db4',
        'DPI': '0x85955046DF4668e1DD369D2DE9f3AEB98DD2A369',
        'stMATIC': '0x3A58a54C066FdC0f2D55FC9C89F0415C92eBf3C4',
        'MaticX': '0xfa68FB4628DFF1028CFEc22b4162FCcd0d45efb6',
        'wstETH': '0x03b54A6e9a984069379fae1a4fC4dBAE93B3bCCD',
    },
    'avalanche': {
        'USDC': '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
        'USDT': '0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7',
        'DAI.e': '0xd586E7F844cEa2F87f50152665BCbc2C279D8d70',
        'WAVAX': '0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7',
        'WETH.e': '0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB',
        'WBTC.e': '0x50b7545627a5162F82A992c33b87aDc75187B218',
        'AAVE.e': '0x63a72806098Bd3D9520cC43356dD78afe5D386D9',
        'LINK.e': '0x5947BB275c521040051D82396192181b413227A3',
        'sAVAX': '0x2b2C81e08f1Af8835a78Bb2A90AE924ACE0eA4bE',
        'FRAX': '0xD24C2Ad096400B6FBcd2ad8B24E7acBc21A1da64',
        'MAI': '0x5c49b268c9841AFF1Cc3B0a418ff5c3442eE3F3b',
        'BTCb': '0x152b9d0FdC40C096757F570A51E494bd4b943E50',
    },
    'bsc': {
        'USDC': '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
        'USDT': '0x55d398326f99059fF775485246999027B3197955',
        'BUSD': '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
        'WBNB': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
        'BTCB': '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c',
        'ETH': '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',
        'CAKE': '0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82',
        'XVS': '0xcF6BB5389c92Bdda8a3747Ddb454cB7a64626C63',
        'ADA': '0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47',
        'DOT': '0x7083609fCE4d1d8Dc0C979AAb8c869Ea2C873402',
        'LINK': '0xF8A0BF9cF54Bb92F17374d9e9A321E6a111a51bD',
        'AAVE': '0xfb6115445Bff7b52FeB98650C87f44907E58f802',
        'TUSD': '0x40af3827F39D0EAcBF4A168f8D4ee67c121D11c9',
        'FDUSD': '0xc5f0f7b66764F6ec8C8Dff7BA683102295E16409',
    }
}

# ABI for Aave V3 Pool
POOL_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "asset", "type": "address"}],
        "name": "getReserveData",
        "outputs": [
            {"internalType": "uint256", "name": "configuration", "type": "uint256"},
            {"internalType": "uint128", "name": "liquidityIndex", "type": "uint128"},
            {"internalType": "uint128", "name": "currentLiquidityRate", "type": "uint128"},
            {"internalType": "uint128", "name": "variableBorrowIndex", "type": "uint128"},
            {"internalType": "uint128", "name": "currentVariableBorrowRate", "type": "uint128"},
            {"internalType": "uint128", "name": "currentStableBorrowRate", "type": "uint128"},
            {"internalType": "uint40", "name": "lastUpdateTimestamp", "type": "uint40"},
            {"internalType": "uint16", "name": "id", "type": "uint16"},
            {"internalType": "address", "name": "aTokenAddress", "type": "address"},
            {"internalType": "address", "name": "stableDebtTokenAddress", "type": "address"},
            {"internalType": "address", "name": "variableDebtTokenAddress", "type": "address"},
            {"internalType": "address", "name": "interestRateStrategyAddress", "type": "address"},
            {"internalType": "uint128", "name": "accruedToTreasury", "type": "uint128"},
            {"internalType": "uint128", "name": "unbacked", "type": "uint128"},
            {"internalType": "uint128", "name": "isolationModeTotalDebt", "type": "uint128"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
]

def discover_aave_tokens():
    """Discover all Aave V3 tokens across all chains"""
    all_tokens = {}
    all_prices_needed = set()
    
    for chain, pool_address in AAVE_V3_POOLS.items():
        print(f"\n{'='*60}")
        print(f"🔍 Discovering Aave V3 tokens on {chain.upper()}")
        print(f"{'='*60}")
        
        try:
            w3 = Web3(Web3.HTTPProvider(RPC_URLS[chain], request_kwargs={'timeout': 15}))
            if not w3.is_connected():
                print(f"❌ Could not connect to {chain}")
                continue
            
            pool = w3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=POOL_ABI)
            
            chain_tokens = {
                'aave': {},
                'aave_debt': {}
            }
            
            tokens_to_check = COMMON_TOKENS.get(chain, {})
            print(f"\n📊 Checking {len(tokens_to_check)} tokens...")
            
            for symbol, token_address in tokens_to_check.items():
                try:
                    reserve_data = pool.functions.getReserveData(Web3.to_checksum_address(token_address)).call()
                    atoken_address = reserve_data[8]
                    variable_debt_token = reserve_data[10]
                    
                    # Check if the reserve is active (aToken address is not zero)
                    if atoken_address != '0x0000000000000000000000000000000000000000':
                        # Get aToken symbol
                        try:
                            atoken_contract = w3.eth.contract(address=Web3.to_checksum_address(atoken_address), abi=ERC20_ABI)
                            atoken_symbol = atoken_contract.functions.symbol().call()
                        except:
                            # Construct symbol if we can't read it
                            chain_prefix = {
                                'ethereum': 'aEth',
                                'arbitrum': 'aArb',
                                'polygon': 'aPol',
                                'avalanche': 'aAva',
                                'bsc': 'aBsc'
                            }
                            atoken_symbol = f"{chain_prefix.get(chain, 'a')}{symbol.replace('.e', '').replace('.', '')}"
                        
                        # Get debt token symbol
                        try:
                            debt_contract = w3.eth.contract(address=Web3.to_checksum_address(variable_debt_token), abi=ERC20_ABI)
                            debt_symbol = debt_contract.functions.symbol().call()
                        except:
                            chain_prefix = {
                                'ethereum': 'variableDebtEth',
                                'arbitrum': 'variableDebtArb',
                                'polygon': 'variableDebtPol',
                                'avalanche': 'variableDebtAva',
                                'bsc': 'variableDebtBsc'
                            }
                            debt_symbol = f"{chain_prefix.get(chain, 'variableDebt')}{symbol.replace('.e', '').replace('.', '')}"
                        
                        chain_tokens['aave'][atoken_symbol] = atoken_address
                        chain_tokens['aave_debt'][debt_symbol] = variable_debt_token
                        
                        # Track underlying token for price mapping
                        underlying = symbol.replace('.e', '').replace('.', '').upper()
                        all_prices_needed.add(underlying)
                        
                        print(f"  ✅ {symbol:12} → aToken: {atoken_symbol:20} | Debt: {debt_symbol}")
                    
                except Exception as e:
                    # Token not in Aave V3 on this chain
                    pass
            
            all_tokens[chain] = chain_tokens
            print(f"\n📈 Found {len(chain_tokens['aave'])} supply tokens and {len(chain_tokens['aave_debt'])} debt tokens on {chain}")
            
        except Exception as e:
            print(f"❌ Error discovering tokens on {chain}: {e}")
    
    return all_tokens, all_prices_needed

def generate_python_config(all_tokens, all_prices_needed):
    """Generate Python configuration code"""
    print(f"\n{'='*60}")
    print("📝 Generating Python Configuration")
    print(f"{'='*60}\n")
    
    # Generate DEFI_PROTOCOLS section
    print("# Add this to DEFI_PROTOCOLS in app.py:\n")
    print("DEFI_PROTOCOLS = {")
    
    for chain, protocols in all_tokens.items():
        print(f"    '{chain}': {{")
        
        # Supply tokens
        print(f"        # Aave V3 aTokens (Supply/Lend positions)")
        print(f"        'aave': {{")
        for token_name, address in sorted(protocols['aave'].items()):
            print(f"            '{token_name}': '{address}',")
        print(f"        }},")
        
        # Debt tokens
        print(f"        # Aave V3 Variable Debt Tokens (Borrow positions)")
        print(f"        'aave_debt': {{")
        for token_name, address in sorted(protocols['aave_debt'].items()):
            print(f"            '{token_name}': '{address}',")
        print(f"        }},")
        
        print(f"    }},")
    
    print("}\n")
    
    # Generate price mapping additions
    print("\n# Add these to symbol_to_coingecko in get_token_price_simple():\n")
    
    # Common CoinGecko mappings
    coingecko_mappings = {
        'USDC': 'usd-coin',
        'USDCE': 'usd-coin',
        'USDT': 'tether',
        'DAI': 'dai',
        'DAIE': 'dai',
        'BUSD': 'binance-usd',
        'WETH': 'ethereum',
        'WETHE': 'ethereum',
        'ETH': 'ethereum',
        'WBTC': 'wrapped-bitcoin',
        'WBTCE': 'wrapped-bitcoin',
        'BTCB': 'bitcoin',
        'TBTC': 'bitcoin',
        'AAVE': 'aave',
        'AAVEE': 'aave',
        'LINK': 'chainlink',
        'LINKE': 'chainlink',
        'ARB': 'arbitrum',
        'MATIC': 'matic-network',
        'WMATIC': 'matic-network',
        'AVAX': 'avalanche-2',
        'WAVAX': 'avalanche-2',
        'SAVAX': 'benqi-liquid-staked-avax',
        'BNB': 'binancecoin',
        'WBNB': 'binancecoin',
        'CAKE': 'pancakeswap-token',
        'CRV': 'curve-dao-token',
        'BAL': 'balancer',
        'SUSHI': 'sushi',
        'UNI': 'uniswap',
        'SNX': 'havven',
        'MKR': 'maker',
        'LDO': 'lido-dao',
        'CBETH': 'coinbase-wrapped-staked-eth',
        'RETH': 'rocket-pool-eth',
        'WSTETH': 'wrapped-steth',
        'STETH': 'staked-ether',
        'STMATIC': 'lido-staked-matic',
        'MATICX': 'stader-maticx',
        'LUSD': 'liquity-usd',
        'FRAX': 'frax',
        'MAI': 'mimatic',
        'GHST': 'aavegotchi',
        'DPI': 'defipulse-index',
        'JEUR': 'jarvis-synthetic-euro',
        'AGEUR': 'ageur',
        'EURS': 'stasis-eurs',
        'XVS': 'venus',
        'ADA': 'cardano',
        'DOT': 'polkadot',
        'TUSD': 'true-usd',
        'FDUSD': 'first-digital-usd',
    }
    
    print("symbol_to_coingecko = {")
    for symbol in sorted(all_prices_needed):
        coingecko_id = coingecko_mappings.get(symbol, f"'{symbol.lower()}'  # VERIFY THIS ID")
        print(f"    '{symbol}': '{coingecko_id}',")
    print("}\n")

if __name__ == "__main__":
    print("🚀 Aave V3 Token Discovery Tool")
    print("="*60)
    
    all_tokens, all_prices_needed = discover_aave_tokens()
    
    # Save to JSON
    output = {
        'tokens': all_tokens,
        'prices_needed': sorted(list(all_prices_needed))
    }
    
    output_file = '/Users/slavid/Documents/GitHub/rindfolio/evm-balance-checker/aave_tokens_discovered.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Saved discovery results to: {output_file}")
    
    # Generate configuration
    generate_python_config(all_tokens, all_prices_needed)
    
    print("\n✅ Discovery complete!")
    print(f"📊 Total unique underlying tokens needing prices: {len(all_prices_needed)}")

