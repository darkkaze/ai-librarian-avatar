# VRM AVATAR BONE MANIPULATION RULES

## BONE HIERARCHY

```yaml
bones:
  - id: 17
    name: joint_HipMaster
    type: Bone
    pos: { x: 0.0, y: 1.03, z: 0.01 }
    rot: { x: 0.0, y: 0.0, z: 0.0 }
  - id: 18
    name: '!joint_HipMasterTip'
    type: Bone
    pos: { x: 0.0, y: -0.12, z: -0.0 }
    rot: { x: 0.0, y: 0.0, z: 0.0 }
  - id: 19
    name: joint_Torso
    type: Bone
    pos: { x: 0.0, y: 0.0, z: -0.0 }
    rot: { x: 0.0, y: 0.0, z: 0.0 }
    children:
      - id: 20
        name: joint_Torso1
        type: Bone
        pos: { x: 0.0, y: 0.11, z: -0.01 }
        rot: { x: 0.0, y: 0.0, z: 0.0 }
      - id: 21
        name: joint_Torso2
        type: Bone
        pos: { x: 0.0, y: 0.21, z: -0.0 }
        rot: { x: 0.0, y: 0.0, z: 0.0 }
        children:
          - id: 22
            name: joint_Neck
            type: Bone
            pos: { x: 0.0, y: 0.2, z: 0.05 }
            rot: { x: 0.0, y: 0.0, z: 0.0 }
            children:
              - id: 23
                name: joint_Head
                type: Bone
                pos: { x: 0.0, y: 0.09, z: -0.02 }
                rot: { x: 0.0, y: 0.0, z: 0.0 }
                children:
                  - id: 24
                    name: '!joint_HeadTip'
                    type: Bone
                    pos: { x: 0.0, y: 0.19, z: -0.03 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                  - id: 25
                    name: joint_RightEye
                    type: Bone
                    pos: { x: 0.02, y: 0.04, z: -0.02 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                  - id: 27
                    name: joint_LeftEye
                    type: Bone
                    pos: { x: -0.02, y: 0.04, z: -0.02 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                  - id: 29
                    name: '!joint_Eyes'
                    type: Bone
                    pos: { x: 0.0, y: 0.25, z: 0.02 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                    children:
                      - id: 30
                        name: '!joint_EyesTip'
                        type: Bone
                        pos: { x: 0.0, y: 0.0, z: -0.09 }
                        rot: { x: 0.0, y: 0.0, z: 0.0 }
          - id: 32
            name: joint_RightShoulder
            type: Bone
            pos: { x: 0.03, y: 0.17, z: 0.06 }
            rot: { x: 0.0, y: 0.0, z: 0.0 }
            children:
              - id: 33
                name: '!joint_RightShoulderC'
                type: Bone
                pos: { x: 0.08, y: 0.0, z: 0.0 }
                rot: { x: 0.0, y: 0.0, z: 0.0 }
              - id: 34
                name: joint_RightArm
                type: Bone
                pos: { x: 0.08, y: 0.0, z: 0.0 }
                rot: { x: 0.0, y: 0.0, z: 0.0 }
                children:
                  - id: 35
                    name: joint_RightArmTwist
                    type: Bone
                    pos: { x: 0.14, y: -0.01, z: -0.0 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                  - id: 36
                    name: joint_RightArmTwist1
                    type: Bone
                    pos: { x: 0.08, y: -0.0, z: -0.0 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                  - id: 37
                    name: joint_RightArmTwist2
                    type: Bone
                    pos: { x: 0.13, y: -0.01, z: -0.0 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                  - id: 38
                    name: joint_RightArmTwist3
                    type: Bone
                    pos: { x: 0.18, y: -0.01, z: -0.0 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                  - id: 39
                    name: joint_RightElbow
                    type: Bone
                    pos: { x: 0.24, y: -0.01, z: -0.0 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                    children:
                      - id: 44
                        name: joint_RightWrist
                        type: Bone
                        pos: { x: 0.24, y: -0.0, z: -0.0 }
                        rot: { x: 0.0, y: 0.0, z: 0.0 }
                        children:
                          - id: 47
                            name: joint_RightThumb0
                            type: Bone
                            pos: { x: -0.0, y: -0.0, z: -0.0 }
                            rot: { x: 0.0, y: 0.0, z: 0.0 }
                          - id: 51
                            name: joint_RightIndex1
                            type: Bone
                            pos: { x: 0.06, y: -0.01, z: -0.03 }
                            rot: { x: 0.0, y: 0.0, z: 0.0 }
                            children:
                              - id: 52
                                name: joint_RightIndex2
                                type: Bone
                                pos: { x: 0.03, y: -0.0, z: -0.0 }
                                rot: { x: 0.0, y: 0.0, z: 0.0 }
                                children:
                                  - id: 53
                                    name: joint_RightIndex3
                                    type: Bone
                                    pos: { x: 0.02, y: -0.0, z: -0.0 }
                                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                                    children:
                                      - id: 54
                                        name: '!joint_RightIndexTip'
                                        type: Bone
                                        pos: { x: 0.02, y: 0.0, z: -0.0 }
                                        rot: { x: 0.0, y: 0.0, z: 0.0 }
                          - id: 55
                            name: joint_RightMiddle1
                            type: Bone
                            pos: { x: 0.06, y: -0.01, z: -0.02 }
                            rot: { x: 0.0, y: 0.0, z: 0.0 }
                            children:
                              - id: 56
                                name: joint_RightMiddle2
                                type: Bone
                                pos: { x: 0.04, y: -0.0, z: -0.0 }
                                rot: { x: 0.0, y: 0.0, z: 0.0 }
                                children:
                                  - id: 57
                                    name: joint_RightMiddle3
                                    type: Bone
                                    pos: { x: 0.03, y: -0.0, z: -0.0 }
                                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                                    children:
                                      - id: 58
                                        name: '!joint_RightMiddleTip'
                                        type: Bone
                                        pos: { x: 0.03, y: -0.0, z: -0.0 }
                                        rot: { x: 0.0, y: 0.0, z: 0.0 }
                          - id: 59
                            name: joint_RightRing1
                            type: Bone
                            pos: { x: 0.06, y: -0.01, z: -0.0 }
                            rot: { x: 0.0, y: 0.0, z: 0.0 }
                            children:
                              - id: 60
                                name: joint_RightRing2
                                type: Bone
                                pos: { x: 0.03, y: -0.0, z: -0.0 }
                                rot: { x: 0.0, y: 0.0, z: 0.0 }
                                children:
                                  - id: 61
                                    name: joint_RightRing3
                                    type: Bone
                                    pos: { x: 0.02, y: -0.0, z: -0.0 }
                                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                                    children:
                                      - id: 62
                                        name: '!joint_RightRingTip'
                                        type: Bone
                                        pos: { x: 0.02, y: -0.0, z: -0.0 }
                                        rot: { x: 0.0, y: 0.0, z: 0.0 }
                          - id: 845
                            name: '!joint_RightThumb0M'
                            type: Bone
                            pos: { x: 0.01, y: -0.01, z: -0.02 }
                            rot: { x: 0.0, y: 0.0, z: 0.0 }
                            children:
                              - id: 48
                                name: joint_RightThumb1
                                type: Bone
                                pos: { x: 0.01, y: -0.01, z: -0.02 }
                                rot: { x: 0.0, y: 0.0, z: 0.0 }
                                children:
                                  - id: 49
                                    name: joint_RightThumb2
                                    type: Bone
                                    pos: { x: 0.01, y: -0.01, z: -0.02 }
                                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                                    children:
                                      - id: 50
                                        name: '!joint_RightThumbTip'
                                        type: Bone
                                        pos: { x: 0.01, y: -0.01, z: -0.03 }
                                        rot: { x: 0.0, y: 0.0, z: 0.0 }
          - id: 68
            name: joint_LeftShoulder
            type: Bone
            pos: { x: -0.03, y: 0.17, z: 0.06 }
            rot: { x: 0.0, y: 0.0, z: 0.0 }
            children:
              - id: 69
                name: '!joint_LeftShoulderC'
                type: Bone
                pos: { x: -0.08, y: 0.0, z: 0.0 }
                rot: { x: 0.0, y: 0.0, z: 0.0 }
              - id: 70
                name: joint_LeftArm
                type: Bone
                pos: { x: -0.08, y: 0.0, z: 0.0 }
                rot: { x: 0.0, y: 0.0, z: 0.0 }
                children:
                  - id: 71
                    name: joint_LeftArmTwist
                    type: Bone
                    pos: { x: -0.14, y: -0.01, z: -0.0 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                  - id: 72
                    name: joint_LeftArmTwist1
                    type: Bone
                    pos: { x: -0.08, y: -0.0, z: -0.0 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                  - id: 73
                    name: joint_LeftArmTwist2
                    type: Bone
                    pos: { x: -0.13, y: -0.01, z: -0.0 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                  - id: 74
                    name: joint_LeftArmTwist3
                    type: Bone
                    pos: { x: -0.18, y: -0.01, z: -0.0 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                  - id: 75
                    name: joint_LeftElbow
                    type: Bone
                    pos: { x: -0.24, y: -0.01, z: -0.0 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                    children:
                      - id: 80
                        name: joint_LeftWrist
                        type: Bone
                        pos: { x: -0.24, y: -0.0, z: -0.0 }
                        rot: { x: 0.0, y: 0.0, z: 0.0 }
                        children:
                          - id: 83
                            name: joint_LeftThumb0
                            type: Bone
                            pos: { x: 0.01, y: -0.0, z: 0.0 }
                            rot: { x: 0.0, y: 0.0, z: 0.0 }
                          - id: 87
                            name: joint_LeftIndex1
                            type: Bone
                            pos: { x: -0.06, y: -0.01, z: -0.03 }
                            rot: { x: 0.0, y: 0.0, z: 0.0 }
                            children:
                              - id: 88
                                name: joint_LeftIndex2
                                type: Bone
                                pos: { x: -0.03, y: -0.0, z: -0.0 }
                                rot: { x: 0.0, y: 0.0, z: 0.0 }
                                children:
                                  - id: 89
                                    name: joint_LeftIndex3
                                    type: Bone
                                    pos: { x: -0.02, y: -0.0, z: -0.0 }
                                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                                    children:
                                      - id: 90
                                        name: '!joint_LeftIndexTip'
                                        type: Bone
                                        pos: { x: -0.02, y: 0.0, z: -0.0 }
                                        rot: { x: 0.0, y: 0.0, z: 0.0 }
                          - id: 91
                            name: joint_LeftMiddle1
                            type: Bone
                            pos: { x: -0.06, y: -0.01, z: -0.02 }
                            rot: { x: 0.0, y: 0.0, z: 0.0 }
                            children:
                              - id: 92
                                name: joint_LeftMiddle2
                                type: Bone
                                pos: { x: -0.04, y: -0.0, z: -0.0 }
                                rot: { x: 0.0, y: 0.0, z: 0.0 }
                                children:
                                  - id: 93
                                    name: joint_LeftMiddle3
                                    type: Bone
                                    pos: { x: -0.03, y: -0.0, z: -0.0 }
                                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                                    children:
                                      - id: 94
                                        name: '!joint_LeftMiddleTip'
                                        type: Bone
                                        pos: { x: -0.03, y: -0.0, z: -0.0 }
                                        rot: { x: 0.0, y: 0.0, z: 0.0 }
                          - id: 95
                            name: joint_LeftRing1
                            type: Bone
                            pos: { x: -0.06, y: -0.01, z: -0.0 }
                            rot: { x: 0.0, y: 0.0, z: 0.0 }
                            children:
                              - id: 96
                                name: joint_LeftRing2
                                type: Bone
                                pos: { x: -0.03, y: -0.0, z: -0.0 }
                                rot: { x: 0.0, y: 0.0, z: 0.0 }
                                children:
                                  - id: 97
                                    name: joint_LeftRing3
                                    type: Bone
                                    pos: { x: -0.02, y: -0.0, z: -0.0 }
                                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                                    children:
                                      - id: 98
                                        name: '!joint_LeftRingTip'
                                        type: Bone
                                        pos: { x: -0.02, y: -0.0, z: -0.0 }
                                        rot: { x: 0.0, y: 0.0, z: 0.0 }
                          - id: 844
                            name: '!joint_LeftThumb0M'
                            type: Bone
                            pos: { x: -0.01, y: -0.01, z: -0.02 }
                            rot: { x: 0.0, y: 0.0, z: 0.0 }
                            children:
                              - id: 84
                                name: joint_LeftThumb1
                                type: Bone
                                pos: { x: -0.01, y: -0.01, z: -0.02 }
                                rot: { x: 0.0, y: 0.0, z: 0.0 }
                                children:
                                  - id: 85
                                    name: joint_LeftThumb2
                                    type: Bone
                                    pos: { x: -0.01, y: -0.01, z: -0.02 }
                                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                                    children:
                                      - id: 86
                                        name: '!joint_LeftThumbTip'
                                        type: Bone
                                        pos: { x: -0.01, y: -0.01, z: -0.03 }
                                        rot: { x: 0.0, y: 0.0, z: 0.0 }
      - id: 835
        name: joint_RightHipD
        type: Bone
        pos: { x: 0.0, y: 0.0, z: 0.0 }
        rot: { x: 0.0, y: 0.0, z: 0.0 }
        children:
          - id: 836
            name: joint_RightKneeD
            type: Bone
            pos: { x: -0.0, y: -0.43, z: 0.01 }
            rot: { x: 0.0, y: 0.0, z: 0.0 }
            children:
              - id: 104
                name: '!joint_RightHip'
                type: Bone
                pos: { x: 0.0, y: 0.43, z: -0.01 }
                rot: { x: 0.0, y: 0.0, z: 0.0 }
                children:
                  - id: 105
                    name: '!joint_RightKnee'
                    type: Bone
                    pos: { x: 0.01, y: -0.43, z: 0.02 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                    children:
                      - id: 106
                        name: '!joint_RightFoot'
                        type: Bone
                        pos: { x: 0.01, y: -0.41, z: 0.05 }
                        rot: { x: 0.0, y: 0.0, z: 0.0 }
              - id: 837
                name: joint_RightFootD
                type: Bone
                pos: { x: -0.01, y: -0.41, z: 0.05 }
                rot: { x: 0.0, y: 0.0, z: 0.0 }
      - id: 839
        name: joint_LeftHipD
        type: Bone
        pos: { x: 0.0, y: 0.0, z: 0.0 }
        rot: { x: 0.0, y: 0.0, z: 0.0 }
        children:
          - id: 840
            name: joint_LeftKneeD
            type: Bone
            pos: { x: 0.0, y: -0.43, z: 0.01 }
            rot: { x: 0.0, y: 0.0, z: 0.0 }
            children:
              - id: 109
                name: '!joint_LeftHip'
                type: Bone
                pos: { x: -0.0, y: 0.43, z: -0.01 }
                rot: { x: 0.0, y: 0.0, z: 0.0 }
                children:
                  - id: 110
                    name: '!joint_LeftKnee'
                    type: Bone
                    pos: { x: -0.01, y: -0.43, z: 0.02 }
                    rot: { x: 0.0, y: 0.0, z: 0.0 }
                    children:
                      - id: 111
                        name: '!joint_LeftFoot'
                        type: Bone
                        pos: { x: -0.01, y: -0.41, z: 0.05 }
                        rot: { x: 0.0, y: 0.0, z: 0.0 }
              - id: 841
                name: joint_LeftFootD
                type: Bone
                pos: { x: 0.01, y: -0.41, z: 0.05 }
                rot: { x: 0.0, y: 0.0, z: 0.0 }
```

