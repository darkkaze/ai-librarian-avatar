/**
 * Avatar Renderer composable for Waifu Avatar System
 * Enhanced VRM/VRMA rendering with expressions, animations, and breathing
 */

import { ref, onUnmounted, readonly, type Ref } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { VRM, VRMLoaderPlugin } from '@pixiv/three-vrm'
import { VRMAnimationLoaderPlugin, createVRMAnimationClip } from '@pixiv/three-vrm-animation'
import type { AnimationSequence, AnimationKeyframe, Expression, Visema } from '@/types/waifu-protocol'
import { AvatarState } from '@/types/waifu-protocol'

interface AvatarConfig {
  modelUrl: string
  animationServiceUrl: string
  backgroundGradient?: [string, string]
  baseAnimation?: string  // Default animation to return to, if not specified will use the first available
}

interface BreathingConfig {
  duration: number
  chestExpansion: number
  enabled: boolean
}

const DEFAULT_BREATHING: BreathingConfig = {
  duration: 4.5,
  chestExpansion: 0.04,
  enabled: false  // Disabled for now - breathing commented out
}

export function useAvatarRenderer(container: Ref<HTMLElement | undefined>, config: AvatarConfig) {
  // Reactive state
  const avatarState = ref<AvatarState>('loading' as AvatarState)
  const loadingProgress = ref(0)
  const errorMessage = ref<string | null>(null)
  const currentAnimation = ref<string | null>(null)

  // Three.js objects
  let scene: THREE.Scene | null = null
  let camera: THREE.PerspectiveCamera | null = null
  let renderer: THREE.WebGLRenderer | null = null
  let vrm: VRM | null = null
  let mixer: THREE.AnimationMixer | null = null
  let animationId: number | null = null

  // Animation management
  let currentAction: THREE.AnimationAction | null = null
  const loadedAnimations = new Map<string, THREE.AnimationClip>()
  const loadedSequences = new Map<string, AnimationSequence>()
  
  // Clean idle system
  let idleTimer: number | null = null
  let currentAnimationState: 'idle' | 'specific' = 'idle'
  const availableIdles = ['idle', 'idle2']

  // Expression management
  let expressionQueue: Expression[] = []
  let currentExpressionIndex = 0
  let expressionStartTime = 0
  const currentExpressionValues: Record<string, number> = {}  // Track current expression values for interpolation
  const targetExpressionValues: Record<string, number> = {}   // Track target expression values for interpolation

  // Visema management for lip-sync
  const visemaQueue: Visema[] = []
  let currentVisemaIndex = 0
  const visemaStartTime = 0

  // Breathing configuration
  let breathingConfig: BreathingConfig = { ...DEFAULT_BREATHING }

  // Timing
  const clock = new THREE.Clock()


  /**
   * Initialize the avatar renderer
   */
  const initialize = async (): Promise<void> => {
    try {
      avatarState.value = AvatarState.Loading
      loadingProgress.value = 0
      errorMessage.value = null

      await initializeThreeJS()
      loadingProgress.value = 30

      await loadAvatarModel()
      loadingProgress.value = 70

      await loadIdleAnimation()
      loadingProgress.value = 100

      avatarState.value = AvatarState.Ready
      console.log('✅ Avatar renderer initialized successfully')

    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to initialize avatar'
      handleError(message)
    }
  }

  /**
   * Initialize Three.js scene
   */
  const initializeThreeJS = async (): Promise<void> => {
    if (!container.value) {
      throw new Error('Container element not available')
    }

    // Create scene
    scene = new THREE.Scene()

    // Set background
    if (config.backgroundGradient) {
      const [color1] = config.backgroundGradient
      scene.background = new THREE.Color(color1)
      // TODO: Implement gradient background
    } else {
      scene.background = new THREE.Color(0x212121)
    }

    // Create camera
    camera = new THREE.PerspectiveCamera(
      30,
      container.value.clientWidth / container.value.clientHeight,
      0.1,
      100
    )
    camera.position.set(0, 1.5, 2.5)
    camera.lookAt(0, 1.5, 0)

    // Create renderer
    renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: false
    })
    renderer.setSize(container.value.clientWidth, container.value.clientHeight)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFSoftShadowMap
    renderer.outputColorSpace = THREE.SRGBColorSpace

    container.value.appendChild(renderer.domElement)

    // Setup lighting
    setupLighting()

    // Setup resize handler
    window.addEventListener('resize', handleResize)

    // Start render loop
    startRenderLoop()
  }

  /**
   * Setup scene lighting
   */
  const setupLighting = (): void => {
    if (!scene) return

    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8)
    scene.add(ambientLight)

    // Main directional light
    const mainLight = new THREE.DirectionalLight(0xffffff, 1.2)
    mainLight.position.set(0.5, 1, 2)
    mainLight.castShadow = true
    mainLight.shadow.mapSize.setScalar(1024)
    scene.add(mainLight)

    // Fill light
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.4)
    fillLight.position.set(-0.5, 0.5, 1)
    scene.add(fillLight)

    // Rim light
    const rimLight = new THREE.DirectionalLight(0xffffff, 0.3)
    rimLight.position.set(0, 1, -1)
    scene.add(rimLight)
  }

  /**
   * Load avatar VRM model
   */
  const loadAvatarModel = async (): Promise<void> => {
    const loader = new GLTFLoader()
    loader.register((parser) => new VRMLoaderPlugin(parser))

    try {
      const gltf = await loader.loadAsync(config.modelUrl)
      vrm = gltf.userData.vrm

      if (!vrm) {
        throw new Error('VRM data not found in model file')
      }

      if (!scene) {
        throw new Error('Scene not initialized')
      }

      // Add to scene
      scene.add(vrm.scene)

      // Position and scale the model
      positionAvatar()

      // Create animation mixer
      mixer = new THREE.AnimationMixer(vrm.scene)

      // Log available expressions for debugging
      if (vrm.expressionManager) {
        const expressions = Object.keys(vrm.expressionManager.expressionMap)
        console.log('👄 Available VRM expressions:', expressions)
      } else {
        console.log('⚠️ No expression manager available')
      }

      console.log('✅ VRM model loaded and positioned')

    } catch (error) {
      throw new Error(`Failed to load VRM model: ${error}`)
    }
  }

  /**
   * Position and scale the avatar
   */
  const positionAvatar = (): void => {
    if (!vrm || !camera) return

    // Rotate to face camera
    vrm.scene.rotation.set(0, Math.PI, 0)

    // Calculate bounding box
    const box = new THREE.Box3().setFromObject(vrm.scene)
    const size = box.getSize(new THREE.Vector3())

    // Scale to fit nicely
    const maxDim = Math.max(size.x, size.y, size.z)
    const scale = 1.4 / maxDim
    vrm.scene.scale.setScalar(scale)

    // Position at ground level
    vrm.scene.position.set(0, -size.y * scale * 0.17, 0)

    // Adjust camera for head level
    const eyeHeight = size.y * scale * 0.68
    camera.position.set(0, eyeHeight, 1.7) //  - serca, + lejos
    camera.lookAt(0, eyeHeight * 0.95, 0)
  }

  /**
   * Load idle animation
   */
  const loadIdleAnimation = async (): Promise<void> => {
    // Load both idle animations
    await loadAnimation('idle')
    await loadAnimation('idle2')

    // Wait a small delay to ensure everything is initialized, then start clean idle system
    setTimeout(() => {
      startIdleSystem()
    }, 100)
  }

  /**
   * Start the idle system - clean and simple
   */
  const startIdleSystem = (): void => {
    console.log('🔄 Starting clean idle system')
    currentAnimationState = 'idle'
    playNextIdle()
  }

  /**
   * Play next random idle with natural timing
   */
  const playNextIdle = (): void => {
    if (currentAnimationState !== 'idle') {
      console.log('🚫 Not playing idle - specific animation is active')
      return
    }

    // Clear any existing timer
    if (idleTimer) {
      clearTimeout(idleTimer)
      idleTimer = null
    }

    // Select random idle
    const randomIdle = availableIdles[Math.floor(Math.random() * availableIdles.length)]
    console.log(`🎲 Playing idle: ${randomIdle}`)
    
    // Play the idle animation with natural duration-based transition
    playIdleWithNaturalRotation(randomIdle)
  }

  /**
   * Play idle with natural rotation after it finishes one cycle
   */
  const playIdleWithNaturalRotation = async (idleName: string): Promise<void> => {
    try {
      // Load animation if not loaded
      if (!loadedSequences.has(idleName)) {
        await loadAnimation(idleName)
      }

      const sequence = loadedSequences.get(idleName)
      if (!sequence?.vrma_file) {
        console.error(`❌ Idle animation ${idleName} not found`)
        return
      }

      const keyframeName = extractKeyframeName(sequence.vrma_file)
      const clip = loadedAnimations.get(keyframeName)
      if (!clip || !mixer) {
        console.error(`❌ Clip not found for ${keyframeName}`)
        return
      }

      const newAction = mixer.clipAction(clip)
      
      // Configure for continuous loop to avoid T-pose
      newAction.setLoop(THREE.LoopRepeat, Infinity)
      newAction.clampWhenFinished = false

      // Setup and play
      newAction.reset()
      newAction.setEffectiveWeight(1.0)
      newAction.setEffectiveTimeScale(1.0)

      // Crossfade from current action
      if (currentAction && currentAction !== newAction) {
        newAction.play()
        currentAction.crossFadeTo(newAction, 1.5, false)
      } else {
        newAction.play()
      }

      currentAction = newAction
      console.log(`✅ Playing idle naturally: ${idleName}`)

      // Schedule next idle after one complete cycle
      const animationDuration = clip.duration * 1000
      console.log(`⏱️ ${idleName} will loop for ${clip.duration.toFixed(1)}s then crossfade to next`)
      
      idleTimer = setTimeout(() => {
        if (currentAnimationState === 'idle') {
          playNextIdle() // Switch to next random idle
        }
      }, animationDuration)

    } catch (error) {
      console.error(`❌ Error playing idle ${idleName}:`, error)
    }
  }

  /**
   * Stop idle system
   */
  const stopIdleSystem = (): void => {
    if (idleTimer) {
      clearTimeout(idleTimer)
      idleTimer = null
    }
  }

  /**
   * Load animation from service
   */
  const loadAnimation = async (animationName: string): Promise<void> => {
    // TEMPORARILY FORCE RELOAD FOR TESTING - Remove cache check
    console.log(`Force reloading animation: ${animationName}`)
    // if (loadedSequences.has(animationName)) {
    //   console.log(`Animation sequence ${animationName} already loaded`)
    //   return
    // }

    try {
      // Get animation data from service
      const response = await fetch(`${config.animationServiceUrl}/sequence/${animationName}`)

      if (!response.ok) {
        throw new Error(`Failed to fetch animation: ${animationName}`)
      }

      const animationData: AnimationSequence = await response.json()

      console.log(`🔍 Animation data received for ${animationName}:`, JSON.stringify(animationData, null, 2))
      
      // 🔍 LOG ESPECIAL PARA IDLE
      if (animationName === 'idle') {
        console.group('🏠 IDLE Animation Deep Dive')
        console.log('📋 Complete idle config:', animationData)
        console.log('🎭 Has keyframes:', !!animationData.keyframes)
        console.log('📁 Has single file:', !!animationData.vrma_file)
        console.log('🔁 Is looping:', animationData.loop)
        console.log('⚡ Is temporary:', animationData.temporary)
        console.groupEnd()
      }

      // Handle keyframes format (multiple VRMA files)
      if (animationData.keyframes) {
        console.log(`Loading ${animationData.keyframes.length} keyframes for ${animationName}`)

        for (const keyframe of animationData.keyframes) {
          const vrmaUrl = keyframe.vrma
          const keyframeName = extractKeyframeName(vrmaUrl)

          if (!loadedAnimations.has(keyframeName)) {
            await loadVRMAFile(keyframeName, vrmaUrl)
          }
        }
      }
      // Handle single VRMA file format
      else if (animationData.vrma_file) {
        console.log(`Loading single VRMA file for ${animationName}: ${animationData.vrma_file}`)
        const keyframeName = extractKeyframeName(animationData.vrma_file)

        if (!loadedAnimations.has(keyframeName)) {
          await loadVRMAFile(keyframeName, animationData.vrma_file)
        }
      }
      else {
        throw new Error(`Animation ${animationName} has neither keyframes nor vrma_file`)
      }

      // Store the sequence data
      loadedSequences.set(animationName, animationData)

      console.log(`✅ Animation sequence loaded: ${animationName}`)

    } catch (error) {
      console.error(`Failed to load animation ${animationName}:`, error)
      throw error
    }
  }

  /**
   * Extract keyframe name from VRMA URL
   */
  const extractKeyframeName = (vrmaUrl: string): string => {
    const filename = vrmaUrl.split('/').pop() || vrmaUrl
    return filename.replace('.vrma', '')
  }

  /**
   * Load VRMA animation file
   */
  const loadVRMAFile = async (name: string, vrmaUrl: string): Promise<void> => {
    if (!vrm || !mixer) return

    const loader = new GLTFLoader()
    loader.register((parser) => new VRMAnimationLoaderPlugin(parser))

    try {
      const gltf = await loader.loadAsync(vrmaUrl)

      if (gltf.userData.vrmAnimations && gltf.userData.vrmAnimations.length > 0) {
        const vrmAnimation = gltf.userData.vrmAnimations[0]
        
        // 🔍 LOG DETALLADO DE LA ESTRUCTURA VRMA
        console.group(`📊 VRMA Structure Analysis: ${name}`)
        console.log('🎬 Raw VRMA Animation Object:', vrmAnimation)
        
        if (vrmAnimation.tracks) {
          console.log(`🎭 Total tracks: ${vrmAnimation.tracks.length}`)
          
          vrmAnimation.tracks.forEach((track, index) => {
            console.group(`📦 Track ${index}: ${track.name}`)
            console.log('⏱️ Times:', track.times)
            console.log('🎯 Values:', track.values) 
            console.log('🔧 Type:', track.constructor.name)
            console.log('📏 Duration:', track.times ? track.times[track.times.length - 1] : 'N/A')
            console.groupEnd()
          })
        }
        
        if (vrmAnimation.duration) {
          console.log(`⏱️ Total duration: ${vrmAnimation.duration}s`)
        }
        
        console.groupEnd()
        
        const clip = createVRMAnimationClip(vrmAnimation, vrm)

        if (clip) {
          // 🔍 LOG DETALLADO DEL CLIP GENERADO
          console.group(`🎬 Generated AnimationClip: ${name}`)
          console.log('🎭 Clip object:', clip)
          console.log(`⏱️ Duration: ${clip.duration}s`)
          console.log(`📦 Tracks: ${clip.tracks.length}`)
          
          clip.tracks.forEach((track, index) => {
            console.group(`🎯 Clip Track ${index}`)
            console.log('📛 Name:', track.name)
            console.log('🎨 Type:', track.constructor.name)
            console.log('⏰ Times length:', track.times?.length)
            console.log('📊 Values length:', track.values?.length)
            console.groupEnd()
          })
          
          console.groupEnd()
          
          loadedAnimations.set(name, clip)
          console.log(`✅ VRMA loaded: ${name}`)
        }
      }

    } catch (error) {
      console.error(`Failed to load VRMA file ${vrmaUrl}:`, error)
      throw error
    }
  }

  /**
   * Clean animation player - replaces the complex playAnimation
   */
  const playAnimationClean = async (animationName: string, isIdle: boolean = false, crossfadeDuration: number = 1.5): Promise<void> => {
    console.log(`🎭 Playing ${isIdle ? 'idle' : 'specific'} animation: ${animationName}`)

    if (!mixer) {
      console.log('❌ No mixer available')
      return
    }

    try {
      // Load animation if not loaded
      if (!loadedSequences.has(animationName)) {
        console.log(`🔄 Loading animation: ${animationName}`)
        await loadAnimation(animationName)
      }

      const sequence = loadedSequences.get(animationName)
      if (!sequence) {
        console.error(`❌ Animation ${animationName} not found`)
        return
      }

      // Handle specific animations (from webhook)
      if (!isIdle) {
        currentAnimationState = 'specific'
        stopIdleSystem() // Stop idle rotation
        console.log(`🎯 Playing specific animation: ${animationName}`)
      }

      // Play the animation
      await playAnimationSequence(sequence, animationName, isIdle, crossfadeDuration)

    } catch (error) {
      console.error(`❌ Error playing animation ${animationName}:`, error)
    }
  }

  /**
   * Play animation sequence with proper cleanup
   */
  const playAnimationSequence = async (sequence: AnimationSequence, animationName: string, isIdle: boolean, crossfadeDuration: number): Promise<void> => {
    // Handle single VRMA file format
    if (sequence.vrma_file) {
      await playSingleVRMA(sequence.vrma_file, animationName, isIdle, crossfadeDuration)
    }
    // Handle keyframes format (if needed)
    else if (sequence.keyframes && sequence.keyframes.length > 0) {
      console.log(`🎭 Keyframe sequences not implemented in clean system yet`)
    }
    else {
      console.error(`❌ Unknown animation format for ${animationName}`)
    }
  }

  /**
   * Play single VRMA file with proper state management
   */
  const playSingleVRMA = async (vrmaUrl: string, animationName: string, isIdle: boolean, crossfadeDuration: number): Promise<void> => {
    if (!mixer) return

    const keyframeName = extractKeyframeName(vrmaUrl)
    const clip = loadedAnimations.get(keyframeName)
    if (!clip) {
      console.error(`❌ Clip not found for ${keyframeName} from ${vrmaUrl}`)
      return
    }

    const newAction = mixer.clipAction(clip)
    
    // Configure animation based on type
    if (isIdle) {
      // Idle animations loop continuously
      newAction.setLoop(THREE.LoopRepeat, Infinity)
      newAction.clampWhenFinished = false
    } else {
      // Specific animations play once
      newAction.setLoop(THREE.LoopOnce, 1)
      newAction.clampWhenFinished = true
      
      // Set up return to idle when specific animation finishes
      const duration = clip.duration * 1000
      setTimeout(() => {
        console.log(`🔄 Specific animation ${animationName} finished, returning to idle`)
        currentAnimationState = 'idle'
        startIdleSystem()
      }, duration)
    }

    // Setup and play
    newAction.reset()
    newAction.setEffectiveWeight(1.0)
    newAction.setEffectiveTimeScale(1.0)

    // Crossfade from current action
    if (currentAction && currentAction !== newAction) {
      newAction.play()
      currentAction.crossFadeTo(newAction, crossfadeDuration, false)
    } else {
      newAction.play()
    }

    currentAction = newAction
    currentAnimation.value = animationName
    console.log(`✅ Playing ${isIdle ? 'idle' : 'specific'}: ${animationName}`)
  }

  /**
   * Main animation function - now uses clean system
   */
  const playAnimation = async (animationName: string, crossfadeDuration: number = 0.8): Promise<void> => {
    console.log(`🎭 Playing animation: ${animationName}`)
    
    // Determine if this is an idle or specific animation
    const isIdle = availableIdles.includes(animationName)
    
    // Use the clean system
    await playAnimationClean(animationName, isIdle, crossfadeDuration)
  }


  /**
   * Play expressions sequence
   */
  const playExpressions = (expressions: Expression[]): void => {
    if (!vrm?.expressionManager) {
      console.warn('Expression manager not available')
      return
    }

    expressionQueue = [...expressions].sort((a, b) => a.tiempo - b.tiempo)
    currentExpressionIndex = 0
    expressionStartTime = clock.getElapsedTime()

    // Initialize interpolation values for expressions
    // Get all unique expressions mentioned in the queue
    const allExpressions = [...new Set(expressions.map(e => e.expresion))]
    allExpressions.forEach(expressionName => {
      currentExpressionValues[expressionName] = 0
      targetExpressionValues[expressionName] = 0
    })

    console.log(`😊 Playing ${expressions.length} expressions with interpolation:`, expressions.map(e => `${e.expresion}@${e.tiempo}s (${e.intensidad})`))
  }

  /**
   * Play visemas sequence with smooth transitions (like AvatarDemo.vue)
   */
  const playVisemas = (visemas: Visema[]): void => {
    if (!vrm?.expressionManager) {
      console.warn('Expression manager not available for visemas')
      return
    }

    console.log(`👄 🎬 STARTING SMOOTH VISEMAS: ${visemas.length} visemas`)

    // Launch smooth visema animation asynchronously
    animateVisemasSmooth(visemas)
  }

  /**
   * Animate visemas with smooth transitions (async version like AvatarDemo.vue)
   */
  const animateVisemasSmooth = async (visemas: Visema[]): Promise<void> => {
    if (!vrm?.expressionManager) return

    const startTime = Date.now()
    console.log(`👄 ✨ Starting smooth visema animation with ${visemas.length} visemas`)

    for (const visemaData of visemas) {
      const targetTime = visemaData.tiempo * 1000
      const currentTime = Date.now() - startTime

      if (targetTime > currentTime) {
        await new Promise(resolve => setTimeout(resolve, targetTime - currentTime))
      }

      const visemaName = visemaData.visema
      if (vrm.expressionManager.expressionMap[visemaName]) {
        // Smooth transition like AvatarDemo.vue
        await smoothTransition(visemaName, 0.75, 150) // Fade in quickly

        // Auto fade out after brief hold
        setTimeout(async () => {
          if (vrm?.expressionManager) {
            await smoothTransition(visemaName, 0.0, 150) // Fade out
          }
        }, 200)

        console.log(`👄 ✨ SMOOTH Applied: ${visemaName} at ${visemaData.tiempo}s`)
      } else {
        console.warn(`👄 ⚠️ Visema NOT found in VRM: ${visemaName} at ${visemaData.tiempo}s`)
      }
    }

    console.log(`👄 🎬 SMOOTH VISEMAS COMPLETED`)
  }

  /**
   * Smooth transition function for expressions/visemas
   */
  const smoothTransition = async (expressionName: string, targetValue: number, durationMs: number): Promise<void> => {
    if (!vrm?.expressionManager) return

    const startValue = vrm.expressionManager.getValue(expressionName) || 0
    const startTime = Date.now()

    return new Promise<void>((resolve) => {
      const animate = () => {
        const elapsed = Date.now() - startTime
        const progress = Math.min(elapsed / durationMs, 1)

        // Ease out cubic for smoother transition
        const easeProgress = 1 - Math.pow(1 - progress, 3)
        const currentValue = startValue + (targetValue - startValue) * easeProgress

        if (vrm?.expressionManager) {
          vrm.expressionManager.setValue(expressionName, currentValue)
        }

        if (progress < 1) {
          requestAnimationFrame(animate)
        } else {
          resolve()
        }
      }

      requestAnimationFrame(animate)
    })
  }

  /**
   * Update expressions based on timeline with smooth interpolation (DISABLED)
   */
  const _updateExpressions = (): void => {
    if (!vrm?.expressionManager || expressionQueue.length === 0) return

    const currentTime = clock.getElapsedTime() - expressionStartTime

    // Process next expressions in queue to set targets
    while (currentExpressionIndex < expressionQueue.length) {
      const expression = expressionQueue[currentExpressionIndex]

      if (currentTime >= expression.tiempo) {
        // Check if expression exists in VRM
        const expressionExists = vrm.expressionManager.expressionMap.hasOwnProperty(expression.expresion)

        if (expressionExists) {
          // Set target value for interpolation
          targetExpressionValues[expression.expresion] = expression.intensidad
          console.log(`😊 ✅ Expression target set: ${expression.expresion} (${expression.intensidad}) at ${expression.tiempo}s`)
        } else {
          console.warn(`😊 ⚠️ Expression NOT found in VRM: ${expression.expresion} at ${expression.tiempo}s`)
        }
        currentExpressionIndex++
      } else {
        break
      }
    }

    // Apply smooth interpolation to all expression values
    if (vrm?.expressionManager) {
      const deltaTime = clock.getDelta()
      const interpolationSpeed = 6.0 // Slightly slower than visemes for more natural emotions

      // Get all expressions that have values (current or target)
      const allExpressionNames = new Set([
        ...Object.keys(currentExpressionValues),
        ...Object.keys(targetExpressionValues)
      ])

      allExpressionNames.forEach(expressionName => {
        // SKIP VISEMA EXPRESSIONS - Don't let expressions overwrite lip-sync
        const visemaExpressions = ['ou', 'ee', 'oh', 'neutral', 'aa', 'ih']
        if (visemaExpressions.includes(expressionName)) {
          console.log(`😊 SKIPPING visema expression: ${expressionName} (reserved for lip-sync)`)
          return
        }

        const currentValue = currentExpressionValues[expressionName] || 0
        const targetValue = targetExpressionValues[expressionName] || 0

        // Smooth interpolation using lerp
        const newValue = currentValue + (targetValue - currentValue) * interpolationSpeed * deltaTime

        // Update current value and apply to VRM
        currentExpressionValues[expressionName] = newValue

        // Only apply if expression exists in VRM and it's not a viseme
        if (vrm!.expressionManager!.expressionMap.hasOwnProperty(expressionName)) {
          vrm!.expressionManager!.setValue(expressionName, newValue)
        }
      })
    }
  }

  /**
   * Update visemas based on timeline for lip-sync with smooth interpolation (DISABLED)
   */
  const _updateVisemas = (): void => {
    if (!vrm?.expressionManager || visemaQueue.length === 0) return

    const currentTime = clock.getElapsedTime() - visemaStartTime

    // DEBUG: Log timing info every few seconds
    if (Math.floor(currentTime * 2) !== Math.floor((currentTime - clock.getDelta()) * 2)) {
      console.log(`👄 DEBUG: currentTime: ${currentTime.toFixed(2)}s, currentVisemaIndex: ${currentVisemaIndex}/${visemaQueue.length}`)
    }

    // Process next visemas in queue to set targets
    while (currentVisemaIndex < visemaQueue.length) {
      const visema = visemaQueue[currentVisemaIndex]

      if (currentTime >= visema.tiempo) {
        const visemaExists = vrm.expressionManager.expressionMap.hasOwnProperty(visema.visema)

        if (visemaExists) {
          // DIRECT APPLICATION - NO INTERPOLATION
          const availableVisemas = ['ou', 'ee', 'oh', 'neutral']

          // Reset all visemas to 0 directly
          availableVisemas.forEach(v => {
            vrm!.expressionManager!.setValue(v, 0)
          })

          // Apply current visema directly
          const intensity = 0.7  // Full intensity for clear lip movements
          vrm!.expressionManager!.setValue(visema.visema, intensity)

          console.log(`👄 🎯 DIRECT Applied: ${visema.visema} at ${visema.tiempo}s (intensity: ${intensity})`)
        } else {
          console.warn(`👄 ⚠️ Visema NOT found in VRM: ${visema.visema} at ${visema.tiempo}s`)
        }
        currentVisemaIndex++
      } else {
        break
      }
    }

    // INTERPOLATION DISABLED - USING DIRECT APPLICATION ONLY
  }

  /**
   * Apply breathing animation
   */
  const updateBreathing = (): void => {
    if (!vrm?.humanoid || !breathingConfig.enabled) return

    const time = clock.getElapsedTime()
    const { duration, chestExpansion } = breathingConfig

    // Calculate breathing cycle
    const breathingPhase = (Math.sin(time * (Math.PI * 2) / duration) + 1) / 2
    const breathingIntensity = Math.sin(breathingPhase * Math.PI)

    // Apply to chest bone
    const chestBone = vrm.humanoid.humanBones.chest?.node
    if (chestBone) {
      const baseRotation = chestBone.userData.baseRotation || chestBone.rotation.x
      if (!chestBone.userData.baseRotation) {
        chestBone.userData.baseRotation = chestBone.rotation.x
      }

      chestBone.rotation.x = baseRotation + (breathingIntensity * chestExpansion * 0.3)
    }
  }

  /**
   * Start render loop
   */
  const startRenderLoop = (): void => {
    const animate = () => {
      animationId = requestAnimationFrame(animate)

      const deltaTime = clock.getDelta()

      if (vrm) {
        vrm.update(deltaTime)

        // Update animation mixer
        if (mixer) {
          mixer.update(deltaTime)
        }

        // VISEMAS NOW USE SMOOTH TRANSITIONS - No longer updated in render loop
        // updateVisemas() // DISABLED - using smooth transitions instead

        // EXPRESSIONS TEMPORARILY DISABLED FOR TESTING
        // updateExpressions()

        // Update breathing - COMMENTED OUT FOR NOW
        // updateBreathing()
      }

      if (renderer && scene && camera) {
        renderer.render(scene, camera)
      }
    }

    animate()
  }

  /**
   * Handle window resize
   */
  const handleResize = (): void => {
    if (!container.value || !camera || !renderer) return

    const width = container.value.clientWidth
    const height = container.value.clientHeight

    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize(width, height)
  }

  /**
   * Set breathing configuration
   */
  const setBreathingConfig = (config: Partial<BreathingConfig>): void => {
    breathingConfig = { ...breathingConfig, ...config }
    console.log('🫁 Breathing config updated:', breathingConfig)
  }

  /**
   * Handle errors
   */
  const handleError = (message: string): void => {
    console.error('Avatar renderer error:', message)
    errorMessage.value = message
    avatarState.value = AvatarState.Error
  }

  /**
   * Cleanup resources
   */
  const cleanup = (): void => {
    // Stop idle system
    stopIdleSystem()
    
    // Stop render loop
    if (animationId) {
      cancelAnimationFrame(animationId)
      animationId = null
    }

    // Remove resize listener
    window.removeEventListener('resize', handleResize)

    // Cleanup Three.js objects
    if (renderer && container.value?.contains(renderer.domElement)) {
      container.value.removeChild(renderer.domElement)
    }

    // Dispose of resources
    if (mixer) {
      mixer.stopAllAction()
      mixer = null
    }

    if (vrm) {
      // VRM doesn't have dispose method, just clear the reference
      vrm = null
    }

    if (renderer) {
      renderer.dispose()
      renderer = null
    }

    if (scene) {
      scene.clear()
      scene = null
    }

    loadedAnimations.clear()
    expressionQueue = []
  }

  // Cleanup on component unmount
  onUnmounted(() => {
    cleanup()
  })

  return {
    // State
    avatarState: readonly(avatarState),
    loadingProgress: readonly(loadingProgress),
    errorMessage: readonly(errorMessage),
    currentAnimation: readonly(currentAnimation),

    // Methods
    initialize,
    playAnimation,
    playExpressions,
    playVisemas,
    setBreathingConfig,

    // Utils
    cleanup
  }
}
