<template>
  <div class="waifu-home">
    <!-- Avatar Renderer Container -->
    <div
      ref="avatarContainer"
      class="avatar-container"
      :class="{ 'avatar-speaking': isSpeaking }"
    >
      <!-- Loading Overlay -->
      <v-overlay
        v-model="showLoadingOverlay"
        contained
        class="loading-overlay"
      >
        <div class="loading-content">
          <v-progress-circular
            :model-value="loadingProgress"
            size="80"
            width="6"
            color="primary"
          />
          <div class="loading-text mt-4">
            {{ loadingMessage }}
          </div>
          <div class="loading-progress mt-2">
            {{ loadingProgress }}%
          </div>
        </div>
      </v-overlay>

      <!-- Error Overlay -->
      <v-overlay
        v-model="showErrorOverlay"
        contained
        class="error-overlay"
      >
        <div class="error-content">
          <v-icon size="64" color="error" class="mb-4">
            mdi-alert-circle-outline
          </v-icon>
          <div class="error-title mb-2">Error de Conexión</div>
          <div class="error-message mb-4">{{ errorMessage }}</div>
          <v-btn
            color="primary"
            variant="elevated"
            @click="handleRetry"
            :loading="isRetrying"
          >
            Reintentar
          </v-btn>
        </div>
      </v-overlay>
    </div>

    <!-- Control Panel -->
    <div class="control-panel">
      <!-- Connection Status -->
      <div class="connection-status mb-4">
        <v-chip
          :color="connectionStatusColor"
          :prepend-icon="connectionStatusIcon"
          size="large"
        >
          {{ connectionStatusText }}
        </v-chip>
      </div>

      <!-- Voice Controls -->
      <div class="voice-controls mb-4">
        <v-card class="pa-4" elevation="2">
          <v-card-title class="text-h6 mb-2">
            <v-icon class="me-2">mdi-microphone</v-icon>
            Control de Voz
          </v-card-title>

          <!-- Voice Status -->
          <div class="voice-status mb-3">
            <v-chip
              :color="voiceStatusColor"
              :prepend-icon="voiceStatusIcon"
              size="small"
            >
              {{ voiceStatusText }}
            </v-chip>
          </div>

          <!-- Transcript Display -->
          <v-textarea
            v-model="displayTranscript"
            label="Transcripción"
            rows="3"
            readonly
            variant="outlined"
            class="transcript-display mb-3"
            :class="{ 'transcript-active': isListening }"
          />

          <!-- Voice Toggle Button -->
          <v-btn
            :color="buttonColor"
            :disabled="buttonDisabled"
            size="large"
            block
            variant="elevated"
            @click="handleVoiceAction"
          >
            <v-icon class="me-2">
              {{ buttonIcon }}
            </v-icon>
            {{ buttonText }}
          </v-btn>
        </v-card>
      </div>

      <!-- Audio Controls -->
      <div class="audio-controls mb-4" v-if="showAudioControls">
        <v-card class="pa-4" elevation="2">
          <v-card-title class="text-h6 mb-2">
            <v-icon class="me-2">mdi-volume-high</v-icon>
            Audio
          </v-card-title>

          <!-- Playback Progress -->
          <div class="audio-progress mb-3">
            <v-slider
              :model-value="audioProgress"
              :disabled="!audioState.isPlaying"
              color="primary"
              track-color="grey-lighten-3"
              thumb-label
              hide-details
            />
            <div class="audio-time d-flex justify-space-between text-caption">
              <span>{{ formatTime(audioState.currentTime) }}</span>
              <span>{{ formatTime(audioState.duration) }}</span>
            </div>
          </div>

          <!-- Volume Control -->
          <div class="volume-control">
            <v-slider
              :model-value="audioVolume"
              @update:model-value="setAudioVolume"
              prepend-icon="mdi-volume-low"
              append-icon="mdi-volume-high"
              min="0"
              max="100"
              step="1"
              color="primary"
              hide-details
            />
          </div>
        </v-card>
      </div>

      <!-- Debug Panel -->
      <div class="debug-panel" v-if="showDebugInfo">
        <v-card class="pa-4" elevation="2">
          <v-card-title class="text-h6 mb-2">
            <v-icon class="me-2">mdi-bug</v-icon>
            Debug Info
          </v-card-title>

          <div class="debug-stats">
            <div class="debug-stat">
              <strong>Fast Outputs:</strong> {{ responseStats.totalFastOutputs }}
            </div>
            <div class="debug-stat">
              <strong>Complete Responses:</strong> {{ responseStats.totalCompleteResponses }}
            </div>
            <div class="debug-stat">
              <strong>Avg Response Time:</strong> {{ Math.round(responseStats.averageCompletionTime) }}ms
            </div>
            <div class="debug-stat">
              <strong>Current Animation:</strong> {{ currentAnimation || 'None' }}
            </div>
            <div class="debug-stat">
              <strong>Pending Responses:</strong> {{ pendingResponseIds.join(', ') || 'None' }}
            </div>
          </div>

          <v-btn
            size="small"
            variant="outlined"
            @click="clearDebugStats"
            class="mt-2"
          >
            Clear Stats
          </v-btn>
        </v-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useWebSocket } from '@/composables/useWebSocket'
