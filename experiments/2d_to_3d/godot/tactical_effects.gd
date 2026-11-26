extends "res://combat_effects169.gd"


func tactical_attack(action: String, from: Vector3, target: Vector3, hit: bool,
  damage: int, precision: bool) -> void:
 var travel := target - from
 var miss_offset := travel.normalized().cross(Vector3.UP) * .65 + Vector3.UP * .21
 var destination := target if hit else target + miss_offset
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
 if hit and damage > 0:
  spark(target, action == "psi")
  sound("hit", target, -15)


func tactical_aid(position_value: Vector3) -> void:
 sound("aid", position_value, -13, 1.08)
 for index in 6:
  var angle := index * TAU / 6.0
  var offset := Vector3(cos(angle),0,sin(angle)) * .31
  var base := position_value + offset - Vector3.UP*.30
  line(base, base + Vector3.UP*.22, Color(.24,1,.61), .012, .36)
  motes[-1].velocity = Vector3.UP * .6
