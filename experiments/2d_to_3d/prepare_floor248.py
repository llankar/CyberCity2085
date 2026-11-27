"""Remove source prop drawings only under surveyed replacement rectangles on E:."""
import json,hashlib,argparse,math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
from blender.dockside_vessels import VESSEL_OUTLINES
from blender.freight_stock import SOUTH_SIDING_LOADS
from blender.waterfront_skiffs import SKIFFS
ROOT=Path(__file__).resolve().parents[2];LAB=Path('E:/CyberCity2085-3d-lab')
NAME='city_interior_research_lab'

def prepare(source,survey,*,include_side_walls=False):
    original=np.asarray(source.convert('RGB')).copy();height,width=original.shape[:2]
    mask=np.zeros((height,width),dtype=np.uint8)
    sx=width/survey['canvas_size'][0];sy=height/survey['canvas_size'][1]
    for item in survey['walls']:
        if not include_side_walls and item['id'] in ('west_wall','east_wall'):continue
        if item.get('kind') == 'water':continue
        if 'polygon' in item:
            points=np.array([[round(x*sx),round(y*sy)] for x,y in item['polygon']],dtype=np.int32)
            cv2.fillPoly(mask,[points],255)
        elif 'rect' in item:
            x1,y1,x2,y2=item['rect']
            mask[round(y1*sy):round(y2*sy),round(x1*sx):round(x2*sx)]=255
        elif 'points' in item:
            points=np.array([[round(x*sx),round(y*sy)] for x,y in item['points']],dtype=np.int32)
            cv2.polylines(mask,[points],False,255,max(1,round(item['width']*(sx+sy)/2)))
    # Inferred hidden floor, not recovered authentic art. Work at survey scale;
    # write back only masked pixels so original corridors are byte-identical.
    small=cv2.resize(original,tuple(survey['canvas_size']),interpolation=cv2.INTER_AREA)
    smallmask=cv2.resize(mask,tuple(survey['canvas_size']),interpolation=cv2.INTER_NEAREST)
    repaired=cv2.inpaint(small,smallmask,5,cv2.INPAINT_TELEA)
    repaired=cv2.resize(repaired,(width,height),interpolation=cv2.INTER_CUBIC)
    result=original.copy();result[mask>0]=repaired[mask>0]
    return Image.fromarray(result),mask


def restore_surface_detail(floor, mask, sample, tile_size):
    tile = sample.convert("L").resize((tile_size,tile_size), Image.Resampling.LANCZOS)
    soft = tile.filter(ImageFilter.GaussianBlur(max(1, tile_size*.035)))
    detail = ImageChops.subtract(tile, soft, scale=1.35, offset=128)
    texture = Image.new("L", floor.size, 128)
    for row, y in enumerate(range(0, floor.height, tile_size)):
        for column, x in enumerate(range(0, floor.width, tile_size)):
            piece = ImageOps.mirror(detail) if column % 2 else detail
            texture.paste(ImageOps.flip(piece) if row % 2 else piece, (x,y))
    textured = ImageChops.add(floor, Image.merge("RGB", (texture,texture,texture)), offset=-128)
    mask_image = Image.fromarray(mask)
    alpha = ImageChops.multiply(mask_image, mask_image.filter(ImageFilter.GaussianBlur(4)))
    return Image.composite(textured, floor, alpha)


TECH_MARKET_DONORS = {
    "western_canopy": (750, 228, 818, 318),
    "western_red_stall": (458, 493, 508, 550),
    "north_eastern_shops": (1309, 147, 1356, 207),
    "east_corner_shop": (1475, 403, 1520, 461),
    "central_market_stall": (1010, 356, 1076, 436),
    "east_center_market": (1320, 616, 1414, 648),
    "south_center_market": (1062, 904, 1120, 980),
    "southeast_large_canopy": (1414, 836, 1460, 914),
}

# Sample clean asphalt on each original. Restrict the transferred grain to
# vehicle footprints on the road, leaving the dirt shoulder repairs alone.
ROAD_GRAIN_SAMPLES = {
    "_ruined_downtown": ((453,247,483,281), (0,540)),
    "_downtown_intersection": ((449,215,472,243), (0,540)),
    "_parking_garage": ((285,213,309,239), (0,540)),
    "_convoy_crossing": ((202,209,230,230), (221,291)),
    "_wrecked_highway": ((453,281,484,307), (190,345)),
}

