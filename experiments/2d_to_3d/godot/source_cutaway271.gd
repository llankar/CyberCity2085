extends RefCounted
## Retained segment/AABB detection with crisp cutaway, avoiding layered ghosts.
var groups:Array=[]
var actors:Array=[]
var camera:Camera3D
var project_view_rays := false
func configure(environment:Node3D,targets:Array,view:Camera3D,project_rays := false) -> void:
 actors=targets
 camera=view
 project_view_rays=project_rays
 for group in environment.find_children("Occludable_*","Node3D",true,false):
  var bounds:=AABB()
  var first:=true
  var meshes:Array=[]
  for mesh in group.find_children("*","MeshInstance3D",true,false):
   var box:AABB=mesh.global_transform*mesh.get_aabb()
   bounds=box if first else bounds.merge(box)
   first=false
   meshes.append({"node":mesh,"original_visible":mesh.visible})
  if not first:groups.append({"bounds":bounds,"meshes":meshes,"hidden":false,"clear_seconds":0.0})
func update(delta:float) -> int:
 var hidden:=0
 var rays: Array[Dictionary] = []
 for actor in actors:
  var target: Vector3 = actor.global_position+Vector3(0,1,0)
  var origin := camera.global_position
  if project_view_rays and camera.projection == Camera3D.PROJECTION_ORTHOGONAL:
   origin = camera.project_ray_origin(camera.unproject_position(target))
  rays.append({"origin":origin,"target":target})
 for group in groups:
  var blocked:=false
  for ray in rays:
   if group.bounds.intersects_segment(ray.origin,ray.target)!=null:
    blocked=true
    break
  group.clear_seconds=0.0 if blocked else float(group.clear_seconds)+delta
  var cut:bool=blocked or (bool(group.hidden) and float(group.clear_seconds)<.12)
  if cut!=bool(group.hidden):
   for entry in group.meshes:entry.node.visible=bool(entry.original_visible) and not cut
   group.hidden=cut
  if group.hidden:hidden+=1
 return hidden