=== HUMANOID BONES MAPPING ===
hips -> 17joint_HipMaster
leftUpperLeg -> 839joint_LeftHipD
rightUpperLeg -> 835joint_RightHipD
leftLowerLeg -> 840joint_LeftKneeD
rightLowerLeg -> 836joint_RightKneeD
leftFoot -> 841joint_LeftFootD
rightFoot -> 837joint_RightFootD
spine -> 19joint_Torso
chest -> 21joint_Torso2
neck -> 22joint_Neck
head -> 23joint_Head
leftShoulder -> 68joint_LeftShoulder
rightShoulder -> 32joint_RightShoulder
leftUpperArm -> 70joint_LeftArm
rightUpperArm -> 34joint_RightArm
leftLowerArm -> 75joint_LeftElbow
rightLowerArm -> 39joint_RightElbow
leftHand -> 80joint_LeftWrist
rightHand -> 44joint_RightWrist
leftToes -> 842joint_hidariashisakiEX
rightToes -> 838joint_migiashisakiEX
leftEye -> 27joint_LeftEye
rightEye -> 25joint_RightEye
leftThumbMetacarpal -> 844!joint_LeftThumb0M
leftThumbProximal -> 84joint_LeftThumb1
leftThumbDistal -> 85joint_LeftThumb2
leftIndexProximal -> 87joint_LeftIndex1
leftIndexIntermediate -> 88joint_LeftIndex2
leftIndexDistal -> 89joint_LeftIndex3
leftMiddleProximal -> 91joint_LeftMiddle1
leftMiddleIntermediate -> 92joint_LeftMiddle2
leftMiddleDistal -> 93joint_LeftMiddle3
leftRingProximal -> 95joint_LeftRing1
leftRingIntermediate -> 96joint_LeftRing2
leftRingDistal -> 97joint_LeftRing3
leftLittleProximal -> 99joint_LeftPinky1
leftLittleIntermediate -> 100joint_LeftPinky2
leftLittleDistal -> 101joint_LeftPinky3
rightThumbMetacarpal -> 845!joint_RightThumb0M
rightThumbProximal -> 48joint_RightThumb1
rightThumbDistal -> 49joint_RightThumb2
rightIndexProximal -> 51joint_RightIndex1
rightIndexIntermediate -> 52joint_RightIndex2
rightIndexDistal -> 53joint_RightIndex3
rightMiddleProximal -> 55joint_RightMiddle1
rightMiddleIntermediate -> 56joint_RightMiddle2
rightMiddleDistal -> 57joint_RightMiddle3
rightRingProximal -> 59joint_RightRing1
rightRingIntermediate -> 60joint_RightRing2
rightRingDistal -> 61joint_RightRing3
rightLittleProximal -> 63joint_RightPinky1
rightLittleIntermediate -> 64joint_RightPinky2
rightLittleDistal -> 65joint_RightPinky3