import { useVoiceCapture } from '@/composables/useVoiceCapture'
import { useAvatarRenderer } from '@/composables/useAvatarRenderer'
import { useAudioPlayback } from '@/composables/useAudioPlayback'
import { useResponseCoordinator } from '@/composables/useResponseCoordinator'

// Template refs
const avatarContainer = ref<HTMLElement>()

// Server error state
const serverError = ref<string | null>(null)
const showServerError = ref(false)

// Configuration
const config = {
  websocketUrl: 'ws://localhost:8765',
  animationServiceUrl: 'http://localhost:5003',
  modelUrl: 'http://localhost:5003/models/avatar.vrm',
  audioBaseUrl: 'http://localhost:5002',
  backgroundGradient: ['#1a1a1a', '#2d2d2d'] as [string, string]
}

// Composables
const websocket = useWebSocket({
  websocketUrl: config.websocketUrl,
  heartbeatInterval: 45000,
  reconnectDelay: 2000,
  maxReconnectAttempts: 5
})

const voiceCapture = useVoiceCapture({
  voiceTimeout: 3000
})

const avatarRenderer = useAvatarRenderer(avatarContainer, {
  modelUrl: config.modelUrl,
  animationServiceUrl: config.animationServiceUrl,
  backgroundGradient: config.backgroundGradient
})

const audioPlayback = useAudioPlayback({
  baseUrl: config.audioBaseUrl,
  volume: 0.8
})

const responseCoordinator = useResponseCoordinator()

// Local state
const isRetrying = ref(false)
const showDebugInfo = ref(true)
const audioVolume = ref(80)

// Computed properties
const showLoadingOverlay = computed(() =>
  avatarRenderer.avatarState.value === 'loading'
)

const showErrorOverlay = computed(() =>
  websocket.connectionState.value === 'error' ||
  avatarRenderer.avatarState.value === 'error' ||
  showServerError.value
)

const showAudioControls = computed(() =>
  audioPlayback.state.value.isPlaying || audioPlayback.state.value.duration > 0
)

const loadingProgress = computed(() => avatarRenderer.loadingProgress.value)

const loadingMessage = computed(() => {
  if (avatarRenderer.avatarState.value === 'loading') {
    if (loadingProgress.value < 30) return 'Inicializando escena 3D...'
    if (loadingProgress.value < 70) return 'Cargando modelo de avatar...'
    return 'Configurando animaciones...'
  }
  return 'Cargando...'
})

const errorMessage = computed(() =>
  serverError.value ||
  websocket.lastError.value ||
  avatarRenderer.errorMessage.value ||
  'Error desconocido'
)

// Connection status
const connectionStatusColor = computed(() => {
  switch (websocket.connectionState.value) {
    case 'connected': return 'success'
    case 'connecting':
    case 'reconnecting': return 'warning'
    case 'error': return 'error'
    default: return 'default'
  }
})

const connectionStatusIcon = computed(() => {
  switch (websocket.connectionState.value) {
    case 'connected': return 'mdi-wifi'
    case 'connecting': return 'mdi-wifi-sync'
    case 'reconnecting': return 'mdi-wifi-sync'
    case 'error': return 'mdi-wifi-off'
    default: return 'mdi-wifi-off'
  }
})

const connectionStatusText = computed(() => {
  switch (websocket.connectionState.value) {
    case 'connected': return 'Conectado'
    case 'connecting': return 'Conectando...'
    case 'reconnecting': return 'Reconectando...'
    case 'error': return 'Error de Conexión'
    default: return 'Desconectado'
  }
})

