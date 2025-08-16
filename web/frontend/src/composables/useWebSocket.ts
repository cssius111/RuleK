/**
 * WebSocket连接管理Hook
 * 支持自动重连、心跳检测、消息队列等功能
 */

import { ref, onMounted, onUnmounted } from 'vue'
import type { Ref } from 'vue'

// 消息类型定义
interface WebSocketMessage {
  id: string
  type: string
  data: any
  timestamp: string
  sequence: number
}

// 连接状态
export enum ConnectionState {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

// 配置选项
export interface UseWebSocketOptions {
  url: string
  clientId: string
  reconnect?: boolean
  reconnectInterval?: number
  reconnectMaxAttempts?: number
  heartbeatInterval?: number
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Error) => void
}

export function useWebSocket(options: UseWebSocketOptions) {
  const {
    url,
    clientId,
    reconnect = true,
    reconnectInterval = 3000,
    reconnectMaxAttempts = 5,
    heartbeatInterval = 30000,
    onMessage,
    onConnect,
    onDisconnect,
    onError
  } = options

  // 响应式状态
  const ws: Ref<WebSocket | null> = ref(null)
  const connectionState: Ref<ConnectionState> = ref(ConnectionState.DISCONNECTED)
  const reconnectAttempts = ref(0)
  const messageQueue: Ref<any[]> = ref([])
  const lastSequence = ref(0)

  // 定时器
  let heartbeatTimer: number | null = null
  let reconnectTimer: number | null = null

  /**
   * 建立WebSocket连接
   */
  const connect = () => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      return
    }

    connectionState.value = ConnectionState.CONNECTING
    
    try {
      // 创建WebSocket连接
      const wsUrl = `${url}?client_id=${clientId}`
      ws.value = new WebSocket(wsUrl)

      // 连接打开
      ws.value.onopen = () => {
        console.log(`WebSocket connected to ${url}`)
        connectionState.value = ConnectionState.CONNECTED
        reconnectAttempts.value = 0
        
        // 发送重连消息（如果有队列消息）
        if (messageQueue.value.length > 0) {
          send({ type: 'reconnect', data: { last_sequence: lastSequence.value } })
        }
        
        // 启动心跳
        startHeartbeat()
        
        // 回调
        onConnect?.()
      }

      // 接收消息
      ws.value.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          
          // 更新序列号
          if (message.sequence) {
            lastSequence.value = message.sequence
          }
          
          // 处理不同类型的消息
          switch (message.type) {
            case 'ping':
              // 响应心跳
              send({ type: 'pong', data: {} })
              break
              
            case 'stream_chunk':
              // 流式数据块
              handleStreamChunk(message.data)
              break
              
            default:
              // 其他消息，传递给回调
              onMessage?.(message)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      // 连接关闭
      ws.value.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        connectionState.value = ConnectionState.DISCONNECTED
        stopHeartbeat()
        
        // 尝试重连
        if (reconnect && reconnectAttempts.value < reconnectMaxAttempts) {
          scheduleReconnect()
        }
        
        // 回调
        onDisconnect?.()
      }

      // 连接错误
      ws.value.onerror = (event) => {
        console.error('WebSocket error:', event)
        connectionState.value = ConnectionState.ERROR
        
        // 回调
        onError?.(new Error('WebSocket connection error'))
      }
      
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      connectionState.value = ConnectionState.ERROR
      onError?.(error as Error)
      
      // 尝试重连
      if (reconnect && reconnectAttempts.value < reconnectMaxAttempts) {
        scheduleReconnect()
      }
    }
  }

  /**
   * 断开WebSocket连接
   */
  const disconnect = () => {
    stopHeartbeat()
    
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    
    connectionState.value = ConnectionState.DISCONNECTED
  }

  /**
   * 发送消息
   */
  const send = (data: any): boolean => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      try {
        ws.value.send(JSON.stringify(data))
        return true
      } catch (error) {
        console.error('Failed to send WebSocket message:', error)
        // 加入队列
        messageQueue.value.push(data)
        return false
      }
    } else {
      // 连接未就绪，加入队列
      messageQueue.value.push(data)
      
      // 尝试重连
      if (connectionState.value === ConnectionState.DISCONNECTED && reconnect) {
        connect()
      }
      
      return false
    }
  }

  /**
   * 处理流式数据块
   */
  const streamBuffer = ref<Map<number, string>>(new Map())
  
  const handleStreamChunk = (data: any) => {
    const { chunk_id, content, is_final } = data
    
    if (is_final) {
      // 流结束，清理缓冲区
      streamBuffer.value.clear()
    } else {
      // 累积数据块
      streamBuffer.value.set(chunk_id, content)
    }
    
    // 传递给消息处理器
    onMessage?.({
      id: `stream_${chunk_id}`,
      type: 'stream_chunk',
      data,
      timestamp: new Date().toISOString(),
      sequence: lastSequence.value
    })
  }

  /**
   * 启动心跳
   */
  const startHeartbeat = () => {
    stopHeartbeat()
    
    heartbeatTimer = window.setInterval(() => {
      if (ws.value?.readyState === WebSocket.OPEN) {
        // 心跳会由服务器发送ping，客户端只需响应pong
        // 这里可以添加额外的健康检查
      } else {
        // 连接已断开，停止心跳
        stopHeartbeat()
      }
    }, heartbeatInterval)
  }

  /**
   * 停止心跳
   */
  const stopHeartbeat = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  /**
   * 计划重连
   */
  const scheduleReconnect = () => {
    if (reconnectTimer) {
      return
    }
    
    reconnectAttempts.value++
    connectionState.value = ConnectionState.RECONNECTING
    
    console.log(`Scheduling reconnect attempt ${reconnectAttempts.value}/${reconnectMaxAttempts}`)
    
    reconnectTimer = window.setTimeout(() => {
      reconnectTimer = null
      connect()
    }, reconnectInterval * Math.min(reconnectAttempts.value, 3)) // 指数退避
  }

  /**
   * 发送队列中的消息
   */
  const flushMessageQueue = () => {
    while (messageQueue.value.length > 0) {
      const message = messageQueue.value.shift()
      if (!send(message)) {
        // 发送失败，放回队列
        messageQueue.value.unshift(message)
        break
      }
    }
  }

  // 生命周期
  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  // 返回公共API
  return {
    // 状态
    connectionState,
    reconnectAttempts,
    messageQueue,
    
    // 方法
    connect,
    disconnect,
    send,
    
    // 工具方法
    isConnected: () => ws.value?.readyState === WebSocket.OPEN,
    getBufferedAmount: () => ws.value?.bufferedAmount || 0,
    flushMessageQueue
  }
}

// 导出类型
export type { WebSocketMessage, UseWebSocketOptions }