## BONE ROTATION AXIS BEHAVIOR RULES

### X, Y, Z AXIS FUNCTIONALITY

**X-Axis (Pitch):**

- Controls forward/backward rotation
- **Positive values (+):** Rotate bone forward/down
- **Negative values (-):** Rotate bone backward/up
- Most natural for nodding motions and forward/back arm movements

**Y-Axis (Yaw):**

- Controls left/right rotation
- **Positive values (+):** Rotate bone toward body center/inward
- **Negative values (-):** Rotate bone away from body center/outward
- Most natural for side-to-side movements and horizontal arm crossing

**Z-Axis (Roll):**

- Controls up/down rotation (elevation)
- **Positive values (+):** Lift/raise bone upward
- **Negative values (-):** Lower/drop bone downward

## standing pose

Relaxed arms

hips: { x: 0.000, y: 0.000, z: 0.000 }
spine: { x: -0.000, y: -0.000, z: 0.000 }
chest: { x: 0.000, y: -0.000, z: -0.000 }
neck: { x: -0.000, y: -0.000, z: 0.000 }
head: { x: 0.000, y: -0.000, z: -0.000 }
leftShoulder: { x: -0.000, y: -0.000, z: 0.000 }
rightShoulder: { x: -0.000, y: -0.000, z: -0.000 }
leftUpperArm: { x: -0.278, y: -0.150, z: 1.279 }
rightUpperArm: { x: -0.278, y: 0.150, z: -1.279 }
leftLowerArm: { x: 0.035, y: -0.039, z: 0.000 }
rightLowerArm: { x: 0.035, y: 0.039, z: -0.000 }
leftHand: { x: 0.008, y: 0.000, z: -0.003 }
rightHand: { x: 0.008, y: -0.000, z: 0.003 }
leftUpperLeg: { x: 0.000, y: -0.004, z: 0.029 }
rightUpperLeg: { x: 0.000, y: 0.004, z: -0.029 }
leftLowerLeg: { x: -0.000, y: -0.001, z: -0.000 }
rightLowerLeg: { x: -0.000, y: 0.001, z: 0.000 }
leftFoot: { x: 0.000, y: -0.004, z: 0.001 }
rightFoot: { x: 0.000, y: 0.004, z: -0.001 }
leftEye: { x: 0.000, y: 0.000, z: 0.000 }
rightEye: { x: 0.000, y: 0.000, z: 0.000 }
leftThumbMetacarpal: { x: 0.025, y: 0.022, z: 0.132 }
leftThumbProximal: { x: -0.008, y: 0.456, z: -0.002 }
leftThumbDistal: { x: 0.046, y: 0.033, z: 0.022 }
leftIndexProximal: { x: -0.009, y: -0.007, z: -0.002 }
leftIndexIntermediate: { x: -0.025, y: -0.009, z: 0.003 }
leftIndexDistal: { x: -0.026, y: -0.009, z: -0.014 }
leftMiddleProximal: { x: -0.007, y: 0.021, z: 0.005 }
leftMiddleIntermediate: { x: 0.000, y: 0.000, z: 0.001 }
leftMiddleDistal: { x: 0.000, y: 0.000, z: 0.001 }
leftRingProximal: { x: 0.001, y: -0.002, z: 0.000 }
leftRingIntermediate: { x: 0.000, y: 0.000, z: 0.008 }
leftRingDistal: { x: -0.000, y: 0.000, z: 0.003 }
leftLittleProximal: { x: -0.006, y: 0.018, z: -0.001 }
leftLittleIntermediate: { x: 0.000, y: 0.000, z: 0.038 }
leftLittleDistal: { x: -0.000, y: 0.000, z: 0.001 }
rightThumbMetacarpal: { x: 0.025, y: -0.022, z: -0.132 }
rightThumbProximal: { x: -0.008, y: -0.456, z: 0.002 }
rightThumbDistal: { x: 0.046, y: -0.033, z: -0.022 }
rightIndexProximal: { x: -0.009, y: 0.007, z: 0.002 }
rightIndexIntermediate: { x: -0.025, y: 0.009, z: -0.003 }
rightIndexDistal: { x: -0.026, y: 0.009, z: 0.014 }
rightMiddleProximal: { x: -0.007, y: -0.021, z: -0.005 }
rightMiddleIntermediate: { x: 0.000, y: -0.000, z: -0.001 }
rightMiddleDistal: { x: 0.000, y: -0.000, z: -0.001 }
rightRingProximal: { x: 0.001, y: 0.002, z: -0.000 }
rightRingIntermediate: { x: 0.000, y: -0.000, z: -0.008 }
rightRingDistal: { x: -0.000, y: -0.000, z: -0.003 }
rightLittleProximal: { x: -0.006, y: -0.018, z: 0.001 }
rightLittleIntermediate: { x: 0.000, y: -0.000, z: -0.038 }
rightLittleDistal: { x: -0.000, y: -0.000, z: -0.001 }

