"""
Advanced Configuration for DeFi Indexer Generator

This file contains extended protocol definitions, custom event mappings,
and advanced configuration options.
"""

# Extended protocol list with more detailed configurations
EXTENDED_PROTOCOLS = {
    # === LENDING PROTOCOLS ===
    'aave-v2': {
        'name': 'Aave V2',
        'category': 'lending',
        'events': ['Deposit', 'Withdraw', 'Borrow', 'Repay', 'LiquidationCall', 'FlashLoan'],
        'contracts': {
            'ethereum': {
                'LendingPool': '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9',
                'LendingPoolAddressesProvider': '0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5'
            },
            'polygon': {
                'LendingPool': '0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf'
            },
            'avalanche': {
                'LendingPool': '0x4F01AeD16D97E3aB5ab2B501154DC9bb0F1A5A2C'
            }
        }
    },
    'morpho': {
        'name': 'Morpho',
        'category': 'lending',
        'events': ['Supplied', 'Withdrawn', 'Borrowed', 'Repaid'],
        'contracts': {
            'ethereum': {
                'MorphoAaveV3': '0x33333aea097c193e66081E930c33020272b33333'
            }
        }
    },
    'spark': {
        'name': 'Spark Protocol',
        'category': 'lending',
        'events': ['Supply', 'Withdraw', 'Borrow', 'Repay'],
        'contracts': {
            'ethereum': {
                'Pool': '0xC13e21B648A5Ee794902342038FF3aDAB66BE987'
            }
        }
    },
    
    # === DEX PROTOCOLS ===
    'uniswap-v2': {
        'name': 'Uniswap V2',
        'category': 'dex',
        'events': ['Mint', 'Burn', 'Swap', 'Sync'],
        'contracts': {
            'ethereum': {
                'Factory': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
                'Router': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
            }
        }
    },
    'sushiswap': {
        'name': 'SushiSwap',
        'category': 'dex',
        'events': ['Mint', 'Burn', 'Swap', 'Sync'],
        'contracts': {
            'ethereum': {
                'Factory': '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac'
            },
            'arbitrum': {
                'Factory': '0xc35DADB65012eC5796536bD9864eD8773aBc74C4'
            },
            'polygon': {
                'Factory': '0xc35DADB65012eC5796536bD9864eD8773aBc74C4'
            }
        }
    },
    'pancakeswap': {
        'name': 'PancakeSwap',
        'category': 'dex',
        'events': ['Mint', 'Burn', 'Swap', 'Sync'],
        'contracts': {
            'ethereum': {
                'Factory': '0x1097053Fd2ea711dad45caCcc45EfF7548fCB362'
            }
        }
    },
    'trader-joe': {
        'name': 'Trader Joe',
        'category': 'dex',
        'events': ['Mint', 'Burn', 'Swap'],
        'contracts': {
            'avalanche': {
                'Factory': '0x9Ad6C38BE94206cA50bb0d90783181662f0Cfa10'
            },
            'arbitrum': {
                'Factory': '0xaE4EC9901c3076D0DdBe76A520F9E90a6227aCB7'
            }
        }
    },
    
    # === STAKING PROTOCOLS ===
    'frax-ether': {
        'name': 'Frax Ether',
        'category': 'staking',
        'events': ['Deposit', 'Withdraw', 'Transfer'],
        'contracts': {
            'ethereum': {
                'sfrxETH': '0xac3E018457B222d93114458476f3E3416Abbe38F'
            }
        }
    },
    'stakewise': {
        'name': 'StakeWise',
        'category': 'staking',
        'events': ['Staked', 'Redeemed'],
        'contracts': {
            'ethereum': {
                'StakedEthToken': '0xFe2e637202056d30016725477c5da089Ab0A043A'
            }
        }
    },
    
    # === YIELD AGGREGATORS ===
    'beefy': {
        'name': 'Beefy Finance',
        'category': 'vault',
        'events': ['Deposit', 'Withdraw'],
        'contracts': {
            'polygon': {
                'BeefyVaultV6': '0x...'  # Multiple vaults
            },
            'arbitrum': {
                'BeefyVaultV6': '0x...'
            },
            'avalanche': {
                'BeefyVaultV6': '0x...'
            }
        }
    },
    
    # === PERPETUALS ===
    'gains-network': {
        'name': 'Gains Network',
        'category': 'perp',
        'events': ['MarketExecuted', 'LimitExecuted'],
        'contracts': {
            'arbitrum': {
                'Trading': '0x...'
            },
            'polygon': {
                'Trading': '0x...'
            }
        }
    },
    'kwenta': {
        'name': 'Kwenta',
        'category': 'perp',
        'events': ['PositionModified', 'PositionLiquidated'],
        'contracts': {
            'optimism': {
                'FuturesMarketManager': '0x...'
            }
        }
    },
    
    # === LIQUID STAKING DERIVATIVES ===
    'ankr': {
        'name': 'Ankr',
        'category': 'staking',
        'events': ['Staked', 'Unstaked'],
        'contracts': {
            'ethereum': {
                'ankrETH': '0xE95A203B1a91a908F9B9CE46459d101078c2c3cb'
            }
        }
    },
    'stader': {
        'name': 'Stader',
        'category': 'staking',
        'events': ['Deposit', 'Withdraw'],
        'contracts': {
            'ethereum': {
                'ETHx': '0xA35b1B31Ce002FBF2058D22F30f95D405200A15b'
            }
        }
    },
    
    # === OPTIONS ===
    'lyra': {
        'name': 'Lyra',
        'category': 'options',
        'events': ['Trade', 'PositionOpened', 'PositionClosed'],
        'contracts': {
            'optimism': {
                'OptionMarket': '0x...'
            },
            'arbitrum': {
                'OptionMarket': '0x...'
            }
        }
    },
    
    # === REAL WORLD ASSETS ===
    'maple': {
        'name': 'Maple Finance',
        'category': 'lending',
        'events': ['Deposit', 'Withdraw', 'FundLoan'],
        'contracts': {
            'ethereum': {
                'Pool': '0x...'
            }
        }
    },
    
    # === BRIDGES ===
    'stargate': {
        'name': 'Stargate',
        'category': 'bridge',
        'events': ['Swap', 'AddLiquidity', 'RemoveLiquidity'],
        'contracts': {
            'ethereum': {
                'Router': '0x8731d54E9D02c286767d56ac03e8037C07e01e98'
            },
            'arbitrum': {
                'Router': '0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614'
            },
            'polygon': {
                'Router': '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd'
            },
            'optimism': {
                'Router': '0xB0D502E938ed5f4df2E681fE6E419ff29631d62b'
            },
            'avalanche': {
                'Router': '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd'
            },
            'base': {
                'Router': '0x45f1A95A4D3f3836523F5c83673c797f4d4d263B'
            }
        }
    }
}