WATERFRONT_WRECKS = (
    {"id": "west_edge_wreck_art", "polygon": [
        (0,385), (40,364), (86,353), (153,340), (203,339),
        (214,351), (202,387), (159,426), (79,474), (0,503),
    ]},
    {"id": "west_basin_wreck_art", "polygon": [
        (251,470), (257,450), (319,384), (337,380), (352,391),
        (352,418), (303,491), (275,501), (247,475),
    ]},
    {"id": "east_basin_wreck_art", "polygon": [
        (511,479), (512,404), (521,363), (542,350), (566,354),
        (580,369), (575,439), (560,495), (532,511),
    ]},
)

DOWNTOWN_WRECK_ART = (
    {"id": "east_curb_wreck_art", "polygon": [
        (582,182), (639,171), (648,174), (696,165), (708,184),
        (697,198), (645,205), (586,208),
    ]},
    {"id": "north_edge_wreck_art", "polygon": [
        (544,40), (579,16), (600,31), (592,51), (556,68), (542,58),
    ]},
    {"id": "south_crossing_wreck_art", "polygon": [
        (503,386), (518,371), (553,399), (565,415), (549,435), (522,410),
    ]},
    {"id": "west_curb_wreck_art", "polygon": [
        (246,325), (281,324), (310,338), (308,353), (282,361), (244,353),
    ]},
)

BURNED_MARKET_AWNING_ART = (
    {"id": "stall_north_awning_art", "polygon": [
        (325,68), (379,68), (385,96), (371,103), (326,99),
    ]},
    {"id": "stall_east_awning_art", "polygon": [
        (709,313), (730,317), (739,351), (730,369), (714,364),
    ]},
)

FLOODED_CIVIC_WRECK_ART = (
    {"id": "southwest_curb_wreck_art", "polygon": [
        (88,402), (98,386), (125,375), (144,388), (135,402), (107,426), (93,423),
    ]},
    {"id": "north_curb_wreck_art", "polygon": [
        (578,101), (593,79), (609,73), (621,83), (615,99), (593,123), (583,118),
    ]},
)


