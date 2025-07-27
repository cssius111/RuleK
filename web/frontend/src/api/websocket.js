import { ref } from 'vue'

export function useWebSocket(gameId, options = {}) {
  const ws = ref(null)
  const connected = ref(false)
  const reconnectTimer = ref(null)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5
  const reconnectDelay = 3000

  const connect = () => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/ws/${gameId}`

    try {
      ws.value = new WebSocket(url)

      ws.value.onopen = () => {
        console.log('WebSocket connected')
        connected.value = true
        reconnectAttempts.value = 0
        
        // 发送ping保持连接
        sendPing()
        
        if (options.onConnect) {
          options.onConnect()
        }
      }

      ws.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // 处理pong响应
          if (data.type === 'pong') {
            return
          }
          
          // 处理游戏更新
          if (options.onUpdate) {
            options.onUpdate(data)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.value.onerror = (error) => {
        console.error('WebSocket error:', error)
        if (options.onError) {
          options.onError(error)
        }
      }

      ws.value.onclose = () => {
        console.log('WebSocket disconnected')
        connected.value = false
        ws.value = null
        
        if (options.onDisconnect) {
          options.onDisconnect()
        }
        
        // 自动重连
        attemptReconnect()
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
    }
  }

  const disconnect = () => {
    if (reconnectTimer.value) {
      clearTimeout(reconnectTimer.value)
      reconnectTimer.value = null
    }
    
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    
    connected.value = false
  }

  const send = (message) => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  const sendPing = () => {
    if (connected.value) {
      send({ type: 'ping' })
      // 每30秒发送一次ping
      setTimeout(sendPing, 30000)
    }
  }

  const attemptReconnect = () => {
    if (reconnectAttempts.value >= maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      if (options.onReconnectFailed) {
        options.onReconnectFailed()
      }
      return
    }
    
    reconnectAttempts.value++
    console.log(`Reconnecting... (attempt ${reconnectAttempts.value})`)
    
    reconnectTimer.value = setTimeout(() => {
      connect()
    }, reconnectDelay)
  }

  // 发送游戏动作
  const sendAction = (actionType, data = {}) => {
    send({
      type: 'action',
      data: {
        action_type: actionType,
        ...data
      }
    })
  }

  return {
    connected,
    connect,
    disconnect,
    send,
    sendAction
  }
}
