extends RefCounted
## Native checks against the actual camera, AnimationPlayer and atlas regions.
func run_checks(stage,overlay) -> void:
	var old_yaw: float=stage.yaw
	var player: AnimationPlayer=overlay.player
	var cases:=0
	var missing_original:=0
	var expected_original := {"CombatReadyStudy":[0,0,1],"walk":[0,0,3],"MeleeStudy":[0,1,1],"DeathStudy":[0,1,1]}
	for direction in range(8):
		stage.yaw=direction*TAU/8;stage.update_camera()
		for clip in ["CombatReadyStudy","walk","PistolFireStudy","MeleeStudy","DeathStudy"]:
			stage.selected=0;stage.play_clip(clip)
			var manifest: Dictionary=overlay.manifests[clip]
			var animation: Dictionary=manifest.animations[clip.to_lower()]
			var count: int=animation.rows[0].size()
			var points := [0,int(count/2),count-1]
			for sample_index in range(3):
				var sample: int=points[sample_index]
				player.seek(sample/24.0,true);player.pause();overlay.refresh()
				var state: Dictionary=overlay.state
				assert(state.clip==clip and state.sample==sample)
				assert(state.facing==(direction+2)%8)
				assert(state.orbit==(direction+6)%8)
				assert(state.atlas_index==animation.rows[state.orbit][sample])
				assert(state.original_available==(clip!="PistolFireStudy"))
				if not state.original_available:
					assert(not overlay.original.visible);missing_original+=1
				else:assert(state.original_sample==expected_original[clip][sample_index])
				assert(absf(state.projected_reference_px-62.208)<.1)
				cases+=1
	# Unsupported generated Run must not silently use Idle or another action.
	stage.play_clip("run");player.seek(.2,true);overlay.refresh()
	assert(not overlay.state.generated_available and not overlay.picture.visible)
	stage.play_clip("CombatReadyStudy");player.seek(0,true);player.advance(.1);overlay.refresh()
	assert(overlay.state.sample==2)
	stage.play_clip("walk");player.seek(0,true);player.advance(1.125);overlay.refresh()
	assert(overlay.state.sample==3 and overlay.state.original_sample==1)
	stage.play_clip("DeathStudy");player.seek(0,true);player.advance(3.);overlay.refresh()
	assert(overlay.state.sample==58)
	stage.yaw=old_yaw;stage.update_camera();stage.play_clip("CombatReadyStudy")
	player.seek(0,true);player.pause();overlay.refresh()
	var original_size: float=stage.camera.size
	for factor in [1.,3.]:
		stage.camera.size=original_size*factor;overlay.refresh()
		assert(absf(overlay.state.projected_reference_px-62.208/factor)<.1)
		assert(absf(overlay.picture.size.y-192./factor)<.1)
		assert(absf(overlay.original.size.y*float(overlay.original_manifest.reference_height_uv)-62.208/factor)<.1)
	stage.camera.size=original_size
	stage.elevation=.35;stage.update_camera();overlay.refresh()
	assert(not overlay.state.view_supported and not overlay.picture.visible and not overlay.original.visible)
	stage.elevation=.6;stage.update_camera();overlay.refresh()
	var model_path: String=overlay.folder+"../human.glb"
	var hashes: Dictionary={}
	for clip in overlay.manifests:hashes[clip]=FileAccess.get_sha256(overlay.folder+clip+"_atlas.json")
	var proof: Dictionary={"status":"PASS","camera_action_time_cases":cases,"native_clock_advance_cases":3,"original_cadence_preserved":true,"explicit_missing_original_shoot_cases":missing_original,"unsupported_generated_run_hidden":true,"unsupported_elevation_hidden":true,"close_overview_scales_verified":true,"reference_px":overlay.state.projected_reference_px,"atlas_manifest_sha256":hashes,"model_glb_sha256":FileAccess.get_sha256(model_path),"scope":"Actual native action clock, facing projection and region selection; not pixel-identical lighting or artistic acceptance"}
	var file:=FileAccess.open(overlay.folder+"synchronized_comparison131.json",FileAccess.WRITE)
	assert(file!=null);file.store_string(JSON.stringify(proof,"  "));file.close()
	print("GENERATED_ATLAS_SYNCHRONIZATION_PASS ",JSON.stringify(proof))
