#!/usr/bin/env python3
"""
EVM Balance Checker - Multi-chain balance, DeFi positions, and transaction history
Supports: Ethereum, Arbitrum, Polygon, Avalanche, BNB Chain
"""

from flask import Flask, render_template, request, jsonify
from web3 import Web3
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

app = Flask(__name__)

# Multi-chain RPC Configuration
CHAINS = {
    'ethereum': {
        'name': 'Ethereum',
        'chain_id': 1,
        'rpc': os.getenv('ETH_RPC_URL', 'https://eth.llamarpc.com'),
        'explorer': 'https://etherscan.io',
        'native_token': 'ETH',
        'coingecko_id': 'ethereum'
    },
    'arbitrum': {
        'name': 'Arbitrum',
        'chain_id': 42161,
        'rpc': os.getenv('ARB_RPC_URL', 'https://arb1.arbitrum.io/rpc'),
        'explorer': 'https://arbiscan.io',
        'native_token': 'ETH',
        'coingecko_id': 'ethereum'
    },
    'polygon': {
        'name': 'Polygon',
        'chain_id': 137,
        'rpc': os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com'),
        'explorer': 'https://polygonscan.com',
        'native_token': 'MATIC',
        'coingecko_id': 'matic-network'
    },
    'avalanche': {
        'name': 'Avalanche',
        'chain_id': 43114,
        'rpc': os.getenv('AVAX_RPC_URL', 'https://api.avax.network/ext/bc/C/rpc'),
        'explorer': 'https://snowtrace.io',
        'native_token': 'AVAX',
        'coingecko_id': 'avalanche-2'
    },
    'bsc': {
        'name': 'BNB Chain',
        'chain_id': 56,
        'rpc': os.getenv('BSC_RPC_URL', 'https://bsc-dataseed1.binance.org'),
        'explorer': 'https://bscscan.com',
        'native_token': 'BNB',
        'coingecko_id': 'binancecoin'
    }
}

# Initialize Web3 instances for each chain
web3_instances = {}
for chain, config in CHAINS.items():
    try:
        web3_instances[chain] = Web3(Web3.HTTPProvider(config['rpc'], request_kwargs={'timeout': 10}))
    except Exception as e:
        print(f"Failed to initialize {chain}: {e}")

# Token addresses per chain
TOKENS_BY_CHAIN = {
    'ethereum': {
        'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
        'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
        'AAVE': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
        'UNI': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
        'LINK': '0x514910771AF9Ca656af840dff83E8264EcF986CA',
    },
    'arbitrum': {
        'USDC': '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
        'USDT': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
        'DAI': '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
        'WETH': '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
        'WBTC': '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
        'ARB': '0x912CE59144191C1204E64559FE8253a0e49E6548',
        'LINK': '0xf97f4df75117a78c1A5a0DBb814Af92458539FB4',
    },
    'polygon': {
        'USDC': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
        'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
        'DAI': '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',
        'WETH': '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
        'WBTC': '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6',
        'WMATIC': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
        'AAVE': '0xD6DF932A45C0f255f85145f286eA0b292B21C90B',
    },
    'avalanche': {
        'USDC': '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
        'USDT': '0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7',
        'DAI': '0xd586E7F844cEa2F87f50152665BCbc2C279D8d70',
        'WAVAX': '0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7',
        'WETH': '0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB',
        'WBTC': '0x50b7545627a5162F82A992c33b87aDc75187B218',
        'AAVE': '0x63a72806098Bd3D9520cC43356dD78afe5D386D9',
    },
    'bsc': {
        'USDC': '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
        'USDT': '0x55d398326f99059fF775485246999027B3197955',
        'DAI': '0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3',
        'WBNB': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
        'BTCB': '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c',
        'ETH': '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',
        'CAKE': '0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82',
    }
}

