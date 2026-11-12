import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Remove a legacy preference before the first paint. This prevents a flash of
// unreadable white-on-white text on every route for returning users.
document.documentElement.classList.remove('dark')

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
