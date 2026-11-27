extends Node3D

const CAST := "E:/CyberCity2085-3d-lab/generated/phase2/"
var animation: AnimationPlayer
var clips: Dictionary
var movement: Tween
var destination := Vector3.ZERO
var fallen := false
var ring: MeshInstance3D
var pistol_parts: Array[Node3D] = []


func configure(allied: bool, support: bool, initial: Vector3,
 model_cache: Dictionary[String, PackedScene]) -> bool:
 var path := "support167/human.glb" if allied else "armored203/armored_actions.glb"
 clips = {"idle": "Hard stand", "walk": "Walk (1_24)", "fire": "ShootStudy", "death": "DeathStudy",
  "melee": "MeleeStudy", "psi": "PsiCast", "aid": "MedicalAidPrototype"} if allied else {
  "idle": "Idle", "walk": "Walk", "fire": "Pistol_Attack_Study", "death": "Death", "melee": "Attack"}
 var packed := model_cache.get(path) as PackedScene
 if packed == null:
  var document := GLTFDocument.new()
  var state := GLTFState.new()
  if document.append_from_file(CAST + path, state) != OK:
   return false
  var imported := document.generate_scene(state)
  if imported == null:
   return false
  packed = PackedScene.new()
  var pack_error := packed.pack(imported)
  imported.free()
  if pack_error != OK:
   return false
  model_cache[path] = packed
 var model := packed.instantiate() as Node3D
 if model == null:
  return false
 add_child(model)
 var players := model.find_children("*", "AnimationPlayer", true, false)
 if players.is_empty():
  return false
 animation = players[0] as AnimationPlayer
 if allied:
  for mesh in model.find_children("EquippedPistol_*", "MeshInstance3D", true, false):
   pistol_parts.append(mesh)
   mesh.hide()
 if support and not configure_support_appearance(model):
  return false
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
 var tint := Color(.62,.28,1.0) if support else Color(.12,.85,1.0) if allied else Color(1.0,.24,.10)
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


func configure_support_appearance(model: Node3D) -> bool:
 var rigs := model.find_children("*", "Skeleton3D", true, false)
 if rigs.is_empty():
  return false
 var rig := rigs[0] as Skeleton3D
 var head := rig.find_bone("DEF-spine_006")
 if head < 0:
  head = rig.find_bone("DEF-spine.006")
 if head < 0:
  return false
 var document := GLTFDocument.new()
 var state := GLTFState.new()
 if document.append_from_file(CAST + "modularity166/body_0_helmet_restfixed.glb", state) != OK:
  return false
 var donor := document.generate_scene(state)
 var source := donor.find_child("HelmetModule166", true, false) as MeshInstance3D
 if source == null:
  donor.free()
  return false
 var helmet := MeshInstance3D.new()
 helmet.name = "OracleHelmet"
 helmet.mesh = source.mesh
 for surface in helmet.mesh.get_surface_count():
  var original := source.get_active_material(surface) as StandardMaterial3D
  if original != null:
   var material := original.duplicate() as StandardMaterial3D
   material.albedo_color *= Color(.42,.44,.58)
   material.roughness = maxf(material.roughness, .68)
   material.metallic = minf(material.metallic, .30)
   helmet.set_surface_override_material(surface, material)
 donor.free()
 var head_mount := BoneAttachment3D.new()
 head_mount.bone_name = rig.get_bone_name(head)
 rig.add_child(head_mount)
 head_mount.add_child(helmet)
 var rest := rig.get_bone_global_rest(head)
 var center := helmet.mesh.get_aabb().get_center()
 var fit := Basis.from_scale(Vector3(1.09, 1.08, 1.12))
 helmet.transform = (rig.global_transform * rest).affine_inverse() * model.global_transform * (
  Transform3D(fit, center - fit * center + Vector3(0, -.025, -.016)))
 for hair in model.find_children("ActualCopperQuiff*", "MeshInstance3D", true, false):
  hair.hide()
 var body := model.find_child("Character", true, false) as MeshInstance3D
 if body != null:
  for surface in body.mesh.get_surface_count():
   var original := body.get_active_material(surface) as StandardMaterial3D
   if original != null and original.resource_name in ["Jacket", "Pants"]:
    var material := original.duplicate() as StandardMaterial3D
    material.albedo_color *= Color(.63, .49, .94) if original.resource_name == "Jacket" else Color(.52,.57,.75)
    body.set_surface_override_material(surface, material)
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
  set_pistol_visible(false)
  if movement != null:
   movement.kill()
  animation.play(clips.death, .08)
  return
 if destination.is_equal_approx(point):
  return
 if movement != null:
  movement.kill()
 destination = point
 set_pistol_visible(false)
 face(point)
 animation.play(clips.walk, .08)
 movement = create_tween()
 movement.tween_property(self, "position", point, clampf(position.distance_to(point)*.34, .15, 1.1))
 movement.finished.connect(func(): animation.play(clips.idle, .12))


func fire_at(point: Vector3, melee := false) -> void:
 play_action(point, "melee" if melee else "fire")


func play_action(point: Vector3, action: String) -> void:
 if fallen:
  return
 if movement != null and movement.is_running():
  movement.kill()
  position = destination
 face(point)
 animation.stop()
 set_pistol_visible(action == "fire")
 animation.play(clips[action], .06)


func _clip_finished(clip: StringName) -> void:
 if not fallen and clip != clips.death:
  set_pistol_visible(false)
  animation.play(clips.idle, .12)


func set_pistol_visible(value: bool) -> void:
 for part in pistol_parts:
  part.visible = value
