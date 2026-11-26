extends "res://street211.gd"
const PACE:=1.7
var captured_phases:={}
func simulation_delta(delta: float) -> float:
 return super.simulation_delta(delta)*PACE
func presentation_time(simulation_time: float) -> float:
 return simulation_time/PACE
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"tempo212/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 print("TEMPO212_READY scene clock1.7; audio pitch unchanged; no video retiming")
func capture() -> void:
 if not capturing:return
 capturing=false
 # Interactive playback must not stall on GPU readback/PNG compression.
 # Keep screenshots for explicit still capture and native movie/frame exports.
 if not record and not OS.has_feature("movie") and not ("--capture-stills" in OS.get_cmdline_user_args()):return
 # Keep gallery phase identifiers; filenames are simulation phases, not video frames.
 var phases:={30:"clean_0030",120:"preview",145:"cannon_0145",146:"cannon_0146",147:"cannon_0147",254:"clean_0254",460:"clean_0460",590:"clean_0590",603:"impact_0603",609:"impact_0609",630:"clean_0630",750:"clean_0750"}
 for phase in phases:
  if time_value>=float(phase)/30 and not captured_phases.has(phase):
   captured_phases[phase]=true
   get_viewport().get_texture().get_image().save_png(delivery_folder+phases[phase]+".png")
