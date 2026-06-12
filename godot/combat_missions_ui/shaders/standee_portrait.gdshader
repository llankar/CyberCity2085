shader_type canvas_item;
// Standee portrait shader — preserves full sprite transparency without any
// circle clip.  Only applies a red-flicker tint when HP is critically low.

uniform float hp_fraction : hint_range(0.0, 1.0) = 1.0;

void fragment() {
    COLOR = texture(TEXTURE, UV);
    if (hp_fraction <= 0.25) {
        float t       = clamp((0.25 - hp_fraction) * 4.0, 0.0, 1.0);
        float flicker = sin(TIME * 11.3) * sin(TIME * 6.7) * 0.5 + 0.5;
        float gray    = dot(COLOR.rgb, vec3(0.299, 0.587, 0.114));
        vec3  tinted  = mix(vec3(gray), vec3(0.78, 0.10, 0.08), 0.52);
        COLOR.rgb     = mix(COLOR.rgb, tinted, t * (0.55 + flicker * 0.30));
        COLOR.r       = min(COLOR.r + flicker * t * 0.18, 1.0);
    }
}
