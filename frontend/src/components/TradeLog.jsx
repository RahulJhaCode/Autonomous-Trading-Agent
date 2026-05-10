// Demo data uses Indian Nifty 50 / Sensex stocks and INR prices
const DEMO_TRADES = [
  { ticker: 'RELIANCE',  company: 'Reliance Industries', action: 'BUY',  confidence: '84%', size: '₹49,200', approved: true,  time: '13:02' },
  { ticker: 'TCS',       company: 'Tata Consultancy Services', action: 'HOLD', confidence: '53%', size: '—',      approved: false, time: '12:41' },
  { ticker: 'HDFCBANK',  company: 'HDFC Bank',           action: 'BUY',  confidence: '91%', size: '₹47,800', approved: true,  time: '11:15' },
  { ticker: 'INFY',      company: 'Infosys',              action: 'SELL', confidence: '76%', size: '₹32,000', approved: true,  time: '10:30' },
  { ticker: 'ICICIBANK', company: 'ICICI Bank',           action: 'BUY',  confidence: '69%', size: '₹42,000', approved: true,  time: '09:45' },
]

export default function TradeLog({ trades }) {
  const displayTrades = trades.length > 0 ? trades : DEMO_TRADES

  return (
    <table className="trade-table" id="trade-log-table">
      <thead>
        <tr>
          <th>Symbol (NSE)</th>
          <th>Company</th>
          <th>Action</th>
          <th>Confidence</th>
          <th>Position (INR)</th>
          <th>Status</th>
          <th>Time (IST)</th>
        </tr>
      </thead>
      <tbody>
        {displayTrades.map((t, i) => (
          <tr key={i}>
            <td>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: 14 }}>
                {t.ticker || '—'}
              </span>
            </td>
            <td style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
              {t.company || '—'}
            </td>
            <td>
              <span className={`badge badge-${(t.action || 'HOLD').toLowerCase()}`}>
                {t.action || 'SIGNAL'}
              </span>
            </td>
            <td style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
              {t.confidence || '—'}
            </td>
            <td style={{ fontFamily: 'var(--font-mono)' }}>{t.size || '—'}</td>
            <td>
              <span className={`badge ${t.approved ? 'badge-approved' : 'badge-rejected'}`}>
                {t.approved ? '✅ Approved' : '❌ Rejected'}
              </span>
            </td>
            <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>
              {t.time || new Date().toLocaleTimeString('en-IN')}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
