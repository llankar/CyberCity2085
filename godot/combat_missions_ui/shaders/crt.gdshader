shader_type canvas_item;

// Sample the already-rendered frame with nearest to avoid extra softening
uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_nearest;
uniform float scan_intensity : hint_range(0.0, 0.08) = 0.018;
uniform float aberration     : hint_range(0.0, 0.002) = 0.0002;
uniform float vignette       : hint_range(0.0, 1.0)   = 0.18;
uniform float scan_scale     : hint_range(0.5, 4.0)   = 1.4;
// Explicit height avoids VIEWPORT_SIZE which is unavailable in gl_compatibility
uniform float screen_height  : hint_range(240.0, 2160.0) = 720.0;

void fragment() {
	vec2 uv = SCREEN_UV;

	// Very subtle chromatic aberration — barely visible colour fringe, no blur
	float r     = texture(SCREEN_TEXTURE, uv + vec2(aberration, 0.0)).r;
	float g     = texture(SCREEN_TEXTURE, uv).g;
	float b_val = texture(SCREEN_TEXTURE, uv - vec2(aberration, 0.0)).b;
	COLOR = vec4(r, g, b_val, 1.0);

	// Gentle scanlines
	float scan = sin(uv.y * screen_height * scan_scale) * scan_intensity;
	COLOR.rgb -= scan;

	// Mild vignette — darken edges only slightly
	vec2 vig_uv = uv * 2.0 - 1.0;
	float vig   = 1.0 - dot(vig_uv, vig_uv) * vignette;
	COLOR.rgb  *= clamp(vig, 0.0, 1.0);
}
