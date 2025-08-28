/**
 * Response Coordinator composable for Waifu Avatar System
 * Handles coordination between fast output and complete responses
 */

import { reactive, readonly } from 'vue'
import type {
  ServerResponse,
  FastOutputResponse,
  AudioVisemaResponse,
  ExpressionsResponse,
  AnimationsResponse,
  CompleteResponse,
  ResponseStatus,
  ServerErrorResponse
} from '@/types/waifu-protocol'
import {
  isFastOutputResponse,
  isAudioVisemaResponse,
  isExpressionsResponse,
  isAnimationsResponse,
  isServerHeartbeat,
  isServerErrorResponse
} from '@/types/waifu-protocol'

export function useResponseCoordinator() {
  // Pending complete responses (by message_id)
  const pendingResponses = reactive(new Map<string, CompleteResponse>())
  const responseStatuses = reactive(new Map<string, ResponseStatus>())

  // Statistics
  const stats = reactive({
    totalFastOutputs: 0,
    totalCompleteResponses: 0,
    averageCompletionTime: 0
  })

  // Event callbacks
  const fastOutputCallbacks = new Set<(response: FastOutputResponse) => void>()
  const completeResponseCallbacks = new Set<(response: CompleteResponse) => void>()
  const errorCallbacks = new Set<(response: ServerErrorResponse) => void>()

  /**
   * Process incoming server response
   */
  const processResponse = (response: ServerResponse): void => {
    // Ignore heartbeat responses
    if (isServerHeartbeat(response)) {
      return
    }

    // Handle server error responses
    if (isServerErrorResponse(response)) {
      handleServerError(response)
      return
    }

    // Handle fast output response (no message_id)
    if (isFastOutputResponse(response)) {
      handleFastOutput(response)
      return
    }

    // Handle complete response parts (with message_id)
    if (isAudioVisemaResponse(response) || ('audio_url' in response && typeof response === 'object' && response !== null)) {
      handleAudioVisemaResponse(response as AudioVisemaResponse)
    } else if (isExpressionsResponse(response) || ('expresiones' in response && typeof response === 'object' && response !== null)) {
      handleExpressionsResponse(response as ExpressionsResponse)
    } else if (isAnimationsResponse(response)) {
      handleAnimationsResponse(response as AnimationsResponse)
    } else {
      console.warn('Unknown response type:', response)
    }
  }

  /**
   * Handle server error response
   */
  const handleServerError = (response: ServerErrorResponse): void => {
    console.error('🚨 Server error received:', response.error)
    
    // Notify error callbacks
    errorCallbacks.forEach(callback => callback(response))
  }

  /**
   * Handle fast output response
   */
  const handleFastOutput = (response: FastOutputResponse): void => {
    console.log('📤 Fast output received:', response.text)
    console.log('📤 Fast output full JSON:', JSON.stringify(response, null, 2))

    stats.totalFastOutputs++

    // Immediately notify callbacks
    fastOutputCallbacks.forEach(callback => callback(response))
  }

  /**
   * Handle audio + visemas response
   */
  const handleAudioVisemaResponse = (response: AudioVisemaResponse): void => {
    console.log('🎵 Audio + visemas received for:', response.message_id)

    const completeResponse = getOrCreateCompleteResponse(response.message_id)
    completeResponse.audio = response

    updateResponseStatus(response.message_id, 'hasAudio', true)
    checkCompletionAndNotify(response.message_id)
  }

  /**
   * Handle expressions response
   */
  const handleExpressionsResponse = (response: ExpressionsResponse): void => {
    console.log('😊 Expressions received for:', response.message_id)

    const completeResponse = getOrCreateCompleteResponse(response.message_id)
    completeResponse.expressions = response

    updateResponseStatus(response.message_id, 'hasExpressions', true)
    checkCompletionAndNotify(response.message_id)
  }

  /**
   * Handle animations response
   */
  const handleAnimationsResponse = (response: AnimationsResponse): void => {
    console.log('💃 Animations received for:', response.message_id)

    const completeResponse = getOrCreateCompleteResponse(response.message_id)
    completeResponse.animations = response

    updateResponseStatus(response.message_id, 'hasAnimations', true)
    checkCompletionAndNotify(response.message_id)
  }

  /**
   * Get or create complete response entry
   */
  const getOrCreateCompleteResponse = (messageId: string): CompleteResponse => {
    if (!pendingResponses.has(messageId)) {
      pendingResponses.set(messageId, {
        messageId,
        audio: undefined,
        expressions: undefined,
        animations: undefined
      })
    }

    return pendingResponses.get(messageId)!
  }

  /**
   * Update response status
   */
  const updateResponseStatus = (messageId: string, field: keyof Omit<ResponseStatus, 'messageId' | 'isComplete' | 'timestamp'>, value: boolean): void => {
    if (!responseStatuses.has(messageId)) {
      responseStatuses.set(messageId, {
        messageId,
        hasAudio: false,
        hasExpressions: false,
        hasAnimations: false,
        isComplete: false,
        timestamp: Date.now()
      })
    }

    const status = responseStatuses.get(messageId)!
    status[field] = value

    // Check if complete
    status.isComplete = status.hasAudio && status.hasExpressions && status.hasAnimations
  }

  /**
   * Check if response is complete and notify
   */
  const checkCompletionAndNotify = (messageId: string): void => {
    const status = responseStatuses.get(messageId)
    const completeResponse = pendingResponses.get(messageId)

    if (!status || !completeResponse) {
      return
    }

    if (status.isComplete) {
      console.log('✅ Complete response ready for:', messageId)

      // Calculate completion time
      const completionTime = Date.now() - status.timestamp
      updateAverageCompletionTime(completionTime)

      stats.totalCompleteResponses++

      // Notify callbacks
      completeResponseCallbacks.forEach(callback => callback(completeResponse))

      // Cleanup
      pendingResponses.delete(messageId)
      responseStatuses.delete(messageId)
    }
  }

  /**
   * Update average completion time
   */
  const updateAverageCompletionTime = (newTime: number): void => {
    const totalResponses = stats.totalCompleteResponses

    if (totalResponses === 0) {
      stats.averageCompletionTime = newTime
    } else {
      stats.averageCompletionTime = ((stats.averageCompletionTime * totalResponses) + newTime) / (totalResponses + 1)
    }
  }

  /**
   * Subscribe to fast output responses
   */
  const onFastOutput = (callback: (response: FastOutputResponse) => void): (() => void) => {
    fastOutputCallbacks.add(callback)

    return () => {
      fastOutputCallbacks.delete(callback)
    }
  }

  /**
   * Subscribe to complete responses
   */
  const onCompleteResponse = (callback: (response: CompleteResponse) => void): (() => void) => {
    completeResponseCallbacks.add(callback)

    return () => {
      completeResponseCallbacks.delete(callback)
    }
  }

  /**
   * Subscribe to server error responses
   */
  const onServerError = (callback: (response: ServerErrorResponse) => void): (() => void) => {
    errorCallbacks.add(callback)

    return () => {
      errorCallbacks.delete(callback)
    }
  }

  /**
   * Get pending response status for debugging
   */
  const getPendingStatus = (messageId: string): ResponseStatus | undefined => {
    return responseStatuses.get(messageId)
  }

  /**
   * Get all pending message IDs
   */
  const getPendingMessageIds = (): string[] => {
    return Array.from(pendingResponses.keys())
  }

  /**
   * Clear old pending responses (timeout cleanup)
   */
  const clearOldResponses = (maxAge: number = 30000): void => {
    const now = Date.now()

    for (const [messageId, status] of responseStatuses.entries()) {
      if (now - status.timestamp > maxAge) {
        console.warn(`Clearing old pending response: ${messageId}`)
        pendingResponses.delete(messageId)
        responseStatuses.delete(messageId)
      }
    }
  }

  /**
   * Reset all state
   */
  const reset = (): void => {
    pendingResponses.clear()
    responseStatuses.clear()
    fastOutputCallbacks.clear()
    completeResponseCallbacks.clear()
    errorCallbacks.clear()

    stats.totalFastOutputs = 0
    stats.totalCompleteResponses = 0
    stats.averageCompletionTime = 0
  }

  return {
    // State
    pendingResponses: readonly(pendingResponses),
    responseStatuses: readonly(responseStatuses),
    stats: readonly(stats),

    // Methods
    processResponse,
    getPendingStatus,
    getPendingMessageIds,
    clearOldResponses,
    reset,

    // Event subscriptions
    onFastOutput,
    onCompleteResponse,
    onServerError
  }
}
