"""Shared treatment-bed and warehouse-rack meshes."""
import math

import bpy

from create_hardsurface_crate import box
from library_placement import place


def build_bed(group, x, y, w, d, steel, linen, pad, *, stretcher=False, floor_bedding=False,
              privacy_side=0, intensive_care=False):
    long_y = d > w
    length, width = (d,w) if long_y else (w,d)
    parts = []
    def piece(label, along, across, z, half_length, half_width, half_height, material):
        dx,dy = (across,along) if long_y else (along,across)
        a,b = (half_width,half_length) if long_y else (half_length,half_width)
        parts.append(box(label,(x+dx,y+dy,z),(a,b,half_height),material,.025))
    if floor_bedding:
        piece("Shelter floor mattress",0,0,.087,length*.46,width*.43,.086,linen)
        piece("Shelter folded blanket",-length*.08,0,.178,length*.33,width*.415,.026,pad)
        piece("Shelter improvised pillow",length*.33,0,.195,length*.095,width*.29,.041,linen)
        for part in parts:
            part.parent = group
        return
    for end in (-1,1):
        for side in (-1,1):
            piece("Bed leg",end*length*.32,side*width*.31,.24,.05,.05,.24,steel)
    piece("Bed frame",0,0,.48,length*.46,width*.43,.065,steel)
    if stretcher:
        piece("Stretcher body pad",-length*.08,0,.566,length*.32,width*.34,.046,pad)
        piece("Stretcher headrest",length*.335,0,.58,length*.08,width*.32,.056,pad)
        if intensive_care:
            piece("Treatment sheet",-length*.10,0,.626,length*.29,width*.32,.025,linen)
            pole_along, pole_across = length*.30,width*.419
            piece("Infusion stand",pole_along,pole_across,.89,.021,.021,.55,steel)
            piece("Infusion hanger",pole_along-length*.045,pole_across,1.43,
                  length*.062,.021,.020,steel)
            piece("Infusion bag",pole_along-length*.088,pole_across,1.32,
                  length*.026,.033,.074,linen)
        for side in (-1,1):
            piece("Stretcher undercarriage brace",0,side*width*.31,.19,length*.32,.025,.025,steel)
            piece("Stretcher side rail",0,side*width*.425,.62,length*.31,.025,.026,steel)
            for end in (-1,1):
                piece("Stretcher rail upright",end*length*.29,side*width*.425,.57,.025,.025,.06,steel)
        for end in (-1,1):
            piece("Stretcher end handle",end*length*.465,0,.60,.029,width*.30,.025,steel)
        if privacy_side:
            across = privacy_side*width*.445
            for end in (-1, 1):
                piece("Privacy screen post", end*length*.32,across,1.05,.024,.024,.49,steel)
            for fold in (-1, 0, 1):
                piece("Privacy screen cloth", fold*length*.21,across,.995,length*.102,.025,.40,pad)
    else:
        piece("Bed mattress",0,0,.57,length*.44,width*.4,.075,linen)
        piece("Bed pillow",length*.30,0,.66,length*.105,width*.31,.045,linen)
        piece("Bed cover",-length*.13,0,.644,length*.29,width*.405,.021,pad)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    bpy.context.object.name="Clinic treatment bed"
    bpy.context.object.parent=group


def build_rack(group, x, y, w, d, steel, beam, *, records=False):
    parts = []
    def rack_part(label, location, dimensions, material):
        parts.append(box(label, location, dimensions, material, .012))

    for side_x in (-1, 1):
        for side_y in (-1, 0, 1):
            rack_part("Rack upright", (x+side_x*w*.43,y+side_y*d*.44,1.12),
                      (.046,.05,1.12), steel)
    for height in (.38,1.16,1.94):
        rack_part("Slotted shelf deck", (x,y,height), (w*.43,d*.45,.038), steel)
        for side in (-1,1):
            rack_part("Safety shelf rail", (x+side*w*.42,y,height+.01),
                      (.048,d*.46,.065), beam)
        if records:
            for offset, height_factor in ((-.30,.9),(-.10,.74),(.13,.95),(.32,.82)):
                vertical = d > w
                location = (x,y+offset*d) if vertical else (x+offset*w,y)
                footprint = (w*.32,d*.064) if vertical else (w*.064,d*.32)
                half_height = .13*height_factor
                rack_part("Records shelf binders", (*location,height+.038+half_height),
                          (*footprint,half_height), beam if offset < 0 else steel)
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    bpy.context.object.name = "Warehouse pallet rack"
    bpy.context.object.parent = group


