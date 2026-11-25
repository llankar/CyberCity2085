extends RefCounted
## Current150 source: preserve source clock offsets and the original sprite cadence.
func run_checks(stage,overlay) -> void:
	var old_yaw: float=stage.yaw
	var player: AnimationPlayer=overlay.player
	# Static source idle loops at its .75s boundary; seeking exactly to end wraps.
	var expected_original:={"Hard stand":[0,0,0],"Walk (1_24)":[0,0,0],"MeleeStudy":[0,1,1],"DeathStudy":[0,1,1]}
	var cases:=0
	var missing:=0
	for direction in range(8):
		stage.yaw=direction*TAU/8;stage.update_camera()
		for clip in overlay.original_actions:
			stage.selected=0;stage.play_clip(clip)
			var manifest: Dictionary=overlay.manifests[clip]
			var animation: Dictionary=manifest.animations[overlay.atlas_actions[clip]]
			var count: int=animation.rows[0].size()
			var points:=[0,int(count/2),count-1]
			for point_index in range(3):
				var sample: int=points[point_index]
				var time:=float(manifest.source_strip_frames[0])/120.+sample/float(animation.fps)
				if manifest.static_pose:time=player.get_animation(clip).length*point_index/2.
				player.seek(time,true);player.pause();overlay.refresh()
				var state: Dictionary=overlay.state
				assert(state.clip==clip and state.sample==(0 if manifest.static_pose else sample))
				assert(state.facing==(direction+2)%8 and state.orbit==(direction+6)%8)
				assert(state.atlas_index==animation.rows[state.orbit][state.sample])
				assert(state.original_available==(clip!="ShootStudy"))
				if state.original_available:assert(state.original_sample==expected_original[clip][point_index],"Original cadence %s point%d t=%.9f got%d expected%d"%[clip,point_index,time,state.original_sample,expected_original[clip][point_index]])
				else:assert(not overlay.original.visible);missing+=1
				assert(absf(state.projected_reference_px-62.208)<.1)
				cases+=1
	stage.play_clip("Walk (1_24)");player.seek(5./120.+.1,true);player.advance(.1);overlay.refresh()
	assert(overlay.state.sample==4 and overlay.state.original_sample==1)
	stage.play_clip("Hard stand");player.seek(.6,true);player.pause();overlay.refresh()
	assert(overlay.state.sample==0 and overlay.state.original_sample==1)
	stage.play_clip("Run (1_18)");player.seek(.2,true);overlay.refresh()
	assert(not overlay.state.generated_available and not overlay.picture.visible)
	stage.play_clip("Walk (1_24)");player.seek(.4,true);player.pause()
	var original_size: float=stage.camera.size
	for factor in [1.,3.]:
		stage.camera.size=original_size*factor;overlay.refresh()
		assert(absf(overlay.state.projected_reference_px-62.208/factor)<.1)
		assert(absf(overlay.picture.size.y-192./factor)<.1)
		assert(absf(overlay.original.size.y*float(overlay.original_manifest.reference_height_uv)-62.208/factor)<.1)
	stage.camera.size=original_size
	stage.elevation=.35;stage.update_camera();overlay.refresh()
	assert(not overlay.state.view_supported and not overlay.picture.visible and not overlay.original.visible)
	stage.elevation=.6;stage.yaw=old_yaw;stage.update_camera();overlay.refresh()
	var hashes:={}
	for clip in overlay.manifests:hashes[clip]=FileAccess.get_sha256(overlay.folder+clip+"_atlas.json")
	var proof:={"status":"PASS","camera_action_time_cases":cases,"missing_original_shoot_cases":missing,
		"source_walk_origin_s":5./120.,"live_clock_advance":true,"unsupported_run_hidden":true,
		"unsupported_elevation_hidden":true,"close_overview_scales_verified":true,"reference_height_m":1.8,
		"reference_px":62.208,"model_glb_sha256":FileAccess.get_sha256(overlay.model_path),
		"atlas_manifest_sha256":hashes,"scope":"Actual native 3D/generated-atlas/original-sprite clock, facing and scaling; no pixel-identical lighting or final art acceptance"}
	var file:=FileAccess.open(overlay.folder+"synchronized_comparison152.json",FileAccess.WRITE)
	assert(file!=null);file.store_string(JSON.stringify(proof,"  "));file.close()
	print("WARDROBE_ATLAS_SYNCHRONIZATION_PASS ",JSON.stringify(proof))
