import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Mount React app
// If running standalone (Vite dev server), App will render the full page
// If embedded in Flask template, App will detect and only render wallet connect
const rootElement = document.getElementById('root')
if (rootElement) {
    const root = ReactDOM.createRoot(rootElement)
    root.render(
        <React.StrictMode>
            <App />
        </React.StrictMode>
    )
} else {
    console.error('Root element not found! Make sure <div id="root"></div> exists.')
}