// Voice status
const voiceStatusColor = computed(() => {
  switch (voiceCapture.voiceState.value) {
    case 'listening': return 'primary'
    case 'processing': return 'accent'
    case 'sending': return 'success'
    default: return 'default'
  }
})

const voiceStatusIcon = computed(() => {
  switch (voiceCapture.voiceState.value) {
    case 'listening': return 'mdi-microphone'
    case 'processing': return 'mdi-sync'
    case 'sending': return 'mdi-send'
    default: return 'mdi-microphone-off'
  }
})

const voiceStatusText = computed(() => {
  switch (voiceCapture.voiceState.value) {
    case 'listening': return 'Escuchando...'
    case 'processing': return 'Procesando...'
    case 'sending': return 'Enviando...'
    default: return 'Inactivo'
  }
})

// Voice controls
const displayTranscript = computed(() => voiceCapture.displayText.value)
const isListening = computed(() => voiceCapture.isListening.value)
const canUseVoice = computed(() =>
  voiceCapture.canStart.value && websocket.connectionState.value === 'connected'
)

// Enhanced voice control logic
const buttonColor = computed(() => {
  if (isSpeaking.value) return 'warning'  // Avatar speaking - interrupt button
  if (isListening.value) return 'error'   // Listening - stop button
  return 'primary'                        // Ready to listen
})

const buttonDisabled = computed(() => {
  if (isSpeaking.value) return false      // Can always interrupt avatar
  if (isListening.value) return false     // Can always stop listening
  return !canUseVoice.value               // Check connection when starting
})

const buttonIcon = computed(() => {
  if (isSpeaking.value) return 'mdi-stop'           // Stop/interrupt icon
  if (isListening.value) return 'mdi-microphone-off' // Stop listening icon
  return 'mdi-microphone'                           // Start listening icon
})

const buttonText = computed(() => {
  if (isSpeaking.value) return 'INTERRUMPIR'        // Interrupt avatar
  if (isListening.value) return 'DETENER'           // Stop listening
  return 'HABLAR'                                   // Start listening
})

// Audio controls
const audioState = computed(() => audioPlayback.state.value)
const audioProgress = computed(() => audioPlayback.progressPercentage.value)
const isSpeaking = computed(() => audioState.value.isPlaying)

// Debug info
const responseStats = computed(() => responseCoordinator.stats)
const pendingResponseIds = computed(() => responseCoordinator.getPendingMessageIds())
const currentAnimation = computed(() => avatarRenderer.currentAnimation.value)

/**
 * Initialize the application
 */
const initializeApp = async (): Promise<void> => {
  try {
    console.log('🚀 Initializing Waifu application...')

    // Initialize avatar renderer first
    await avatarRenderer.initialize()

    // Initialize voice capture
    voiceCapture.initialize()

    // Connect to WebSocket
    await websocket.connect()

    console.log('✅ Application initialized successfully')

  } catch (error) {
    console.error('❌ Failed to initialize application:', error)
  }
}

/**
 * Setup event handlers
 */
const setupEventHandlers = (): void => {
  // WebSocket response handler
  websocket.onResponse((response) => {
    responseCoordinator.processResponse(response)
  })

  // Voice message handler
  voiceCapture.onMessage((message) => {
    const messageId = websocket.generateMessageId()
    websocket.sendMessage(message, messageId)
  })

  // Fast output handler
  responseCoordinator.onFastOutput((response) => {
    console.log('🚀 Playing fast output:', response.text || '[no text]')
    console.log('🚀 Fast output has audio_url?', !!response.audio_url)
    console.log('🚀 Fast output has visemas?', !!response.visemas)
    console.log('🚀 Fast output full object:', JSON.stringify(response, null, 2))

    if (response.audio_url && response.visemas) {
      console.log('🎵 Attempting to play audio:', response.audio_url)
      audioPlayback.playAudio(response.audio_url, response.visemas)
      // Also send visemas directly to avatar for lip-sync
      avatarRenderer.playVisemas(response.visemas)
    } else if (response.visemas) {
      console.log('🎵 Playing visemas without audio')
      // Send visemas directly to avatar for lip-sync
      avatarRenderer.playVisemas(response.visemas)
    } else {
      console.log('⚠️ No audio/visemas in fast output, skipping playback')
    }
  })

  // Server error handler
  responseCoordinator.onServerError((response) => {
    console.error('🚨 Server error:', response.error)
    serverError.value = `Error del servidor: ${response.error}`
    showServerError.value = true
  })

  // Complete response handler
  responseCoordinator.onCompleteResponse((response) => {
    console.log('🎯 Playing complete response for:', response.messageId, response)

    // Play audio with visemas
    if (response.audio?.audio_url && response.audio?.visemas) {
      audioPlayback.playAudio(response.audio.audio_url, response.audio.visemas)
      // Also send visemas directly to avatar for lip-sync
      avatarRenderer.playVisemas(response.audio.visemas)
    }

    // Play expressions
    if (response.expressions?.expresiones) {
      avatarRenderer.playExpressions(response.expressions.expresiones)
    }

    // Play animations - TEMPORARILY COMMENTED FOR TESTING
    // if (response.animations) {
    //   avatarRenderer.playAnimation(response.animations.sequence, 0.8)

    //   // Update breathing config based on animation
    //   avatarRenderer.setBreathingConfig({
    //     enabled: response.animations.breathing
    //   })
    // }
    console.log('🎭 Animations disabled for testing, only visemas and expressions will play')
  })

  // Audio visema handler
  audioPlayback.onVisema((visema) => {
    // TODO: Apply visema to avatar lip sync
    console.log(`👄 Visema: ${visema}`)
  })
}