def build_containment_chamber(group, x, y, w, d, steel, trim, screen):
    box("Containment footprint deck", (x, y, .075), (w*.50, d*.50, .075), steel).parent = group
    box("Containment specimen tray", (x, y, .27), (w*.28, d*.37, .12), trim).parent = group
    for side in (-1, 1):
        edge = x + side*w*.34
        box("Containment drive housing", (edge, y, .38), (w*.14, d*.44, .26), steel).parent = group
        box("Containment light rail", (x+side*w*.215, y, .49),
            (.025, d*.35, .028), screen).parent = group
        for offset in (-.31, 0, .31):
            box("Containment clamp", (edge, y+offset*d, .67),
                (w*.11, d*.077, .043), trim).parent = group
        box("Containment end bulkhead", (x, y+side*d*.396, .40),
            (w*.20, d*.055, .17), steel).parent = group


def build_medical_scanner(group, x, y, w, d, enamel, trim, screen):
    box("Scanner chassis", (x, y, .13), (w*.48, d*.47, .13), trim).parent = group
    box("Scanner patient table", (x, y-d*.09, .40),
        (w*.23, d*.34, .08), enamel).parent = group
    box("Scanner table pad", (x, y-d*.13, .50), (w*.19, d*.22, .035), screen).parent = group
    radius = min(w*.33, .57)
    gantry_y = y+d*.20
    box("Scanner gantry support", (x, gantry_y, .37), (w*.43, d*.13, .24), enamel).parent = group
    for label, offset, tube, material in (
        ("Scanner gantry shell", 0, .12, enamel),
        ("Scanner gantry light", -.10, .028, screen),
    ):
        bpy.ops.mesh.primitive_torus_add(
            major_segments=32, minor_segments=10, major_radius=radius, minor_radius=tube,
            location=(x, gantry_y+offset, .60+radius), rotation=(math.pi/2, 0, 0),
        )
        ring = bpy.context.object
        ring.name = label
        ring.data.materials.append(material)
        ring.parent = group



def build_diagnostic_bench(group, x, y, w, d, housing, steel, screen, *, telemetry=False):
    box("Diagnostic housing", (x,y,.37), (w*.45,d*.47,.37), housing, .035).parent = group
    box("Diagnostic steel rim", (x,y,.75), (w*.48,d*.48,.055), steel, .025).parent = group
    panel_count = 3 if d > w*2 else 2
    for panel in range(panel_count):
        panel_y = y+d*((panel+.5)/panel_count-.5)*.87
        box("Diagnostic screen", (x-w*.065,panel_y,.81),
            (w*.28,d*.33/panel_count,.016), screen, .012).parent = group
        box("Diagnostic button bank", (x+w*.30,panel_y,.81),
            (w*.075,d*.22/panel_count,.025), housing, .012).parent = group
    if telemetry:
        for side in (-1, 1):
            post_x = x+side*w*.32
            box("Telemetry support", (post_x,y+d*.32,1.03),
                (.046,.045,.25),steel,.009).parent = group
        box("Telemetry monitor housing", (x,y+d*.32,1.32),
            (w*.34,d*.072,.17),housing,.022).parent = group
        box("Telemetry monitor face", (x,y+d*.239,1.33),
            (w*.29,d*.016,.112),screen,.009).parent = group
    merge_fixture_meshes(group, "Medbay telemetry station" if telemetry else "Clinic diagnostic bench")


def build_operating_table(group, x, y, w, d, housing, steel, screen):
    vertical = d > w
    length, width = (d, w) if vertical else (w, d)

    def section(label, offset, height, half_length, half_width, half_height, material):
        center = (x, y + offset * length, height) if vertical else (x + offset * length, y, height)
        along, across = half_length * length, half_width * width
        footprint = (across, along) if vertical else (along, across)
        box(label, center, (*footprint, half_height), material, .025).parent = group

    section("Surgery pedestal foot", 0, .08, .29, .35, .08, housing)
    section("Surgery lift housing", 0, .39, .17, .24, .25, steel)
    section("Surgery articulated deck", 0, .70, .46, .46, .08, housing)
    for offset, size in ((-.35, .10), (-.08, .15), (.24, .15)):
        section("Surgery patient pad", offset, .82, size, .35, .04, steel)
    section("Surgery control strip", .43, .79, .025, .30, .018, screen)
    merge_fixture_meshes(group, "Surgery operating table")


