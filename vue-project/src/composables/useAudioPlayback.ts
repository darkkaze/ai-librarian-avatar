/**
 * Audio Playback composable for Waifu Avatar System
 * Handles audio loading, playback, and synchronization with visemas
 */

import { ref, computed, onUnmounted, readonly } from 'vue'
import type { Visema } from '@/types/waifu-protocol'

interface AudioPlaybackState {
  isPlaying: boolean
  isLoading: boolean
  currentTime: number
  duration: number
  volume: number
  error: string | null
}

interface PlaybackOptions {
  baseUrl?: string
  volume?: number
  autoplay?: boolean
}

export function useAudioPlayback(options: PlaybackOptions = {}) {
  const baseUrl = options.baseUrl || 'http://localhost:5002'
  const defaultVolume = options.volume || 0.8
  
  // Reactive state
  const state = ref<AudioPlaybackState>({
    isPlaying: false,
    isLoading: false,
    currentTime: 0,
    duration: 0,
    volume: defaultVolume,
    error: null
  })
  
  // Internal state
  let currentAudio: HTMLAudioElement | null = null
  let animationFrame: number | null = null
  const loadingPromises = new Map<string, Promise<HTMLAudioElement>>()
  
  // Event callbacks
  const playbackCallbacks = new Set<(isPlaying: boolean) => void>()
  const timeUpdateCallbacks = new Set<(currentTime: number, duration: number) => void>()
  const visemaCallbacks = new Set<(visema: string) => void>()
  const errorCallbacks = new Set<(error: string) => void>()
  
  // Computed
  const progress = computed(() => {
    if (state.value.duration === 0) return 0
    return state.value.currentTime / state.value.duration
  })
  
  const progressPercentage = computed(() => Math.round(progress.value * 100))
  
  const canPlay = computed(() => !state.value.isLoading && !state.value.error)
  
  /**
   * Load audio file
   */
  const loadAudio = async (audioUrl: string): Promise<HTMLAudioElement> => {
    // Check if already loading
    if (loadingPromises.has(audioUrl)) {
      return loadingPromises.get(audioUrl)!
    }
    
    const fullUrl = audioUrl.startsWith('http') ? audioUrl : `${baseUrl}${audioUrl}`
    
    const loadPromise = new Promise<HTMLAudioElement>((resolve, reject) => {
      const audio = new Audio()
      
      audio.onloadeddata = () => {
        console.log(`Audio loaded: ${audioUrl}`)
        resolve(audio)
      }
      
      audio.onerror = () => {
        const error = `Failed to load audio: ${audioUrl}`
        console.error(error)
        reject(new Error(error))
      }
      
      audio.onloadstart = () => {
        console.log(`Loading audio: ${audioUrl}`)
      }
      
      // Set properties
      audio.volume = state.value.volume
      audio.preload = 'auto'
      
      // Load the audio
      audio.src = fullUrl
      audio.load()
    })
    
    loadingPromises.set(audioUrl, loadPromise)
    
    try {
      const audio = await loadPromise
      loadingPromises.delete(audioUrl)
      return audio
    } catch (error) {
      loadingPromises.delete(audioUrl)
      throw error
    }
  }
  
  /**
   * Play audio with optional visemas
   */
  const playAudio = async (audioUrl: string, visemas: Visema[] = []): Promise<void> => {
    try {
      state.value.isLoading = true
      state.value.error = null
      
      // Stop current audio if playing
      stop()
      
      // Load new audio
      const audio = await loadAudio(audioUrl)
      currentAudio = audio
      
      // Setup audio event handlers
      setupAudioHandlers(audio)
      
      // Setup visemas synchronization
      if (visemas.length > 0) {
        setupVisemaSync(visemas)
      }
      
      // Play audio
      await audio.play()
      
      state.value.isLoading = false
      state.value.isPlaying = true
      state.value.duration = audio.duration
      
      // Start time updates
      startTimeUpdates()
      
      // Notify callbacks
      playbackCallbacks.forEach(callback => callback(true))
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Audio playback failed'
      handleError(errorMessage)
    }
  }
  
  /**
   * Stop audio playback
   */
  const stop = (): void => {
    if (currentAudio) {
      currentAudio.pause()
      currentAudio.currentTime = 0
      cleanupAudio()
    }
    
    stopTimeUpdates()
    
    state.value.isPlaying = false
    state.value.currentTime = 0
    
    playbackCallbacks.forEach(callback => callback(false))
  }
  
  /**
   * Pause audio playback
   */
  const pause = (): void => {
    if (currentAudio && state.value.isPlaying) {
      currentAudio.pause()
      state.value.isPlaying = false
      stopTimeUpdates()
      
      playbackCallbacks.forEach(callback => callback(false))
    }
  }
  
  /**
   * Resume audio playback
   */
  const resume = async (): Promise<void> => {
    if (currentAudio && !state.value.isPlaying) {
      try {
        await currentAudio.play()
        state.value.isPlaying = true
        startTimeUpdates()
        
        playbackCallbacks.forEach(callback => callback(true))
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to resume audio'
        handleError(errorMessage)
      }
    }
  }
  
  /**
   * Set volume
   */
  const setVolume = (volume: number): void => {
    const clampedVolume = Math.max(0, Math.min(1, volume))
    state.value.volume = clampedVolume
    
    if (currentAudio) {
      currentAudio.volume = clampedVolume
    }
  }
  
  /**
   * Seek to time
   */
  const seekTo = (time: number): void => {
    if (currentAudio) {
      currentAudio.currentTime = Math.max(0, Math.min(state.value.duration, time))
      state.value.currentTime = currentAudio.currentTime
    }
  }
  
  /**
   * Setup audio event handlers
   */
  const setupAudioHandlers = (audio: HTMLAudioElement): void => {
    audio.onended = () => {
      console.log('Audio playback ended')
      state.value.isPlaying = false
      state.value.currentTime = 0
      stopTimeUpdates()
      
      playbackCallbacks.forEach(callback => callback(false))
    }
    
    audio.onerror = () => {
      handleError('Audio playback error occurred')
    }
    
    audio.onpause = () => {
      if (state.value.isPlaying) {
        state.value.isPlaying = false
        stopTimeUpdates()
        playbackCallbacks.forEach(callback => callback(false))
      }
    }
  }
  
  /**
   * Setup visema synchronization
   */
  const setupVisemaSync = (visemas: Visema[]): void => {
    console.log(`Setting up visema sync with ${visemas.length} visemas`)
    
    // Sort visemas by time
    const sortedVisemas = [...visemas].sort((a, b) => a.tiempo - b.tiempo)
    let currentVisemaIndex = 0
    
    const checkVisemas = () => {
      const currentTime = state.value.currentTime
      
      // Check if we need to trigger next visema
      while (currentVisemaIndex < sortedVisemas.length) {
        const visema = sortedVisemas[currentVisemaIndex]
        
        if (currentTime >= visema.tiempo) {
          console.log(`Triggering visema: ${visema.visema} at ${currentTime}s`)
          visemaCallbacks.forEach(callback => callback(visema.visema))
          currentVisemaIndex++
        } else {
          break
        }
      }
      
      // Continue checking if still playing
      if (state.value.isPlaying && currentVisemaIndex < sortedVisemas.length) {
        requestAnimationFrame(checkVisemas)
      }
    }
    
    // Start visema checking
    requestAnimationFrame(checkVisemas)
  }
  
  /**
   * Start time updates
   */
  const startTimeUpdates = (): void => {
    stopTimeUpdates()
    
    const updateTime = () => {
      if (currentAudio && state.value.isPlaying) {
        state.value.currentTime = currentAudio.currentTime
        state.value.duration = currentAudio.duration || 0
        
        timeUpdateCallbacks.forEach(callback => 
          callback(state.value.currentTime, state.value.duration)
        )
        
        animationFrame = requestAnimationFrame(updateTime)
      }
    }
    
    updateTime()
  }
  
  /**
   * Stop time updates
   */
  const stopTimeUpdates = (): void => {
    if (animationFrame) {
      cancelAnimationFrame(animationFrame)
      animationFrame = null
    }
  }
  
  /**
   * Handle errors
   */
  const handleError = (error: string): void => {
    console.error('Audio playback error:', error)
    state.value.error = error
    state.value.isLoading = false
    state.value.isPlaying = false
    
    stopTimeUpdates()
    errorCallbacks.forEach(callback => callback(error))
  }
  
  /**
   * Cleanup audio resources
   */
  const cleanupAudio = (): void => {
    if (currentAudio) {
      currentAudio.onended = null
      currentAudio.onerror = null
      currentAudio.onpause = null
      currentAudio = null
    }
  }
  
  /**
   * Subscribe to playback state changes
   */
  const onPlaybackChange = (callback: (isPlaying: boolean) => void): (() => void) => {
    playbackCallbacks.add(callback)
    return () => playbackCallbacks.delete(callback)
  }
  
  /**
   * Subscribe to time updates
   */
  const onTimeUpdate = (callback: (currentTime: number, duration: number) => void): (() => void) => {
    timeUpdateCallbacks.add(callback)
    return () => timeUpdateCallbacks.delete(callback)
  }
  
  /**
   * Subscribe to visema triggers
   */
  const onVisema = (callback: (visema: string) => void): (() => void) => {
    visemaCallbacks.add(callback)
    return () => visemaCallbacks.delete(callback)
  }
  
  /**
   * Subscribe to errors
   */
  const onError = (callback: (error: string) => void): (() => void) => {
    errorCallbacks.add(callback)
    return () => errorCallbacks.delete(callback)
  }
  
  /**
   * Cleanup resources
   */
  const cleanup = (): void => {
    stop()
    cleanupAudio()
    loadingPromises.clear()
    
    playbackCallbacks.clear()
    timeUpdateCallbacks.clear()
    visemaCallbacks.clear()
    errorCallbacks.clear()
  }
  
  // Cleanup on component unmount
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    // State
    state: readonly(state),
    progress: readonly(progress),
    progressPercentage: readonly(progressPercentage),
    canPlay: readonly(canPlay),
    
    // Methods
    loadAudio,
    playAudio,
    stop,
    pause,
    resume,
    setVolume,
    seekTo,
    
    // Event subscriptions
    onPlaybackChange,
    onTimeUpdate,
    onVisema,
    onError
  }
}