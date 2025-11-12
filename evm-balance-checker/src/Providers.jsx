import React, { useState, useMemo } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { WagmiProvider, createConfig, http } from 'wagmi'
import { mainnet, arbitrum, polygon, avalanche, bsc, base, optimism } from 'wagmi/chains'
import { injected, metaMask, walletConnect } from 'wagmi/connectors'

// Get WalletConnect project ID from environment or window (set by Flask template)
function getProjectId() {
    if (typeof window !== 'undefined' && window.WALLETCONNECT_PROJECT_ID) {
        return window.WALLETCONNECT_PROJECT_ID
    }
    return import.meta.env.VITE_WALLETCONNECT_PROJECT_ID || ''
}

// Supported chains for multi-chain portfolio tracking
const chains = [mainnet, arbitrum, polygon, avalanche, bsc, base, optimism]

// Create config only on client side to avoid SSR issues with WalletConnect
function createWagmiConfig() {
    const projectId = getProjectId()
    
    // Build connectors array conditionally
    const connectors = [
        injected(),
        metaMask(),
    ]

    // Only add WalletConnect if project ID is provided and we're on client
    if (typeof window !== 'undefined' && projectId) {
        try {
            const wcConnector = walletConnect({
                projectId,
                showQrModal: true,
                metadata: {
                    name: 'Multi-Chain Portfolio Tracker',
                    description: 'Track your crypto portfolio across multiple chains',
                    url: window.location.origin,
                    icons: [`${window.location.origin}/favicon.ico`],
                },
                qrModalOptions: {
                    themeMode: 'dark',
                },
            })
            
            connectors.push(wcConnector)
            
            if (import.meta.env.DEV) {
                console.log('✅ WalletConnect connector added with project ID:', projectId)
            }
        } catch (error) {
            console.error('❌ Failed to create WalletConnect connector:', error)
            if (import.meta.env.DEV) {
                console.error('Make sure WALLETCONNECT_PROJECT_ID is set')
            }
        }
    } else if (typeof window !== 'undefined' && import.meta.env.DEV) {
        console.warn('⚠️ WalletConnect not configured: WALLETCONNECT_PROJECT_ID is missing')
        console.warn('   Get a free project ID at: https://cloud.walletconnect.com/')
    }

    // Create transports for all supported chains
    // Use custom RPC URL from environment if provided
    const customRpcUrl = typeof window !== 'undefined' 
        ? (window.NEXT_PUBLIC_RPC_URL || import.meta.env.VITE_RPC_URL)
        : import.meta.env.VITE_RPC_URL
    
    const transports = {}
    chains.forEach(chain => {
        // Use custom RPC for Ethereum mainnet, default http() for others
        if (chain.id === 1 && customRpcUrl) {
            transports[chain.id] = http(customRpcUrl)
        } else {
            transports[chain.id] = http()
        }
    })

    return createConfig({
        chains,
        connectors,
        transports,
        ssr: false, // Disable SSR to avoid history conflicts
        storage: typeof window !== 'undefined' ? window.localStorage : undefined,
    })
}

export function Providers({ children }) {
    const [queryClient] = useState(() => new QueryClient())
    
    // Only create config on client side
    const config = useMemo(() => {
        return createWagmiConfig()
    }, [])

    return (
        <WagmiProvider config={config}>
            <QueryClientProvider client={queryClient}>
                {children}
            </QueryClientProvider>
        </WagmiProvider>
    )
}

