/**
 * Voice Capture composable for Waifu Avatar System
 * Enhanced speech-to-text with intelligent buffering and silence detection
 */

import { ref, computed, onUnmounted, readonly } from 'vue'
import { VoiceState } from '@/types/waifu-protocol'
import type { WaifuConfig } from '@/types/waifu-protocol'

export function useVoiceCapture(config: Partial<Pick<WaifuConfig, 'voiceTimeout'>> = {}) {
  const voiceTimeout = config.voiceTimeout || 3000
  
  // Reactive state
  const voiceState = ref<VoiceState>(VoiceState.Idle)
  const currentTranscript = ref('')
  const finalTranscript = ref('')
  const isSupported = ref(false)
  const errorMessage = ref<string | null>(null)
  
  // Internal state
  let recognition: any = null
  let silenceTimeout: number | null = null
  let isActive = false
  
  // Event callbacks
  const messageCallbacks = new Set<(message: string) => void>()
  const stateCallbacks = new Set<(state: VoiceState) => void>()
  
  // Computed
  const displayText = computed(() => {
    if (finalTranscript.value && currentTranscript.value) {
      return `${finalTranscript.value} ${currentTranscript.value}`
    }
    return finalTranscript.value || currentTranscript.value
  })
  
  const isListening = computed(() => voiceState.value === VoiceState.Listening)
  const isProcessing = computed(() => voiceState.value === VoiceState.Processing)
  const canStart = computed(() => isSupported.value && voiceState.value === VoiceState.Idle)
  
  /**
   * Initialize speech recognition
   */
  const initialize = (): boolean => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      errorMessage.value = 'Speech recognition not supported in this browser'
      isSupported.value = false
      return false
    }
    
    recognition = new SpeechRecognition()
    recognition.lang = 'es-ES'
    recognition.continuous = true
    recognition.interimResults = true
    recognition.maxAlternatives = 1
    
    setupSpeechHandlers()
    
    isSupported.value = true
    errorMessage.value = null
    
    console.log('Voice capture initialized')
    return true
  }
  
  /**
   * Start voice capture
   */
  const start = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!recognition) {
        if (!initialize()) {
          reject(new Error('Speech recognition not available'))
          return
        }
      }
      
      if (isActive) {
        console.warn('Voice capture already active')
        resolve()
        return
      }
      
      try {
        clearSilenceTimeout()
        currentTranscript.value = ''
        finalTranscript.value = ''
        errorMessage.value = null
        
        isActive = true
        recognition!.start()
        resolve()
      } catch (error) {
        reject(error)
      }
    })
  }
  
  /**
   * Stop voice capture
   */
  const stop = (): void => {
    if (!isActive || !recognition) {
      return
    }
    
    isActive = false
    clearSilenceTimeout()
    
    try {
      recognition.stop()
    } catch (error) {
      console.warn('Error stopping recognition:', error)
    }
    
    updateState(VoiceState.Idle)
  }
  
  /**
   * Toggle voice capture
   */
  const toggle = async (): Promise<void> => {
    if (isListening.value) {
      stop()
    } else {
      await start()
    }
  }
  
  /**
   * Subscribe to voice messages
   */
  const onMessage = (callback: (message: string) => void): (() => void) => {
    messageCallbacks.add(callback)
    
    return () => {
      messageCallbacks.delete(callback)
    }
  }
  
  /**
   * Subscribe to voice state changes
   */
  const onStateChange = (callback: (state: VoiceState) => void): (() => void) => {
    stateCallbacks.add(callback)
    
    return () => {
      stateCallbacks.delete(callback)
    }
  }
  
  /**
   * Setup speech recognition event handlers
   */
  const setupSpeechHandlers = (): void => {
    if (!recognition) return
    
    recognition.onstart = () => {
      console.log('Voice capture started')
      updateState(VoiceState.Listening)
    }
    
    recognition.onend = () => {
      console.log('Voice capture ended')
      
      if (isActive) {
        // Unexpected end, restart if still active
        setTimeout(() => {
          if (isActive && recognition) {
            try {
              recognition.start()
            } catch (error) {
              console.error('Failed to restart recognition:', error)
              handleError('Failed to restart voice capture')
            }
          }
        }, 100)
      } else {
        updateState(VoiceState.Idle)
      }
    }
    
    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error)
      
      // Handle specific errors
      switch (event.error) {
        case 'network':
          handleError('Network error - check internet connection')
          break
        case 'not-allowed':
          handleError('Microphone access denied')
          break
        case 'no-speech':
          // Silent error - just continue
          console.log('No speech detected')
          break
        default:
          handleError(`Speech recognition error: ${event.error}`)
      }
    }
    
    recognition.onresult = (event: any) => {
      handleSpeechResult(event)
    }
  }
  
  /**
   * Handle speech recognition results
   */
  const handleSpeechResult = (event: any): void => {
    clearSilenceTimeout()
    
    let interimText = ''
    let finalText = ''
    
    // Process all results
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const result = event.results[i]
      const transcript = result[0].transcript
      
      if (result.isFinal) {
        finalText += transcript
      } else {
        interimText += transcript
      }
    }
    
    // Update transcripts
    if (finalText.trim()) {
      finalTranscript.value += finalText
    }
    currentTranscript.value = interimText
    
    // If we have final text, start silence timer
    if (finalText.trim()) {
      updateState(VoiceState.Processing)
      startSilenceTimeout()
    }
  }
  
  /**
   * Start silence timeout
   */
  const startSilenceTimeout = (): void => {
    clearSilenceTimeout()
    
    silenceTimeout = window.setTimeout(() => {
      const message = finalTranscript.value.trim()
      
      if (message) {
        console.log('Voice message detected:', message)
        
        // Send message to callbacks
        messageCallbacks.forEach(callback => callback(message))
        
        // Reset state
        updateState(VoiceState.Sending)
        
        // Clear transcripts after a delay
        setTimeout(() => {
          finalTranscript.value = ''
          currentTranscript.value = ''
          updateState(VoiceState.Listening)
        }, 1000)
      } else {
        updateState(VoiceState.Listening)
      }
    }, voiceTimeout)
  }
  
  /**
   * Clear silence timeout
   */
  const clearSilenceTimeout = (): void => {
    if (silenceTimeout) {
      clearTimeout(silenceTimeout)
      silenceTimeout = null
    }
  }
  
  /**
   * Update voice state
   */
  const updateState = (newState: VoiceState): void => {
    if (voiceState.value !== newState) {
      voiceState.value = newState
      stateCallbacks.forEach(callback => callback(newState))
    }
  }
  
  /**
   * Handle errors
   */
  const handleError = (error: string): void => {
    errorMessage.value = error
    updateState(VoiceState.Idle)
    isActive = false
  }
  
  /**
   * Cleanup resources
   */
  const cleanup = (): void => {
    stop()
    clearSilenceTimeout()
    messageCallbacks.clear()
    stateCallbacks.clear()
    
    if (recognition) {
      recognition.onstart = null
      recognition.onend = null
      recognition.onerror = null
      recognition.onresult = null
      recognition = null
    }
  }
  
  // Cleanup on component unmount
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    // State
    voiceState: readonly(voiceState),
    currentTranscript: readonly(currentTranscript),
    finalTranscript: readonly(finalTranscript),
    displayText: readonly(displayText),
    isSupported: readonly(isSupported),
    errorMessage: readonly(errorMessage),
    
    // Computed
    isListening: readonly(isListening),
    isProcessing: readonly(isProcessing),
    canStart: readonly(canStart),
    
    // Methods
    initialize,
    start,
    stop,
    toggle,
    
    // Event subscriptions
    onMessage,
    onStateChange
  }
}