def build_security_bay(group, identifier, x, y, w, d, wall, crate, steel, trim, screen):
    # Side bays face the main aisle. The northern bays and guardrooms face south.
    yaw = 0
    if identifier.startswith(("southwest_", "west_middle_")):
        yaw = math.pi/2
    elif identifier.startswith(("southeast_", "east_middle_")):
        yaw = -math.pi/2
    front_width, depth = (w,d) if yaw == 0 else (d,w)
    cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)

    def center(u, v, z):
        return x+u*cos_yaw-v*sin_yaw, y+u*sin_yaw+v*cos_yaw, z

    def part(label, u, v, z, dimensions, material):
        piece = box(label, center(u,v,z), dimensions, material, .015)
        piece.rotation_euler.z = yaw
        piece.parent = group

    part("Security bay floor pan", 0,0,.038, (front_width*.495,depth*.495,.038), trim)
    part("Security bay doorway threshold", 0,-depth*.453,.094,
         (front_width*.16,.065,.024), steel)
    spans = [
        (0,depth*.44,front_width*.94,0),
        (-front_width*.46,0,depth*.84,math.pi/2),
        (front_width*.46,0,depth*.84,math.pi/2),
    ]
    for side in (-1,1):
        spans.append((side*front_width*.335,-depth*.44,front_width*.27,0))
    for u,v,length,turn in spans:
        count = max(1, math.ceil(length/2.0))
        span = length/count
        for i in range(count):
            offset = ((i+.5)/count-.5)*length
            place(wall, group, center(u+offset*math.cos(turn),v+offset*math.sin(turn),.076),
                  (span,.36,1.37), yaw=yaw+turn, merge=True)
    part("Security bay worktop", -front_width*.13,depth*.20,.70,
         (front_width*.235,.32,.065), steel)
    part("Security bay console cabinet", -front_width*.13,depth*.20,.38,
         (front_width*.21,.28,.30), trim)
    part("Security bay monitor enclosure", -front_width*.15,depth*.24,.90,
         (.23,.052,.14), steel)
    part("Security bay monitor", -front_width*.15,depth*.24-.057,.90,
         (.19,.012,.095), screen)
    place(crate, group, center(front_width*.28,depth*.12,.076),
          (front_width*.26,depth*.38,.72), yaw=yaw)



def build_checkpoint_fixture(group, identifier, x, y, w, d, steel, trim, screen, warning):
    vertical = d > w
    length, width = (d,w) if vertical else (w,d)

    def part(label, along, across, z, half_length, half_width, half_height, material):
        dx,dy = (across,along) if vertical else (along,across)
        a,b = (half_width,half_length) if vertical else (half_length,half_width)
        box(label, (x+dx,y+dy,z), (a,b,half_height), material, .018).parent = group

    if identifier.startswith("barrier_"):
        segments = max(2, round(length/1.6))
        span = length*.94/segments
        for index in range(segments):
            offset = ((index+.5)-segments/2)*span
            part("Barrier inset panel", offset,0,.41,span*.45,min(width*.25,.24),.23,trim)
            part("Barrier top rail", offset,0,.66,span*.46,min(width*.31,.28),.033,steel)
        for index in range(segments+1):
            offset = (index-segments/2)*span
            part("Barrier anchor post", offset,0,.43,.062,min(width*.36,.32),.43,warning)
            part("Barrier mounting foot", offset,0,.058,.11,min(width*.46,.38),.058,steel)
    elif identifier.startswith("scanner_"):
        part("Scanner conveyor bed", 0,0,.26,length*.44,width*.31,.24,trim)
        for index in range(8):
            offset = (index-3.5)*length*.10
            part("Scanner conveyor slat", offset,0,.514,length*.036,width*.27,.024,steel)
        for side in (-1,1):
            part("Scanner arch upright", length*.05,side*width*.37,.64,length*.13,width*.095,.57,steel)
            part("Scanner status strip", length*.05,side*width*.469,.79,length*.074,.017,.16,screen)
        part("Scanner arch cap", length*.05,0,1.22,length*.132,width*.465,.06,steel)
    else:
        part("Checkpoint terminal plinth", 0,0,.09,length*.47,width*.47,.09,trim)
        part("Checkpoint terminal housing", 0,0,.51,length*.34,width*.38,.40,steel)
        part("Checkpoint terminal fascia", 0,0,.91,length*.30,width*.33,.053,trim)
        part("Checkpoint reader display", -length*.12,0,.975,length*.104,width*.24,.020,screen)
        part("Checkpoint terminal warning panel", length*.17,0,.967,length*.077,width*.23,.016,warning)