# Event signature mappings for accurate ABI parsing
EVENT_SIGNATURES = {
    # Aave V2/V3
    'Deposit': 'event Deposit(address indexed reserve, address user, address indexed onBehalfOf, uint256 amount, uint16 indexed referral)',
    'Supply': 'event Supply(address indexed reserve, address user, address indexed onBehalfOf, uint256 amount, uint16 indexed referral)',
    'Withdraw': 'event Withdraw(address indexed reserve, address indexed user, address indexed to, uint256 amount)',
    'Borrow': 'event Borrow(address indexed reserve, address user, address indexed onBehalfOf, uint256 amount, uint256 borrowRateMode, uint256 borrowRate, uint16 indexed referral)',
    'Repay': 'event Repay(address indexed reserve, address indexed user, address indexed repayer, uint256 amount)',
    'LiquidationCall': 'event LiquidationCall(address indexed collateralAsset, address indexed debtAsset, address indexed user, uint256 debtToCover, uint256 liquidatedCollateralAmount, address liquidator, bool receiveAToken)',
    'FlashLoan': 'event FlashLoan(address indexed target, address indexed initiator, address indexed asset, uint256 amount, uint256 premium, uint16 referralCode)',
    
    # Uniswap V2/V3
    'Mint': 'event Mint(address indexed sender, uint256 amount0, uint256 amount1)',
    'Burn': 'event Burn(address indexed sender, uint256 amount0, uint256 amount1, address indexed to)',
    'Swap': 'event Swap(address indexed sender, uint256 amount0In, uint256 amount1In, uint256 amount0Out, uint256 amount1Out, address indexed to)',
    'Sync': 'event Sync(uint112 reserve0, uint112 reserve1)',
    
    # Curve
    'AddLiquidity': 'event AddLiquidity(address indexed provider, uint256[2] token_amounts, uint256[2] fees, uint256 invariant, uint256 token_supply)',
    'RemoveLiquidity': 'event RemoveLiquidity(address indexed provider, uint256[2] token_amounts, uint256[2] fees, uint256 token_supply)',
    'RemoveLiquidityOne': 'event RemoveLiquidityOne(address indexed provider, uint256 token_amount, uint256 coin_amount)',
    'TokenExchange': 'event TokenExchange(address indexed buyer, int128 sold_id, uint256 tokens_sold, int128 bought_id, uint256 tokens_bought)',
    
    # Staking
    'Staked': 'event Staked(address indexed user, uint256 amount, uint256 shares, address indexed referral)',
    'Unstaked': 'event Unstaked(address indexed user, uint256 amount)',
    'Submitted': 'event Submitted(address indexed sender, uint256 amount, address referral)',
    'Withdrawal': 'event Withdrawal(address indexed sender, uint256 amount)',
    
    # Vaults
    'DepositVault': 'event Deposit(address indexed caller, address indexed owner, uint256 assets, uint256 shares)',
    'WithdrawVault': 'event Withdraw(address indexed caller, address indexed receiver, address indexed owner, uint256 assets, uint256 shares)',
    
    # Balancer
    'PoolBalanceChanged': 'event PoolBalanceChanged(bytes32 indexed poolId, address indexed liquidityProvider, address[] tokens, int256[] deltas, uint256[] protocolFeeAmounts)',
    'PoolCreated': 'event PoolCreated(bytes32 indexed poolId, address indexed poolAddress)',
    
    # GMX
    'Stake': 'event Stake(address indexed account, address token, uint256 amount)',
    'Unstake': 'event Unstake(address indexed account, address token, uint256 amount)',
    
    # Compound
    'SupplyCollateral': 'event SupplyCollateral(address indexed from, address indexed dst, address indexed asset, uint amount)',
    'WithdrawCollateral': 'event WithdrawCollateral(address indexed src, address indexed to, address indexed asset, uint amount)',
    
    # Morpho
    'Supplied': 'event Supplied(address indexed caller, address indexed onBehalf, address indexed market, uint256 assets, uint256 shares)',
    'Withdrawn': 'event Withdrawn(address indexed caller, address indexed onBehalf, address indexed receiver, address indexed market, uint256 assets, uint256 shares)',
    'Borrowed': 'event Borrowed(address indexed caller, address indexed onBehalf, address indexed receiver, address indexed market, uint256 assets, uint256 shares)',
    'Repaid': 'event Repaid(address indexed caller, address indexed onBehalf, address indexed market, uint256 assets, uint256 shares)',
    
    # Stargate
    'SwapRemote': 'event SwapRemote(uint16 indexed chainId, bytes indexed srcAddress, uint256 nonce, uint256 srcPoolId, uint256 dstPoolId, uint256 dstGasForCall, uint256 amount, uint256 minAmount, address indexed to, bytes payload)',
    
    # Generic
    'Transfer': 'event Transfer(address indexed from, address indexed to, uint256 value)',
    'Approval': 'event Approval(address indexed owner, address indexed spender, uint256 value)',
    'RewardPaid': 'event RewardPaid(address indexed user, uint256 reward)'
}

