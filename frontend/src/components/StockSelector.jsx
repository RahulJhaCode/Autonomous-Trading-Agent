// Quick-pick panel for Nifty 50 / Sensex 30 stocks
const NIFTY_50 = [
  { symbol: 'RELIANCE',   name: 'Reliance',  sector: 'Energy' },
  { symbol: 'TCS',        name: 'TCS',       sector: 'IT' },
  { symbol: 'HDFCBANK',   name: 'HDFC Bank', sector: 'Banking' },
  { symbol: 'INFY',       name: 'Infosys',   sector: 'IT' },
  { symbol: 'ICICIBANK',  name: 'ICICI Bank',sector: 'Banking' },
  { symbol: 'HINDUNILVR', name: 'HUL',       sector: 'FMCG' },
  { symbol: 'SBIN',       name: 'SBI',       sector: 'Banking' },
  { symbol: 'BHARTIARTL', name: 'Airtel',    sector: 'Telecom' },
  { symbol: 'KOTAKBANK',  name: 'Kotak Bank',sector: 'Banking' },
  { symbol: 'LT',         name: 'L&T',       sector: 'Industrials' },
  { symbol: 'HCLTECH',    name: 'HCL Tech',  sector: 'IT' },
  { symbol: 'BAJFINANCE', name: 'Bajaj Fin', sector: 'Financials' },
  { symbol: 'ASIANPAINT', name: 'Asian Paint',sector: 'Materials' },
  { symbol: 'AXISBANK',   name: 'Axis Bank', sector: 'Banking' },
  { symbol: 'TITAN',      name: 'Titan',     sector: 'Consumer' },
  { symbol: 'MARUTI',     name: 'Maruti',    sector: 'Auto' },
  { symbol: 'SUNPHARMA',  name: 'Sun Pharma',sector: 'Pharma' },
  { symbol: 'WIPRO',      name: 'Wipro',     sector: 'IT' },
  { symbol: 'NTPC',       name: 'NTPC',      sector: 'Utilities' },
  { symbol: 'TATAMOTORS', name: 'Tata Motors',sector: 'Auto' },
]

const SECTOR_COLORS = {
  'IT': '#3b82f6', 'Banking': '#8b5cf6', 'Energy': '#f59e0b',
  'FMCG': '#10b981', 'Telecom': '#06b6d4', 'Industrials': '#f97316',
  'Financials': '#ec4899', 'Materials': '#84cc16', 'Consumer': '#a78bfa',
  'Auto': '#fb923c', 'Pharma': '#34d399', 'Utilities': '#94a3b8',
}

export default function StockSelector({ onSelect }) {
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
      <span style={{ fontSize: 11, color: 'var(--text-muted)', alignSelf: 'center', marginRight: 4 }}>
        Quick pick (Nifty 50):
      </span>
      {NIFTY_50.map(s => (
        <button
          key={s.symbol}
          onClick={() => onSelect(s.symbol)}
          title={`${s.name} — ${s.sector}`}
          style={{
            padding: '3px 8px',
            borderRadius: 4,
            border: `1px solid ${SECTOR_COLORS[s.sector] || 'var(--border)'}22`,
            background: `${SECTOR_COLORS[s.sector] || '#3b82f6'}11`,
            color: SECTOR_COLORS[s.sector] || 'var(--text-secondary)',
            fontSize: 11,
            fontFamily: 'var(--font-mono)',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.15s',
          }}
          onMouseEnter={e => e.target.style.opacity = '0.7'}
          onMouseLeave={e => e.target.style.opacity = '1'}
        >
          {s.symbol}
        </button>
      ))}
    </div>
  )
}
