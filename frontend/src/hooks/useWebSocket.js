import { useState, useEffect, useCallback } from 'react'

const WS_URL = 'ws://localhost:8000/ws'

export function useWebSocket() {
  const [socket, setSocket]         = useState(null)
  const [connected, setConnected]   = useState(false)
  const [messages, setMessages]     = useState([])
  const [agentEvents, setAgentEvents] = useState([])

  const connect = useCallback(() => {
    const ws = new WebSocket(WS_URL)

    ws.onopen = () => {
      setConnected(true)
      console.log('🔌 WebSocket connected')
    }

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        setMessages(prev => [data, ...prev].slice(0, 100))
        if (data.type === 'agent_event') {
          setAgentEvents(prev => {
            const filtered = prev.filter(a => a.agent !== data.agent)
            return [...filtered, data]
          })
        }
      } catch (_) {}
    }

    ws.onclose = () => {
      setConnected(false)
      // Auto-reconnect after 3 seconds
      setTimeout(connect, 3000)
    }

    ws.onerror = () => ws.close()
    setSocket(ws)
  }, [])

  useEffect(() => {
    connect()
    return () => socket?.close()
  }, [])

  return { connected, messages, agentEvents }
}