def restore_donor_pavement(floor, original, survey, donors):
    floor = floor.copy()
    original = original.convert("RGB")
    cw, ch = survey["canvas_size"]
    sx, sy = floor.width/cw, floor.height/ch

    def pixel(point):
        return round(point[0]*sx), round(point[1]*sy)

    for row in survey["walls"]:
        if row["id"] not in donors:
            continue
        x1,y1,x2,y2 = donors[row["id"]]
        donor = original.crop((*pixel((x1,y1)), *pixel((x2,y2))))
        points = None
        if "rect" in row:
            x1, y1, x2, y2 = row["rect"]
            left, top = pixel((x1, y1))
            right, bottom = pixel((x2, y2))
        else:
            points = [pixel(point) for point in row["polygon"]]
            xs, ys = zip(*points)
            left, top = min(xs), min(ys)
            right, bottom = max(xs)+1, max(ys)+1
        patch = Image.new("RGB", (right-left,bottom-top))
        mirror = ImageOps.mirror(donor)
        for iy,y in enumerate(range(0,patch.height,donor.height)):
            for ix,x in enumerate(range(0,patch.width,donor.width)):
                tile = mirror if ix % 2 else donor
                patch.paste(ImageOps.flip(tile) if iy % 2 else tile, (x,y))
        mask = Image.new("L", patch.size, 255 if points is None else 0)
        if points is not None:
            ImageDraw.Draw(mask).polygon([(x-left,y-top) for x,y in points], fill=255)
        # Fade inward from the outline so the donor cannot create a sharp
        # brightness step where its paving meets the original floor.
        padded = np.pad(np.asarray(mask), 1)
        distance = cv2.distanceTransform(padded, cv2.DIST_L2, 5)[1:-1, 1:-1]
        feather = max(2, min(8*min(sx, sy), min(patch.size)/4))
        weight = np.clip((distance-1)/feather, 0, 1)
        weight = weight*weight*(3-2*weight)
        alpha = Image.fromarray(np.rint(weight*(255*.82)).astype(np.uint8))
        floor.paste(patch,(left,top),alpha)
    return floor

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--map',default=NAME)
    parser.add_argument('--output',type=Path,default=LAB/'generated/phase2/lab248')
    parser.add_argument('--objects',help='Comma-separated identifiers of actual 3D replacements')
    parser.add_argument('--include-side-walls',action='store_true',help='Mask replaced east and west wall drawings')
    parser.add_argument('--decorative-rects', type=json.loads, default=[],
                        help='Additional decoration footprints in survey coordinates')
    parser.add_argument('--surface-detail', type=Path,
                        help='Apply fine material detail inside the repaired footprints')
    args=parser.parse_args()
    if Path(args.map).name!=args.map or '/' in args.map or '\\' in args.map:raise ValueError('Invalid map identifier')
    source=ROOT/f'assets/maps/{args.map}.png';raw=source.read_bytes()
    survey=json.loads((ROOT/f'assets/maps/{args.map}.wall-traces.json').read_text())
    if args.objects:
        requested=set(args.objects.split(','));known={r['id'] for r in survey['walls']}
        if not requested<=known:raise ValueError('Unknown source object identifiers')
        survey['walls']=[r for r in survey['walls'] if r['id'] in requested]
    survey['walls'].extend(args.decorative_rects)
    if args.map == "wasteland_city_11_ruined_transit_plaza":
        survey["walls"].append({"id": "south_carriage_art", "rect": [347, 453, 613, 502]})
    if args.map == "wasteland_city_12_cratered_waterfront":
        survey["walls"].extend(WATERFRONT_WRECKS)
        survey["walls"].append({"id": "fallen_crane_jib_art", "polygon": [
            (778,493), (803,455), (872,383), (913,333), (959,293),
            (959,321), (926,353), (891,403), (824,479), (803,510),
        ]})
        for label, stern, bow, beam in SKIFFS:
            dx, dy = bow[0]-stern[0], bow[1]-stern[1]
            span = math.hypot(dx,dy)
            half = beam*.86 / span
            pad = 4 / span
            start = (stern[0]-dx*pad, stern[1]-dy*pad)
            end = (bow[0]+dx*pad, bow[1]+dy*pad)
            survey["walls"].append({"id": f"landing_skiff_{label}_art", "polygon": [
                (x-side*dy*half, y+side*dx*half)
                for (x,y),side in ((start,-1),(end,-1),(end,1),(start,1))
            ]})
    if args.map.endswith("_ruined_downtown"):
        survey["walls"].extend(DOWNTOWN_WRECK_ART)
    if args.map.endswith("_burned_market_block"):
        survey["walls"].extend(BURNED_MARKET_AWNING_ART)
    if args.map.endswith("_flooded_civic_square"):
        survey["walls"].extend(FLOODED_CIVIC_WRECK_ART)
    if args.map == "city_industrial_dockside_terminal":
        survey["walls"].extend(
            {"id": label, "polygon": [(2*x, 2*y) for x,y in outline]}
            for label, outline in VESSEL_OUTLINES.items()
        )
    if args.map == "city_transit_freight_yard":
        survey["walls"].extend(
            {"id": f"south_siding_load_{index}", "rect": bounds}
            for index, bounds in enumerate(SOUTH_SIDING_LOADS, 1)
        )
    out=args.output.resolve()
    if not out.is_relative_to((LAB/'generated').resolve()):raise ValueError('Output must remain in E: generated experiments')
    out.mkdir(parents=True,exist_ok=True)
    original = Image.open(source)
    result,mask=prepare(original,survey,include_side_walls=args.include_side_walls)
    if args.map == "city_district_tech_market":
        result = restore_donor_pavement(result, original, survey, TECH_MARKET_DONORS)
        concrete = Image.open(LAB / "sources/environment169/concrete_wall_001/diff.jpg")
        ImageOps.colorize(concrete.convert("L"), "#151f27", "#667685").save(out / "facade_concrete.png")
    if args.surface_detail:
        result = restore_surface_detail(result, mask, Image.open(args.surface_detail), max(16, result.width//40))
    if args.map.endswith("_transit_interchange"):
        cw, ch = survey["canvas_size"]
        sx, sy = result.width/cw, result.height/ch
        shelter_repairs = np.zeros_like(mask)
        for row in survey["walls"]:
            if row["id"].startswith("station_") and "rect" in row:
                left, top, right, bottom = row["rect"]
                shelter_repairs[round(top*sy):round(bottom*sy), round(left*sx):round(right*sx)] = 255
        sample = (170,232,213,248) if args.map.startswith("cybercity_street_06_") else (232,230,276,243)
        left, top, right, bottom = sample
        paving = original.crop((round(left*sx),round(top*sy),round(right*sx),round(bottom*sy)))
        result = restore_surface_detail(result, shelter_repairs & mask, paving, round(28*sx))
    if args.map.endswith(("_scavenger_plaza", "_burned_market_block")):
        cw, ch = survey["canvas_size"]
        sx, sy = result.width/cw, result.height/ch
        plaza_repairs = np.zeros_like(mask)
        for row in survey["walls"]:
            identifier = row["id"]
            if (identifier.startswith(("market_", "stall_")) or "ruin" in identifier
                    or identifier in {"ne_corner", "south_stall"}) and "rect" in row:
                x1,y1,x2,y2 = row["rect"]
                plaza_repairs[round(y1*sy):round(y2*sy), round(x1*sx):round(x2*sx)] = 255
        sample = (443,309,488,350) if args.map.endswith("_scavenger_plaza") else (369,275,414,316)
        left, top, right, bottom = sample
        paving = original.crop((round(left*sx),round(top*sy),round(right*sx),round(bottom*sy)))
        result = restore_surface_detail(result, plaza_repairs & mask, paving, round(42*sx))
    if args.map == "wasteland_outdoor_12_salt_flat_ambush":
        cw, ch = survey["canvas_size"]
        sx, sy = result.width/cw, result.height/ch
        sample = original.crop((round(448*sx),round(175*sy),round(495*sx),round(217*sy)))
        result = restore_surface_detail(result, mask, sample, round(46*sx))
    if args.map.endswith("_irradiated_basin"):
        cw, ch = survey["canvas_size"]
        sx, sy = result.width/cw, result.height/ch
        barrel_mask = np.zeros_like(mask)
        for row in survey["walls"]:
            if "barrels" in row["id"] and "rect" in row:
                left, top, right, bottom = row["rect"]
                barrel_mask[round(top*sy):round(bottom*sy), round(left*sx):round(right*sx)] = 255
        gravel = original.crop((round(706*sx),round(479*sy),round(738*sx),round(510*sy)))
        result = restore_surface_detail(result, barrel_mask & mask, gravel, round(32*sx))
    for suffix, (sample_rect, road_rows) in ROAD_GRAIN_SAMPLES.items():
        if not args.map.endswith(suffix):
            continue
        cw, ch = survey["canvas_size"]
        sx, sy = result.width/cw, result.height/ch
        road_repairs = np.zeros_like(mask)
        for row in survey["walls"]:
            if row["id"].startswith(("car_", "wreck_", "bus_", "truck_", "convoy_")) and "rect" in row:
                x1,y1,x2,y2 = row["rect"]
                top, bottom = max(y1,road_rows[0]), min(y2,road_rows[1])
                road_repairs[round(top*sy):round(bottom*sy), round(x1*sx):round(x2*sx)] = 255
        x1,y1,x2,y2 = sample_rect
        road_sample = original.crop((round(x1*sx),round(y1*sy),round(x2*sx),round(y2*sy)))
        result = restore_surface_detail(result, road_repairs & mask, road_sample, round(32*sx))
    if args.map == "city_transit_freight_yard":
        # Recover paving grain without pasting a second set of rails or lamps.
        cw, ch = survey["canvas_size"]
        sx, sy = result.width/cw, result.height/ch
        crane_mask = np.zeros_like(mask)
        for row in survey["walls"]:
            if row["id"].startswith("crane_"):
                x1,y1,x2,y2 = row["rect"]
                crane_mask[round(y1*sy):round(y2*sy),round(x1*sx):round(x2*sx)] = 255
        for top, bottom in ((130,156), (328,352)):
            crane_mask[round(top*sy):round(bottom*sy)] = 0
        sample = original.crop((round(455*sx),round(176*sy),round(489*sx),round(214*sy)))
        result = restore_surface_detail(result, crane_mask & mask, sample, round(34*sx))
        # Continue the original sleeper pattern through the masked crossings.
        # Match the source row so both sides of each track stay aligned.
        crossing_donors = {
            "crane_n": (646,130,695,156),
            "crane_w": (151,328,192,352),
            "crane_c": (539,328,580,352),
        }
        crossings = []
        for row in survey["walls"]:
            if row["id"] in crossing_donors:
                x1,y1,x2,y2 = row["rect"]
                _,top,_,bottom = crossing_donors[row["id"]]
                crossings.append({"id": row["id"], "rect": [max(x1,83),max(y1,top),x2,min(y2,bottom)]})
        result = restore_donor_pavement(result, original, {**survey, "walls": crossings}, crossing_donors)
    if args.map.endswith("_rusted_trainyard"):
        result = restore_donor_pavement(result, original, survey, {"wagon_turntable": (642,196,710,232)})
    if args.map == "wasteland_city_11_ruined_transit_plaza":
        # Sample the same horizontal track so the rail and sleeper heights
        # line up across the area formerly occupied by the painted car.
        result = restore_donor_pavement(result, original, survey,
                                        {"south_carriage_art": (52,453,256,502)})
    if args.map.endswith("_flooded_civic_square"):
        sx = result.width / survey["canvas_size"][0]
        sy = result.height / survey["canvas_size"][1]
        curb_repairs = np.zeros_like(mask)
        for row in FLOODED_CIVIC_WRECK_ART:
            points = np.array([(round(x*sx), round(y*sy)) for x,y in row["polygon"]],
                              dtype=np.int32)
            cv2.fillPoly(curb_repairs, [points], 255)
        paving = original.crop((round(436*sx), round(310*sy), round(474*sx), round(344*sy)))
        result = restore_surface_detail(result, curb_repairs & mask, paving, round(36*sx))
    if args.map.endswith("_burned_market_block"):
        result = restore_donor_pavement(result, original, survey, {
            "stall_north_awning_art": (369,275,414,316),
            "stall_east_awning_art": (743,280,778,321),
        })
    if args.map.endswith("_ruined_downtown"):
        result = restore_donor_pavement(result, original, survey, {
            "east_curb_wreck_art": (664,207,709,237),
            "north_edge_wreck_art": (447,48,476,91),
            "south_crossing_wreck_art": (485,439,514,471),
            "west_curb_wreck_art": (161,315,196,342),
        })
        sx = result.width / survey["canvas_size"][0]
        sy = result.height / survey["canvas_size"][1]
        wreck_repairs = np.zeros_like(mask)
        for row in DOWNTOWN_WRECK_ART:
            points = np.array([(round(x*sx), round(y*sy)) for x,y in row["polygon"]],
                              dtype=np.int32)
            cv2.fillPoly(wreck_repairs, [points], 255)
        result = restore_surface_detail(result, wreck_repairs & mask, road_sample, round(32*sx))
    if args.map == "wasteland_city_12_cratered_waterfront":
        water_donors = {
            "west_edge_wreck_art": (98, 472, 200, 535),
            "west_basin_wreck_art": (204, 418, 247, 468),
            "east_basin_wreck_art": (455, 421, 505, 473),
        }
        water_donors.update({
            f"landing_skiff_{label}_art": (581, 355, 601, 380)
            for label, *_ in SKIFFS
        })
        result = restore_donor_pavement(result, original, survey, water_donors)
        # Keep the dock repair on the land side of the shoreline.
        dock = {"id": "crane_dock_paving", "polygon": [
            (810,447), (872,383), (913,333), (959,293), (959,321),
            (926,353), (891,403), (839,458), (806,466),
        ]}
        result = restore_donor_pavement(result, original, {**survey, "walls": [dock]},
                                        {"crane_dock_paving": (861,145,902,176)})
    if args.map == "city_industrial_dockside_terminal":
        result = restore_donor_pavement(result, original, survey, {
            "North moored cargo vessel": (264, 444, 322, 604),
            "South moored cargo vessel": (270, 860, 330, 1030),
        })
    result.save(out/'floor.png')
    Image.fromarray(mask).save(out/'replacement_mask.png')
    assert source.read_bytes()==raw
    (out/'floor.json').write_text(json.dumps({'source_sha256':hashlib.sha256(raw).hexdigest(),'method':'Inferred floor only inside surveyed replacement rectangles; original corridors retained','masked_pixels':int(np.count_nonzero(mask))},indent=2))
    print('LAB248_FLOOR_PREPARED',int(np.count_nonzero(mask)))

if __name__=='__main__':main()
