export default function AgentStatusPanel({ agents, statuses, isRunning }) {
  return (
    <div className="agent-grid">
      {agents.map((agent, i) => {
        const status = statuses[agent.id] || (isRunning && i < 4 ? 'running' : 'idle')
        return (
          <div key={agent.id} className={`agent-card ${status}`} id={`agent-${agent.id}`}>
            <div className="agent-avatar" style={{ background: `${agent.color}22` }}>
              {agent.icon}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div className="agent-name">{agent.name}</div>
              <div className="agent-status">
                {status === 'running'   && '⚙️ Processing...'}
                {status === 'completed' && '✅ Complete'}
                {status === 'error'     && '❌ Error'}
                {status === 'idle'      && 'Standby'}
              </div>
            </div>
            <div className={`status-dot ${status}`} />
          </div>
        )
      })}
    </div>
  )
}
