extends "res://combat_effects169.gd"


func tactical_attack(action: String, from: Vector3, target: Vector3, hit: Variant,
  damage: int, precision: bool) -> void:
 var travel := target - from
 var miss_offset := travel.normalized().cross(Vector3.UP) * .65 + Vector3.UP * .21
 var destination := target + miss_offset if hit == false else target
 match action:
  "fire":
   var color := Color(.72,.9,1) if precision else Color(1,.7,.25)
   sound("pistol", from, -8, .78 if precision else 1.0)
   line(from, destination, color, .012, .11)
   line(from, from + (destination-from).normalized()*.22, color, .038, .075)
  "melee":
   sound("melee", from, -12)
  "psi":
   psychic(from, destination, false)
 if hit == true and damage > 0:
  spark(target, action == "psi")
  sound("hit", target, -15)
 show_attack_outcome(target, hit, damage)


func show_attack_outcome(target: Vector3, hit: Variant, damage: int) -> void:
 var label := Label3D.new()
 label.name = "AttackOutcome"
 label.text = "NO HP LOST" if hit == null else (
  "MISS" if hit == false else ("NO DAMAGE" if damage <= 0 else "-%d HP" % damage))
 label.modulate = Color(.82,.87,.91) if hit != true else (
  Color(1,.77,.34) if damage <= 0 else Color(1,.49,.32))
 label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
 label.no_depth_test = true
 label.font_size = 30
 label.outline_size = 8
 label.pixel_size = .006
 add_child(label)
 label.global_position = target + Vector3.UP*.48
 var drift := label.create_tween()
 drift.tween_property(label, "position:y", label.position.y + .33, .72)
 drift.tween_property(label, "modulate:a", 0.0, .18)
 drift.tween_callback(label.queue_free)


func tactical_aid(position_value: Vector3) -> void:
 sound("aid", position_value, -13, 1.08)
 for index in 6:
  var angle := index * TAU / 6.0
  var offset := Vector3(cos(angle),0,sin(angle)) * .31
  var base := position_value + offset - Vector3.UP*.30
  line(base, base + Vector3.UP*.22, Color(.24,1,.61), .012, .36)
  motes[-1].velocity = Vector3.UP * .6
