extends RefCounted
## Versioned local transport; campaign saves remain exclusively Python-owned.
static func publish(path: String, payload: Dictionary) -> bool:
	if path.is_empty(): return false
	if DirAccess.make_dir_recursive_absolute(path.get_base_dir()) != OK: return false
	var temporary := path + ".tmp"
	var file := FileAccess.open(temporary, FileAccess.WRITE)
	if file == null: return false
	file.store_string(JSON.stringify(payload, "  "))
	file.close()
	return DirAccess.rename_absolute(temporary, path) == OK

static func status(session: Dictionary, event: String, ready: bool = true) -> bool:
	if session.is_empty(): return false
	return publish(str(session.get("status_path", "")), {
		"protocol_version": 2, "session_id": session.get("session_id", ""),
		"mission_id": session.get("mission_id", ""), "event": event,
		"ready": ready, "monotonic_ms": Time.get_ticks_msec()})
