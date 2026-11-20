shader_type canvas_item;
render_mode unshaded;
uniform float shadow_opacity : hint_range(0.0,0.5) = 0.23;
uniform vec4 frame_uv = vec4(0.0,0.0,1.0,1.0);

void fragment() {
    float opacity=0.0;
    for (int x=-1;x<=1;x++) {
        for (int y=-1;y<=1;y++) {
            vec2 sample_uv = UV + vec2(float(x), float(y)) * TEXTURE_PIXEL_SIZE * 1.4;
            if (all(greaterThanEqual(sample_uv, frame_uv.xy)) && all(lessThanEqual(sample_uv, frame_uv.zw))) {
                opacity += smoothstep(0.04, 0.55, texture(TEXTURE, sample_uv).a);
            }
        }
    }
    COLOR=vec4(0.008,0.012,0.018,opacity/9.0*shadow_opacity);
}
