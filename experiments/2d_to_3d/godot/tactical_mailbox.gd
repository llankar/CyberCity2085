extends RefCounted
## One outstanding command. Python publishes the only authoritative snapshot.
var directory: String
var sequence := 0
var pending := false
var state: Dictionary = {}
var message := ""

func _init(session_directory: String) -> void:
 directory = session_directory

func refresh() -> bool:
 var path := directory.path_join("reply.json")
 if not FileAccess.file_exists(path):
  return false
 var parser := JSON.new()
 if parser.parse(FileAccess.get_file_as_string(path)) != OK:
  return false
 var reply: Variant = parser.data
 if not reply is Dictionary or not reply.get("state") is Dictionary:
  return false
 if int(reply.get("sequence", -1)) != sequence:
  return false
 state = reply.state
 message = str(reply.get("message", ""))
 pending = false
 return true

func send(command: Dictionary) -> Error:
 if pending or state.is_empty():
  return ERR_BUSY
 var next := sequence + 1
 var path := directory.path_join("command-%d.json" % next)
 var temporary := path + ".tmp"
 var file := FileAccess.open(temporary, FileAccess.WRITE)
 if file == null:
  return FileAccess.get_open_error()
 file.store_string(JSON.stringify(command))
 file.close()
 var error := DirAccess.rename_absolute(temporary, path)
 if error == OK:
  sequence = next
  pending = true
 return error