# Chain-specific configurations
CHAIN_CONFIGS = {
    'ethereum': {
        'start_block': 12000000,  # DeFi summer start
        'block_time': 12,  # seconds
        'max_batch_size': 10000
    },
    'arbitrum': {
        'start_block': 1,
        'block_time': 0.25,
        'max_batch_size': 50000
    },
    'polygon': {
        'start_block': 11000000,
        'block_time': 2,
        'max_batch_size': 30000
    },
    'optimism': {
        'start_block': 1,
        'block_time': 2,
        'max_batch_size': 30000
    },
    'avalanche': {
        'start_block': 2000000,
        'block_time': 2,
        'max_batch_size': 30000
    },
    'base': {
        'start_block': 1,
        'block_time': 2,
        'max_batch_size': 30000
    }
}

# Protocol categories and their typical events
CATEGORY_EVENTS = {
    'lending': ['Supply', 'Withdraw', 'Borrow', 'Repay', 'LiquidationCall', 'Deposit'],
    'dex': ['Mint', 'Burn', 'Swap', 'AddLiquidity', 'RemoveLiquidity', 'TokenExchange'],
    'staking': ['Stake', 'Unstake', 'Staked', 'Unstaked', 'Submitted', 'Withdrawal', 'Deposit', 'Withdraw'],
    'vault': ['Deposit', 'Withdraw', 'RewardPaid'],
    'yield': ['Staked', 'Withdrawn', 'RewardPaid', 'Deposit', 'Withdraw'],
    'perp': ['PositionModified', 'PositionLiquidated', 'MarketExecuted', 'Trade'],
    'options': ['Trade', 'PositionOpened', 'PositionClosed'],
    'bridge': ['Swap', 'SwapRemote', 'AddLiquidity', 'RemoveLiquidity']
}

