shader_type canvas_item;
render_mode unshaded;
uniform vec4 frame_uv = vec4(0.0,0.0,1.0,1.0);

float silhouette(sampler2D source_texture,vec2 uv) {
    if (any(lessThan(uv,frame_uv.xy)) || any(greaterThan(uv,frame_uv.zw))) return 0.0;
    return smoothstep(0.04,0.55,texture(source_texture,uv).a);
}

void fragment() {
    float opacity=0.0;
    for (int x=-1;x<=1;x++) {
        for (int y=-1;y<=1;y++) {
            opacity+=silhouette(TEXTURE,UV+vec2(float(x),float(y))*TEXTURE_PIXEL_SIZE*1.4);
        }
    }
    COLOR=vec4(0.008,0.012,0.018,opacity/9.0*0.23);
}
