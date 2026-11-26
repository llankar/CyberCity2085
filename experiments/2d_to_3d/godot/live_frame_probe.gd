extends Node
## Optional short native-frame measurement. No images or video encoded by this probe.
var startup_ms:=0.0
var tag:="live"
var previous_us:=0
var samples:Array[float]=[]
var spikes:Array[Dictionary]=[]
func _ready() -> void:
 previous_us=Time.get_ticks_usec()
 RenderingServer.frame_post_draw.connect(sample_frame)
func sample_frame() -> void:
 var now:=Time.get_ticks_usec()
 var ms:=float(now-previous_us)/1000.0;previous_us=now
 samples.append(ms)
 if ms>33.333:spikes.append({"simulation_time":get_parent().get("time_value"),"ms":ms})
func _exit_tree() -> void:
 if samples.is_empty():return
 var ordered:=samples.duplicate();ordered.sort()
 var total:=0.0
 for ms in samples:total+=ms
 var report={"samples":samples.size(),"startup_ms":startup_ms,"mean_fps":1000.0*samples.size()/total,
  "median_ms":ordered[int((ordered.size()-1)*.5)],"p95_ms":ordered[int((ordered.size()-1)*.95)],
  "p99_ms":ordered[int((ordered.size()-1)*.99)],"max_ms":ordered[-1],"over_33ms":spikes.size(),
  "spikes":spikes,"movie_mode":OS.has_feature("movie"),"scope":"Current native showcase post-draw intervals; startup separate; not production/campaign performance"}
 var path="E:/CyberCity2085-3d-lab/generated/phase2/library227/live_"+tag+".json"
 FileAccess.open(path,FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print("LIVE_FRAME_PROBE ",tag," fps=",report.mean_fps," p95=",report.p95_ms," max=",report.max_ms," >33ms=",spikes.size())