def build_industrial_fixture(group, kind, x, y, w, d, steel, trim, rail, *, depot=False):
    if kind == "workbench":
        box("Workbench steel top", (x,y,.78), (w*.49,d*.47,.065), rail).parent = group
        box("Workbench drawer cabinet", (x-w*.27,y,.37), (w*.18,d*.40,.36), steel).parent = group
        for z in (.23,.42,.61):
            box("Workbench drawer pull", (x-w*.27,y-d*.42,z), (w*.09,.025,.019), rail).parent = group
        box("Workbench end support", (x+w*.38,y,.355), (.045,d*.39,.35), trim).parent = group
        box("Workbench lower shelf", (x+w*.10,y,.22), (w*.27,d*.37,.032), steel).parent = group
        if depot:
            vise_x, vise_y = x+w*.29, y-d*.24
            box("Depot workbench vise base", (vise_x,vise_y,.875),
                (min(.14,w*.11),min(.10,d*.14),.03),trim,.012).parent = group
            for side in (-1, 1):
                box("Depot workbench vise jaw", (vise_x+side*min(.065,w*.05),vise_y,.942),
                    (min(.035,w*.028),min(.081,d*.12),.037),steel,.009).parent = group
            box("Depot workbench parts tray", (x-w*.19,y+d*.17,.869),
                (w*.19,d*.20,.024),trim,.009).parent = group
        return
    if kind == "drums":
        radius = min(w*.22,d*.34)
        for side in (-1,1):
            center_x = x + side*w*.24
            bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=.75,
                                                location=(center_x,y,.375))
            drum = bpy.context.object
            drum.name = "Warehouse service drum"
            drum.data.materials.append(steel)
            drum.parent = group
            for z in (.12,.63):
                bpy.ops.mesh.primitive_torus_add(major_segments=20, minor_segments=6,
                                                 major_radius=radius, minor_radius=.025,
                                                 location=(center_x,y,z))
                rim = bpy.context.object
                rim.name = "Warehouse service drum rim"
                rim.data.materials.append(rail)
                rim.parent = group
        return
    box("Valve pedestal", (x,y,.36), (w*.34,d*.32,.36), trim).parent = group
    radius = min(w,d)*.33
    bpy.ops.mesh.primitive_torus_add(major_segments=20, minor_segments=6,
                                     major_radius=radius, minor_radius=.037,
                                     location=(x,y,.82))
    wheel = bpy.context.object
    wheel.name = "Service valve handwheel"
    wheel.data.materials.append(rail)
    wheel.parent = group
    for angle in (0,math.pi/2):
        spoke = box("Service valve spoke", (x,y,.82), (radius,.027,.028), steel)
        spoke.rotation_euler.z = angle
        spoke.parent = group



def build_safehouse_fixture(group, kind, x, y, w, d, steel, enamel, rail):
    if kind == "gym_weights":
        box("Weight rack base", (x,y,.10), (w*.49,d*.46,.10), steel).parent = group
        box("Weight rack horizontal bar", (x,y,.65), (w*.44,.039,.043), rail).parent = group
        for side in (-1,1):
            post_x = x + side*w*.36
            box("Weight rack upright", (post_x,y,.39), (.055,d*.17,.35), steel).parent = group
            bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=min(.24,d*.22), depth=.14,
                                                location=(post_x,y,.65), rotation=(0,math.pi/2,0))
            plate = bpy.context.object
            plate.name = "Weight plate"
            plate.data.materials.append(steel)
            plate.parent = group
        return
    if kind == "bath_sink":
        box("Washbasin vanity", (x,y,.41), (w*.42,d*.40,.41), steel).parent = group
        box("Washbasin bowl", (x,y,.85), (w*.45,d*.44,.054), enamel).parent = group
        box("Washbasin inset", (x,y-d*.04,.909), (w*.29,d*.28,.009), steel).parent = group
        box("Tap stem", (x,y+d*.31,.99), (.032,.035,.087), rail).parent = group
        box("Tap spout", (x,y+d*.24,1.066), (.034,d*.11,.024), rail).parent = group
        return
    if kind in {"bath_tub", "bath_toilet", "stove"}:
        vertical = d > w
        length, breadth = (d,w) if vertical else (w,d)

        def fitted(label, along, across, z, half_length, half_breadth, half_height, material):
            dx,dy = (across,along) if vertical else (along,across)
            sx,sy = (half_breadth,half_length) if vertical else (half_length,half_breadth)
            box(label, (x+dx,y+dy,z), (sx,sy,half_height), material,.018).parent = group

        if kind == "bath_tub":
            fitted("Tub enamel shell", 0,0,.23,length*.46,breadth*.45,.23,enamel)
            fitted("Tub basin inset", 0,0,.472,length*.36,breadth*.32,.012,steel)
            fitted("Tub tap", length*.37,0,.55,.033,.046,.079,rail)
        elif kind == "bath_toilet":
            fitted("Toilet porcelain base", 0,0,.24,length*.41,breadth*.38,.24,enamel)
            fitted("Toilet seat recess", -length*.1,0,.493,length*.24,breadth*.29,.016,steel)
            fitted("Toilet cistern", length*.31,0,.67,length*.127,breadth*.35,.22,enamel)
        else:
            fitted("Stove cabinet", 0,0,.39,length*.46,breadth*.44,.39,steel)
            fitted("Stove cooktop", 0,0,.811,length*.45,breadth*.42,.034,rail)
            for side in (-1,1):
                fitted("Stove burner", side*length*.22,0,.854,length*.13,breadth*.24,.021,steel)
        return
    if kind == "toilet_stalls":
        for offset in (-.26,.26):
            sy = y+offset*d
            box("Stall toilet", (x-w*.22,sy,.33), (w*.19,d*.135,.28), enamel).parent = group
            box("Stall cistern", (x-w*.35,sy,.65), (w*.09,d*.16,.18), enamel).parent = group
        for offset in (-.47,0,.47):
            box("Stall privacy divider", (x,y+offset*d,.70), (w*.44,.035,.64), steel).parent = group
        return
    box("Shower tiled base", (x,y,.075), (w*.49,d*.49,.075), enamel).parent = group
    box("Shower plumbing wall", (x-w*.42,y,.83), (w*.068,d*.48,.74), steel).parent = group
    for offset in (-.17,.17):
        sy = y+offset*d
        box("Shower riser", (x-w*.31,sy,1.08), (.025,.027,.40), rail).parent = group
        box("Shower head", (x-w*.23,sy,1.49), (w*.12,.083,.034), rail).parent = group
    box("Shower divider", (x,y, .66), (w*.41,.039,.51), steel).parent = group