## hello pose

saying hello with left hand

hips: { x: -0.001, y: 0.019, z: -0.002 }
spine: { x: -0.000, y: -0.000, z: 0.000 }
chest: { x: 0.002, y: 0.354, z: 0.044 }
neck: { x: -0.064, y: -0.331, z: -0.173 }
head: { x: 0.000, y: 0.000, z: 0.000 }
leftShoulder: { x: -0.000, y: -0.000, z: 0.000 }
rightShoulder: { x: -0.000, y: -0.000, z: -0.000 }
leftUpperArm: { x: -0.352, y: 0.023, z: 1.009 }
rightUpperArm: { x: 0.078, y: -0.471, z: -1.298 }
leftLowerArm: { x: 0.035, y: -0.039, z: 0.000 }
rightLowerArm: { x: -2.305, y: 1.028, z: 3.097 }
leftHand: { x: 0.008, y: 0.000, z: -0.003 }
rightHand: { x: -0.027, y: -0.000, z: 0.002 }
leftUpperLeg: { x: 0.121, y: -0.011, z: 0.075 }
rightUpperLeg: { x: -0.239, y: 0.013, z: -0.042 }
leftLowerLeg: { x: -0.000, y: -0.001, z: -0.000 }
rightLowerLeg: { x: -0.000, y: 0.001, z: 0.000 }
leftFoot: { x: -0.136, y: 0.004, z: -0.113 }
rightFoot: { x: 0.000, y: 0.004, z: -0.001 }
leftEye: { x: 0.000, y: 0.000, z: 0.000 }
rightEye: { x: 0.000, y: 0.000, z: 0.000 }
leftThumbMetacarpal: { x: 0.163, y: -0.331, z: 0.193 }
leftThumbProximal: { x: 0.024, y: 0.198, z: 0.010 }
leftThumbDistal: { x: 0.024, y: 0.198, z: 0.010 }
leftIndexProximal: { x: 0.089, y: -0.250, z: 0.311 }
leftIndexIntermediate: { x: -0.009, y: -0.006, z: 0.382 }
leftIndexDistal: { x: -0.009, y: -0.006, z: 0.382 }
leftMiddleProximal: { x: 0.040, y: -0.111, z: 0.302 }
leftMiddleIntermediate: { x: 0.000, y: 0.000, z: 0.382 }
leftMiddleDistal: { x: 0.000, y: 0.000, z: 0.382 }
leftRingProximal: { x: -0.040, y: 0.111, z: 0.302 }
leftRingIntermediate: { x: 0.000, y: 0.000, z: 0.382 }
leftRingDistal: { x: -0.000, y: -0.000, z: 0.382 }
leftLittleProximal: { x: -0.094, y: 0.248, z: 0.312 }
leftLittleIntermediate: { x: 0.000, y: 0.000, z: 0.382 }
leftLittleDistal: { x: -0.000, y: -0.000, z: 0.382 }
rightThumbMetacarpal: { x: 0.433, y: 0.525, z: -0.105 }
rightThumbProximal: { x: 0.082, y: 0.208, z: -0.046 }
rightThumbDistal: { x: 0.082, y: 0.208, z: -0.046 }
rightIndexProximal: { x: 0.078, y: 0.462, z: 0.276 }
rightIndexIntermediate: { x: -0.032, y: 0.009, z: 0.147 }
rightIndexDistal: { x: -0.032, y: 0.009, z: 0.147 }
rightMiddleProximal: { x: 0.040, y: 0.191, z: 0.287 }
rightMiddleIntermediate: { x: 0.000, y: -0.000, z: 0.148 }
rightMiddleDistal: { x: 0.000, y: -0.000, z: 0.148 }
rightRingProximal: { x: -0.040, y: -0.191, z: 0.287 }
rightRingIntermediate: { x: 0.000, y: -0.000, z: 0.148 }
rightRingDistal: { x: -0.000, y: -0.000, z: 0.148 }
rightLittleProximal: { x: -0.096, y: -0.460, z: 0.271 }
rightLittleIntermediate: { x: 0.000, y: -0.000, z: 0.148 }
rightLittleDistal: { x: -0.000, y: -0.000, z: 0.148 }