# DeFi Protocol Addresses
DEFI_PROTOCOLS = {
    'ethereum': {
        # Aave V3 aTokens (Supply/Lend positions) - Auto-discovered
        'aave': {
            'aEthAAVE': '0xA700b4eB416Be35b2911fd5Dee80678ff64fF6C9',
            'aEthBAL': '0x2516E7B3F76294e03C42AA4c5b5b4DCE9C436fB8',
            'aEthCRV': '0x7B95Ec873268a6BFC6427e7a28e396Db9D0ebc65',
            'aEthDAI': '0x018008bfb33d285247A21d44E50697654f754e63',
            'aEthLDO': '0x9A44fd41566876A39655f74971a3A6eA0a17a454',
            'aEthLINK': '0x5E8C8A7243651DB1384C0dDfDbE39761E8e7E51a',
            'aEthLUSD': '0x3Fe6a295459FAe07DF8A0ceCC36F37160FE86AA9',
            'aEthMKR': '0x8A458A9dc9048e005d22849F470891b840296619',
            'aEthSNX': '0xC7B4c17861357B8ABB91F25581E7263E08DCB59c',
            'aEthUNI': '0xF6D2224916DDFbbab6e6bd0D1B7034f4Ae0CaB18',
            'aEthUSDC': '0x98C23E9d8f34FEFb1B7BD6a91B7FF122F4e16F5c',
            'aEthUSDT': '0x23878914EFE38d27C4D67Ab83ed1b93A74D4086a',
            'aEthWBTC': '0x5Ee5bf7ae06D1Be5997A1A72006FE6C607eC6DE8',
            'aEthWETH': '0x4d5F47FA6A74757f35C14fD3a6Ef8E3C9BC514E8',
            'aEthcbETH': '0x977b6fc5dE62598B08C85AC8Cf2b745874E8b78c',
            'aEthrETH': '0xCc9EE9483f662091a1de4795249E24aC0aC2630f',
            'aEthtBTC': '0x10Ac93971cdb1F5c778144084242374473c350Da',
        },
        # Aave V3 Variable Debt Tokens (Borrow positions) - Auto-discovered
        'aave_debt': {
            'variableDebtEthAAVE': '0xBae535520Abd9f8C85E58929e0006A2c8B372F74',
            'variableDebtEthBAL': '0x3D3efceb4Ff0966D34d9545D3A2fa2dcdBf451f2',
            'variableDebtEthCRV': '0x1b7D3F4b3c032a5AE656e30eeA4e8E1Ba376068F',
            'variableDebtEthDAI': '0xcF8d0c70c850859266f5C338b38F9D663181C314',
            'variableDebtEthLDO': '0xc30808705C01289A3D306ca9CAB081Ba9114eC82',
            'variableDebtEthLINK': '0x4228F8895C7dDA20227F6a5c6751b8Ebf19a6ba8',
            'variableDebtEthLUSD': '0x33652e48e4B74D18520f11BfE58Edd2ED2cEc5A2',
            'variableDebtEthMKR': '0x6Efc73E54E41b27d2134fF9f98F15550f30DF9B1',
            'variableDebtEthSNX': '0x8d0de040e8aAd872eC3c33A3776dE9152D3c34ca',
            'variableDebtEthUNI': '0xF64178Ebd2E2719F2B1233bCb5Ef6DB4bCc4d09a',
            'variableDebtEthUSDC': '0x72E95b8931767C79bA4EeE721354d6E99a61D004',
            'variableDebtEthUSDT': '0x6df1C1E379bC5a00a7b4C6e67A203333772f45A8',
            'variableDebtEthWBTC': '0x40aAbEf1aa8f0eEc637E0E7d92fbfFB2F26A8b7B',
            'variableDebtEthWETH': '0xeA51d7853EEFb32b6ee06b1C12E6dcCA88Be0fFE',
            'variableDebtEthcbETH': '0x0c91bcA95b5FE69164cE583A2ec9429A569798Ed',
            'variableDebtEthrETH': '0xae8593DD575FE29A9745056aA91C4b746eee62C8',
            'variableDebtEthtBTC': '0xAC50890a80A2731eb1eA2e9B4F29569CeB06D960',
        },
        # Compound V3 cTokens
        'compound': {
            'cUSDCv3': '0xc3d688B66703497DAA19211EEdff47f25384cdc3',
            'cWETHv3': '0xA17581A9E3356d9A858b789D68B4d866e593aE94',
        },
        # Uniswap V3 LP Positions (common pools)
        'uniswap_v3': {
            'USDC-WETH-005': '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640',  # 0.05% fee
            'USDC-WETH-03': '0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8',   # 0.3% fee
            'WBTC-WETH-03': '0xCBCdF9626bC03E24f779434178A73a0B4bad62eD',   # 0.3% fee
            'DAI-USDC-001': '0x5777d92f208679DB4b9778590Fa3CAB3aC9e2168',   # 0.01% fee
        },
        # Curve LP tokens
        'curve': {
            '3pool': '0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490',  # DAI+USDC+USDT
            'stETH': '0x06325440D014e39736583c165C2963BA99fAf14E',  # stETH/ETH
            'frxETH': '0xf43211935C781D5ca1a41d2041F397B8A7366C7A', # frxETH/ETH
        },
        # Lido Staking
        'lido': {
            'stETH': '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84',
            'wstETH': '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0',
        },
        # Rocket Pool
        'rocketpool': {
            'rETH': '0xae78736Cd615f374D3085123A210448E74Fc6393',
        },
        # Convex Finance
        'convex': {
            'cvxCRV': '0x62B9c7356A2Dc64a1969e19C23e4f579F9810Aa7',
            'CVX': '0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B',
        },
        # SushiSwap
        'sushiswap': {
            'SUSHI': '0x6B3595068778DD592e39A122f4f5a5cF09C90fE2',
            'xSUSHI': '0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272',
        },
        # Balancer
        'balancer': {
            'BAL': '0xba100000625a3754423978a60c9317c58a424e3D',
            'B-80BAL-20WETH': '0x5c6Ee304399DBdB9C8Ef030aB642B10820DB8F56',
        },
        # Yearn Finance Vaults
        'yearn': {
            'yvUSDC': '0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE',
            'yvDAI': '0xdA816459F1AB5631232FE5e97a05BBBb94970c95',
            'yvWETH': '0xa258C4606Ca8206D8aA700cE2143D7db854D168c',
        },
        # Frax Finance
        'frax': {
            'FRAX': '0x853d955aCEf822Db058eb8505911ED77F175b99e',
            'FXS': '0x3432B6A60D23Ca0dFCa7761B7ab56459D9C964D0',
            'sfrxETH': '0xac3E018457B222d93114458476f3E3416Abbe38F',
        },
        # Verse Staking (tBTC earn pool)
        'verse': {
            'stVERSE': '0xcBE5F4E8A112F25C2F902714E3cBB7955F19bb36',  # Verse staking contract
            'VERSE': '0x249cA82617eC3DfB2589c4c17ab7EC9765350a18',  # Verse token
            'vTeam': '0x78190e4c7c7b2c2c3b0562f1f155a1fc2f5160ca',  # vTeam token (1:1 with VERSE)
        },
    },
    'arbitrum': {
        # Aave V3 aTokens (Supply/Lend positions) - Auto-discovered
        'aave': {
            'aArbAAVE': '0xf329e36C7bF6E5E86ce2150875a84Ce77f477375',
            'aArbARB': '0x6533afac2E7BCCB20dca161449A13A32D391fb00',
            'aArbDAI': '0x82E64f49Ed5EC1bC6e43DAD4FC8Af9bb3A2312EE',
            'aArbEURS': '0x6d80113e533a2C0fe82EaBD35f1875DcEA89Ea97',
            'aArbLINK': '0x191c10Aa4AF7C30e871E70C95dB0E4eb77237530',
            'aArbLUSD': '0x8ffDf2DE812095b1D19CB146E4c004587C0A0692',
            'aArbUSDC': '0x625E7708f30cA75bfd92586e17077590C60eb4cD',
            'aArbUSDCn': '0x724dc807b04555b71ed48a6896b6F41593b8C637',
            'aArbUSDT': '0x6ab707Aca953eDAeFBc4fD23bA73294241490620',
            'aArbWBTC': '0x078f358208685046a11C85e8ad32895DED33A249',
            'aArbWETH': '0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8',
            'aArbrETH': '0x8Eb270e296023E9D92081fdF967dDd7878724424',
            'aArbwstETH': '0x513c7E3a9c69cA3e22550eF58AC1C0088e918FFf',
        },
        # Aave V3 Variable Debt Tokens (Borrow positions) - Auto-discovered
        'aave_debt': {
            'variableDebtArbAAVE': '0xE80761Ea617F66F96274eA5e8c37f03960ecC679',
            'variableDebtArbARB': '0x44705f578135cC5d703b4c9c122528C73Eb87145',
            'variableDebtArbDAI': '0x8619d80FB0141ba7F184CbF22fd724116D9f7ffC',
            'variableDebtArbEURS': '0x4a1c3aD6Ed28a636ee1751C69071f6be75DEb8B8',
            'variableDebtArbLINK': '0x953A573793604aF8d41F306FEb8274190dB4aE0e',
            'variableDebtArbLUSD': '0xA8669021776Bc142DfcA87c21b4A52595bCbB40a',
            'variableDebtArbUSDC': '0xFCCf3cAbbe80101232d343252614b6A3eE81C989',
            'variableDebtArbUSDCn': '0xf611aEb5013fD2c0511c9CD55c7dc5C1140741A6',
            'variableDebtArbUSDT': '0xfb00AC187a8Eb5AFAE4eACE434F493Eb62672df7',
            'variableDebtArbWBTC': '0x92b42c66840C7AD907b4BF74879FF3eF7c529473',
            'variableDebtArbWETH': '0x0c84331e39d6658Cd6e6b9ba04736cC4c4734351',
            'variableDebtArbrETH': '0xCE186F6Cccb0c955445bb9d10C59caE488Fea559',
            'variableDebtArbwstETH': '0x77CA01483f379E58174739308945f044e1a764dc',
        },
        # Uniswap V3
        'uniswap_v3': {
            'USDC-WETH-005': '0xC31E54c7a869B9FcBEcc14363CF510d1c41fa443',
            'ARB-WETH-005': '0xC6F780497A95e246EB9449f5e4770916DCd6396A',
        },
        # GMX Staking
        'gmx': {
            'GMX': '0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a',
            'GLP': '0x4277f8F2c384827B5273592FF7CeBd9f2C1ac258',
        },
        # SushiSwap Arbitrum
        'sushiswap': {
            'SUSHI': '0xd4d42F0b6DEF4CE0383636770eF773390d85c61A',
        },
        # Radiant Capital
        'radiant': {
            'RDNT': '0x3082CC23568eA640225c2467653dB90e9250AaA0',
        },
    },
    'polygon': {
        # Aave V3 aTokens (Supply/Lend positions) - Auto-discovered
        'aave': {
            'aPolAAVE': '0xf329e36C7bF6E5E86ce2150875a84Ce77f477375',
            'aPolAGEUR': '0x8437d7C167dFB82ED4Cb79CD44B7a32A1dd95c77',
            'aPolBAL': '0x8ffDf2DE812095b1D19CB146E4c004587C0A0692',
            'aPolCRV': '0x513c7E3a9c69cA3e22550eF58AC1C0088e918FFf',
            'aPolDAI': '0x82E64f49Ed5EC1bC6e43DAD4FC8Af9bb3A2312EE',
            'aPolDPI': '0x724dc807b04555b71ed48a6896b6F41593b8C637',
            'aPolGHST': '0x8Eb270e296023E9D92081fdF967dDd7878724424',
            'aPolJEUR': '0x6533afac2E7BCCB20dca161449A13A32D391fb00',
            'aPolLINK': '0x191c10Aa4AF7C30e871E70C95dB0E4eb77237530',
            'aPolMATICX': '0x80cA0d8C38d2e2BcbaB66aA1648Bd1C7160500FE',
            'aPolSTMATIC': '0xEA1132120ddcDDA2F119e99Fa7A27a0d036F7Ac9',
            'aPolSUSHI': '0xc45A479877e1e9Dfe9FcD4056c699575a1045dAA',
            'aPolUSDC': '0x625E7708f30cA75bfd92586e17077590C60eb4cD',
            'aPolUSDT': '0x6ab707Aca953eDAeFBc4fD23bA73294241490620',
            'aPolWBTC': '0x078f358208685046a11C85e8ad32895DED33A249',
            'aPolWETH': '0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8',
            'aPolWMATIC': '0x6d80113e533a2C0fe82EaBD35f1875DcEA89Ea97',
            'aPolwstETH': '0xf59036CAEBeA7dC4b86638DFA2E3C97dA9FcCd40',
        },
        # Aave V3 Variable Debt Tokens (Borrow positions) - Auto-discovered
        'aave_debt': {
            'variableDebtPolAAVE': '0xE80761Ea617F66F96274eA5e8c37f03960ecC679',
            'variableDebtPolAGEUR': '0x3ca5FA07689F266e907439aFd1fBB59c44fe12f6',
            'variableDebtPolBAL': '0xA8669021776Bc142DfcA87c21b4A52595bCbB40a',
            'variableDebtPolCRV': '0x77CA01483f379E58174739308945f044e1a764dc',
            'variableDebtPolDAI': '0x8619d80FB0141ba7F184CbF22fd724116D9f7ffC',
            'variableDebtPolDPI': '0xf611aEb5013fD2c0511c9CD55c7dc5C1140741A6',
            'variableDebtPolGHST': '0xCE186F6Cccb0c955445bb9d10C59caE488Fea559',
            'variableDebtPolJEUR': '0x44705f578135cC5d703b4c9c122528C73Eb87145',
            'variableDebtPolLINK': '0x953A573793604aF8d41F306FEb8274190dB4aE0e',
            'variableDebtPolMATICX': '0xB5b46F918C2923fC7f26DB76e8a6A6e9C4347Cf9',
            'variableDebtPolSTMATIC': '0x6b030Ff3FB9956B1B69f475B77aE0d3Cf2CC5aFa',
            'variableDebtPolSUSHI': '0x34e2eD44EF7466D5f9E0b782B5c08b57475e7907',
            'variableDebtPolUSDC': '0xFCCf3cAbbe80101232d343252614b6A3eE81C989',
            'variableDebtPolUSDT': '0xfb00AC187a8Eb5AFAE4eACE434F493Eb62672df7',
            'variableDebtPolWBTC': '0x92b42c66840C7AD907b4BF74879FF3eF7c529473',
            'variableDebtPolWETH': '0x0c84331e39d6658Cd6e6b9ba04736cC4c4734351',
            'variableDebtPolWMATIC': '0x4a1c3aD6Ed28a636ee1751C69071f6be75DEb8B8',
            'variableDebtPolwstETH': '0x77fA66882a8854d883101Fb8501BD3CaD347Fc32',
        },
        # Uniswap V3
        'uniswap_v3': {
            'USDC-WETH-005': '0xA374094527e1673A86dE625aa59517c5dE346d32',
            'WMATIC-USDC-005': '0xA374094527e1673A86dE625aa59517c5dE346d32',
        },
        # Curve
        'curve': {
            'am3CRV': '0xE7a24EF0C5e95Ffb0f6684b813A78F2a3AD7D171',  # aave pool
        },
        # Verse Staking (tBTC earn pool)
        'verse': {
            'stVERSE': '0x66b0FBbEb420B63155d61eC5922293148BB796ec',  # Verse staking contract on Polygon
            'VERSE': '0xc708D6F2153933DAa50B2D0758955Be0A93A8FEf',  # Verse token on Polygon
        },
    },
    'avalanche': {
        # Aave V3 aTokens (Supply/Lend positions) - Auto-discovered
        'aave': {
            'aAvaAAVE': '0xf329e36C7bF6E5E86ce2150875a84Ce77f477375',
            'aAvaBTC.b': '0x8ffDf2DE812095b1D19CB146E4c004587C0A0692',
            'aAvaDAI': '0x82E64f49Ed5EC1bC6e43DAD4FC8Af9bb3A2312EE',
            'aAvaFRAX': '0xc45A479877e1e9Dfe9FcD4056c699575a1045dAA',
            'aAvaLINK': '0x191c10Aa4AF7C30e871E70C95dB0E4eb77237530',
            'aAvaMAI': '0x8Eb270e296023E9D92081fdF967dDd7878724424',
            'aAvaSAVAX': '0x513c7E3a9c69cA3e22550eF58AC1C0088e918FFf',
            'aAvaUSDC': '0x625E7708f30cA75bfd92586e17077590C60eb4cD',
            'aAvaUSDT': '0x6ab707Aca953eDAeFBc4fD23bA73294241490620',
            'aAvaWAVAX': '0x6d80113e533a2C0fe82EaBD35f1875DcEA89Ea97',
            'aAvaWBTC': '0x078f358208685046a11C85e8ad32895DED33A249',
            'aAvaWETH': '0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8',
        },
        # Aave V3 Variable Debt Tokens (Borrow positions) - Auto-discovered
        'aave_debt': {
            'variableDebtAvaAAVE': '0xE80761Ea617F66F96274eA5e8c37f03960ecC679',
            'variableDebtAvaBTC.b': '0xA8669021776Bc142DfcA87c21b4A52595bCbB40a',
            'variableDebtAvaDAI': '0x8619d80FB0141ba7F184CbF22fd724116D9f7ffC',
            'variableDebtAvaFRAX': '0x34e2eD44EF7466D5f9E0b782B5c08b57475e7907',
            'variableDebtAvaLINK': '0x953A573793604aF8d41F306FEb8274190dB4aE0e',
            'variableDebtAvaMAI': '0xCE186F6Cccb0c955445bb9d10C59caE488Fea559',
            'variableDebtAvaSAVAX': '0x77CA01483f379E58174739308945f044e1a764dc',
            'variableDebtAvaUSDC': '0xFCCf3cAbbe80101232d343252614b6A3eE81C989',
            'variableDebtAvaUSDT': '0xfb00AC187a8Eb5AFAE4eACE434F493Eb62672df7',
            'variableDebtAvaWAVAX': '0x4a1c3aD6Ed28a636ee1751C69071f6be75DEb8B8',
            'variableDebtAvaWBTC': '0x92b42c66840C7AD907b4BF74879FF3eF7c529473',
            'variableDebtAvaWETH': '0x0c84331e39d6658Cd6e6b9ba04736cC4c4734351',
        },
        # Trader Joe
        'traderjoe': {
            'JOE': '0x6e84a6216eA6dACC71eE8E6b0a5B7322EEbC0fDd',
        },
    },
    'bsc': {
        # Aave V3 aTokens (Supply/Lend positions) - Auto-discovered
        'aave': {
            'aBnbBTCB': '0x56a7ddc4e848EbF43845854205ad71D5D5F72d3D',
            'aBnbCAKE': '0x4199CC1F5ed0d796563d7CcB2e036253E2C18281',
            'aBnbETH': '0x2E94171493fAbE316b6205f1585779C887771E2F',
            'aBnbFDUSD': '0x75bd1A659bdC62e4C313950d44A2416faB43E785',
            'aBnbUSDC': '0x00901a076785e0906d1028c7d6372d247bec7d61',
            'aBnbUSDT': '0xa9251ca9DE909CB71783723713B21E4233fbf1B1',
            'aBnbWBNB': '0x9B00a09492a626678E5A3009982191586C444Df9',
        },
        # Aave V3 Variable Debt Tokens (Borrow positions) - Auto-discovered
        'aave_debt': {
            'variableDebtBnbBTCB': '0x7b1E82F4f542fbB25D64c5523Fe3e44aBe4F2702',
            'variableDebtBnbCAKE': '0xE20dBC7119c635B1B51462f844861258770e0699',
            'variableDebtBnbETH': '0x8FDea7891b4D6dbdc746309245B316aF691A636C',
            'variableDebtBnbFDUSD': '0xE628B8a123e6037f1542e662B9F55141a16945C8',
            'variableDebtBnbUSDC': '0xcDBBEd5606d9c5C98eEedd67933991dC17F0c68d',
            'variableDebtBnbUSDT': '0xF8bb2Be50647447Fb355e3a77b81be4db64107cd',
            'variableDebtBnbWBNB': '0x0E76414d433ddfe8004d2A7505d218874875a996',
        },
        # Venus Protocol
        'venus': {
            'vUSDC': '0xecA88125a5ADbe82614ffC12D0DB554E2e2867C8',
            'vUSDT': '0xfD5840Cd36d94D7229439859C0112a4185BC0255',
            'vDAI': '0x334b3eCB4DCa3593BCCC3c7EBD1A1C1d1780FBF1',
            'vBNB': '0xA07c5b74C9B40447a954e1466938b865b6BBea36',
        },
        # PancakeSwap V3
        'pancakeswap': {
            'CAKE': '0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82',
        },
    }
}

