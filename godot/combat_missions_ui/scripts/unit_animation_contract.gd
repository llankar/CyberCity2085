extends RefCounted
## Validate resources once at load; incomplete action coverage is allowed.
static func valid(data: Dictionary, image: Image, root: String) -> bool:
	root=root.simplify_path().trim_suffix("/")
	if image==null:return false
	var size: Variant=data.get("frame_size",[])
	if not size is Array or size.size()!=2:return false
	var w:=int(size[0]);var h:=int(size[1])
	if w<=0 or h<=0 or image.get_width()%w!=0 or image.get_height()%h!=0:return false
	var clips: Variant=data.get("animations",{})
	if not clips is Dictionary or not clips.has("idle"):return false
	var total: int=(image.get_width()/w)*(image.get_height()/h)
	for clip: Variant in clips.values():
		if not clip is Dictionary:return false
		var rows: Variant=clip.get("rows",[])
		if not rows is Array or rows.size()!=8 or float(clip.get("fps",0))<=0 or float(clip.get("fps",0))>60:return false
		for row: Variant in rows:
			if not row is Array or row.is_empty():return false
			for frame: Variant in row:
				if not (frame is int or frame is float) or float(frame)!=float(int(frame)) or int(frame)<0 or int(frame)>=total:return false
	if data.has("anchor_uv"):
		var anchor: Variant=data.anchor_uv
		if not anchor is Array or anchor.size()!=2:return false
		for value: Variant in anchor:
			if not (value is int or value is float) or float(value)<0 or float(value)>1:return false
	if data.has("source_image"):
		var path:=root.path_join(str(data.source_image)).simplify_path()
		if not path.begins_with(root.simplify_path()+"/assets/units/"):return false
		if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=str(data.get("source_sha256","")):return false
	return true