## shi pose

moving the left hand up and down like saying "it was nothing"

hips: { x: 0.022, y: -0.026, z: 0.001 }
spine: { x: 0.013, y: 0.004, z: 0.020 }
chest: { x: 0.006, y: 0.001, z: 0.010 }
neck: { x: -0.055, y: -0.009, z: -0.039 }
head: { x: -0.248, y: 0.055, z: -0.062 }
leftShoulder: { x: -0.004, y: 0.031, z: 0.023 }
rightShoulder: { x: -0.006, y: -0.040, z: 0.169 }
leftUpperArm: { x: -0.165, y: -0.454, z: 1.155 }
rightUpperArm: { x: 0.149, y: 0.333, z: -0.711 }
leftLowerArm: { x: 0.148, y: -0.457, z: 0.151 }
rightLowerArm: { x: 1.865, y: 0.946, z: -1.855 }
leftHand: { x: 0.297, y: 0.009, z: 0.019 }
rightHand: { x: 0.663, y: 0.413, z: -0.275 }
leftUpperLeg: { x: -0.014, y: 0.024, z: 0.007 }
rightUpperLeg: { x: -0.023, y: -0.020, z: -0.016 }
leftLowerLeg: { x: -0.009, y: 0.015, z: 0.000 }
rightLowerLeg: { x: 0.012, y: 0.018, z: -0.001 }
leftFoot: { x: 0.005, y: -0.011, z: 0.003 }
rightFoot: { x: -0.009, y: 0.042, z: -0.013 }
leftEye: { x: 0.000, y: 0.000, z: 0.000 }
rightEye: { x: 0.000, y: 0.000, z: 0.000 }
leftThumbMetacarpal: { x: -0.536, y: 0.453, z: 0.473 }
leftThumbProximal: { x: 0.029, y: 0.165, z: 0.012 }
leftThumbDistal: { x: 0.046, y: 0.032, z: 0.022 }
leftIndexProximal: { x: -0.490, y: 0.414, z: 0.988 }
leftIndexIntermediate: { x: 0.014, y: 0.019, z: 1.188 }
leftIndexDistal: { x: 0.008, y: 0.008, z: 0.893 }
leftMiddleProximal: { x: -0.561, y: 0.383, z: 1.254 }
leftMiddleIntermediate: { x: -0.000, y: -0.000, z: 1.378 }
leftMiddleDistal: { x: -0.000, y: -0.000, z: 1.417 }
leftRingProximal: { x: -0.586, y: 0.487, z: 1.287 }
leftRingIntermediate: { x: -0.000, y: -0.000, z: 1.469 }
leftRingDistal: { x: -0.000, y: -0.000, z: 1.509 }
leftLittleProximal: { x: -0.667, y: 0.531, z: 1.431 }
leftLittleIntermediate: { x: -0.000, y: -0.000, z: 1.196 }
leftLittleDistal: { x: -0.000, y: -0.000, z: 1.196 }
rightThumbMetacarpal: { x: -0.688, y: -0.393, z: -0.608 }
rightThumbProximal: { x: 0.014, y: -0.278, z: -0.005 }
rightThumbDistal: { x: 0.050, y: -0.007, z: -0.024 }
rightIndexProximal: { x: -0.092, y: -0.256, z: -0.027 }
rightIndexIntermediate: { x: -0.024, y: 0.009, z: -0.031 }
rightIndexDistal: { x: -0.027, y: 0.009, z: 0.027 }
rightMiddleProximal: { x: -0.002, y: -0.013, z: 0.044 }
rightMiddleIntermediate: { x: 0.000, y: -0.000, z: -0.125 }
rightMiddleDistal: { x: 0.000, y: -0.000, z: -0.082 }
rightRingProximal: { x: 0.012, y: 0.083, z: 0.156 }
rightRingIntermediate: { x: 0.000, y: -0.000, z: -0.123 }
rightRingDistal: { x: -0.000, y: -0.000, z: -0.019 }
rightLittleProximal: { x: -0.008, y: -0.024, z: 0.004 }
rightLittleIntermediate: { x: 0.000, y: -0.000, z: -0.101 }
rightLittleDistal: { x: -0.000, y: 0.000, z: -0.054 }

