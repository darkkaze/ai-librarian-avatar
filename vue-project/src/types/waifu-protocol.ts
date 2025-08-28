/**
 * TypeScript types for Waifu Avatar System WebSocket Protocol
 * Based on backend_frontend_integration.md
 */

// ============= Client Messages =============

export interface ClientMessage {
  message: string
  id: string
}

export type ClientHeartbeat = 'alive'

export type ClientRequest = ClientMessage | ClientHeartbeat

// ============= Server Responses =============

export interface Visema {
  tiempo: number
  visema: string
}

export interface Expression {
  expresion: string
  tiempo: number
  intensidad: number
}

export interface AnimationKeyframe {
  vrma: string
  duration: number
  crossfade: number
}

export interface AnimationSequence {
  sequence: string
  description?: string
  keyframes?: AnimationKeyframe[]  // Para formato de múltiples keyframes
  vrma_file?: string  // Para formato de un solo archivo VRMA
  breathing: boolean
  delay: number
  temporary?: boolean  // Si es true, regresa a idle después de ejecutarse una vez
}

// ============= WebSocket Response Types =============

/**
 * Fast Output Response (no message_id)
 * Execute immediately (ASAP)
 */
export interface FastOutputResponse {
  audio_url?: string
  visemas?: Visema[]
  text?: string
}

/**
 * Complete Response - Audio + Visemas (with message_id)
 * Wait for other 2 JSONs before processing
 */
export interface AudioVisemaResponse {
  audio_url: string
  visemas: Visema[]
  message_id: string
}

/**
 * Complete Response - Expressions (with message_id)
 * Wait for other 2 JSONs before processing  
 */
export interface ExpressionsResponse {
  expresiones: Expression[]
  message_id: string
}

/**
 * Complete Response - Animations (with message_id)
 * Wait for other 2 JSONs before processing
 */
export interface AnimationsResponse extends AnimationSequence {
  message_id: string
}

/**
 * Server Error Response
 */
export interface ServerErrorResponse {
  error: string
  type: 'error'
}

/**
 * Server Heartbeat Response
 */
export type ServerHeartbeat = 'alive'

/**
 * All possible server responses
 */
export type ServerResponse = 
  | FastOutputResponse
  | AudioVisemaResponse  
  | ExpressionsResponse
  | AnimationsResponse
  | ServerErrorResponse
  | ServerHeartbeat

// ============= Response Coordination =============

/**
 * Complete response set for synchronized playback
 */
export interface CompleteResponse {
  messageId: string
  audio?: AudioVisemaResponse
  expressions?: ExpressionsResponse
  animations?: AnimationsResponse
}

/**
 * Response status for coordination
 */
export interface ResponseStatus {
  messageId: string
  hasAudio: boolean
  hasExpressions: boolean
  hasAnimations: boolean
  isComplete: boolean
  timestamp: number
}

// ============= Connection States =============

export enum ConnectionState {
  Disconnected = 'disconnected',
  Connecting = 'connecting', 
  Connected = 'connected',
  Reconnecting = 'reconnecting',
  Error = 'error'
}

export enum VoiceState {
  Idle = 'idle',
  Listening = 'listening',
  Processing = 'processing',
  Sending = 'sending'
}

export enum AvatarState {
  Loading = 'loading',
  Ready = 'ready',
  Speaking = 'speaking',
  Error = 'error'
}

// ============= Utility Types =============

/**
 * Type guard for Fast Output Response
 */
export function isFastOutputResponse(response: unknown): response is FastOutputResponse {
  return typeof response === 'object' && response !== null && !('message_id' in response) && 
    (('text' in response) || ('audio_url' in response) || ('visemas' in response))
}

/**
 * Type guard for Audio Visema Response
 */
export function isAudioVisemaResponse(response: unknown): response is AudioVisemaResponse {
  return typeof response === 'object' && response !== null && 'audio_url' in response && 'visemas' in response && 'message_id' in response
}

/**
 * Type guard for Expressions Response
 */
export function isExpressionsResponse(response: unknown): response is ExpressionsResponse {
  return typeof response === 'object' && response !== null && 'expresiones' in response && 'message_id' in response
}

/**
 * Type guard for Animations Response  
 */
export function isAnimationsResponse(response: unknown): response is AnimationsResponse {
  return typeof response === 'object' && response !== null && ('keyframes' in response || 'vrma_file' in response) && 'message_id' in response
}

/**
 * Type guard for Server Error Response
 */
export function isServerErrorResponse(response: unknown): response is ServerErrorResponse {
  return typeof response === 'object' && response !== null && 'error' in response && 'type' in response && (response as any).type === 'error'
}

/**
 * Type guard for Server Heartbeat
 */
export function isServerHeartbeat(response: unknown): response is ServerHeartbeat {
  return response === 'alive'
}

// ============= Configuration =============

export interface WaifuConfig {
  websocketUrl: string
  animationServiceUrl: string
  heartbeatInterval: number
  voiceTimeout: number
  reconnectDelay: number
  maxReconnectAttempts: number
}

export const DEFAULT_CONFIG: WaifuConfig = {
  websocketUrl: 'ws://localhost:8765',
  animationServiceUrl: 'http://localhost:5003',
  heartbeatInterval: 45000, // 45 seconds
  voiceTimeout: 3000, // 3 seconds of silence
  reconnectDelay: 2000, // 2 seconds
  maxReconnectAttempts: 5
}