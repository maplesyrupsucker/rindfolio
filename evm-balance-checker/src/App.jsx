import React, { useState, useEffect, useCallback, useRef } from 'react'
import { Providers } from './Providers'
import { WalletConnect } from './WalletConnect'
import { PortfolioChart, DefiChart } from './Charts'
import { TokenIcon, ChainIcon } from './utils/tokenIcons'
import './index.css'

const loadingMessages = [
    "🔍 Resolving address...",
    "⚡ Checking balances...",
    "🌐 Scanning across chains...",
    "🏦 Checking DeFi positions...",
    "💰 Calculating USD rates...",
    "🔎 Hang tight, found another position...",
    "📊 Almost there...",
    "🎨 Building the page...",
    "⏳ Please stand by...",
    "🚀 Finalizing results..."
]

function App() {
    // React is now the full frontend - no embedded detection needed

    const [address, setAddress] = useState('')
    const addressRef = useRef('') // Keep ref in sync with state
    const [loading, setLoading] = useState(false)
    const [loadingMessage, setLoadingMessage] = useState(loadingMessages[0])
    const [error, setError] = useState('')
    const [results, setResults] = useState(null)
    const [theme, setTheme] = useState(() => {
        return localStorage.getItem('theme') || 'dark'
    })
    
    // Keep ref in sync with state
    useEffect(() => {
        addressRef.current = address
    }, [address])

    const checkAddress = useCallback(async (inputAddress = null) => {
        // Use inputAddress if provided, otherwise get from current address ref
        const input = inputAddress || addressRef.current.trim()
        if (!input) {
            setError('Please enter an address or ENS name')
            return
        }

        setError('')
        setLoading(true)
        setResults(null)

        try {
            // Resolve ENS if needed
            let resolvedAddress = input
            if (!input.startsWith('0x') || input.length !== 42) {
                const response = await fetch(`/api/resolve-ens/${encodeURIComponent(input)}`)
                const data = await response.json()
                if (!response.ok || !data.address) {
                    throw new Error(data.error || 'Failed to resolve ENS')
                }
                resolvedAddress = data.address
            }

            // Fetch portfolio data
            const response = await fetch(`/api/check/${resolvedAddress}`)
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}))
                throw new Error(errorData.error || `Failed to fetch data: ${response.status} ${response.statusText}`)
            }
            
            const data = await response.json()

            setResults(data)
            setAddress(resolvedAddress)
            // Save to localStorage for next visit
            localStorage.setItem('lastCheckedAddress', resolvedAddress)
        } catch (err) {
            let errorMessage = err.message
            // Check if it's a network error (Flask not running)
            if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
                errorMessage = 'Cannot connect to backend API. Make sure Flask server is running on port 5001.'
            }
            setError(`Error: ${errorMessage}`)
        } finally {
            setLoading(false)
        }
    }, []) // No dependencies - function is stable, uses parameters/refs

    // Auto-check address if provided via URL params or localStorage
    useEffect(() => {
        // Check URL params first (e.g., /address/0x123... or /address/vitalik.eth)
        const pathParts = window.location.pathname.split('/').filter(p => p)
        const addressFromPath = pathParts[pathParts.length - 1]
        
        // Check URL hash (e.g., #0x123...)
        const addressFromHash = window.location.hash.replace('#', '')
        
        // Check localStorage for saved address
        const savedAddress = localStorage.getItem('lastCheckedAddress')
        
        // Valid address starts with 0x and is 42 chars, or ENS name ends with .eth
        const isValidAddress = (addr) => {
            if (!addr) return false
            return (addr.startsWith('0x') && addr.length === 42) || addr.endsWith('.eth')
        }
        
        const initialAddress = isValidAddress(addressFromPath) ? addressFromPath :
                              isValidAddress(addressFromHash) ? addressFromHash :
                              savedAddress || ''
        
        if (initialAddress) {
            setAddress(initialAddress)
            checkAddress(initialAddress)
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme)
    }, [theme])

    const toggleTheme = () => {
        const newTheme = theme === 'dark' ? 'light' : 'dark'
        setTheme(newTheme)
        localStorage.setItem('theme', newTheme)
    }

    // Track last checked address to prevent infinite loops
    const lastCheckedAddressRef = useRef('')
    
    const handleAddressChange = useCallback((walletAddress) => {
        if (walletAddress && walletAddress !== lastCheckedAddressRef.current) {
            lastCheckedAddressRef.current = walletAddress
            setAddress(walletAddress)
            checkAddress(walletAddress)
        }
    }, [checkAddress])

    useEffect(() => {
        let messageIndex = 0
        let interval = null

        if (loading) {
            setLoadingMessage(loadingMessages[0])
            interval = setInterval(() => {
                messageIndex = (messageIndex + 1) % loadingMessages.length
                setLoadingMessage(loadingMessages[messageIndex])
            }, 4500) // Change message every 4.5 seconds
        }

        return () => {
            if (interval) {
                clearInterval(interval)
            }
        }
    }, [loading])

    return (
        <div className="container">
            <div className="header">
                <div className="header-controls">
                    <label className="theme-switch" title="Toggle theme">
                        <input
                            type="checkbox"
                            checked={theme === 'light'}
                            onChange={toggleTheme}
                        />
                        <span className="slider"></span>
                    </label>
                </div>
                <h1>🌐 Multi-Chain Portfolio Tracker</h1>
            </div>

            <div className="search-box">
                <div className="input-group address-input-container">
                    <input
                        type="text"
                        id="react-addressInput"
                        placeholder="Enter address or ENS name (e.g., vitalik.eth)"
                        value={address}
                        onChange={(e) => setAddress(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && checkAddress()}
                    />
                    <button id="react-checkButton" onClick={() => checkAddress()} disabled={loading}>
                        {loading ? 'Checking...' : 'Check Address'}
                    </button>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Providers>
                            <WalletConnect onAddressChange={handleAddressChange} />
                        </Providers>
                    </div>
                </div>
            </div>

            {error && (
                <div className="error active">{error}</div>
            )}

            {loading && (
                <div className="loading active">
                    <div className="spinner"></div>
                    <p id="loadingMessage">{loadingMessage}</p>
                </div>
            )}

            {results && (
                <div className="results active" id="react-results">
                    <div className="card">
                        <div className="card-header">
                            <h2>💰 Portfolio Summary</h2>
                        </div>
                        <div className="total-summary">
                            <div className="summary-card">
                                <div className="summary-label">Total Value</div>
                                <div className="summary-value mono">
                                    ${results.total_value_usd?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
                                </div>
                            </div>
                            <div className="summary-card clickable-summary">
                                <div className="summary-label">Wallet Tokens</div>
                                <div className="summary-value mono">
                                    ${results.wallet_value_usd?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
                                </div>
                            </div>
                            <div className="summary-card clickable-summary">
                                <div className="summary-label">DeFi Positions</div>
                                <div className="summary-value mono">
                                    ${results.defi_value_usd?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
                                </div>
                            </div>
                        </div>
                        <div className="stats-bar">
                            <div className="stat-item">
                                <span>📊 Tokens:</span>
                                <span className="stat-value mono">{results.wallet_balances?.length || 0}</span>
                            </div>
                            <div className="stat-item">
                                <span>🏦 Positions:</span>
                                <span className="stat-value mono">{results.defi_positions?.length || 0}</span>
                            </div>
                            <div className="stat-item">
                                <span>⛓️ Chains:</span>
                                <span className="stat-value mono">
                                    {new Set([
                                        ...(results.wallet_balances || []).map(b => b.chain),
                                        ...(results.defi_positions || []).map(p => p.chain)
                                    ]).size}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Charts Section */}
                    <div className="charts-section">
                        <PortfolioChart walletBalances={results.wallet_balances || []} />
                        <DefiChart defiPositions={results.defi_positions || []} />
                    </div>

                    <div className="card" id="walletSection">
                        <h2>💎 Wallet Tokens</h2>
                        <div className="chain-filters">
                            <div className="chain-filter active">All</div>
                            <div className="chain-filter">ETH</div>
                            <div className="chain-filter">ARB</div>
                            <div className="chain-filter">POL</div>
                            <div className="chain-filter">AVAX</div>
                            <div className="chain-filter">BNB</div>
                            <div className="chain-filter">BASE</div>
                        </div>
                        <div>
                            {results.wallet_balances?.length > 0 ? (
                                results.wallet_balances.map((balance, idx) => (
                                    <div key={idx} className="wide-card">
                                        <div className="token-icon-wrapper">
                                            <div className="token-icon">
                                                <TokenIcon symbol={balance.symbol} />
                                            </div>
                                            <div className="token-info">
                                                <div className="token-symbol">{balance.symbol}</div>
                                                <div className="token-chain">
                                                    <ChainIcon chainName={balance.chain} size={16} />
                                                </div>
                                            </div>
                                        </div>
                                        <div className="token-amount">
                                            <div className="amount-value mono">{balance.balance}</div>
                                        </div>
                                        <div className="usd-value">
                                            <div className="usd-amount mono">${balance.balance_usd?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}</div>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="empty-state">No wallet balances found</div>
                            )}
                        </div>
                    </div>

                    <div className="card" id="defiSection">
                        <h2>🏦 DeFi Positions</h2>
                        <div>
                            {results.defi_positions?.length > 0 ? (
                                results.defi_positions.map((position, idx) => {
                                    const valueUsd = Math.abs(position.value_usd || 0)
                                    const isDebt = position.is_debt || false
                                    const tokenDisplay = position.token_display || position.token || 'Unknown'
                                    const positionType = position.position_type || position.type || 'Position'
                                    
                                    const tokenSymbol = tokenDisplay.split('/')[0]
                                    return (
                                        <div key={idx} className="wide-card defi-card">
                                            <div className="token-icon-wrapper">
                                                <div className="token-icon">
                                                    <TokenIcon symbol={tokenSymbol} />
                                                </div>
                                                <div className="token-info">
                                                    <div className="token-symbol">
                                                        {tokenDisplay}
                                                        <span className={`protocol-badge ${isDebt ? 'borrow-badge' : 'supply-badge'}`}>
                                                            {position.protocol}
                                                        </span>
                                                    </div>
                                                    <div className="position-type">{positionType} • {position.chain}</div>
                                                </div>
                                            </div>
                                            <div className="token-amount">
                                                <div className={`amount-value mono ${isDebt ? 'negative' : ''}`}>
                                                    {position.amount || '0.000000'}
                                                </div>
                                                <div className="amount-label">{tokenDisplay}</div>
                                            </div>
                                            <div className="usd-value">
                                                <div className={`usd-amount mono ${isDebt ? 'negative' : ''}`}>
                                                    ${valueUsd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                                </div>
                                            </div>
                                        </div>
                                    )
                                })
                            ) : (
                                <div className="empty-state">No DeFi positions found</div>
                            )}
                        </div>
                    </div>
                </div>
            )}
            
            {/* Footer */}
            <div className="footer">
                <div className="footer-links">
                    <span>Powered by</span>
                    <a href="https://wallet.bitcoin.com" target="_blank" rel="noopener">Bitcoin.com Wallet</a>
                    <span>&</span>
                    <a href="https://rindexer.xyz" target="_blank" rel="noopener">Rindexer</a>
                </div>
            </div>
        </div>
    )
}

export default App

