/**
 * WebSocket composable for Waifu Avatar System
 * Handles connection, protocol, heartbeat, and reconnection logic
 */

import { ref, onUnmounted, readonly } from 'vue'
import type { 
  ClientMessage, 
  ServerResponse, 
  ConnectionState, 
  WaifuConfig
} from '@/types/waifu-protocol'
import { DEFAULT_CONFIG } from '@/types/waifu-protocol'

export function useWebSocket(config: Partial<WaifuConfig> = {}) {
  // Merge with default config
  const finalConfig: WaifuConfig = { ...DEFAULT_CONFIG, ...config }
  
  // Reactive state
  const connectionState = ref<ConnectionState>('disconnected' as ConnectionState)
  const lastError = ref<string | null>(null)
  const isReconnecting = ref(false)
  
  // Internal state
  let ws: WebSocket | null = null
  let heartbeatInterval: number | null = null
  let reconnectTimeout: number | null = null
  let reconnectAttempts = 0
  let isIntentionalDisconnect = false
  
  // Event callbacks
  const responseCallbacks = new Set<(response: ServerResponse) => void>()
  const connectionCallbacks = new Set<(state: ConnectionState) => void>()
  
  /**
   * Connect to WebSocket server
   */
  const connect = async (): Promise<void> => {
    if (ws?.readyState === WebSocket.OPEN) {
      console.warn('WebSocket already connected')
      return
    }
    
    isIntentionalDisconnect = false
    connectionState.value = 'connecting' as ConnectionState
    lastError.value = null
    
    try {
      ws = new WebSocket(finalConfig.websocketUrl)
      setupWebSocketHandlers()
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      handleConnectionError(error instanceof Error ? error.message : 'Unknown error')
    }
  }
  
  /**
   * Disconnect from WebSocket server
   */
  const disconnect = (): void => {
    isIntentionalDisconnect = true
    cleanup()
    connectionState.value = 'disconnected' as ConnectionState
  }
  
  /**
   * Send message to server
   */
  const sendMessage = (message: string, messageId?: string): void => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected')
    }
    
    const clientMessage: ClientMessage = {
      message,
      id: messageId || generateMessageId()
    }
    
    ws.send(JSON.stringify(clientMessage))
  }
  
  /**
   * Send heartbeat
   */
  const sendHeartbeat = (): void => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      return
    }
    
    ws.send('alive')
  }
  
  /**
   * Subscribe to server responses
   */
  const onResponse = (callback: (response: ServerResponse) => void): (() => void) => {
    responseCallbacks.add(callback)
    
    // Return unsubscribe function
    return () => {
      responseCallbacks.delete(callback)
    }
  }
  
  /**
   * Subscribe to connection state changes
   */
  const onConnectionState = (callback: (state: ConnectionState) => void): (() => void) => {
    connectionCallbacks.add(callback)
    
    // Return unsubscribe function
    return () => {
      connectionCallbacks.delete(callback)
    }
  }
  
  /**
   * Setup WebSocket event handlers
   */
  const setupWebSocketHandlers = (): void => {
    if (!ws) return
    
    ws.onopen = () => {
      console.log('WebSocket connected')
      connectionState.value = 'connected' as ConnectionState
      isReconnecting.value = false
      reconnectAttempts = 0
      lastError.value = null
      
      // Start heartbeat
      startHeartbeat()
      
      // Notify callbacks
      connectionCallbacks.forEach(callback => callback(connectionState.value))
    }
    
    ws.onmessage = (event) => {
      try {
        let response: ServerResponse
        
        // Handle heartbeat response
        if (event.data === 'alive') {
          response = 'alive'
        } else {
          // Parse JSON response
          response = JSON.parse(event.data)
        }
        
        // Notify all response callbacks
        responseCallbacks.forEach(callback => callback(response))
        
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
        console.error('Raw message:', event.data)
      }
    }
    
    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)
      stopHeartbeat()
      
      if (!isIntentionalDisconnect) {
        handleConnectionLoss()
      } else {
        connectionState.value = 'disconnected' as ConnectionState
        connectionCallbacks.forEach(callback => callback(connectionState.value))
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      handleConnectionError('WebSocket error occurred')
    }
  }
  
  /**
   * Handle connection errors
   */
  const handleConnectionError = (errorMessage: string): void => {
    lastError.value = errorMessage
    connectionState.value = 'error' as ConnectionState
    connectionCallbacks.forEach(callback => callback(connectionState.value))
    
    if (!isIntentionalDisconnect) {
      scheduleReconnect()
    }
  }
  
  /**
   * Handle connection loss
   */
  const handleConnectionLoss = (): void => {
    connectionState.value = 'disconnected' as ConnectionState
    connectionCallbacks.forEach(callback => callback(connectionState.value))
    
    if (!isIntentionalDisconnect) {
      scheduleReconnect()
    }
  }
  
  /**
   * Schedule reconnection attempt
   */
  const scheduleReconnect = (): void => {
    if (reconnectAttempts >= finalConfig.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached')
      connectionState.value = 'error' as ConnectionState
      lastError.value = 'Max reconnection attempts exceeded'
      return
    }
    
    reconnectAttempts++
    isReconnecting.value = true
    connectionState.value = 'reconnecting' as ConnectionState
    
    console.log(`Scheduling reconnect attempt ${reconnectAttempts}/${finalConfig.maxReconnectAttempts}`)
    
    reconnectTimeout = window.setTimeout(() => {
      connect()
    }, finalConfig.reconnectDelay)
    
    connectionCallbacks.forEach(callback => callback(connectionState.value))
  }
  
  /**
   * Start heartbeat interval
   */
  const startHeartbeat = (): void => {
    stopHeartbeat() // Clear any existing interval
    
    heartbeatInterval = window.setInterval(() => {
      sendHeartbeat()
    }, finalConfig.heartbeatInterval)
  }
  
  /**
   * Stop heartbeat interval
   */
  const stopHeartbeat = (): void => {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
  }
  
  /**
   * Generate unique message ID
   */
  const generateMessageId = (): string => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  /**
   * Cleanup resources
   */
  const cleanup = (): void => {
    stopHeartbeat()
    
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }
    
    if (ws) {
      ws.close()
      ws = null
    }
    
    responseCallbacks.clear()
    connectionCallbacks.clear()
  }
  
  // Cleanup on component unmount
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    // State
    connectionState: readonly(connectionState),
    lastError: readonly(lastError),
    isReconnecting: readonly(isReconnecting),
    
    // Methods
    connect,
    disconnect,
    sendMessage,
    sendHeartbeat,
    
    // Event subscriptions
    onResponse,
    onConnectionState,
    
    // Utils
    generateMessageId
  }
}