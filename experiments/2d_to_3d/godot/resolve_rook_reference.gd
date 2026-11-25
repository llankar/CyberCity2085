extends SceneTree
## Match the production deterministic sprite selection, without changing it.
func _initialize() -> void:
	for agent_name in ["Rook", "ROOK"]:
		var index := (str(agent_name).hash() & 0x7FFFFFFF) % 25 + 1
		print("ROOK_COMBAT_REFERENCE ", agent_name, " agent_diverse_%02d" % index)
	quit()
