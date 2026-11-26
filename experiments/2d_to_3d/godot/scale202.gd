extends Node3D
## Native side-by-side visual comparison; no campaign and no new animation tests.
const LAB:="E:/CyberCity2085-3d-lab/"
const SUBJECTS:=[
 ["Rook retained","sole_skin162/human.glb","Hard stand","agent_samurai"],
 ["Hunyuan candidate","rig177/human.glb","Idle","agent_samurai"],
 ["Helmeted raider","modularity166/body_0_helmet_restfixed.glb","Rocketbox_Idle","enemy_raider_grunt"],
 ["Painted combat robot","robot193/robot_actions.glb","Idle","enemy_corp_samurai_robot_heavy"]]
func caption(parent: Node,text: String,at: Vector2,size_value:=18) -> void:
	var label:=Label.new();label.text=text;label.position=at;label.add_theme_font_size_override("font_size",size_value);parent.add_child(label)
func _ready() -> void:
	get_window().size=Vector2i(1920,720)
	var canvas:=CanvasLayer.new();add_child(canvas)
	var background:=ColorRect.new();background.color=Color(.065,.08,.095);background.size=Vector2(1920,720);canvas.add_child(background)
	caption(canvas,"CyberCity 2085 | Sprites and current 3D models",Vector2(24,12),20)
	for column in 4:
		caption(canvas,SUBJECTS[column][0],Vector2(column*480+24,52),21)
		for row in 2:
			var height_value:float=[41.0,62.0][row]
			var viewport:=SubViewport.new();viewport.size=Vector2i(480,300);viewport.own_world_3d=true;add_child(viewport)
			var doc:=GLTFDocument.new();var state:=GLTFState.new();var asset:String=SUBJECTS[column][1]
			assert(doc.append_from_file(LAB+"generated/phase2/"+asset,state)==OK)
			var actor:=doc.generate_scene(state);viewport.add_child(actor)
			var player:=actor.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
			assert(player.has_animation(SUBJECTS[column][2]));player.play(SUBJECTS[column][2]);player.seek(.4,true);player.active=false
			var world:=WorldEnvironment.new();world.environment=Environment.new();world.environment.background_mode=Environment.BG_COLOR;world.environment.background_color=background.color
			world.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;world.environment.ambient_light_color=Color.WHITE;world.environment.ambient_light_energy=.65;viewport.add_child(world)
			var lamp:=DirectionalLight3D.new();lamp.rotation_degrees=Vector3(-50,-30,0);lamp.light_energy=1.2;viewport.add_child(lamp)
			var camera:=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;viewport.add_child(camera)
			camera.position=Vector3(3,3.8,5.5);camera.look_at(Vector3(0,.9,0));camera.size=8
			var nominal:=2.4 if column==3 else 1.8
			var requested:=height_value*1.65 if column==3 else height_value
			await RenderingServer.frame_post_draw
			var measured:=absf(camera.unproject_position(Vector3(0,nominal,0)).y-camera.unproject_position(Vector3.ZERO).y)
			camera.size*=measured/requested
			var display:=TextureRect.new();display.texture=viewport.get_texture();display.position=Vector2(column*480,100+row*310);display.size=Vector2(480,300);canvas.add_child(display)
			var manifest=JSON.parse_string(FileAccess.get_file_as_string("res://../../../assets/combat_visual/animations/"+SUBJECTS[column][3]+".json"))
			var atlas:=Image.load_from_file(ProjectSettings.globalize_path("res://../../../"+manifest.texture))
			var tile:=atlas.get_region(Rect2i(0,0,manifest.frame_size[0],manifest.frame_size[1]))
			var reference:=TextureRect.new();reference.texture=ImageTexture.create_from_image(tile);reference.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
			var pixels:=requested/float(manifest.reference_height_uv);reference.size=Vector2.ONE*pixels
			var feet:=camera.unproject_position(Vector3.ZERO)+display.position
			reference.position=feet+Vector2(-100,0)-reference.size*Vector2(manifest.anchor_uv[0],manifest.anchor_uv[1]);canvas.add_child(reference)
			caption(canvas,"2D       3D   |   "+str(int(height_value))+" px humain",Vector2(column*480+70,360+row*310),15)
	await RenderingServer.frame_post_draw;await RenderingServer.frame_post_draw
	var out:=LAB+"generated/phase2/scale202/";DirAccess.make_dir_recursive_absolute(out)
	get_viewport().get_texture().get_image().save_png(out+"comparison_native.png")
	FileAccess.open(out+"scope.txt",FileAccess.WRITE).store_string("Current models, nominal1.8m humans/2.4m robot. Human41/62px; robot1.65sprite multiplier. Actual first idle atlas tile; neutral scene. No full animation or artistic acceptance implied.")
	print("SCALE202_CAPTURED");get_tree().quit()
