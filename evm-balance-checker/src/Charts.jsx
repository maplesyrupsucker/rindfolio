import React, { useEffect, useRef, useState } from 'react'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'react-chartjs-2'

ChartJS.register(ArcElement, Tooltip, Legend)

const chartColors = [
    '#667eea', '#764ba2', '#f093fb', '#4facfe',
    '#43e97b', '#fa709a', '#fee140', '#30cfd0',
    '#a8edea', '#fed6e3', '#c471f5', '#fa71cd'
]

function getChartTextColor() {
    return getComputedStyle(document.documentElement).getPropertyValue('--text-primary') || '#e0e0e0'
}

function getChartBackgroundColor() {
    return getComputedStyle(document.documentElement).getPropertyValue('--card-bg') || '#0f3460'
}

export function PortfolioChart({ walletBalances }) {
    const [mode, setMode] = useState('token')
    const [isMobile, setIsMobile] = useState(false)
    
    useEffect(() => {
        const checkMobile = () => setIsMobile(window.innerWidth < 769)
        checkMobile()
        window.addEventListener('resize', checkMobile)
        return () => window.removeEventListener('resize', checkMobile)
    }, [])
    
    if (!walletBalances || walletBalances.length === 0) {
        return null
    }

    let labels, data

    if (mode === 'token') {
        // Group by token
        const tokenData = {}
        walletBalances.forEach(balance => {
            if (!tokenData[balance.symbol]) {
                tokenData[balance.symbol] = 0
            }
            tokenData[balance.symbol] += balance.balance_usd || 0
        })

        // Sort by value and take top 10
        const sorted = Object.entries(tokenData)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10)

        labels = sorted.map(([token]) => token)
        data = sorted.map(([, value]) => value)
    } else {
        // Group by chain
        const chainData = {}
        walletBalances.forEach(balance => {
            if (!chainData[balance.chain]) {
                chainData[balance.chain] = 0
            }
            chainData[balance.chain] += balance.balance_usd || 0
        })

        labels = Object.keys(chainData)
        data = Object.values(chainData)
    }

    const chartData = {
        labels,
        datasets: [{
            data,
            backgroundColor: chartColors,
            borderWidth: 2,
            borderColor: getChartBackgroundColor()
        }]
    }

    const options = {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: isMobile ? 1.5 : 2,
        plugins: {
            legend: {
                position: isMobile ? 'bottom' : 'right',
                labels: {
                    color: getChartTextColor(),
                    padding: isMobile ? 6 : 15,
                    font: {
                        size: isMobile ? 9 : 12,
                        family: 'Inter'
                    },
                    boxWidth: isMobile ? 10 : 15
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || ''
                        const value = context.parsed || 0
                        const total = context.dataset.data.reduce((a, b) => a + b, 0)
                        const percentage = ((value / total) * 100).toFixed(1)
                        return `${label}: $${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} (${percentage}%)`
                    }
                }
            }
        },
        animation: {
            animateRotate: true,
            duration: 1000
        }
    }

    return (
        <div className="chart-card">
            <div className="chart-header">
                <h3 className="chart-title">Portfolio Distribution</h3>
                <div className="chart-toggle">
                    <button 
                        className={`chart-toggle-btn ${mode === 'token' ? 'active' : ''}`}
                        onClick={() => setMode('token')}
                    >
                        By Token
                    </button>
                    <button 
                        className={`chart-toggle-btn ${mode === 'chain' ? 'active' : ''}`}
                        onClick={() => setMode('chain')}
                    >
                        By Chain
                    </button>
                </div>
            </div>
            <div className="chart-container">
                <Doughnut data={chartData} options={options} />
            </div>
        </div>
    )
}

export function DefiChart({ defiPositions }) {
    const [mode, setMode] = useState('protocol')
    const [isMobile, setIsMobile] = useState(false)
    
    useEffect(() => {
        const checkMobile = () => setIsMobile(window.innerWidth < 769)
        checkMobile()
        window.addEventListener('resize', checkMobile)
        return () => window.removeEventListener('resize', checkMobile)
    }, [])
    
    if (!defiPositions || defiPositions.length === 0) {
        return null
    }

    let labels, data

    if (mode === 'protocol') {
        // Group by protocol - use absolute values
        const protocolData = {}
        defiPositions.forEach(position => {
            if (!protocolData[position.protocol]) {
                protocolData[position.protocol] = 0
            }
            const value = Math.abs(parseFloat(position.value_usd) || 0)
            protocolData[position.protocol] += value
        })

        // Sort by value and filter out zero values
        const sorted = Object.entries(protocolData)
            .filter(([, value]) => value > 0)
            .sort((a, b) => b[1] - a[1])

        if (sorted.length === 0) {
            return null
        }

        labels = sorted.map(([protocol]) => protocol)
        data = sorted.map(([, value]) => value)
    } else {
        // Group by chain - use absolute values
        const chainData = {}
        defiPositions.forEach(position => {
            if (!chainData[position.chain]) {
                chainData[position.chain] = 0
            }
            const value = Math.abs(parseFloat(position.value_usd) || 0)
            chainData[position.chain] += value
        })

        labels = Object.keys(chainData).filter(chain => chainData[chain] > 0)
        data = Object.values(chainData).filter(v => v > 0)
    }

    if (labels.length === 0) {
        return null
    }

    const chartData = {
        labels,
        datasets: [{
            data,
            backgroundColor: chartColors,
            borderWidth: 2,
            borderColor: getChartBackgroundColor()
        }]
    }

    const options = {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: isMobile ? 1.5 : 2,
        plugins: {
            legend: {
                position: isMobile ? 'bottom' : 'right',
                labels: {
                    color: getChartTextColor(),
                    padding: isMobile ? 6 : 15,
                    font: {
                        size: isMobile ? 9 : 12,
                        family: 'Inter'
                    },
                    boxWidth: isMobile ? 10 : 15
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || ''
                        const value = context.parsed || 0
                        const total = context.dataset.data.reduce((a, b) => a + b, 0)
                        const percentage = ((value / total) * 100).toFixed(1)
                        return `${label}: $${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} (${percentage}%)`
                    }
                }
            }
        },
        animation: {
            animateRotate: true,
            duration: 1000
        }
    }

    return (
        <div className="chart-card">
            <div className="chart-header">
                <h3 className="chart-title">DeFi Distribution</h3>
                <div className="chart-toggle">
                    <button 
                        className={`chart-toggle-btn ${mode === 'protocol' ? 'active' : ''}`}
                        onClick={() => setMode('protocol')}
                    >
                        By Protocol
                    </button>
                    <button 
                        className={`chart-toggle-btn ${mode === 'chain' ? 'active' : ''}`}
                        onClick={() => setMode('chain')}
                    >
                        By Chain
                    </button>
                </div>
            </div>
            <div className="chart-container">
                <Doughnut data={chartData} options={options} />
            </div>
        </div>
    )
}

