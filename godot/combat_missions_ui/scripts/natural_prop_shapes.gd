extends RefCounted
## Reusable object components in an authored local frame, never collision bounds.
const HEIGHTS := {"sofa":.30,"armchair":.32,"table":.28,"bench":.18,"console":.28,"crate":.19,"machine":.30,"wall":.26,"partition":.20}

static func uv(entry: Dictionary, p: Vector2) -> Vector2:
	return Vector2(entry.origin[0],entry.origin[1])+Vector2(entry.axis_u[0],entry.axis_u[1])*p.x+Vector2(entry.axis_v[0],entry.axis_v[1])*p.y

static func outline(rect: Rect2, bevel: float=.07) -> PackedVector2Array:
	return preload("res://scripts/environment_depth_legacy.gd").beveled_uv(rect,bevel)

static func pieces(entry: Dictionary) -> Array[Dictionary]:
	var family := str(entry.family)
	var h := float(entry.get("height",HEIGHTS.get(family,.2)))
	var result: Array[Dictionary]=[]
	if family in ["sofa","armchair"]:
		# The open seat, back and armrests are distinct shapes, not a raised rug.
		for x in [.10,.82]:
			for y in [.16,.84]:result.append(piece("foot",Rect2(x,y,.06,.07),0,.035,"metal",false))
		result.append(piece("seat_frame",Rect2(.06,.23,.88,.70),.035,h*.40,str(entry.material)))
		var cushions := int(entry.get("cushions",3)) if family=="sofa" else 1
		for i in range(cushions):
			result.append(piece("cushion",Rect2(.16+i*.68/cushions,.32,.68/cushions-.012,.55),h*.40,h*.56,"fabric"))
		result.append(piece("back",Rect2(.08,.03,.84,.23),.035,h,"fabric"))
		for x in [.02,.86]:result.append(piece("arm",Rect2(x,.20,.12,.75),.035,h*.77,"fabric"))
	elif family in ["table","bench"]:
		for x in [.10,.82]:
			for y in [.10,.82]:result.append(piece("leg",Rect2(x,y,.075,.075),0,h-.035,"metal",false))
		result.append(piece("top",Rect2(.02,.02,.96,.96),h-.035,h,str(entry.material)))
	elif family=="console":
		result.append(piece("cabinet",Rect2(.09,.16,.82,.78),0,h*.64,"metal"))
		var screen:=piece("sloped_screen",Rect2(.04,.04,.92,.70),h*.64,h,"metal")
		screen["slope"]=h*.20
		result.append(screen)
	elif family=="machine":
		for x in [.06,.82]:result.append(piece("mount",Rect2(x,.16,.12,.68),0,.045,"metal",false))
		var body:=piece("cylinder",Rect2(.06,.02,.88,.96),.045,h,"metal")
		body["polygon"]=PackedVector2Array([Vector2(.27,.02),Vector2(.73,.02),Vector2(.94,.15),Vector2(.94,.85),Vector2(.73,.98),Vector2(.27,.98),Vector2(.06,.85),Vector2(.06,.15)])
		result.append(body)
	else:
		# Only an explicitly authored crate or narrow architectural cap reaches here.
		result.append(piece(family,Rect2(.02,.02,.96,.96),0,h,str(entry.material)))
	return result

static func piece(role: String, rect: Rect2, low: float, high: float, material: String, textured: bool=true) -> Dictionary:
	return {"role":role,"polygon":outline(rect,.18 if role in ["arm","back","cushion"] else .055),"low":low,"high":high,"material":material,"textured":textured}