def build_server_bank(group, x, y, w, d, housing, frame, indicator, *, vented_lids=False):
    vertical = d > w
    length, depth = (d,w) if vertical else (w,d)
    bay_count = max(1, round(length/1.3))
    span = length*.95/bay_count
    pieces = []

    def part(label, along, across, z, half_length, half_depth, half_height, material):
        dx,dy = (across,along) if vertical else (along,across)
        sx,sy = (half_depth,half_length) if vertical else (half_length,half_depth)
        pieces.append(box(label, (x+dx,y+dy,z), (sx,sy,half_height), material, .008))

    for index in range(bay_count):
        offset = ((index+.5)-bay_count/2)*span
        part("Server cabinet frame", offset,0,.86,span*.48,depth*.45,.86,frame)
        part("Server cabinet lid", offset,0,1.747,span*.46,depth*.465,.038,housing)
        if vented_lids:
            part("Relay exhaust housing", offset,0,1.805,span*.31,depth*.30,.026,frame)
            for slot in (-2,-1,0,1,2):
                part("Relay exhaust fin", offset+slot*span*.102,0,1.846,
                     span*.025,depth*.267,.017,housing)
        for side in (-1,1):
            face = side*depth*.46
            part("Server service face", offset,face,.90,span*.438,.025,.75,housing)
            for tier in range(5):
                z = .34+tier*.249
                part("Server blade", offset,face+side*.027,z,span*.388,.013,.081,frame)
                part("Server status LED", offset+span*.27,face+side*.043,z,
                     span*.056,.011,.018,indicator)
    bpy.ops.object.select_all(action="DESELECT")
    for piece in pieces:
        piece.select_set(True)
    bpy.context.view_layer.objects.active = pieces[0]
    bpy.ops.object.join()
    bpy.context.object.name = "Server cabinet bank"
    bpy.context.object.parent = group



