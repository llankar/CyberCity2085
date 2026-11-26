extends "res://cannon193.gd"
## Match the authored stance displacement to the actual path speed.
const ROBOT_STRIDE := .28
const ROBOT_DUTY := .6
const ROBOT_PERIOD := 1.2
var gait_recorded := false
func _ready() -> void:
	super._ready()
	delivery_folder=ROOT+"gait194/";DirAccess.make_dir_recursive_absolute(delivery_folder)
func travel(index: int,from: Vector3,to: Vector3,start: float,end: float,walk: String,t: float) -> void:
	super.travel(index,from,to,start,end,walk,t)
	if index==2 and t>start and t<end:
		var nominal_speed:=ROBOT_STRIDE/(ROBOT_DUTY*ROBOT_PERIOD)
		var path_speed:=from.distance_to(to)/(end-start)
		players[index].speed_scale=path_speed/nominal_speed
		if not gait_recorded:
			gait_recorded=true
			var report:={"path_speed_m_s":path_speed,"authored_stance_speed_m_s":nominal_speed,"cycle_speed_scale":players[index].speed_scale,"scope":"authored gait cadence; foot contacts still require visible review"}
			FileAccess.open(delivery_folder+"gait.json",FileAccess.WRITE).store_string(JSON.stringify(report))
			print("GAIT194_CADENCE ",report)