# Victory pose

doing the V signal with the hands

hips: { x: 0.065, y: -0.561, z: -0.298 }
spine: { x: 0.030, y: 0.246, z: 0.131 }
chest: { x: 0.002, y: 0.288, z: 0.169 }
neck: { x: -0.035, y: 0.113, z: 0.024 }
head: { x: 0.071, y: 0.103, z: 0.122 }
leftShoulder: { x: -0.004, y: -0.006, z: -0.176 }
rightShoulder: { x: -0.001, y: 0.004, z: 0.075 }
leftUpperArm: { x: 0.310, y: 0.083, z: 1.292 }
rightUpperArm: { x: 0.005, y: -0.281, z: -1.608 }
leftLowerArm: { x: -2.144, y: -0.969, z: -2.763 }
rightLowerArm: { x: -2.306, y: 0.617, z: 3.054 }
leftHand: { x: -0.189, y: 0.494, z: -0.236 }
rightHand: { x: -0.042, y: -0.544, z: 0.289 }
leftUpperLeg: { x: 0.717, y: -0.175, z: 0.415 }
rightUpperLeg: { x: -0.146, y: -0.070, z: 0.205 }
leftLowerLeg: { x: -1.641, y: -0.090, z: -0.218 }
rightLowerLeg: { x: 0.129, y: -0.062, z: 0.004 }
leftFoot: { x: -0.492, y: -0.125, z: 0.101 }
rightFoot: { x: -0.022, y: -0.059, z: 0.050 }
leftEye: { x: 0.000, y: 0.000, z: 0.000 }
rightEye: { x: 0.000, y: 0.000, z: 0.000 }
leftThumbMetacarpal: { x: 0.090, y: 0.198, z: 0.004 }
leftThumbProximal: { x: -0.242, y: 1.336, z: 0.118 }
leftThumbDistal: { x: -0.112, y: 1.082, z: 0.017 }
leftIndexProximal: { x: 0.083, y: -0.308, z: 0.017 }
leftIndexIntermediate: { x: -0.025, y: -0.009, z: 0.003 }
leftIndexDistal: { x: -0.026, y: -0.009, z: -0.014 }
leftMiddleProximal: { x: -0.007, y: 0.021, z: 0.005 }
leftMiddleIntermediate: { x: 0.000, y: 0.000, z: 0.001 }
leftMiddleDistal: { x: 0.000, y: 0.000, z: 0.001 }
leftRingProximal: { x: 0.124, y: -0.024, z: 1.385 }
leftRingIntermediate: { x: -0.000, y: -0.000, z: 1.681 }
leftRingDistal: { x: -0.000, y: -0.000, z: 1.448 }
leftLittleProximal: { x: 0.192, y: -0.020, z: 1.333 }
leftLittleIntermediate: { x: -0.000, y: -0.000, z: 1.387 }
leftLittleDistal: { x: -0.000, y: -0.000, z: 1.592 }
rightThumbMetacarpal: { x: 0.090, y: -0.198, z: -0.004 }
rightThumbProximal: { x: -0.242, y: -1.336, z: -0.118 }
rightThumbDistal: { x: -0.112, y: -1.082, z: -0.017 }
rightIndexProximal: { x: 0.083, y: 0.308, z: -0.017 }
rightIndexIntermediate: { x: -0.025, y: 0.009, z: -0.003 }
rightIndexDistal: { x: -0.026, y: 0.009, z: 0.014 }
rightMiddleProximal: { x: -0.007, y: -0.021, z: -0.005 }
rightMiddleIntermediate: { x: 0.000, y: -0.000, z: -0.001 }
rightMiddleDistal: { x: 0.000, y: -0.000, z: -0.001 }
rightRingProximal: { x: 0.124, y: 0.024, z: -1.385 }
rightRingIntermediate: { x: -0.000, y: 0.000, z: -1.681 }
rightRingDistal: { x: -0.000, y: 0.000, z: -1.448 }
rightLittleProximal: { x: 0.192, y: 0.020, z: -1.333 }
rightLittleIntermediate: { x: -0.000, y: 0.000, z: -1.387 }
rightLittleDistal: { x: -0.000, y: 0.000, z: -1.592 }