# Subgraph endpoints for The Graph queries
SUBGRAPH_ENDPOINTS = {
    'aave-v3': {
        'ethereum': 'https://api.thegraph.com/subgraphs/name/aave/protocol-v3',
        'arbitrum': 'https://api.thegraph.com/subgraphs/name/aave/protocol-v3-arbitrum',
        'polygon': 'https://api.thegraph.com/subgraphs/name/aave/protocol-v3-polygon',
        'optimism': 'https://api.thegraph.com/subgraphs/name/aave/protocol-v3-optimism',
        'avalanche': 'https://api.thegraph.com/subgraphs/name/aave/protocol-v3-avalanche'
    },
    'uniswap-v3': {
        'ethereum': 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
        'arbitrum': 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3-arbitrum',
        'polygon': 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3-polygon',
        'optimism': 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3-optimism'
    },
    'curve': {
        'ethereum': 'https://api.thegraph.com/subgraphs/name/messari/curve-finance-ethereum',
        'arbitrum': 'https://api.thegraph.com/subgraphs/name/messari/curve-finance-arbitrum',
        'polygon': 'https://api.thegraph.com/subgraphs/name/messari/curve-finance-polygon',
        'optimism': 'https://api.thegraph.com/subgraphs/name/messari/curve-finance-optimism'
    }
}

# Priority protocols (will be indexed first)
PRIORITY_PROTOCOLS = [
    'aave-v3',
    'uniswap-v3',
    'curve',
    'compound-v3',
    'lido',
    'balancer-v2'
]

# Protocols to skip (for testing or specific deployments)
SKIP_PROTOCOLS = []

# Custom indexing strategies
INDEXING_STRATEGIES = {
    'aave-v3': {
        'strategy': 'full',  # Index all events
        'batch_size': 5000,
        'priority': 'high'
    },
    'uniswap-v3': {
        'strategy': 'selective',  # Only position-related events
        'events_filter': ['Mint', 'Burn', 'IncreaseLiquidity', 'DecreaseLiquidity'],
        'batch_size': 10000,
        'priority': 'high'
    },
    'curve': {
        'strategy': 'full',
        'batch_size': 5000,
        'priority': 'medium'
    }
}

