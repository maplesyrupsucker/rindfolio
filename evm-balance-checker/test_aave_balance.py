#!/usr/bin/env python3
"""
Quick script to test if an address has Aave aToken balances
"""

import sys
from web3 import Web3

# RPC endpoint
RPC_URL = "https://eth.llamarpc.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Minimal ERC20 ABI
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    }
]

# Aave V3 aToken addresses on Ethereum
AAVE_ATOKENS = {
    'aEthUSDC': '0x98C23E9d8f34FEFb1B7BD6a91B7FF122F4e16F5c',
    'aEthUSDT': '0x23878914EFE38d27C4D67Ab83ed1b93A74D4086a',
    'aEthDAI': '0x018008bfb33d285247A21d44E50697654f754e63',
    'aEthWETH': '0x4d5F47FA6A74757f35C14fD3a6Ef8E3C9BC514E8',
    'aEthWBTC': '0x5Ee5bf7ae06D1Be5997A1A72006FE6C607eC6DE8',
}

def check_aave_balances(address):
    """Check aToken balances for an address"""
    print(f"\n🔍 Checking Aave V3 positions for: {address}")
    print(f"📡 Connected to: {RPC_URL}")
    print(f"⛓️  Block: {w3.eth.block_number:,}\n")
    
    checksum_address = Web3.to_checksum_address(address)
    found_positions = False
    
    for token_name, token_address in AAVE_ATOKENS.items():
        try:
            contract = w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=ERC20_ABI
            )
            
            balance = contract.functions.balanceOf(checksum_address).call()
            
            if balance > 0:
                decimals = contract.functions.decimals().call()
                balance_formatted = balance / (10 ** decimals)
                symbol = contract.functions.symbol().call()
                
                print(f"✅ {symbol}: {balance_formatted:,.6f}")
                found_positions = True
            else:
                print(f"⚪ {token_name}: 0")
                
        except Exception as e:
            print(f"❌ {token_name}: Error - {str(e)[:50]}")
    
    if not found_positions:
        print(f"\n❌ No Aave V3 supply positions found for this address")
        print(f"\n💡 This could mean:")
        print(f"   - Address has no Aave positions")
        print(f"   - Address only has borrow positions (no aTokens)")
        print(f"   - Address supplied but already withdrew everything")
        print(f"\n🔗 Verify at: https://app.aave.com")
    else:
        print(f"\n✅ Found Aave positions!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_aave_balance.py <address>")
        print("\nExample:")
        print("  python3 test_aave_balance.py 0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c")
        sys.exit(1)
    
    address = sys.argv[1]
    check_aave_balances(address)