# power pose

hands in the hips and power actitude

hips: { x: 0.004, y: -0.031, z: -0.246 }
spine: { x: 0.005, y: 0.008, z: 0.140 }
chest: { x: 0.015, y: 0.009, z: 0.089 }
neck: { x: 0.001, y: 0.006, z: 0.019 }
head: { x: 0.002, y: 0.000, z: 0.082 }
leftShoulder: { x: -0.000, y: -0.001, z: -0.004 }
rightShoulder: { x: 0.000, y: 0.001, z: 0.003 }
leftUpperArm: { x: -0.631, y: -0.259, z: 0.298 }
rightUpperArm: { x: -0.620, y: 0.398, z: -0.595 }
leftLowerArm: { x: 1.556, y: -1.530, z: 2.136 }
rightLowerArm: { x: -1.084, y: 1.217, z: 0.510 }
leftHand: { x: -0.273, y: -0.627, z: -0.891 }
rightHand: { x: -0.355, y: 0.414, z: 0.796 }
leftUpperLeg: { x: -0.061, y: -0.054, z: 0.269 }
rightUpperLeg: { x: 0.122, y: 0.118, z: 0.289 }
leftLowerLeg: { x: 0.131, y: -0.110, z: 0.004 }
rightLowerLeg: { x: -0.257, y: 0.231, z: 0.036 }
leftFoot: { x: -0.254, y: -0.126, z: -0.051 }
rightFoot: { x: 0.143, y: 0.062, z: -0.043 }
leftEye: { x: 0.000, y: 0.000, z: 0.000 }
rightEye: { x: 0.000, y: 0.000, z: 0.000 }
leftThumbMetacarpal: { x: -0.264, y: -0.266, z: 0.487 }
leftThumbProximal: { x: 0.023, y: 0.209, z: 0.009 }
leftThumbDistal: { x: 0.015, y: 0.277, z: 0.006 }
leftIndexProximal: { x: -0.009, y: -0.007, z: -0.002 }
leftIndexIntermediate: { x: 0.004, y: 0.004, z: 0.773 }
leftIndexDistal: { x: -0.028, y: -0.009, z: -0.051 }
leftMiddleProximal: { x: -0.018, y: -0.008, z: 0.511 }
leftMiddleIntermediate: { x: 0.000, y: 0.000, z: 0.001 }
leftMiddleDistal: { x: 0.000, y: 0.000, z: 0.001 }
leftRingProximal: { x: 0.051, y: -0.054, z: 0.458 }
leftRingIntermediate: { x: 0.000, y: 0.000, z: 0.008 }
leftRingDistal: { x: -0.000, y: 0.000, z: 0.003 }
leftLittleProximal: { x: 0.063, y: 0.033, z: 0.927 }
leftLittleIntermediate: { x: 0.000, y: 0.000, z: 0.038 }
leftLittleDistal: { x: -0.000, y: 0.000, z: 0.001 }
rightThumbMetacarpal: { x: -0.401, y: 0.463, z: -0.669 }
rightThumbProximal: { x: -0.012, y: -0.495, z: 0.003 }
rightThumbDistal: { x: 0.015, y: -0.277, z: -0.006 }
rightIndexProximal: { x: -0.009, y: 0.007, z: 0.002 }
rightIndexIntermediate: { x: 0.004, y: -0.004, z: -0.773 }
rightIndexDistal: { x: -0.028, y: 0.009, z: 0.051 }
rightMiddleProximal: { x: -0.018, y: 0.008, z: -0.511 }
rightMiddleIntermediate: { x: 0.000, y: -0.000, z: -0.001 }
rightMiddleDistal: { x: 0.000, y: -0.000, z: -0.001 }
rightRingProximal: { x: 0.051, y: 0.054, z: -0.458 }
rightRingIntermediate: { x: 0.000, y: -0.000, z: -0.008 }
rightRingDistal: { x: -0.000, y: -0.000, z: -0.003 }
rightLittleProximal: { x: 0.063, y: -0.033, z: -0.927 }
rightLittleIntermediate: { x: 0.000, y: -0.000, z: -0.038 }
rightLittleDistal: { x: -0.000, y: -0.000, z: -0.001 }

