// Token icon utilities - matches Flask template logic
import React from 'react'

const tokenIconMap = {
    'ETH': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/info/logo.png',
    'WETH': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/info/logo.png',
    'USDC': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/assets/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48/logo.png',
    'USDT': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/assets/0xdAC17F958D2ee523a2206206994597C13D831ec7/logo.png',
    'DAI': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/assets/0x6B175474E89094C44Da98b954EedeAC495271d0F/logo.png',
    'WBTC': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/assets/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599/logo.png',
    'AAVE': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/assets/0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9/logo.png',
    'UNI': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/assets/0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984/logo.png',
    'LINK': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/assets/0x514910771AF9Ca656af840dff83E8264EcF986CA/logo.png',
    'MATIC': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/polygon/info/logo.png',
    'WMATIC': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/polygon/info/logo.png',
    'BNB': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/smartchain/info/logo.png',
    'WBNB': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/smartchain/info/logo.png',
    'AVAX': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/avalanchec/info/logo.png',
    'WAVAX': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/avalanchec/info/logo.png',
    'VERSE': 'https://verse.bitcoin.com/icons/verse-icon-512x512.png',
    'fxVERSE': 'https://verse.bitcoin.com/icons/verse-icon-512x512.png',
    'stVERSE': 'https://verse.bitcoin.com/icons/verse-icon-512x512.png',
    'vTeam': 'https://verse.bitcoin.com/icons/verse-icon-512x512.png',
    'vstBTC': 'https://verse.bitcoin.com/icons/verse-icon-512x512.png'
}

const tokenToCoinGecko = {
    'ETH': 'ethereum', 'WETH': 'ethereum',
    'USDC': 'usd-coin', 'USDT': 'tether', 'DAI': 'dai',
    'WBTC': 'wrapped-bitcoin', 'BTCB': 'bitcoin', 'tBTC': 'tbtc',
    'AAVE': 'aave', 'UNI': 'uniswap', 'LINK': 'chainlink',
    'ARB': 'arbitrum', 'MATIC': 'matic-network', 'WMATIC': 'matic-network',
    'AVAX': 'avalanche-2', 'WAVAX': 'avalanche-2',
    'BNB': 'binancecoin', 'WBNB': 'binancecoin',
    'CAKE': 'pancakeswap-token', 'stETH': 'lido-staked-ether', 'wstETH': 'wrapped-steth',
    'rETH': 'rocket-pool-eth', 'GMX': 'gmx', 'GLP': 'gmx',
    'JOE': 'joe', 'CRV': 'curve-dao-token',
    'CVX': 'convex-finance', 'SUSHI': 'sushi', 'BAL': 'balancer',
    'FRAX': 'frax', 'FXS': 'frax-share',
    'VERSE': 'verse', 'stVERSE': 'verse'
}

const chainIcons = {
    'Ethereum': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/info/logo.png',
    'Arbitrum': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/arbitrum/info/logo.png',
    'Arbitrum One': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/arbitrum/info/logo.png',
    'Polygon': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/polygon/info/logo.png',
    'Avalanche': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/avalanchec/info/logo.png',
    'BNB Chain': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/smartchain/info/logo.png',
    'Base': 'https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/base/info/logo.png'
}

export function getTokenIconUrl(symbol) {
    const iconUrl = tokenIconMap[symbol]
    const coingeckoId = tokenToCoinGecko[symbol]
    
    // Return array of fallback URLs
    const fallbacks = []
    
    if (iconUrl) {
        fallbacks.push(iconUrl)
    }
    
    if (coingeckoId) {
        fallbacks.push(`https://assets.coingecko.com/coins/images/small/${coingeckoId}.png`)
    }
    
    // Cryptologos as additional fallback
    fallbacks.push(`https://cryptologos.cc/logos/${symbol.toLowerCase()}-${symbol.toLowerCase()}-logo.png`)
    
    return fallbacks.length > 0 ? fallbacks : null
}

export function getChainIconUrl(chainName) {
    return chainIcons[chainName] || null
}

export function TokenIcon({ symbol, className = '' }) {
    const [currentSrc, setCurrentSrc] = React.useState(null)
    const [showFallback, setShowFallback] = React.useState(false)
    const fallbacksRef = React.useRef([])
    
    React.useEffect(() => {
        const fallbacks = getTokenIconUrl(symbol)
        if (fallbacks && fallbacks.length > 0) {
            fallbacksRef.current = fallbacks
            setCurrentSrc(fallbacks[0])
            setShowFallback(false)
        } else {
            setShowFallback(true)
        }
    }, [symbol])
    
    const handleError = () => {
        const nextIndex = fallbacksRef.current.indexOf(currentSrc) + 1
        if (nextIndex < fallbacksRef.current.length) {
            setCurrentSrc(fallbacksRef.current[nextIndex])
        } else {
            setShowFallback(true)
        }
    }
    
    if (showFallback) {
        return (
            <div className={`token-fallback ${className}`}>
                {symbol.substring(0, 3).toUpperCase()}
            </div>
        )
    }
    
    return (
        <img 
            src={currentSrc} 
            alt={symbol}
            className={className}
            onError={handleError}
        />
    )
}

export function ChainIcon({ chainName, size = 16 }) {
    const iconUrl = getChainIconUrl(chainName)
    
    if (!iconUrl) {
        return <span>{chainName}</span>
    }
    
    return (
        <span className="chain-icon" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <img 
                src={iconUrl} 
                alt={chainName}
                style={{ width: `${size}px`, height: `${size}px`, borderRadius: '50%' }}
                onError={(e) => e.target.style.display = 'none'}
            />
            {chainName}
        </span>
    )
}

