shader_type canvas_item;
// Clips a square sprite to a circular portrait and applies a damaged glitch tint.
// Used on every UnitToken Sprite2D to produce the VTT miniature-base look.

uniform float hp_fraction : hint_range(0.0, 1.0) = 1.0;

void fragment() {
    // For square textures aspect == 1.0; non-square sprites stay correct.
    float aspect = TEXTURE_PIXEL_SIZE.x / TEXTURE_PIXEL_SIZE.y;

    // Shift center up slightly — shows head/torso rather than legs.
    vec2 uv = UV - vec2(0.5, 0.44);
    uv.y *= aspect;

    float dist     = length(uv);
    float clip_a   = 1.0 - smoothstep(0.44, 0.50, dist);

    // Subtle inner rim brightening — portrait "lens" highlight.
    float rim_glow = smoothstep(0.41, 0.43, dist) * (1.0 - smoothstep(0.43, 0.50, dist));

    COLOR       = texture(TEXTURE, UV);
    COLOR.rgb  += vec3(rim_glow * 0.08);
    COLOR.a    *= clip_a;

    // Critically damaged: RGB glitch flicker tint (matches damaged.gdshader aesthetic).
    if (hp_fraction <= 0.25) {
        float t      = clamp((0.25 - hp_fraction) * 4.0, 0.0, 1.0);
        float flicker = sin(TIME * 11.3) * sin(TIME * 6.7) * 0.5 + 0.5;
        float gray   = dot(COLOR.rgb, vec3(0.299, 0.587, 0.114));
        vec3  tinted = mix(vec3(gray), vec3(0.78, 0.10, 0.08), 0.52);
        COLOR.rgb    = mix(COLOR.rgb, tinted, t * (0.55 + flicker * 0.30));
        COLOR.r      = min(COLOR.r + flicker * t * 0.18, 1.0);
    }
}
