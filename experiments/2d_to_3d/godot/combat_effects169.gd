extends Node3D
## Visible effects and existing sound playback for the isolated showcase.
var motes: Array[Dictionary] = []
var audio_events: Array[Dictionary] = []
var sound_streams: Dictionary[String, AudioStreamWAV] = {}
var clock := 0.0
const SOUNDS := {"pistol":"weapons/fire_pistol_01.wav","laser":"weapons/fire_laser_cc0_01.wav","step":"movement/step_concrete_cc0_01.wav",
	"metal":"combat/impact_metal_cc0_01.wav","hit":"combat/impact_organic_cc0_01.wav",
	"melee":"combat/melee_cc0_01.wav","explode":"combat/explosion_small_cc0_01.wav",
	"psi":"technology/shield_cc0_01.wav","aid":"technology/terminal_cc0_01.wav"}

func material(color: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new(); mat.albedo_color = color
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.emission_enabled = true; mat.emission = color
	return mat

func sound(key: String, position_value: Vector3, gain := -10.0, pitch := 1.0) -> void:
	var path := ProjectSettings.globalize_path("res://../../../assets/audio/overhaul/"+SOUNDS[key])
	var stream: AudioStreamWAV = sound_streams.get(key)
	if stream == null:
		stream = AudioStreamWAV.load_from_file(path)
		if stream == null:
			push_error("Missing showcase sound " + path)
			return
		sound_streams[key] = stream
	var player := AudioStreamPlayer3D.new(); player.stream = stream; player.volume_db = gain
	player.pitch_scale = pitch
	player.unit_size=20
	add_child(player); player.global_position = position_value; player.play()
	player.finished.connect(player.queue_free)
	audio_events.append({"time":clock,"file":path,"gain_db":gain})

func line(a: Vector3, b: Vector3, color: Color, radius: float, life: float) -> MeshInstance3D:
	var node := MeshInstance3D.new(); var mesh := CylinderMesh.new()
	mesh.top_radius = radius; mesh.bottom_radius = radius; mesh.height = maxf(.001,a.distance_to(b)); mesh.radial_segments = 6
	node.mesh = mesh; node.material_override = material(color)
	add_child(node); node.global_position = (a+b)/2
	node.quaternion = Quaternion(Vector3.UP,(b-a).normalized())
	motes.append({"node":node,"life":life,"velocity":Vector3.ZERO})
	return node

func spark(at: Vector3, metal := false) -> void:
	for index in 8:
		var angle := index*2.399
		var direction := Vector3(cos(angle),.5+float(index%3)*.3,sin(angle)).normalized()
		var node := line(at,at+direction*.12,Color(1,.48,.08) if metal else Color(.75,.1,.05),.009,.3)
		motes[-1].velocity = direction*2

func shot(from: Vector3, to: Vector3, metal := false, laser := false) -> void:
	var color := Color(.1,.8,1) if laser else Color(1,.7,.25)
	line(from,to,color,.008,.06)
	line(from,from+(to-from).normalized()*.24,color,.045,.075)
	spark(to,metal); sound("laser" if laser else "pistol",from,-8)
	sound("metal" if metal else "hit",to,-15)

func psychic(from: Vector3, to: Vector3, hit := true) -> void:
	var previous := from
	for index in range(1,19):
		var fraction := float(index)/18
		var point := from.lerp(to,fraction)
		point += Vector3(sin(index*7.1+clock*3),cos(index*5.3),sin(index*3.7))*.13*sin(fraction*PI)
		line(previous,point,Color(.65,.15,1) if index%2 else Color(.12,.75,1),.018,.3)
		previous = point
	if hit:spark(to,true)
	sound("psi",from,-12)

func destroy_robot(model: Node3D) -> void:
	var center := model.global_position+Vector3(0,1,0)
	for index in 4:
		spark(center+Vector3(0,index*.15,0),true)
	var pieces := model.find_children("*","MeshInstance3D",true,false)
	for index in mini(6,pieces.size()):
		var piece := MeshInstance3D.new(); piece.mesh = pieces[index].mesh
		piece.scale = Vector3.ONE*.22
		add_child(piece);piece.global_position = center
		motes.append({"node":piece,"life":2.0,"velocity":Vector3(sin(index*2.4)*2,2+index*.2,cos(index*2.4)*2)})
	sound("explode",center,-7)

func step(delta: float, time_value: float) -> void:
	clock = time_value
	for index in range(motes.size()-1,-1,-1):
		var item: Dictionary = motes[index]; item.life -= delta
		if item.life <= 0:
			item.node.queue_free();motes.remove_at(index)
		else:
			item.node.position += item.velocity*delta
			if item.velocity.length_squared()>0: item.velocity.y -= delta*4
