shader_type canvas_item;
// Applied to thin border ColorRects — animates them as pulsing neon tubes.

uniform float pulse_speed : hint_range(0.5, 8.0) = 2.6;
uniform float min_alpha   : hint_range(0.0, 1.0) = 0.52;
uniform vec4  glow_color  : source_color = vec4(0.1, 0.95, 0.72, 1.0);

void fragment() {
	float pulse = sin(TIME * pulse_speed) * 0.5 + 0.5;
	float alpha = mix(min_alpha, 1.0, pulse) * glow_color.a;
	COLOR = vec4(glow_color.rgb, alpha);
}
