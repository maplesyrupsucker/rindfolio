import React, { useEffect, useState, useRef } from 'react'
import { useAccount, useConnect, useDisconnect } from 'wagmi'

export function WalletConnect({ onAddressChange }) {
    // ALL hooks must be called unconditionally (before any early returns)
    const [mounted, setMounted] = useState(false)
    const [showMenu, setShowMenu] = useState(false)
    const { address, isConnected, connector } = useAccount()
    const { connect, connectors, error: connectError, isPending } = useConnect()
    const { disconnect } = useDisconnect()

    // Track last notified address to prevent infinite loops
    const lastNotifiedAddressRef = useRef('')

    // Prevent hydration mismatch
    useEffect(() => {
        setMounted(true)
    }, [])

    // Notify parent when address changes (only if it actually changed)
    useEffect(() => {
        if (mounted && isConnected && address && onAddressChange) {
            // Only call if address actually changed
            if (address !== lastNotifiedAddressRef.current) {
                lastNotifiedAddressRef.current = address
                onAddressChange(address)
            }
        } else if (!isConnected) {
            // Reset when disconnected
            lastNotifiedAddressRef.current = ''
        }
    }, [mounted, isConnected, address, onAddressChange])

    if (!mounted) {
        return null
    }

    const injectedConnector = connectors.find(c => c.id === 'injected' || c.id === 'metaMask')
    const wcConnector = connectors.find(c =>
        c.id === 'walletConnect' ||
        c.name?.toLowerCase().includes('walletconnect')
    )

    const buttonStyle = {
        padding: '14px 28px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        border: 'none',
        borderRadius: '10px',
        fontSize: '15px',
        fontWeight: '600',
        cursor: isPending ? 'not-allowed' : 'pointer',
        opacity: isPending ? 0.6 : 1,
        transition: 'transform 0.2s, box-shadow 0.2s',
        whiteSpace: 'nowrap',
        marginRight: '8px'
    }

    const handleMouseOver = (e) => {
        if (!isPending) {
            e.target.style.transform = 'translateY(-2px)'
            e.target.style.boxShadow = '0 5px 15px rgba(102, 126, 234, 0.4)'
        }
    }

    const handleMouseOut = (e) => {
        e.target.style.transform = 'translateY(0)'
        e.target.style.boxShadow = 'none'
    }

    return (
        <div className="wallet-connect-container" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0px',
            marginLeft: '0px'
        }}>
            {!isConnected ? (
                <>
                    {/* Browser Wallet Button */}
                    {injectedConnector && (
                        <button
                            onClick={async () => {
                                try {
                                    await connect({ connector: injectedConnector })
                                } catch (error) {
                                    console.error('Browser wallet connection error:', error)
                                    if (error?.code !== 4001 && error?.code !== 'USER_REJECTED') {
                                        alert(`Failed to connect: ${error.message || 'Unknown error'}`)
                                    }
                                }
                            }}
                            disabled={isPending}
                            style={buttonStyle}
                            onMouseOver={handleMouseOver}
                            onMouseOut={handleMouseOut}
                        >
                            {isPending ? 'Connecting...' : '🌐 Browser Wallet'}
                        </button>
                    )}

                    {/* WalletConnect Button */}
                    {wcConnector && (
                        <button
                            onClick={async () => {
                                try {
                                    await connect({ connector: wcConnector })
                                } catch (error) {
                                    console.error('WalletConnect connection error:', error)
                                    if (error?.code !== 4001 && error?.code !== 'USER_REJECTED') {
                                        alert(`Failed to connect: ${error.message || 'Unknown error'}`)
                                    }
                                }
                            }}
                            disabled={isPending}
                            style={buttonStyle}
                            onMouseOver={handleMouseOver}
                            onMouseOut={handleMouseOut}
                        >
                            {isPending ? 'Connecting...' : '📱 WalletConnect'}
                        </button>
                    )}
                </>
            ) : (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                }}>
                    <div style={{
                        fontSize: '15px',
                        color: 'white',
                        padding: '14px 28px',
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        borderRadius: '10px',
                        fontFamily: 'JetBrains Mono, monospace',
                        fontWeight: '600',
                        marginRight: '2px'
                    }}>
                        {address?.substring(0, 6)}...{address?.substring(address.length - 4)}
                    </div>
                    <button
                        onClick={() => disconnect()}
                        style={{
                            padding: '14px 28px',
                            background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                            color: 'white',
                            border: 'none',
                            borderRadius: '10px',
                            fontSize: '15px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'transform 0.2s, box-shadow 0.2s'
                        }}
                        onMouseOver={(e) => {
                            e.target.style.transform = 'translateY(-2px)'
                            e.target.style.boxShadow = '0 5px 15px rgba(239, 68, 68, 0.4)'
                        }}
                        onMouseOut={(e) => {
                            e.target.style.transform = 'translateY(0)'
                            e.target.style.boxShadow = 'none'
                        }}
                    >
                        Disconnect
                    </button>
                </div>
            )}

            {connectError && (
                <div style={{
                    position: 'absolute',
                    top: '100%',
                    right: 0,
                    marginTop: '8px',
                    padding: '8px 12px',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    color: '#ef4444',
                    borderRadius: '6px',
                    fontSize: '0.8em',
                    whiteSpace: 'nowrap',
                    zIndex: 1001
                }}>
                    {connectError.message}
                </div>
            )}
        </div>
    )
}