/**
 * Handle voice action based on current state
 */
const handleVoiceAction = async (): Promise<void> => {
  try {
    if (isSpeaking.value) {
      // Avatar is speaking - interrupt it
      await interruptAvatar()
    } else if (isListening.value) {
      // Currently listening - stop listening
      voiceCapture.stop()
    } else {
      // Ready to start listening
      await voiceCapture.start()
    }
  } catch (error) {
    console.error('Voice action error:', error)
  }
}

/**
 * Interrupt avatar speech
 */
const interruptAvatar = async (): Promise<void> => {
  try {
    console.log('🛑 Interrupting avatar speech...')
    
    // Stop audio playback
    audioPlayback.stop()
    
    // Stop any ongoing visemas/animations if possible
    // Note: This will depend on the specific implementation of the avatar renderer
    
    console.log('✅ Avatar speech interrupted')
  } catch (error) {
    console.error('Error interrupting avatar:', error)
  }
}

/**
 * Set audio volume
 */
const setAudioVolume = (volume: number): void => {
  audioVolume.value = volume
  audioPlayback.setVolume(volume / 100)
}

/**
 * Handle retry button
 */
const handleRetry = async (): Promise<void> => {
  isRetrying.value = true

  try {
    // Clear server error state
    serverError.value = null
    showServerError.value = false
    
    await initializeApp()
  } finally {
    isRetrying.value = false
  }
}

/**
 * Clear debug statistics
 */
const clearDebugStats = (): void => {
  responseCoordinator.reset()
}

/**
 * Format time for display
 */
const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Lifecycle
onMounted(async () => {
  await nextTick()
  setupEventHandlers()
  await initializeApp()
})

// Cleanup old responses periodically
setInterval(() => {
  responseCoordinator.clearOldResponses(30000)
}, 10000)
</script>

<style scoped>
.waifu-home {
  height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
}

.avatar-container {
  flex: 1;
  position: relative;
  min-height: 100vh;
  transition: filter 0.3s ease;
}

.avatar-speaking {
  filter: brightness(1.1) contrast(1.05);
}

.loading-overlay,
.error-overlay {
  background-color: rgba(0, 0, 0, 0.8) !important;
}

.loading-content,
.error-content {
  text-align: center;
  color: white;
}

.loading-text {
  font-size: 1.1rem;
  font-weight: 500;
}

.loading-progress {
  font-size: 0.9rem;
  opacity: 0.8;
}

.error-title {
  font-size: 1.2rem;
  font-weight: 600;
}

.error-message {
  opacity: 0.9;
}

.control-panel {
  width: 350px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 24px;
  overflow-y: auto;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
}

.connection-status {
  text-align: center;
}

.transcript-display {
  transition: all 0.3s ease;
}

.transcript-active {
  border-color: rgb(var(--v-theme-primary)) !important;
}

.audio-time {
  margin-top: 4px;
}

.debug-stats {
  font-size: 0.85rem;
}

.debug-stat {
  margin-bottom: 4px;
  padding: 2px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.debug-stat:last-child {
  border-bottom: none;
}

/* Responsive design */
@media (max-width: 768px) {
  .waifu-home {
    flex-direction: column;
  }

  .control-panel {
    width: 100%;
    height: 300px;
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .avatar-container {
    flex: 1;
    min-height: calc(100vh - 300px);
  }
}
</style>
