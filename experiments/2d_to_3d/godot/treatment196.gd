extends "res://market195.gd"
## Treat from the patient's side rather than leaning face-to-face.
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"treatment196/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 medical_case.position=Vector3(.9,.02,2.3)
func travel(index: int,from: Vector3,to: Vector3,start: float,end: float,walk: String,t: float) -> void:
 if index==3 and start==20:to=Vector3(.1,0,2.65)
 super.travel(index,from,to,start,end,walk,t)
func face(index: int,point: Vector3) -> void:
 if index==0 and time_value>=22:point=Vector3(2,0,1.5)
 super.face(index,point)
