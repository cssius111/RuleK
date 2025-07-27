import { ref } from 'vue'
import type { GameUpdate } from '@/types/game'

export interface WebSocketManager {
  connect(gameId: string): Promise<void>
  disconnect(): void
  send(type: string, data?: any): void
  on(event: string, handler: (data: any) => void): void
  off(event: string, handler: (data: any) => void): void
  isConnected: boolean
}

class WebSocketClient implements WebSocketManager {
  private ws: WebSocket | null = null
  private gameId: string | null = null
  private handlers: Map<string, Set<(data: any) => void>> = new Map()
  private reconnectTimer: number | null = null
  private pingTimer: number | null = null
  private _isConnected = ref(false)
  
  get isConnected() {
    return this._isConnected.value
  }
  
  async connect(gameId: string): Promise<void> {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      if (this.gameId === gameId) {
        return // 已经连接到相同的游戏
      }
      this.disconnect()
    }
    
    this.gameId = gameId
    
    return new Promise((resolve, reject) => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/ws/${gameId}`
      
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log(`WebSocket connected to game: ${gameId}`)
        this._isConnected.value = true
        this.startPing()
        resolve()
      }
      
      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        reject(error)
      }
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this._isConnected.value = false
        this.stopPing()
        this.attemptReconnect()
      }
      
      // 设置连接超时
      setTimeout(() => {
        if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
          this.ws.close()
          reject(new Error('WebSocket connection timeout'))
        }
      }, 10000)
    })
  }
  
  disconnect(): void {
    this.stopReconnect()
    this.stopPing()
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    this.gameId = null
    this._isConnected.value = false
    this.handlers.clear()
  }
  
  send(type: string, data?: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected')
      return
    }
    
    const message = {
      type,
      data,
      timestamp: new Date().toISOString()
    }
    
    this.ws.send(JSON.stringify(message))
  }
  
  on(event: string, handler: (data: any) => void): void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set())
    }
    this.handlers.get(event)!.add(handler)
  }
  
  off(event: string, handler: (data: any) => void): void {
    const handlers = this.handlers.get(event)
    if (handlers) {
      handlers.delete(handler)
      if (handlers.size === 0) {
        this.handlers.delete(event)
      }
    }
  }
  
  private handleMessage(message: GameUpdate): void {
    const handlers = this.handlers.get(message.update_type)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message.data)
        } catch (e) {
          console.error('Error in WebSocket handler:', e)
        }
      })
    }
    
    // 处理 pong 消息
    if (message.type === 'pong') {
      // 收到 pong，连接正常
    }
  }
  
  private startPing(): void {
    this.stopPing()
    this.pingTimer = window.setInterval(() => {
      this.send('ping')
    }, 30000) // 每30秒发送一次ping
  }
  
  private stopPing(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer)
      this.pingTimer = null
    }
  }
  
  private attemptReconnect(): void {
    if (!this.gameId) return
    
    this.stopReconnect()
    
    console.log('Attempting to reconnect in 5 seconds...')
    this.reconnectTimer = window.setTimeout(() => {
      if (this.gameId) {
        this.connect(this.gameId).catch(e => {
          console.error('Reconnection failed:', e)
        })
      }
    }, 5000)
  }
  
  private stopReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }
}

// 创建单例
let wsInstance: WebSocketClient | null = null

export function useWebSocket(): WebSocketManager {
  if (!wsInstance) {
    wsInstance = new WebSocketClient()
  }
  return wsInstance
}
