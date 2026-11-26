extends RefCounted
## Reuses the retained combat169 segment/AABB fade method for independent reviews.
var groups:Array=[]
var actors:Array=[]
var camera:Camera3D
func configure(environment:Node3D,targets:Array,view:Camera3D) -> void:
 actors=targets
 camera=view
 for group in environment.find_children("Occludable_*","Node3D",true,false):
  var bounds:=AABB()
  var first:=true
  var materials:Array[StandardMaterial3D]=[]
  for mesh in group.find_children("*","MeshInstance3D",true,false):
   var box:AABB=mesh.global_transform*mesh.get_aabb()
   bounds=box if first else bounds.merge(box)
   first=false
   for surface in mesh.mesh.get_surface_count():
    var original=mesh.get_active_material(surface)
    if original is StandardMaterial3D:
     var copy=original.duplicate() as StandardMaterial3D
     mesh.set_surface_override_material(surface,copy)
     materials.append(copy)
  if not first:groups.append({"bounds":bounds,"materials":materials,"fade":1.0})
func update(delta:float) -> int:
 var hidden:=0
 for group in groups:
  var blocked:=false
  for actor in actors:
   if group.bounds.intersects_segment(camera.global_position,actor.global_position+Vector3(0,1,0))!=null:blocked=true
  if blocked:hidden+=1
  group.fade=move_toward(float(group.fade),.2 if blocked else 1.0,delta*4)
  for material in group.materials:
   material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA if group.fade<.99 else BaseMaterial3D.TRANSPARENCY_DISABLED
   material.albedo_color.a=group.fade
 return hidden
