shader_type canvas_item;
// Applied to unit sprites when HP <= 25% — RGB glitch flicker effect.

void fragment() {
	vec4 col = texture(TEXTURE, UV);
	if (col.a < 0.01) { discard; }

	// Compound flicker — two sine waves create irregular rhythm
	float flicker = sin(TIME * 13.7) * sin(TIME * 7.3) * 0.5 + 0.5;

	// Horizontal glitch lines — occasional bright scanline artifacts
	float glitch_line = step(0.97, sin(UV.y * 80.0 + TIME * 20.0));
	vec2  shift_uv    = UV + vec2(0.006 * flicker * glitch_line, 0.0);
	float r_glitch    = texture(TEXTURE, clamp(shift_uv, vec2(0.0), vec2(1.0))).r;

	col.r  = mix(col.r, r_glitch, 0.65);
	col.r  = min(col.r + flicker * 0.22, 1.0);
	col.gb *= 1.0 - flicker * 0.18;

	COLOR = col;
}
