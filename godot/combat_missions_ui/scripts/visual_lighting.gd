extends Node2D
## Cached local pools at emissive pixels in the real art. No global color wash.
var points: Array[Dictionary] = []
var glow: Texture2D
var board
var quality := 2
var profile := "city"
var _elapsed := 0.0
var _redraw_clock := 0.0
static var _sample_cache: Dictionary = {}
static var _glow: Texture2D
const PROFILES := {
	"city": {"tint":Color(.12,.8,1), "mix":.18, "radius":3.8, "energy":.75, "reflection":.14},
	"interior": {"tint":Color(.17,.9,1), "mix":.24, "radius":3.0, "energy":.62, "reflection":.08},
	"industrial": {"tint":Color(1,.54,.15), "mix":.40, "radius":4.0, "energy":.82, "reflection":.10},
	"wasteland": {"tint":Color(1,.73,.40), "mix":.48, "radius":4.5, "energy":.40, "reflection":.025},
}

static func profile_for(path: String, weather: String) -> String:
	var filename := path.get_file().to_lower()
	if "industrial" in filename or "factory" in filename or "refinery" in filename or "foundry" in filename or "warehouse" in filename: return "industrial"
	if weather == "interior": return "interior"
	if weather == "dust": return "wasteland"
	return "city"

func configure(texture: Texture2D, battlefield, weather: String, map_path: String = "") -> void:
	board = battlefield
	points.clear()
	profile = profile_for(map_path,weather)
	if texture == null: return
	var key := texture.get_instance_id()
	if not _sample_cache.has(key):
		var source := texture.get_image()
		if source == null: return
		source.resize(96,54,Image.INTERPOLATE_BILINEAR)
		var candidates: Array[Dictionary] = []
		for y in range(2,52):
			for x in range(2,94):
				var color := source.get_pixel(x,y)
				if color.v > .52 and color.s > .27:
					candidates.append({"uv":Vector2(x/96.0,y/54.0),"color":color,"energy":color.v*color.s})
		candidates.sort_custom(func(a,b): return a.energy > b.energy)
		var samples: Array[Dictionary] = []
		for candidate: Dictionary in candidates:
			var separated := true
			for existing: Dictionary in samples:
				if candidate.uv.distance_to(existing.uv) < .12:
					separated = false
					break
			if separated: samples.append(candidate)
			if samples.size() >= 12: break
		if _sample_cache.size() >= 8: _sample_cache.clear()
		_sample_cache[key] = samples
	points.assign(_sample_cache[key])
	glow = glow_texture()
	var mat := CanvasItemMaterial.new()
	mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	material = mat
	queue_redraw()

static func glow_texture() -> Texture2D:
	if _glow == null:
		var image := Image.create(64,64,false,Image.FORMAT_RGBA8)
		for y in range(64):
			for x in range(64):
				var distance := Vector2(x-31.5,y-31.5).length()/32.0
				image.set_pixel(x,y,Color(1,1,1,pow(maxf(0,1-distance),2)*.38))
		_glow = ImageTexture.create_from_image(image)
	return _glow

func _process(delta: float) -> void:
	if not visible or quality == 0: return
	_elapsed += delta
	_redraw_clock += delta
	if _redraw_clock >= 1.0/20.0:
		_redraw_clock = 0
		queue_redraw()

func _draw() -> void:
	if glow == null or quality == 0: return
	var style: Dictionary = PROFILES[profile]
	for i in range(mini(points.size(),12 if quality == 2 else 6)):
		var point: Dictionary = points[i]
		var center: Vector2 = board.uv_to_world(point.uv)
		var radius: float = board.iso_tw*float(style.radius)
		var color: Color = point.color.lerp(style.tint,float(style.mix))
		color.a = float(style.energy)*(.94+.06*sin(_elapsed*1.3+i*1.7))
		draw_texture_rect(glow,Rect2(center-Vector2(radius,radius*.6),Vector2(radius*2,radius*1.2)),false,color)
		if quality == 2:
			# Broken, subdued reflections directly below the sampled light.
			for strip in range(3):
				var y: float = (strip+1)*board.iso_th*.35
				var length: float = radius*(.34-strip*.065)
				draw_line(center+Vector2(-length,y),center+Vector2(length,y),Color(color,float(style.reflection)/(strip+1)),maxf(.5,board.iso_th*.08),true)
