extends "res://combat_effects169.gd"
## Local impact finish: short flashes, soft smoke and a grounded wreck mark.
var clouds: Array[Dictionary] = []
var smoke_shader: Shader

func _ready() -> void:
	smoke_shader=Shader.new()
	smoke_shader.code="""shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, blend_mix;
uniform vec4 tint : source_color = vec4(0.12,0.13,0.14,0.5);
uniform float fade = 1.0;
uniform float seed = 0.0;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p);vec2 f=fract(p);f=f*f*(3.0-2.0*f);
return mix(mix(hash(i),hash(i+vec2(1.,0.)),f.x),mix(hash(i+vec2(0.,1.)),hash(i+vec2(1.,1.)),f.x),f.y);}
void fragment(){float n=noise(UV*7.0+seed)*0.65+noise(UV*17.0-seed)*0.35;
float edge=1.0-smoothstep(0.16,0.52,length(UV-vec2(0.5)));
ALBEDO=tint.rgb;ALPHA=edge*mix(0.25,1.0,n)*tint.a*fade;}
"""
	print("IMPACT179_READY soft procedural smoke and short local flashes")

func puff(at: Vector3, size_value: float, duration: float, velocity: Vector3, ground := false) -> void:
	var node:=MeshInstance3D.new();var quad:=QuadMesh.new();quad.size=Vector2.ONE*size_value;node.mesh=quad
	var paint:=ShaderMaterial.new();paint.shader=smoke_shader
	paint.set_shader_parameter("seed",float(clouds.size())*1.71+clock)
	paint.set_shader_parameter("tint",Color(.035,.03,.025,.6) if ground else Color(.30,.32,.34,.5))
	node.material_override=paint;add_child(node);node.global_position=at
	if ground:node.rotation_degrees.x=-90
	clouds.append({"node":node,"life":duration,"duration":duration,"velocity":velocity,"ground":ground})

func flash(at: Vector3, color: Color, energy: float, duration: float) -> void:
	var light:=OmniLight3D.new();light.light_color=color;light.light_energy=energy;light.omni_range=3.5
	add_child(light);light.global_position=at
	motes.append({"node":light,"life":duration,"velocity":Vector3.ZERO,"flash":energy,"duration":duration})

func shot(from: Vector3, to: Vector3, metal := false, laser := false) -> void:
	super.shot(from,to,metal,laser)
	flash(from,Color(.15,.7,1) if laser else Color(1,.57,.16),1.5,.075)
	flash(to,Color(1,.5,.12),.65,.1)
	if metal:puff(to,.35,.55,Vector3(.08,.25,0))

func destroy_robot(model: Node3D) -> void:
	super.destroy_robot(model)
	var center:=model.global_position+Vector3(0,1.2,0)
	flash(center,Color(1,.45,.08),4,.18)
	for index in 7:
		var angle:=float(index)*2.399
		puff(center+Vector3(cos(angle)*.2,float(index%3)*.12,sin(angle)*.2),
			.85,2.1+float(index%3)*.3,Vector3(cos(angle)*.13,.45,sin(angle)*.13))
	puff(model.global_position+Vector3(0,.035,0),1.6,12,Vector3.ZERO,true)

func step(delta: float, time_value: float) -> void:
	super.step(delta,time_value)
	for item in motes:
		if item.has("flash"):
			(item.node as OmniLight3D).light_energy=float(item.flash)*float(item.life)/float(item.duration)
		elif item.velocity.length_squared()>0 and item.node.position.y<.045:
			item.node.position.y=.045
			item.velocity=Vector3(item.velocity.x*.6,absf(item.velocity.y)*.3,item.velocity.z*.6)
	var camera:=get_viewport().get_camera_3d()
	for index in range(clouds.size()-1,-1,-1):
		var item: Dictionary=clouds[index];item.life-=delta
		if item.life<=0:
			item.node.queue_free();clouds.remove_at(index);continue
		item.node.position+=item.velocity*delta
		var age:=1.0-float(item.life)/float(item.duration)
		item.node.material_override.set_shader_parameter("fade",minf(1,float(item.life)*2))
		if not item.ground:
			item.node.scale=Vector3.ONE*(1+age*.9)
			if camera:item.node.look_at(camera.global_position,Vector3.UP)
