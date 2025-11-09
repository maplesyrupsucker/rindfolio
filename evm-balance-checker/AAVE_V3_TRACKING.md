# Aave V3 Complete Tracking Guide

## ✅ What's Being Tracked

The indexer now tracks **ALL Aave V3 lending pools** across **all supported tokens** on **6 chains**.

### How It Works

Aave V3 uses a single **Pool contract** per chain that handles all reserves (tokens). Every lending action (supply, borrow, repay, withdraw) emits events from this Pool contract with a `reserve` parameter that identifies which token is involved.

This means **one contract tracks all tokens** - you don't need separate contracts for USDC, WETH, DAI, etc.

## 📊 Chains & Contracts

| Chain | Pool Contract | Start Block |
|-------|--------------|-------------|
| **Ethereum** | `0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2` | 16,291,127 |
| **Arbitrum** | `0x794a61358D6845594F94dc1DB02A252b5b4814aD` | 7,740,843 |
| **Polygon** | `0x794a61358D6845594F94dc1DB02A252b5b4814aD` | 25,825,996 |
| **Optimism** | `0x794a61358D6845594F94dc1DB02A252b5b4814aD` | 4,365,693 |
| **Avalanche** | `0x794a61358D6845594F94dc1DB02A252b5b4814aD` | 11,970,477 |
| **Base** | `0xA238Dd80C259a72e81d7e4664a9801593F98d1c5` | 1,371,680 |

## 🎯 Events Tracked (9 Total)

### 1. **Supply** - User deposits tokens to earn interest
```sql
-- Fields: reserve, user, onBehalfOf, amount, referralCode
SELECT * FROM aave_v3_pool_supply WHERE user = '0x...';
```

### 2. **Withdraw** - User withdraws supplied tokens
```sql
-- Fields: reserve, user, to, amount
SELECT * FROM aave_v3_pool_withdraw WHERE user = '0x...';
```

### 3. **Borrow** - User borrows tokens
```sql
-- Fields: reserve, user, onBehalfOf, amount, borrowRateMode, borrowRate, referralCode
SELECT * FROM aave_v3_pool_borrow WHERE user = '0x...';
```

### 4. **Repay** - User repays borrowed tokens
```sql
-- Fields: reserve, user, repayer, amount
SELECT * FROM aave_v3_pool_repay WHERE user = '0x...';
```

### 5. **LiquidationCall** - User position gets liquidated
```sql
-- Fields: collateralAsset, debtAsset, user, debtToCover, liquidatedCollateralAmount, liquidator, receiveAToken
SELECT * FROM aave_v3_pool_liquidation_call WHERE user = '0x...';
```

### 6. **FlashLoan** - Flash loan executed
```sql
-- Fields: target, initiator, asset, amount, interestRateMode, premium, referralCode
SELECT * FROM aave_v3_pool_flash_loan WHERE initiator = '0x...';
```

### 7. **ReserveDataUpdated** - Interest rates updated
```sql
-- Fields: reserve, liquidityRate, stableBorrowRate, variableBorrowRate, liquidityIndex, variableBorrowIndex
-- Use this to track APY changes over time
SELECT * FROM aave_v3_pool_reserve_data_updated WHERE reserve = '0x...';
```

### 8. **ReserveUsedAsCollateralEnabled** - User enables token as collateral
```sql
-- Fields: reserve, user
SELECT * FROM aave_v3_pool_reserve_used_as_collateral_enabled WHERE user = '0x...';
```

### 9. **ReserveUsedAsCollateralDisabled** - User disables token as collateral
```sql
-- Fields: reserve, user
SELECT * FROM aave_v3_pool_reserve_used_as_collateral_disabled WHERE user = '0x...';
```

## 💰 Supported Tokens (Examples)

The indexer tracks **ALL tokens** supported by Aave V3 on each chain. Here are some examples:

### Ethereum
- USDC, USDT, DAI
- WETH, WBTC
- AAVE, LINK
- cbETH, rETH, stETH
- And **all other Aave V3 reserves**

### Arbitrum
- USDC, USDT, DAI
- WETH, WBTC
- ARB, LINK
- And **all other Aave V3 reserves**

### Polygon
- USDC, USDT, DAI
- WETH, WBTC, WMATIC
- AAVE, LINK
- And **all other Aave V3 reserves**

### Optimism, Avalanche, Base
- All tokens supported by Aave V3 on each respective chain

## 📈 Example Queries

### Get User's Total Supplied by Token

```sql
SELECT 
    reserve,
    SUM(amount) as total_supplied
FROM aave_v3_pool_supply
WHERE user = '0xYourAddress'
GROUP BY reserve
ORDER BY total_supplied DESC;
```

### Get User's Net Position (Supplies - Withdrawals)

```sql
WITH supplies AS (
    SELECT reserve, SUM(amount) as amount
    FROM aave_v3_pool_supply
    WHERE user = '0xYourAddress'
    GROUP BY reserve
),
withdrawals AS (
    SELECT reserve, SUM(amount) as amount
    FROM aave_v3_pool_withdraw
    WHERE user = '0xYourAddress'
    GROUP BY reserve
)
SELECT 
    COALESCE(s.reserve, w.reserve) as reserve,
    COALESCE(s.amount, 0) - COALESCE(w.amount, 0) as net_supply
FROM supplies s
FULL OUTER JOIN withdrawals w ON s.reserve = w.reserve
WHERE COALESCE(s.amount, 0) - COALESCE(w.amount, 0) > 0;
```

### Get User's Borrowed Amounts

```sql
SELECT 
    reserve,
    SUM(amount) as total_borrowed
FROM aave_v3_pool_borrow
WHERE user = '0xYourAddress'
GROUP BY reserve
ORDER BY total_borrowed DESC;
```

