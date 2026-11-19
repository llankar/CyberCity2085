shader_type canvas_item;
// Holographic panel overlay — slow vertical scan line sweep.

uniform float scan_speed : hint_range(0.05, 2.0) = 0.24;
uniform float scan_width : hint_range(0.01, 0.3) = 0.07;
uniform float scan_alpha : hint_range(0.0, 0.5)  = 0.11;
uniform vec3  scan_color : source_color           = vec3(0.1, 0.95, 0.72);

void fragment() {
	vec4  base = texture(TEXTURE, UV);
	float t    = fract(TIME * scan_speed);
	float dist = abs(UV.y - t);
	float scan = smoothstep(scan_width, 0.0, dist) * scan_alpha;
	COLOR = base + vec4(scan_color * scan, 0.0);
}