def merge_fixture_meshes(group, label, *, pieces=None):
    """Bake bevels, then merge the meshes without changing their cutaway parent."""
    if pieces is None:
        pieces = list(group.children)
    bpy.ops.object.select_all(action="DESELECT")
    for piece in pieces:
        piece.select_set(True)
    bpy.context.view_layer.objects.active = pieces[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    bpy.context.object.name = label


def build_facility_fixture(group, kind, x, y, w, d, steel, trim, screen):
    vertical = d > w
    length, width = (d,w) if vertical else (w,d)

    def part(label, along, across, z, half_length, half_width, half_height, material):
        dx,dy = (across,along) if vertical else (along,across)
        sx,sy = (half_width,half_length) if vertical else (half_length,half_width)
        box(label, (x+dx,y+dy,z), (sx,sy,half_height), material, .013).parent = group

    if kind == "meeting_table":
        part("Meeting table top", 0,0,.73,length*.44,width*.23,.046,steel)
        part("Meeting table pedestal", 0,0,.34,length*.15,width*.13,.34,trim)
        for side in (-1,1):
            part("Meeting seat", 0,side*width*.36,.42,length*.21,width*.105,.058,trim)
            part("Meeting seat back", 0,side*width*.45,.62,length*.23,width*.034,.19,steel)
    elif kind == "command_table":
        part("Operations table pedestal", 0,0,.36,length*.28,width*.23,.36,trim)
        part("Operations table armor rim", 0,0,.76,length*.46,width*.44,.064,steel)
        part("Inset operations map", 0,0,.831,length*.35,width*.31,.012,trim)
        for side in (-1,1):
            part("Operations map illuminated edge", 0,side*width*.326,.845,length*.34,.017,.012,screen)
            part("Operations table control panel", side*length*.392,0,.847,length*.034,width*.20,.024,steel)
    elif kind == "records_desk":
        for side in (-1,1):
            part("Records desk pedestal", side*length*.34,0,.36,length*.095,width*.35,.36,trim)
        part("Records desk work surface", 0,0,.756,length*.47,width*.44,.043,steel)
        part("Records terminal housing", 0,width*.22,1.04,length*.16,.062,.168,trim)
        part("Records terminal display", 0,width*.22-.067,1.046,length*.136,.009,.128,screen)
        part("Records workstation keyboard", 0,-width*.16,.82,length*.142,width*.12,.018,trim)
        part("Records desk file stack", length*.31,0,.836,length*.09,width*.20,.033,steel)
        merge_fixture_meshes(group, "Records consultation workstation")
    elif kind == "metro_bench":
        for end in (-1, 1):
            part("Platform bench pedestal", end*length*.29,0,.23,length*.075,width*.29,.23,trim)
        part("Platform bench seat", 0,0,.49,length*.46,width*.40,.047,steel)
        part("Platform bench backrest", 0,width*.32,.71,length*.45,width*.075,.21,steel)
        merge_fixture_meshes(group, "Metro platform bench")
    elif kind == "metro_ticket_machine":
        part("Ticket machine plinth", 0,0,.08,length*.45,width*.43,.08,trim)
        part("Ticket machine enclosure", 0,0,.61,length*.38,width*.35,.55,steel)
        part("Ticket machine face", 0,-width*.35,.80,length*.31,width*.046,.28,trim)
        part("Ticket machine display", 0,-width*.405,.94,length*.24,width*.018,.105,screen)
        part("Ticket machine collection slot", 0,-width*.405,.66,length*.16,width*.018,.026,steel)
        merge_fixture_meshes(group, "Metro ticket machine")
    elif kind == "shelter_table":
        for strip in (-1, 0, 1):
            part("Shelter tabletop plank", 0,strip*width*.285,.72,length*.46,width*.138,.045,steel)
        for end in (-1, 1):
            for side in (-1, 1):
                part("Shelter table angle-iron leg", end*length*.34,side*width*.32,.34,.04,.04,.34,trim)
        part("Shelter table cross brace", 0,0,.19,length*.35,.032,.035,trim)
        part("Shelter tin tray", -length*.22,width*.09,.788,length*.135,width*.20,.022,trim)
        for along, across in ((-.23,.08), (.08,-.16), (.28,.13)):
            radius = min(.054,width*.085,length*.055)
            dx,dy = (across*width,along*length) if vertical else (along*length,across*width)
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=.083,
                                                location=(x+dx,y+dy,.827))
            tin = bpy.context.object
            tin.name = "Shelter food tin"
            tin.data.materials.append(trim)
            tin.parent = group
        merge_fixture_meshes(group, "Salvaged shelter table")
    elif kind == "shelter_kitchen":
        part("Shelter kitchen base cabinets", 0,0,.35,length*.46,width*.43,.35,trim)
        for offset in (-.31,.31):
            part("Shelter kitchen worktop", offset*length,0,.75,length*.16,width*.46,.05,steel)
        for side in (-1,1):
            part("Shelter kitchen basin rim", 0,side*width*.37,.75,length*.15,width*.09,.05,steel)
        part("Shelter kitchen basin bottom", 0,0,.711,length*.15,width*.28,.011,steel)
        part("Shelter kitchen tap stem", 0,width*.37,.865,.028,.028,.071,steel)
        part("Shelter kitchen tap spout", 0,width*.26,.927,.027,width*.13,.023,steel)
    elif kind == "clinic_reception":
        part("Clinic reception cabinet", -length*.06,-width*.08,.39,length*.39,width*.28,.39,trim)
        part("Clinic reception worktop", -length*.06,-width*.08,.81,length*.41,width*.30,.043,steel)
        part("Clinic reception end cabinet", length*.36,width*.06,.39,length*.11,width*.36,.39,trim)
        part("Clinic reception return worktop", length*.36,width*.06,.81,length*.12,width*.37,.043,steel)
        part("Clinic reception raised counter", 0,-width*.37,.94,length*.46,width*.065,.072,trim)
        for offset in (-.28,.22):
            part("Clinic terminal stand", length*offset,width*.14,.893,.09,.085,.04,trim)
            part("Clinic idle terminal", length*offset,width*.13,1.045,.17,.045,.15,steel)
        part("Clinic records tray", length*.04,width*.14,.877,.16,.11,.022,trim)
        merge_fixture_meshes(group, "Ruined clinic reception")
    elif kind == "vault_looters_table":
        for end in (-1, 1):
            part("Salvage table trestle", end*length*.33,0,.34,.047,width*.38,.34,trim)
        part("Salvage table worktop", 0,0,.70,length*.47,width*.44,.046,steel)
        part("Salvage sorting tray", -length*.20,width*.09,.782,length*.20,width*.22,.036,trim)
        for offset, inset in ((-.29,.15),(-.12,.03),(.24,-.08)):
            part("Discarded vault fitting", offset*length,inset*width,.829,
                 length*.059,width*.076,.036,screen)
        merge_fixture_meshes(group, "Vault salvage sorting table")
    elif kind == "vault_display":
        part("Vault display cabinet", 0,0,.32,length*.41,width*.39,.32,trim)
        part("Vault display tray", 0,0,.66,length*.44,width*.43,.046,steel)
        for side in (-1,1):
            part("Vault case broken glass channel", 0,side*width*.40,.735,
                 length*.43,.023,.049,trim)
            part("Vault case tray divider", side*length*.16,0,.717,
                 .028,width*.35,.020,trim)
        for offset, inset in ((-.28,.11),(.04,-.17),(.27,.045)):
            part("Vault displaced display fragment", length*offset,width*inset,.716,
                 length*.058,width*.10,.022,trim)
        # Irregular remnants rise out of the two intact glazing channels.
        for side, fragments in ((-1, ((-.39,-.25,-.36,.14), (.12,.24,.20,.09))),
                                (1, ((-.14,.03,-.05,.12), (.29,.41,.37,.18)))):
            vertices, faces = [], []
            for start, end, peak, height in fragments:
                index = len(vertices)
                for along, z in ((start,.774), (end,.774), (peak,.774+height)):
                    u, v = along*length, side*width*.40
                    dx, dy = (v,u) if vertical else (u,v)
                    vertices.append((x+dx,y+dy,z))
                faces.extend(((index,index+1,index+2), (index+2,index+1,index)))
            mesh = bpy.data.meshes.new("Vault broken glazing")
            mesh.from_pydata(vertices, [], faces)
            mesh.materials.append(steel)
            shards = bpy.data.objects.new("Vault broken glazing", mesh)
            bpy.context.collection.objects.link(shards)
            shards.parent = group
    elif kind == "medbay_care_desk":
        part("Care desk drawer cabinet", -length*.28,0,.36,length*.17,width*.40,.36,trim)
        for z in (.24,.45,.62):
            part("Care desk drawer pull", -length*.28,-width*.41,z,length*.084,.025,.014,steel)
        part("Care desk end support", length*.395,0,.36,.035,width*.39,.36,trim)
        part("Care desk worktop", 0,0,.75,length*.48,width*.45,.050,steel)
        part("Care desk terminal housing", length*.19,width*.25,.96,length*.18,width*.12,.17,trim)
        part("Care desk display", length*.19,width*.119,.97,length*.147,width*.016,.119,screen)
        part("Care desk input panel", length*.18,-width*.17,.818,length*.14,width*.125,.024,trim)
        merge_fixture_meshes(group, "Medbay care desk")
    elif kind == "medbay_supply_table":
        for end in (-1, 1):
            for side in (-1, 1):
                part("Triage table leg", end*length*.36,side*width*.32,.35,.035,.035,.35,steel)
        part("Triage table lower shelf", 0,0,.24,length*.39,width*.37,.025,trim)
        part("Triage table worktop", 0,0,.73,length*.48,width*.46,.045,steel)
        part("Dressing tray", -length*.23,width*.10,.806,length*.16,width*.22,.035,trim)
        for pack in (-1, 0, 1):
            part("Sealed dressing pack", length*(.18+pack*.12),-width*.05,.828,
                 length*.049,width*.18,.053,screen)
        merge_fixture_meshes(group, "Medbay triage supply table")
    elif kind == "relay_console":
        for end in (-1, 1):
            part("Relay console pedestal", end*length*.31,0,.38,length*.14,width*.39,.38,trim)
        part("Relay console worktop", 0,0,.82,length*.48,width*.46,.062,steel)
        for end in (-1, 1):
            offset = end*length*.218
            part("Relay terminal housing", offset,width*.25,1.07,length*.176,width*.105,.185,trim)
            part("Relay terminal screen", offset,width*.138,1.09,length*.151,width*.016,.135,screen)
            part("Relay terminal controls", offset,-width*.21,.907,length*.144,width*.13,.025,trim)
        merge_fixture_meshes(group, "Relay service workstation")
    elif kind == "relay_core":
        part("Relay recessed base", 0,0,.13,length*.46,width*.44,.13,trim)
        for lane in (-1, 0, 1):
            across = lane*width*.265
            part("Relay processor enclosure", 0,across,.57,length*.40,width*.119,.31,steel)
            for bay in (-1, 0, 1):
                along = bay*length*.24
                part("Relay processor access plate", along,across,.893,length*.102,width*.096,.017,trim)
                part("Relay processor status strip", along,across,.913,length*.062,width*.018,.009,screen)
        merge_fixture_meshes(group, "Wasteland relay processor array")
        harness = bpy.data.curves.new("Relay cable harness", "CURVE")
        harness.dimensions = "3D"
        harness.resolution_u = 8
        harness.bevel_depth = min(.035,width*.012)
        harness.bevel_resolution = 2
        harness.materials.append(trim)
        for side in (-1, 1):
            for lane in (-1, 0, 1):
                spline = harness.splines.new("BEZIER")
                spline.bezier_points.add(3)
                across = lane*width*.265
                for point, (along, offset, z) in zip(spline.bezier_points, (
                    (.39, 0, .48), (.46, .025, .32), (.465, .079, .17), (.37, .102, .17),
                )):
                    u, v = side*length*along, across+width*offset
                    dx, dy = (v,u) if vertical else (u,v)
                    point.co = (x+dx,y+dy,z)
                    point.handle_left_type = point.handle_right_type = "AUTO"
        cables = bpy.data.objects.new("Relay cable harness", harness)
        bpy.context.collection.objects.link(cables)
        cables.parent = group
        merge_fixture_meshes(group, "Relay cable harness", pieces=[cables])
    elif kind == "data_core":
        part("Data core floor plinth", 0,0,.14,length*.47,width*.47,.14,trim)
        part("Armored data core chassis", 0,0,.56,length*.34,width*.35,.40,steel)
        part("Data core inset blue panel", 0,0,.979,length*.20,width*.21,.027,screen)
        for side in (-1,1):
            part("Data core upper frame", 0,side*width*.28,.975,length*.31,width*.054,.04,trim)
            part("Data core light channel", side*length*.35,0,.62,.022,width*.18,.18,screen)
        merge_fixture_meshes(group, "Industrial data core")
    elif kind == "vault_core":
        part("Vault foundation", 0,0,.14,length*.48,width*.47,.14,trim)
        part("Vault armored housing", 0,0,.49,length*.41,width*.40,.34,steel)
        part("Vault locking plate", 0,0,.86,length*.36,width*.35,.06,trim)
        for end in (-1, 1):
            for side in (-1, 1):
                part("Vault lid locking boss", end*length*.295,side*width*.278,.94,
                     length*.036,width*.038,.025,steel)
            part("Vault case reinforcing rib", end*length*.417,0,.45,
                 length*.022,width*.32,.075,trim)
        radius = width*.18
        bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=6,
                                         major_radius=radius, minor_radius=.034, location=(x,y,.99))
        wheel = bpy.context.object
        wheel.name = "Vault locking handwheel"
        wheel.data.materials.append(steel)
        wheel.parent = group
        part("Vault locking hub", 0,0,.96,.105,.105,.05,steel)
        for index in range(3):
            spoke = box("Vault handwheel spoke", (x,y,.99),(radius,.025,.025),steel,.008)
            spoke.rotation_euler.z = index*math.pi/3
            spoke.parent = group
    elif kind == "inspection_pit":
        part("Inspection trench inset", 0,0,.006,length*.48,width*.48,.015,trim)
        for side in (-1,1):
            part("Inspection pit curb", 0,side*width*.44,.097,length*.48,width*.052,.097,steel)
            part("Inspection pit curb warning strip", 0,side*width*.44,.200,
                 length*.45,width*.025,.009,screen)
            part("Inspection pit end cap", side*length*.463,0,.078,
                 length*.025,width*.385,.078,steel)
            for i in range(4):
                part("Inspection pit access rung", side*(.25+i*.058)*length,0,.055+i*.016,
                     length*.013,width*.34,.013,steel)
    elif kind == "spare_tires":
        radius = min(w,d)*.30
        for level in range(3):
            bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=8, major_radius=radius,
                                             minor_radius=.079, location=(x,y,.09+level*.155))
            tire = bpy.context.object
            tire.name = "Stacked spare tire"
            tire.data.materials.append(trim)
            tire.parent = group
    elif kind == "command_wall":
        part("Command display support", 0,0,.32,length*.48,width*.44,.32,trim)
        for index in range(5):
            offset = (index-2)*length*.186
            part("Command display housing", offset,0,1.26,length*.09,width*.29,.62,steel)
            part("Command vertical display", offset,-width*.305,1.28,length*.078,.023,.43,screen)
            part("Command display visor", offset,0,1.91,length*.092,width*.33,.036,trim)
    else:
        part("Command workstation chassis", 0,0,.39,length*.47,width*.41,.39,trim)
        part("Command workstation desk", 0,0,.83,length*.48,width*.46,.064,steel)
        part("Command map display", 0,width*.14,.908,length*.39,width*.235,.026,screen)
        for side in (-1,1):
            part("Command input bank", side*length*.27,-width*.26,.906,length*.12,width*.108,.024,trim)


def build_floor_grate(group, x, y, w, d, partition_cap, rail, steel):
    box("Drain recessed backing", (x,y,-.012), (w*.49,d*.49,.014), partition_cap,.004).parent = group
    for side in (-1,1):
        box("Drain frame long", (x+side*w*.465,y,.013),
            (w*.029,d*.49,.017), rail,.004).parent = group
        box("Drain frame short", (x,y+side*d*.466,.013),
            (w*.438,d*.027,.017), rail,.004).parent = group
    for index in range(10):
        offset = (index-4.5)*d*.086
        box("Drain grate bar", (x,y+offset,.011), (w*.431,d*.022,.014), steel,.003).parent = group
