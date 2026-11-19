shader_type canvas_item;
render_mode unshaded;

// Only the character art uses this material; ground, HP and terrain stay intact.
uniform vec2 outline_step = vec2(0.003);
uniform vec4 frame_uv = vec4(0.0, 0.0, 1.0, 1.0);
uniform vec4 rim_color : source_color = vec4(0.40, 0.88, 0.94, 1.0);
uniform bool fallen = false;
uniform float focus_strength : hint_range(0.0, 1.0) = 0.0;

varying vec4 item_modulate;

void vertex() {
    item_modulate = COLOR;
}

float frame_alpha(sampler2D source_texture, vec2 uv) {
    if (any(lessThan(uv, frame_uv.xy)) || any(greaterThan(uv, frame_uv.zw))) {
        return 0.0;
    }
    return texture(source_texture, uv).a;
}

void fragment() {
    vec4 modulation = item_modulate;
    vec4 art = texture(TEXTURE, UV);
    if (fallen) {
        COLOR = art * modulation;
    } else {
        float neighbor = 0.0;
        for (int x = -1; x <= 1; x++) {
            for (int y = -1; y <= 1; y++) {
                neighbor = max(neighbor, frame_alpha(TEXTURE, UV + vec2(float(x), float(y)) * outline_step));
            }
        }
        // Restore solid interiors while preserving antialiased silhouette edges.
        float body = smoothstep(0.02, 0.48, art.a);
        float edge = smoothstep(0.05, 0.50, neighbor) * (1.0 - body);
        // Compress highlights before clipping so white metal keeps its panel detail.
        vec3 lifted = (art.rgb - vec3(0.5)) * 1.12 + vec3(0.62);
        vec3 lit = clamp(mix(lifted, vec3(0.72) + (lifted - vec3(0.72)) * 0.45, step(vec3(0.72), lifted)), 0.0, 1.0);
        // A directional rim avoids the flat sticker look; every living unit stays outlined.
        vec2 frame_position = (UV - frame_uv.xy) / max(frame_uv.zw - frame_uv.xy, vec2(0.001));
        float rim_light = clamp(0.90 - frame_position.x * 0.12 - frame_position.y * 0.08, 0.68, 0.90);
        vec3 outline = mix(vec3(0.015, 0.025, 0.035), rim_color.rgb, mix(rim_light, 0.98, focus_strength));
        float alpha = body + edge * 0.90;
        vec3 rgb = (lit * body + outline * edge * 0.90) / max(alpha, 0.001);
        COLOR = vec4(rgb, alpha) * modulation;
    }
}