# ERC20 ABI (minimal)
ERC20_ABI = json.loads('''[
    {"constant": true, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": true, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": true, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": true, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"}
]''')

# Price cache with timestamp
price_cache = {}
PRICE_CACHE_DURATION = 7200  # 2 hours

def get_token_price_by_coingecko(coingecko_id: str) -> float:
    """Get token price from CoinGecko with caching"""
    now = datetime.now().timestamp()
    
    # Check cache
    if coingecko_id in price_cache:
        cached_price, cached_time = price_cache[coingecko_id]
        if now - cached_time < PRICE_CACHE_DURATION:
            return cached_price
    
    try:
        response = requests.get(
            f'https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd',
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            # Check for rate limit or error response
            if 'status' in data and 'error_code' in data['status']:
                print(f"CoinGecko API error for {coingecko_id}: {data['status'].get('error_message', 'Unknown error')}")
            else:
                price = data.get(coingecko_id, {}).get('usd', 0)
                if price and price > 0:
                    price_cache[coingecko_id] = (price, now)
                    print(f"✅ CoinGecko price for {coingecko_id}: ${price}")
                    return price
    except Exception as e:
        print(f"CoinGecko API error for {coingecko_id}: {e}")
    
    # Fallback prices
    fallback = {
        'ethereum': 2000, 'matic-network': 0.8, 'avalanche-2': 30,
        'binancecoin': 300, 'usd-coin': 1, 'tether': 1, 'dai': 1,
        'tbtc': 102000, 'verse-bitcoin': 0.00005836
    }
    price = fallback.get(coingecko_id, 0)
    if price > 0:
        print(f"⚠️  Using fallback price for {coingecko_id}: ${price}")
    else:
        print(f"❌ No price available for {coingecko_id}")
    price_cache[coingecko_id] = (price, now)
    return price

def get_multiple_token_prices(symbols: list) -> dict:
    """Batch fetch multiple token prices from CoinGecko"""
    # Map symbols to CoinGecko IDs
    symbol_to_id = {
        'ETH': 'ethereum', 'WETH': 'ethereum',
        'USDC': 'usd-coin', 'USDT': 'tether', 'DAI': 'dai',
        'WBTC': 'wrapped-bitcoin', 'BTCB': 'wrapped-bitcoin',
        'AAVE': 'aave', 'UNI': 'uniswap', 'LINK': 'chainlink',
        'ARB': 'arbitrum', 'MATIC': 'matic-network', 'WMATIC': 'matic-network',
        'AVAX': 'avalanche-2', 'WAVAX': 'avalanche-2',
        'BNB': 'binancecoin', 'WBNB': 'binancecoin',
        'CAKE': 'pancakeswap-token', 'GMX': 'gmx', 'JOE': 'joe',
        'CRV': 'curve-dao-token', 'CVX': 'convex-finance',
        'SUSHI': 'sushi', 'BAL': 'balancer',
    }
    
    ids = ','.join(set(symbol_to_id.get(s, s.lower()) for s in symbols))
    
    try:
        response = requests.get(
            f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd',
            timeout=10
        )
        if response.status_code == 200:
            prices_data = response.json()
            result = {}
            for symbol in symbols:
                cg_id = symbol_to_id.get(symbol, symbol.lower())
                result[symbol] = prices_data.get(cg_id, {}).get('usd', 0)
            return result
    except Exception as e:
        print(f"Batch price fetch error: {e}")
    
    return {}

def get_native_balance(address: str, chain: str) -> Optional[Dict]:
    """Get native token balance"""
    try:
        w3 = web3_instances.get(chain)
        if not w3:
            return None
        
        chain_config = CHAINS[chain]
        checksum_address = Web3.to_checksum_address(address)
        balance_wei = w3.eth.get_balance(checksum_address)
        balance = float(w3.from_wei(balance_wei, 'ether'))
        
        if balance == 0:
            return None
        
        token_price = get_token_price_by_coingecko(chain_config['coingecko_id'])
        balance_usd = balance * token_price
        
        return {
            'chain': chain_config['name'],
            'symbol': chain_config['native_token'],
            'name': f"{chain_config['name']} Native",
            'balance': f"{balance:.6f}",
            'balance_usd': balance_usd,
            'type': 'wallet'
        }
    except Exception as e:
        print(f"Error getting native balance on {chain}: {e}")
        return None

def get_token_balance(address: str, token_address: str, token_symbol: str, chain: str) -> Optional[Dict]:
    """Get ERC20 token balance"""
    try:
        w3 = web3_instances.get(chain)
        if not w3:
            return None
        
        checksum_address = Web3.to_checksum_address(address)
        token_checksum = Web3.to_checksum_address(token_address)
        
        contract = w3.eth.contract(address=token_checksum, abi=ERC20_ABI)
        balance = contract.functions.balanceOf(checksum_address).call()
        
        if balance == 0:
            return None
        
        decimals = contract.functions.decimals().call()
        try:
            symbol = contract.functions.symbol().call()
            name = contract.functions.name().call()
        except:
            symbol = token_symbol
            name = token_symbol
        
        balance_formatted = balance / (10 ** decimals)
        
        # Get price (simplified)
        token_price = get_token_price_simple(symbol)
        balance_usd = balance_formatted * token_price
        
        return {
            'chain': CHAINS[chain]['name'],
            'symbol': symbol,
            'name': name,
            'balance': f"{balance_formatted:.6f}",
            'balance_usd': balance_usd,
            'type': 'wallet'
        }
    except Exception as e:
        print(f"Error getting {token_symbol} balance on {chain}: {e}")
        return None

def get_defi_position(address: str, token_address: str, token_name: str, protocol: str, chain: str) -> Optional[Dict]:
    """Get DeFi protocol position (aTokens, cTokens, LP tokens, staked tokens, debt tokens, etc.)"""
    try:
        print(f"Checking {protocol} position: {token_name} on {chain}")
        w3 = web3_instances.get(chain)
        if not w3:
            print(f"  ❌ No web3 instance for {chain}")
            return None
        
        checksum_address = Web3.to_checksum_address(address)
        token_checksum = Web3.to_checksum_address(token_address)
        
        # Special handling for Verse getTotalVerse contract
        if token_name == 'VERSE' and protocol == 'verse' and chain == 'ethereum':
            try:
                get_total_verse_abi = [{
                    "name": "getTotalVerse",
                    "type": "function",
                    "inputs": [{"name": "account", "type": "address", "internalType": "address"}],
                    "outputs": [{"name": "totalVerse", "type": "uint256", "internalType": "uint256"}],
                    "stateMutability": "view"
                }]
                verse_contract = w3.eth.contract(address=Web3.to_checksum_address('0x3b089972c36578cf6eab8e7f2dad3b63c27bee07'), abi=get_total_verse_abi)
                balance = verse_contract.functions.getTotalVerse(checksum_address).call()
                decimals = 18
                print(f"  getTotalVerse Balance: {balance}")
            except Exception as e:
                print(f"  getTotalVerse failed, falling back to balanceOf: {e}")
                contract = w3.eth.contract(address=token_checksum, abi=ERC20_ABI)
                balance = contract.functions.balanceOf(checksum_address).call()
                decimals = contract.functions.decimals().call()
        else:
            contract = w3.eth.contract(address=token_checksum, abi=ERC20_ABI)
            balance = contract.functions.balanceOf(checksum_address).call()
            decimals = contract.functions.decimals().call()
        
        print(f"  Balance: {balance}")
        
        # Small delay to avoid rate limiting
        time.sleep(0.05)  # 50ms delay
        
        if balance == 0:
            return None
        
        balance_formatted = balance / (10 ** decimals)
        
        # Check if this is a debt token (borrow position)
        is_debt = protocol.endswith('_debt') or 'debt' in token_name.lower() or 'variableDebt' in token_name
        
        # Determine protocol display name and position type
        protocol_info = {
            'aave': ('Aave V3', 'Lending - Supply'),
            'aave_debt': ('Aave V3', 'Lending - Borrow'),
            'compound': ('Compound V3', 'Lending'),
            'uniswap_v3': ('Uniswap V3', 'Liquidity Pool'),
            'curve': ('Curve', 'Liquidity Pool'),
            'lido': ('Lido', 'Liquid Staking'),
            'rocketpool': ('Rocket Pool', 'Liquid Staking'),
            'gmx': ('GMX', 'Staking'),
            'traderjoe': ('Trader Joe', 'DEX'),
            'venus': ('Venus', 'Lending'),
            'pancakeswap': ('PancakeSwap', 'DEX'),
            'convex': ('Convex', 'Yield Farming'),
            'sushiswap': ('SushiSwap', 'DEX'),
            'balancer': ('Balancer', 'Liquidity Pool'),
            'yearn': ('Yearn', 'Vault'),
            'frax': ('Frax', 'Stablecoin'),
            'radiant': ('Radiant', 'Lending'),
            'verse': ('Verse', 'Staking'),
        }
        
        protocol_name, position_type = protocol_info.get(protocol, (protocol.title(), 'Position'))
        
        # Extract underlying token and calculate USD value
        underlying = extract_underlying_token(token_name, protocol)
        balance_usd = calculate_position_value(underlying, balance_formatted, protocol)
        
        # For debt positions, show negative values
        if is_debt:
            balance_formatted = -balance_formatted
            balance_usd = -balance_usd
            position_type = position_type.replace('Supply', 'Borrow')
        
        print(f"DeFi Position: {protocol_name} - {token_name} -> {underlying} = ${balance_usd:.2f} {'(DEBT)' if is_debt else ''}")
        
        return {
            'chain': CHAINS[chain]['name'],
            'protocol': protocol_name,
            'position_type': position_type,
            'token': underlying,
            'token_display': token_name,
            'amount': f"{balance_formatted:.6f}",
            'value_usd': balance_usd,
            'is_debt': is_debt
        }
    except Exception as e:
        print(f"Error getting {protocol} position {token_name} on {chain}: {e}")
        return None

def calculate_position_value(underlying: str, balance: float, protocol: str) -> float:
    """Calculate USD value of a DeFi position"""
    print(f"  Calculating value for: {underlying} (balance: {balance:.6f})")
    
    # Handle LP tokens (e.g., "USDC/WETH" or "DAI/USDC/USDT")
    if '/' in underlying:
        tokens = underlying.split('/')
        print(f"  LP token detected with components: {tokens}")
        # For LP tokens, estimate value by averaging the component token prices
        # This is a simplification - real LP value depends on pool composition
        total_value = 0
        valid_tokens = 0
        for token in tokens:
            token = token.strip()
            price = get_token_price_simple(token)
            print(f"    {token}: ${price:.2f}")
            if price > 0:
                total_value += price
                valid_tokens += 1
        
        if valid_tokens > 0:
            # Approximate LP token value as average of underlying tokens
            avg_price = total_value / valid_tokens
            total_usd = balance * avg_price
            print(f"  LP value: {balance:.6f} × ${avg_price:.2f} = ${total_usd:.2f}")
            return total_usd
        print(f"  Warning: No valid token prices found for LP")
        return 0
    
    # Handle special tokens
    if underlying == 'GLP':
        # GLP is a basket token, approximate value
        # In reality, GLP price should be fetched from GMX contracts
        # For now, use a reasonable estimate based on basket composition
        total_usd = balance * 1.0  # Approximate $1 per GLP as it's mostly stablecoins
        print(f"  GLP value (estimated): ${total_usd:.2f}")
        return total_usd
    
    # Single token - direct price lookup
    price = get_token_price_simple(underlying)
    total_usd = balance * price
    print(f"  Single token: {balance:.6f} × ${price:.2f} = ${total_usd:.2f}")
    return total_usd

def extract_underlying_token(token_name: str, protocol: str) -> str:
    """Extract underlying token from DeFi token name"""
    print(f"  Extracting underlying from: {token_name} (protocol: {protocol})")
    
    # Handle Aave debt tokens first (variableDebtEthUSDT -> USDT)
    if 'variableDebt' in token_name:
        token = token_name.replace('variableDebtEth', '').replace('variableDebtArb', '').replace('variableDebtPol', '').replace('variableDebtAva', '')
        print(f"  Aave debt token detected: {token_name} -> {token}")
        return token
    
    # Remove protocol prefixes
    token = token_name.replace('aEth', '').replace('aArb', '').replace('aPol', '').replace('aAva', '')
    token = token.replace('cUSDCv3', 'USDC').replace('cWETHv3', 'WETH')
    
    # Handle Aave tokens (aToken format)
    if token.startswith('a') and len(token) > 1:
        # aUSDC -> USDC, aWETH -> WETH, atBTC -> tBTC
        underlying = token[1:]
        print(f"  Aave token detected: {token} -> {underlying}")
        return underlying
    
    # Handle Compound tokens (cToken format)
    if token.startswith('c') and len(token) > 1:
        underlying = token[1:]
        print(f"  Compound token detected: {token} -> {underlying}")
        return underlying
    
    # Handle Venus tokens (vToken format)
    if token.startswith('v') and len(token) > 1 and protocol == 'venus':
        underlying = token[1:]
        print(f"  Venus token detected: {token} -> {underlying}")
        return underlying
    
    # Handle LP tokens
    if '-' in token:
        # For LP tokens like "USDC-WETH-005", return the pair
        parts = token.split('-')
        if len(parts) >= 2:
            lp_pair = f"{parts[0]}/{parts[1]}"
            print(f"  LP token detected: {token} -> {lp_pair}")
            return lp_pair
    
    # Handle special tokens
    special_tokens = {
        '3pool': 'DAI/USDC/USDT',
        'am3CRV': 'DAI/USDC/USDT',
        'stETH': 'stETH',
        'wstETH': 'wstETH',
        'rETH': 'rETH',
        'GLP': 'GLP',
        'tBTC': 'tBTC',
        'stVERSE': 'VERSE',
        'vTeam': 'VERSE'
    }
    
    if token in special_tokens:
        result = special_tokens[token]
        print(f"  Special token: {token} -> {result}")
        return result
    
    print(f"  Using token as-is: {token}")
    return token

def get_token_price_simple(symbol: str) -> float:
    """Simple token price lookup using CoinGecko"""
    # Map token symbols to CoinGecko IDs
    symbol_to_coingecko = {
        'ETH': 'ethereum', 'WETH': 'ethereum', 'WETHE': 'ethereum',
        'USDC': 'usd-coin', 'USDCN': 'usd-coin', 'USDCE': 'usd-coin',
        'USDT': 'tether', 'DAI': 'dai',
        'WBTC': 'wrapped-bitcoin', 'BTCB': 'bitcoin', 'BTCb': 'bitcoin', 'tBTC': 'tbtc',
        'AAVE': 'aave', 'AAVEE': 'aave',
        'UNI': 'uniswap', 'LINK': 'chainlink', 'LINKE': 'chainlink',
        'ARB': 'arbitrum',
        'MATIC': 'matic-network', 'WMATIC': 'matic-network',
        'AVAX': 'avalanche-2', 'WAVAX': 'avalanche-2',
        'BNB': 'binancecoin', 'WBNB': 'binancecoin',
        'CAKE': 'pancakeswap-token', 'GMX': 'gmx', 'JOE': 'joe',
        'CRV': 'curve-dao-token', 'CVX': 'convex-finance',
        'SUSHI': 'sushi', 'BAL': 'balancer',
        'FRAX': 'frax', 'FXS': 'frax-share',
        'stETH': 'staked-ether', 'wstETH': 'wrapped-steth', 'WSTETH': 'wrapped-steth',
        'rETH': 'rocket-pool-eth', 'RETH': 'rocket-pool-eth',
        'CBETH': 'coinbase-wrapped-staked-eth', 'cbETH': 'coinbase-wrapped-staked-eth',
        'LDO': 'lido-dao', 'MKR': 'maker', 'SNX': 'havven',
        'LUSD': 'liquity-usd', 'EURS': 'stasis-eurs',
        'AGEUR': 'ageur', 'JEUR': 'jarvis-synthetic-euro',
        'GHST': 'aavegotchi', 'DPI': 'defipulse-index',
        'STMATIC': 'lido-staked-matic', 'MATICX': 'stader-maticx',
        'SAVAX': 'benqi-liquid-staked-avax', 'sAVAX': 'benqi-liquid-staked-avax',
        'MAI': 'mimatic', 'FDUSD': 'first-digital-usd',
        'VERSE': 'verse-bitcoin', 'stVERSE': 'verse-bitcoin', 'vTeam': 'verse-bitcoin',
    }
    
    coingecko_id = symbol_to_coingecko.get(symbol)
    if coingecko_id:
        return get_token_price_by_coingecko(coingecko_id)
    
    # Fallback for unknown tokens
    return 0

def get_all_balances_for_chain(address: str, chain: str) -> tuple:
    """Get all wallet balances and DeFi positions for a chain"""
    wallet_balances = []
    defi_positions = []
    
    # Get native balance
    native = get_native_balance(address, chain)
    if native:
        wallet_balances.append(native)
    
    # Get ERC20 token balances
    tokens = TOKENS_BY_CHAIN.get(chain, {})
    for symbol, token_address in tokens.items():
        balance = get_token_balance(address, token_address, symbol, chain)
        if balance:
            wallet_balances.append(balance)
    
    # Get DeFi positions from all protocols
    protocols = DEFI_PROTOCOLS.get(chain, {})
    print(f"Checking {len(protocols)} protocols on {chain}")
    for protocol_name, protocol_tokens in protocols.items():
        print(f"  Protocol: {protocol_name} has {len(protocol_tokens)} tokens")
        for token_name, token_address in protocol_tokens.items():
            position = get_defi_position(address, token_address, token_name, protocol_name, chain)
            if position:
                print(f"    ✅ Found position: {token_name}")
                defi_positions.append(position)
    
    return wallet_balances, defi_positions

def get_all_balances_multichain(address: str) -> tuple:
    """Get balances across all chains in parallel"""
    all_wallet_balances = []
    all_defi_positions = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(get_all_balances_for_chain, address, chain): chain
            for chain in CHAINS.keys()
        }
        
        for future in as_completed(futures):
            try:
                wallet_balances, defi_positions = future.result(timeout=15)
                all_wallet_balances.extend(wallet_balances)
                all_defi_positions.extend(defi_positions)
            except Exception as e:
                chain = futures[future]
                print(f"Error fetching data for {chain}: {e}")
    
    return all_wallet_balances, all_defi_positions

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/address/<address>')
def address_route(address):
    """Direct link to address portfolio"""
    return render_template('index.html', prefill_address=address)