# yawn pose

one hand raised relaxedly while the other covers a yawn

hips: { x: 0.115, y: -0.003, z: 0.225 }
spine: { x: -0.006, y: -0.016, z: -0.128 }
chest: { x: 0.001, y: -0.018, z: -0.195 }
neck: { x: 0.004, y: -0.118, z: -0.035 }
head: { x: -0.263, y: -0.158, z: -0.154 }
leftShoulder: { x: -0.060, y: -0.138, z: -0.835 }
rightShoulder: { x: -0.014, y: 0.095, z: 0.383 }
leftUpperArm: { x: 0.853, y: -0.382, z: 0.185 }
rightUpperArm: { x: 0.101, y: 0.211, z: -0.753 }
leftLowerArm: { x: 1.043, y: -0.678, z: 0.265 }
rightLowerArm: { x: 2.160, y: 0.396, z: -2.498 }
leftHand: { x: 0.425, y: 0.174, z: -1.124 }
rightHand: { x: 0.957, y: 0.111, z: 0.098 }
leftUpperLeg: { x: -0.279, y: 0.088, z: -0.224 }
rightUpperLeg: { x: -0.264, y: 0.089, z: -0.221 }
leftLowerLeg: { x: 0.130, y: -0.031, z: 0.002 }
rightLowerLeg: { x: 0.130, y: -0.004, z: 0.000 }
leftFoot: { x: -0.043, y: -0.031, z: 0.025 }
rightFoot: { x: -0.373, y: -0.006, z: 0.004 }
leftEye: { x: 0.000, y: 0.000, z: 0.000 }
rightEye: { x: 0.000, y: 0.000, z: 0.000 }
leftThumbMetacarpal: { x: -0.037, y: -0.074, z: 0.226 }
leftThumbProximal: { x: -0.074, y: 0.918, z: 0.000 }
leftThumbDistal: { x: 0.046, y: 0.033, z: 0.022 }
leftIndexProximal: { x: -0.041, y: -0.070, z: 1.344 }
leftIndexIntermediate: { x: 0.015, y: 0.021, z: 1.243 }
leftIndexDistal: { x: 0.012, y: 0.014, z: 1.053 }
leftMiddleProximal: { x: 0.031, y: -0.079, z: 1.518 }
leftMiddleIntermediate: { x: -0.000, y: -0.000, z: 1.320 }
leftMiddleDistal: { x: -0.000, y: 0.000, z: 1.173 }
leftRingProximal: { x: 0.142, y: -0.013, z: 1.584 }
leftRingIntermediate: { x: -0.000, y: -0.000, z: 1.280 }
leftRingDistal: { x: -0.000, y: -0.000, z: 1.220 }
leftLittleProximal: { x: 0.235, y: -0.017, z: 1.498 }
leftLittleIntermediate: { x: -0.000, y: -0.000, z: 1.225 }
leftLittleDistal: { x: -0.000, y: -0.000, z: 1.346 }
rightThumbMetacarpal: { x: 0.047, y: 0.053, z: -0.145 }
rightThumbProximal: { x: 0.019, y: -0.240, z: -0.008 }
rightThumbDistal: { x: 0.068, y: 0.120, z: -0.036 }
rightIndexProximal: { x: 0.011, y: 0.075, z: 0.001 }
rightIndexIntermediate: { x: -0.025, y: 0.009, z: -0.003 }
rightIndexDistal: { x: -0.026, y: 0.009, z: 0.014 }
rightMiddleProximal: { x: -0.025, y: -0.079, z: -0.011 }
rightMiddleIntermediate: { x: 0.000, y: -0.000, z: -0.001 }
rightMiddleDistal: { x: 0.000, y: -0.000, z: -0.001 }
rightRingProximal: { x: 0.001, y: 0.002, z: -0.000 }
rightRingIntermediate: { x: 0.000, y: -0.000, z: -0.008 }
rightRingDistal: { x: -0.000, y: -0.000, z: -0.004 }
rightLittleProximal: { x: -0.098, y: -0.307, z: -0.044 }
rightLittleIntermediate: { x: 0.000, y: -0.000, z: -0.038 }
rightLittleDistal: { x: -0.000, y: 0.000, z: -0.002 }
