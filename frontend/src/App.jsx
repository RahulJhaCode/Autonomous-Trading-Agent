import { useState } from 'react'
import { useWebSocket } from './hooks/useWebSocket'
import AgentStatusPanel from './components/AgentStatusPanel'
import TradeLog from './components/TradeLog'
import RiskGauge from './components/RiskGauge'
import PortfolioChart from './components/PortfolioChart'
import StockSelector from './components/StockSelector'

const AGENTS = [
  { id: 'fundamental_analyst', name: 'Fundamental Analyst', icon: '📊', color: '#3b82f6' },
  { id: 'sentiment_analyst',   name: 'Sentiment Analyst',   icon: '💬', color: '#8b5cf6' },
  { id: 'technical_analyst',   name: 'Technical Analyst',   icon: '📈', color: '#06b6d4' },
  { id: 'news_analyst',        name: 'News Analyst',        icon: '📰', color: '#f59e0b' },
  { id: 'bull_researcher',     name: 'Bull Researcher',     icon: '🐂', color: '#10b981' },
  { id: 'bear_researcher',     name: 'Bear Researcher',     icon: '🐻', color: '#ef4444' },
  { id: 'trader',              name: 'Trader Agent',        icon: '💼', color: '#3b82f6' },
  { id: 'risk_manager',        name: 'Risk Manager',        icon: '🛡️', color: '#f59e0b' },
  { id: 'fund_manager',        name: 'Fund Manager',        icon: '🏦', color: '#10b981' },
]

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard',   icon: '⚡' },
  { id: 'agents',    label: 'Agents',      icon: '🤖' },
  { id: 'trades',    label: 'Trade Log',   icon: '📋' },
  { id: 'risk',      label: 'Risk Center', icon: '🛡️' },
]

// Portfolio in INR (₹ Lakhs)
const MOCK_PORTFOLIO = [
  { date: 'Apr 20', value: 1000000 },
  { date: 'Apr 21', value: 1012000 },
  { date: 'Apr 22', value: 1008000 },
  { date: 'Apr 23', value: 1034000 },
  { date: 'Apr 24', value: 1029000 },
  { date: 'Apr 25', value: 1056000 },
  { date: 'Apr 26', value: 1072000 },
]

export default function App() {
  const [activePage, setActivePage]     = useState('dashboard')
  const [ticker, setTicker]             = useState('')
  const [loading, setLoading]           = useState(false)
  const [trades, setTrades]             = useState([])
  const [agentStatuses, setAgentStatuses] = useState({})
  const { connected, messages, agentEvents } = useWebSocket()

  // Update agent statuses from WebSocket events
  const getAgentStatuses = () => {
    const statuses = {}
    agentEvents.forEach(e => { statuses[e.agent] = e.status })
    return statuses
  }

  const runCycle = async () => {
    if (!ticker || loading) return
    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/control/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker: ticker.toUpperCase(), timeframe: '1D' }),
      })
      const data = await res.json()
      console.log('Cycle started:', data)
    } catch (e) {
      console.error('Failed to start cycle:', e)
    } finally {
      setTimeout(() => setLoading(false), 3000)
    }
  }

  const recentTrades = messages
    .filter(m => m.type === 'trade_alert' || m.type === 'cycle_completed')
    .slice(0, 20)

  const agentStatusMap = getAgentStatuses()

  return (
    <div className="app-layout">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">🤖</div>
          <div>
            <div className="logo-text">TradeAgent</div>
            <div className="logo-sub">AI Trading System</div>
          </div>
        </div>

        {NAV_ITEMS.map(item => (
          <div
            key={item.id}
            className={`nav-item ${activePage === item.id ? 'active' : ''}`}
            onClick={() => setActivePage(item.id)}
          >
            <span className="icon">{item.icon}</span>
            {item.label}
          </div>
        ))}

        <div style={{ marginTop: 'auto', paddingTop: '16px', borderTop: '1px solid var(--border)' }}>
          <div className={`connection-badge ${connected ? 'connected' : 'disconnected'}`}>
            <span style={{ fontSize: 8 }}>●</span>
            {connected ? 'Live' : 'Disconnected'}
          </div>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <main className="main-content">
        <div className="top-header">
          <div>
            <div className="page-title">Autonomous Trading Agent</div>
          <div className="page-subtitle">
            Indian Market Edition (NSE/BSE) • Azure OpenAI • Nifty 50 + Sensex 30 • {new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </div>
          </div>
          <div className={`connection-badge ${connected ? 'connected' : 'disconnected'}`} style={{ fontSize: 13 }}>
            <span>●</span>
            {connected ? 'Connected to API' : 'API Disconnected'}
          </div>
        </div>

        {/* ── Trade Input Bar ── */}
        <div className="trade-input-bar">
          <input
            className="ticker-input"
            placeholder="NSE Symbol (e.g. RELIANCE, TCS, HDFCBANK)"
            value={ticker}
            onChange={e => setTicker(e.target.value.toUpperCase())}
            onKeyDown={e => e.key === 'Enter' && runCycle()}
            maxLength={12}
            style={{ letterSpacing: '1px' }}
          />
          <select style={{ padding: '10px 14px', borderRadius: 8, background: 'var(--bg-glass)', border: '1px solid var(--border)', color: 'var(--text-primary)', fontSize: 14 }}>
            <option>1D</option>
            <option>1W</option>
            <option>1M</option>
          </select>
          <button
            className="btn btn-primary"
            onClick={runCycle}
            disabled={!ticker || loading}
            id="run-analysis-btn"
          >
            {loading ? '⏳ Analyzing...' : '🚀 Run Analysis'}
          </button>
        </div>

        {/* ── KPI Row ── */}
        <div className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-label">Portfolio Value (INR)</div>
            <div className="kpi-value" style={{ background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>₹10.72L</div>
            <div className="kpi-change up">↑ +7.2% all time</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Total Signals</div>
            <div className="kpi-value">{recentTrades.length || 0}</div>
            <div className="kpi-change up">↑ This session</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Win Rate (NSE)</div>
            <div className="kpi-value" style={{ color: 'var(--accent-green)' }}>68%</div>
            <div className="kpi-change up">↑ Above Nifty benchmark</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Sharpe Ratio</div>
            <div className="kpi-value">1.42</div>
            <div className="kpi-change up">↑ Excellent risk-adj.</div>
          </div>
        </div>

        {/* ── Dashboard Grid ── */}
        <div className="dashboard-grid">
          <PortfolioChart data={MOCK_PORTFOLIO} />
          <RiskGauge />
        </div>

        {/* ── Agent Status Panel ── */}
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="section-title">🤖 Agent Status</div>
          <AgentStatusPanel agents={AGENTS} statuses={agentStatusMap} isRunning={loading} />
        </div>

        {/* ── Trade Log ── */}
        <div className="card">
          <div className="section-title">📋 Recent Signals</div>
          <TradeLog trades={recentTrades} />
        </div>
      </main>
    </div>
  )
}
