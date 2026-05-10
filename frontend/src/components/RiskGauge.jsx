export default function RiskGauge() {
  const risks = [
    { label: 'Portfolio Concentration', value: 38, color: 'var(--accent-blue)' },
    { label: 'Daily Drawdown Used',     value: 12, color: 'var(--accent-green)' },
    { label: 'VIX Exposure',            value: 55, color: 'var(--accent-amber)' },
    { label: 'Open Positions',          value: 30, color: 'var(--accent-purple)' },
  ]

  return (
    <div className="card">
      <div className="card-title">Risk Exposure</div>
      <div className="risk-meter">
        {risks.map(r => (
          <div className="risk-bar-wrap" key={r.label}>
            <div className="risk-bar-label">
              <span>{r.label}</span>
              <span style={{ color: r.value > 70 ? 'var(--accent-red)' : 'var(--text-secondary)' }}>{r.value}%</span>
            </div>
            <div className="risk-bar-track">
              <div className="risk-bar-fill" style={{ width: `${r.value}%`, background: r.color }} />
            </div>
          </div>
        ))}

        <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--border)', fontSize: 12, color: 'var(--text-muted)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Max Drawdown Limit</span>
            <span style={{ color: 'var(--accent-green)' }}>2.0%</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
            <span>Min Confidence Required</span>
            <span style={{ color: 'var(--accent-blue)' }}>65%</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
            <span>Max Open Positions</span>
            <span>10</span>
          </div>
        </div>
      </div>
    </div>
  )
}
