extends Node3D
const FOLDER := "E:/CyberCity2085-3d-lab/generated/phase2/modularity166/"
var templates: Array[Node3D] = []

func fail(message: String) -> void:
	push_error(message)
	get_tree().quit(1)

func _ready() -> void:
	var manifest = JSON.parse_string(FileAccess.get_file_as_string(FOLDER + "exports.json"))
	var helmet_only := "--helmet-only" in OS.get_cmdline_user_args()
	var rest_fixed := "--rest-fixed" in OS.get_cmdline_user_args()
	if helmet_only:
		var suffix := "_restfixed" if rest_fixed else ""
		var proof = JSON.parse_string(FileAccess.get_file_as_string(FOLDER + "helmet_transfer" + suffix + ".json"))
		manifest.exports = [{"file": FOLDER + "body_0_helmet" + suffix + ".glb", "sha256": proof.output_sha256}]
	var results: Array = []
	for item in manifest.exports:
		if FileAccess.get_sha256(item.file) != item.sha256:
			fail("Changed GLB source"); return
		var document := GLTFDocument.new()
		var state := GLTFState.new()
		if document.append_from_file(item.file, state) != OK:
			fail("GLB import failed"); return
		var actor := document.generate_scene(state) as Node3D
		add_child(actor)
		templates.append(actor)
		var players := actor.find_children("*", "AnimationPlayer", true, false)
		var skeletons := actor.find_children("*", "Skeleton3D", true, false)
		if players.size() != 1 or skeletons.size() != 1:
			fail("Expected genuine animated skeleton"); return
		var player := players[0] as AnimationPlayer
		var skeleton := skeletons[0] as Skeleton3D
		if helmet_only:
			var modules := actor.find_children("HelmetModule166", "MeshInstance3D", true, false)
			if modules.size() != 1 or modules[0].skin == null or modules[0].get_node_or_null(modules[0].skeleton) != skeleton:
				fail("Transferred helmet lost its actual skeleton binding"); return
		if skeleton.get_bone_count() < 80:
			fail("Lost skeleton bones"); return
		var clips: Array = []
		var signatures: Array = []
		for clip in player.get_animation_list():
			if clip == "RESET": continue
			clips.append(clip)
			var animation := player.get_animation(clip)
			player.play(clip)
			for fraction in [0.0, 0.5, 1.0]:
				player.seek(animation.length * fraction, true)
				player.advance(0)
				var pose: Array = []
				for bone in skeleton.get_bone_count():
					var q := skeleton.get_bone_pose_rotation(bone)
					if not q.is_finite():
						fail("Non-finite native pose"); return
					pose.append(q)
				signatures.append(hash(pose))
		var unique := {}
		for value in signatures: unique[value] = true
		if clips.size() != 5 or unique.size() < 6:
			fail("Missing clips or static native poses"); return
		results.append({"file": item.file, "sha256": item.sha256,
			"bones": skeleton.get_bone_count(), "clips": clips,
			"sampled_poses": signatures.size(), "distinct_poses": unique.size()})
	var file_name := "native_helmet_restfixed.json" if rest_fixed else ("native_helmet.json" if helmet_only else "native_shared_actions.json")
	var file := FileAccess.open(FOLDER + file_name, FileAccess.WRITE)
	file.store_string(JSON.stringify({"status": "PASS", "bodies": results,
		"scope": "Native clips/bones/finite moving poses; no wardrobe or artistic acceptance"}, "  "))
	file.close()
	print("TWO_BODY_NATIVE_SHARED_ACTIONS_PASS ", JSON.stringify(results))
	get_tree().quit()
