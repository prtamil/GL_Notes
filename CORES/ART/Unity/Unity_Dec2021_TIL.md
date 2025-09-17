# December-2021

## Basic Concepts

1. QWERT
2. Select Object in Hiearchy F will focus it.
3. Project > Assets > Scenes clicking on it will open scenes. Game will have multiple scenes
4. Ctrl+Shif+F on Camera Sync [Scend with Game mode]
5. Install additional Module.[unityhub]
6. prefab
7. packagemanager [Window/PackageManager]
8. Audio Spatial Blend [Treat audio as 3d Audio]
   1. Rolloff of audio defines range in 3d shape,
   2. only one Audio Listener in Scene
   3. Usually camera[Eyes], AudioListener[Ears]
9. RigidBody in Script
   1. GetComponent<RigidBody> <Start >
   2. AddForce(transform.up\*thrust) <FixedUpdate>
10. Update [Update vs FixedUpdate :Dont handle key in fixedupdate]
11. FixUpdate work for Physics update.
12. Update game update (perFrame)

## Create Sprite

1.  Sprite: Add Images
2.  Color: Add Colors
3.  Add Components : RigidBody2D
4.  Add Components : CircleCollider2D [Based on Shape]

## Coliders; Which gives Sprite Phyiscal Shape.

In 3D Primitive already has Built-in Colliders already.

## RigidBody vs Colliders

RigidBody => Control how GameObject interacts with Gravity and airDensity.
Colliders => Adds Additional Properties to Determine how Object interact
with Each Other

## Words

GME => Games, Media, Education
AEC => Architecture, Engineering, Construction.
ATM => Automative, Transportation and Manufacturing.

## Layout.

Editor Layout (Tall)
Save Layout to use it later
drag game scene beneth scene view so we see both.
Project -> (three dots) -> Single column layout.

## CenterPivot

in W mode pressing Z key will switch Center/Pivot
