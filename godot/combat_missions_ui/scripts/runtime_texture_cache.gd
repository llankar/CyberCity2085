extends RefCounted
## Bounded application cache. Source images and geometry are never altered.
const LIMIT_BYTES := 128 * 1024 * 1024
static var _textures := {}
static var _order: Array[String] = []
static var _bytes := 0

static func load_texture(path: String) -> Texture2D:
	if not FileAccess.file_exists(path):return null
	var modified:=FileAccess.get_modified_time(path)
	if _textures.has(path):
		if _textures[path].modified==modified:
			_order.erase(path);_order.append(path)
			return _textures[path].texture
		_remove(path)
	var image:=Image.load_from_file(path)
	if image==null:return null
	var texture:=ImageTexture.create_from_image(image)
	var bytes:=image.get_width()*image.get_height()*4
	if bytes<=LIMIT_BYTES:
		while _bytes+bytes>LIMIT_BYTES and not _order.is_empty():_remove(_order[0])
		_textures[path]={"texture":texture,"bytes":bytes,"modified":modified}
		_order.append(path);_bytes+=bytes
	return texture

static func _remove(path: String) -> void:
	if _textures.has(path):_bytes-=int(_textures[path].bytes);_textures.erase(path)
	_order.erase(path)

static func clear() -> void:
	_textures.clear();_order.clear();_bytes=0