@app.route('/api/resolve-ens/<name>')
def resolve_ens(name):
    """Resolve ENS domain to address"""
    try:
        w3 = web3_instances.get('ethereum')
        if not w3:
            return jsonify({'error': 'Ethereum connection unavailable'}), 500
        
        # Check if it's already an address
        if Web3.is_address(name):
            return jsonify({'address': Web3.to_checksum_address(name)})
        
        # Try to resolve ENS
        try:
            address = w3.ens.address(name)
            if address:
                return jsonify({'address': address})
            else:
                return jsonify({'error': f'ENS name "{name}" not found'}), 404
        except Exception as e:
            return jsonify({'error': f'Failed to resolve ENS: {str(e)}'}), 400
            
    except Exception as e:
        print(f"Error in resolve_ens: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check/<address>')
def check_address(address):
    """API endpoint to check an address across all chains"""
    try:
        if not Web3.is_address(address):
            return jsonify({'error': 'Invalid Ethereum address'}), 400
        
        # Get all data across chains
        wallet_balances, defi_positions = get_all_balances_multichain(address)
        
        # Calculate totals
        total_wallet_value = sum(b.get('balance_usd', 0) for b in wallet_balances)
        total_defi_value = sum(p.get('value_usd', 0) for p in defi_positions)
        total_value_usd = total_wallet_value + total_defi_value
        
        # Sort by USD value
        wallet_balances.sort(key=lambda x: x.get('balance_usd', 0), reverse=True)
        defi_positions.sort(key=lambda x: x.get('value_usd', 0), reverse=True)
        
        return jsonify({
            'address': address,
            'total_value_usd': total_value_usd,
            'wallet_value_usd': total_wallet_value,
            'defi_value_usd': total_defi_value,
            'wallet_balances': wallet_balances,
            'defi_positions': defi_positions,
            'chains_checked': list(CHAINS.keys()),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in check_address: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-chain/<address>/<chain>')
def check_address_chain(address, chain):
    """API endpoint to check an address on a specific chain"""
    try:
        if not Web3.is_address(address):
            return jsonify({'error': 'Invalid Ethereum address'}), 400
        
        if chain not in CHAINS:
            return jsonify({'error': f'Invalid chain: {chain}'}), 400
        
        # Get data for specific chain
        wallet_balances, defi_positions = get_all_balances_for_chain(address, chain)
        
        # Calculate totals for this chain
        total_wallet_value = sum(b.get('balance_usd', 0) for b in wallet_balances)
        total_defi_value = sum(p.get('value_usd', 0) for p in defi_positions)
        
        return jsonify({
            'address': address,
            'chain': chain,
            'wallet_balances': wallet_balances,
            'defi_positions': defi_positions,
            'wallet_value_usd': total_wallet_value,
            'defi_value_usd': total_defi_value,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in check_address_chain: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    chain_status = {}
    for chain, w3 in web3_instances.items():
        try:
            connected = w3.is_connected()
            block = w3.eth.block_number if connected else None
            chain_status[chain] = {'connected': connected, 'block': block}
        except:
            chain_status[chain] = {'connected': False, 'block': None}
    
    return jsonify({
        'status': 'ok',
        'chains': chain_status
    })

if __name__ == '__main__':
    print("🚀 Starting Multi-Chain EVM Balance Checker...")
    print(f"\n📡 Supported Chains:")
    for chain, config in CHAINS.items():
        w3 = web3_instances.get(chain)
        status = "✅" if w3 and w3.is_connected() else "❌"
        print(f"  {status} {config['name']} ({config['native_token']})")
    
    print(f"\n✨ Server running at http://localhost:5001\n")
    app.run(debug=True, host='0.0.0.0', port=5001)