### Get User's Net Debt (Borrows - Repays)

```sql
WITH borrows AS (
    SELECT reserve, SUM(amount) as amount
    FROM aave_v3_pool_borrow
    WHERE user = '0xYourAddress'
    GROUP BY reserve
),
repays AS (
    SELECT reserve, SUM(amount) as amount
    FROM aave_v3_pool_repay
    WHERE user = '0xYourAddress'
    GROUP BY reserve
)
SELECT 
    COALESCE(b.reserve, r.reserve) as reserve,
    COALESCE(b.amount, 0) - COALESCE(r.amount, 0) as net_debt
FROM borrows b
FULL OUTER JOIN repays r ON b.reserve = r.reserve
WHERE COALESCE(b.amount, 0) - COALESCE(r.amount, 0) > 0;
```

### Calculate Health Factor (Simplified)

```sql
-- Get total collateral value and total debt
WITH positions AS (
    SELECT 
        'supply' as type,
        reserve,
        SUM(amount) as amount
    FROM aave_v3_pool_supply
    WHERE user = '0xYourAddress'
    GROUP BY reserve
    
    UNION ALL
    
    SELECT 
        'withdraw' as type,
        reserve,
        -SUM(amount) as amount
    FROM aave_v3_pool_withdraw
    WHERE user = '0xYourAddress'
    GROUP BY reserve
    
    UNION ALL
    
    SELECT 
        'borrow' as type,
        reserve,
        -SUM(amount) as amount
    FROM aave_v3_pool_borrow
    WHERE user = '0xYourAddress'
    GROUP BY reserve
    
    UNION ALL
    
    SELECT 
        'repay' as type,
        reserve,
        SUM(amount) as amount
    FROM aave_v3_pool_repay
    WHERE user = '0xYourAddress'
    GROUP BY reserve
)
SELECT 
    reserve,
    SUM(amount) as net_position
FROM positions
GROUP BY reserve
HAVING SUM(amount) != 0;
```

### Track Interest Rate Changes for a Token

```sql
SELECT 
    block_timestamp,
    liquidity_rate / 1e27 * 100 as supply_apy,
    variable_borrow_rate / 1e27 * 100 as borrow_apy
FROM aave_v3_pool_reserve_data_updated
WHERE reserve = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'  -- USDC on Ethereum
ORDER BY block_timestamp DESC
LIMIT 100;
```

### Find All Liquidations

```sql
SELECT 
    block_timestamp,
    user,
    collateral_asset,
    debt_asset,
    debt_to_cover,
    liquidated_collateral_amount,
    liquidator
FROM aave_v3_pool_liquidation_call
ORDER BY block_timestamp DESC
LIMIT 100;
```

### Track Flash Loans

```sql
SELECT 
    block_timestamp,
    initiator,
    asset,
    amount,
    premium,
    amount + premium as total_repaid
FROM aave_v3_pool_flash_loan
ORDER BY block_timestamp DESC
LIMIT 100;
```

## 🔗 Integration with Web Client

Update your `app.py` to query the indexed data:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

def get_aave_positions(address):
    """Get user's Aave V3 positions from indexed data"""
    conn = psycopg2.connect(
        "postgresql://rindexer:rindexer@localhost:5432/defi_indexer",
        cursor_factory=RealDictCursor
    )
    cur = conn.cursor()
    
    # Get net supply positions
    cur.execute("""
        WITH supplies AS (
            SELECT reserve, SUM(amount) as amount
            FROM aave_v3_pool_supply
            WHERE user = %s
            GROUP BY reserve
        ),
        withdrawals AS (
            SELECT reserve, SUM(amount) as amount
            FROM aave_v3_pool_withdraw
            WHERE user = %s
            GROUP BY reserve
        )
        SELECT 
            COALESCE(s.reserve, w.reserve) as reserve,
            COALESCE(s.amount, 0) - COALESCE(w.amount, 0) as net_supply
        FROM supplies s
        FULL OUTER JOIN withdrawals w ON s.reserve = w.reserve
        WHERE COALESCE(s.amount, 0) - COALESCE(w.amount, 0) > 0
    """, (address.lower(), address.lower()))
    
    supplies = cur.fetchall()
    
    # Get net borrow positions
    cur.execute("""
        WITH borrows AS (
            SELECT reserve, SUM(amount) as amount
            FROM aave_v3_pool_borrow
            WHERE user = %s
            GROUP BY reserve
        ),
        repays AS (
            SELECT reserve, SUM(amount) as amount
            FROM aave_v3_pool_repay
            WHERE user = %s
            GROUP BY reserve
        )
        SELECT 
            COALESCE(b.reserve, r.reserve) as reserve,
            COALESCE(b.amount, 0) - COALESCE(r.amount, 0) as net_debt
        FROM borrows b
        FULL OUTER JOIN repays r ON b.reserve = r.reserve
        WHERE COALESCE(b.amount, 0) - COALESCE(r.amount, 0) > 0
    """, (address.lower(), address.lower()))
    
    borrows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return {
        'supplies': supplies,
        'borrows': borrows
    }
```

## 🎉 Summary

✅ **All Aave V3 tokens are tracked** - No need to add individual token contracts  
✅ **9 comprehensive events** - Supply, Borrow, Repay, Liquidations, Flash Loans, Interest Rates, Collateral  
✅ **6 chains covered** - Ethereum, Arbitrum, Polygon, Optimism, Avalanche, Base  
✅ **Complete position tracking** - Calculate net supplies, net debts, health factors  
✅ **Historical data** - Track interest rate changes, liquidations, flash loans over time  

The Aave V3 Pool contract architecture means you're already tracking **every token** that Aave V3 supports, automatically!

