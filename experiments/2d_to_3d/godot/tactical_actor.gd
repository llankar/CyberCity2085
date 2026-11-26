extends Node3D

const CAST := "E:/CyberCity2085-3d-lab/generated/phase2/"
var animation: AnimationPlayer
var clips: Dictionary
var movement: Tween
var destination := Vector3.ZERO
var fallen := false
var ring: MeshInstance3D


func configure(allied: bool, initial: Vector3) -> bool:
 var path := "sole_skin162/human.glb" if allied else "armored203/armored_actions.glb"
 clips = {"idle": "Hard stand", "walk": "Walk (1_24)", "fire": "ShootStudy", "death": "DeathStudy", "melee": "MeleeStudy"} if allied else {
  "idle": "Idle", "walk": "Walk", "fire": "Pistol_Attack_Study", "death": "Death", "melee": "Attack"}
 var document := GLTFDocument.new()
 var state := GLTFState.new()
 if document.append_from_file(CAST + path, state) != OK:
  return false
 var model := document.generate_scene(state)
 add_child(model)
 var players := model.find_children("*", "AnimationPlayer", true, false)
 if players.is_empty():
  return false
 animation = players[0] as AnimationPlayer
 for action: String in clips:
  if not animation.has_animation(clips[action]):
   push_error("Missing retained animation %s in %s" % [clips[action], path])
   return false
  animation.get_animation(clips[action]).loop_mode = (
   Animation.LOOP_LINEAR if action in ["idle", "walk"] else Animation.LOOP_NONE)
 animation.animation_finished.connect(_clip_finished)
 ring = MeshInstance3D.new()
 var torus := TorusMesh.new()
 torus.inner_radius = .30
 torus.outer_radius = .36
 torus.rings = 24
 torus.ring_segments = 8
 ring.mesh = torus
 var tint := Color(.12,.85,1.0) if allied else Color(1.0,.24,.10)
 var material := StandardMaterial3D.new()
 material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
 material.albedo_color = tint
 ring.material_override = material
 ring.position.y = .05
 add_child(ring)
 destination = initial
 position = initial
 animation.play(clips.idle)
 return true


func face(point: Vector3) -> void:
 if position.distance_squared_to(point) > .0001:
  look_at(point, Vector3.UP, true)


func update_state(point: Vector3, health: int) -> void:
 if fallen:
  return
 if health <= 0:
  fallen = true
  ring.hide()
  if movement != null:
   movement.kill()
  animation.play(clips.death, .08)
  return
 if destination.is_equal_approx(point):
  return
 if movement != null:
  movement.kill()
 destination = point
 face(point)
 animation.play(clips.walk, .08)
 movement = create_tween()
 movement.tween_property(self, "position", point, clampf(position.distance_to(point)*.34, .15, 1.1))
 movement.finished.connect(func(): animation.play(clips.idle, .12))


func fire_at(point: Vector3, melee := false) -> void:
 if fallen:
  return
 if movement != null and movement.is_running():
  movement.kill()
  position = destination
 face(point)
 animation.stop()
 animation.play(clips.melee if melee else clips.fire, .06)


func _clip_finished(clip: StringName) -> void:
 if not fallen and clip in [clips.fire, clips.melee]:
  animation.play(clips.idle, .12)
