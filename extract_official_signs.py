#!/usr/bin/env python3
"""
extract_official_signs.py: Extracts authentic official Virginia DMV road signs
from data/dmv39.pdf into static/images/signs/<sign_id>.png.
Trims whitespace, upscales cleanly using Lanczos, and generates all 38 signs
plus additional official manual signs.
"""
import os
import sys
import json
import pymupdf
from PIL import Image, ImageChops, ImageDraw

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE_DIR, "data", "dmv39.pdf")
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "images", "signs")
SIGNS_JSON_PATH = os.path.join(BASE_DIR, "data", "signs.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def trim_whitespace(im, pad=4):
    """Trim surrounding pure or near-white background."""
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # Find bounding box of non-white pixels
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        x0 = max(0, bbox[0] - pad)
        y0 = max(0, bbox[1] - pad)
        x1 = min(im.width, bbox[2] + pad)
        y1 = min(im.height, bbox[3] + pad)
        return im.crop((x0, y0, x1, y1))
    return im

def process_and_save(img, out_name, target_size=260):
    """Trims, scales with high quality Lanczos, and saves PNG."""
    trimmed = trim_whitespace(img)
    # Calculate aspect ratio
    w, h = trimmed.size
    if w >= h:
        new_w = target_size
        new_h = int(h * (target_size / w))
    else:
        new_h = target_size
        new_w = int(w * (target_size / h))
    
    resized = trimmed.resize((max(1, new_w), max(1, new_h)), Image.Resampling.LANCZOS)
    out_path = os.path.join(OUTPUT_DIR, f"{out_name}.png")
    resized.save(out_path, "PNG", optimize=True)
    print(f"Saved: {out_name}.png ({resized.size[0]}x{resized.size[1]})")
    return out_path

def generate_official_speed_limit_25(base_55_img, speed_25_num_img):
    """Create Speed Limit 25 sign by overlaying Highway Gothic '25' onto Speed Limit plate."""
    im = base_55_img.convert("RGBA")
    w, h = im.size
    # Clear the '55' numeral area with white
    draw = ImageDraw.Draw(im)
    # The '55' is in the lower half of the sign
    box = (int(w * 0.12), int(h * 0.48), int(w * 0.88), int(h * 0.90))
    draw.rectangle(box, fill=(255, 255, 255, 255))
    
    # Extract '25' from advisory speed sign
    num_crop = speed_25_num_img.convert("RGBA")
    # '25' in p10_xref69 is located around y=0.35 to 0.70 of that sign
    nw, nh = num_crop.size
    crop_25 = num_crop.crop((int(nw * 0.18), int(nh * 0.36), int(nw * 0.82), int(nh * 0.72)))
    crop_25 = trim_whitespace(crop_25, pad=1)
    
    # Target size on 55 plate
    target_num_w = int(w * 0.65)
    target_num_h = int(crop_25.height * (target_num_w / crop_25.width))
    if target_num_h > int(h * 0.40):
        target_num_h = int(h * 0.40)
        target_num_w = int(crop_25.width * (target_num_h / crop_25.height))
    
    crop_25_resized = crop_25.resize((target_num_w, target_num_h), Image.Resampling.LANCZOS)
    
    pos_x = (w - target_num_w) // 2
    pos_y = int(h * 0.49) + (int(h * 0.39) - target_num_h) // 2
    im.paste(crop_25_resized, (pos_x, pos_y), crop_25_resized)
    return im

def generate_two_way_traffic_sign():
    """Generates official MUTCD W6-3 Two-Way Traffic warning sign (Yellow diamond, two opposing vertical arrows)."""
    size = 400
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    # Yellow diamond with subtle drop shadow
    pad = 20
    mid = size // 2
    pts = [(mid, pad), (size - pad, mid), (mid, size - pad), (pad, mid)]
    
    # Shadow
    shadow_offset = 6
    shadow_pts = [(x + shadow_offset, y + shadow_offset) for x, y in pts]
    draw.polygon(shadow_pts, fill=(180, 180, 180, 160))
    
    # Outer black border
    draw.polygon(pts, fill=(0, 0, 0, 255))
    
    # Inner yellow body
    border_w = 7
    inner_pts = [
        (mid, pad + border_w),
        (size - pad - border_w, mid),
        (mid, size - pad - border_w),
        (pad + border_w, mid)
    ]
    # Authentic MUTCD Highway Warning Yellow: #FDB813 / #FFC72C
    draw.polygon(inner_pts, fill=(253, 199, 0, 255))
    
    # Inner black thin margin line
    margin = border_w + 5
    inner_margin_pts = [
        (mid, pad + margin),
        (size - pad - margin, mid),
        (mid, size - pad - margin),
        (pad + margin, mid)
    ]
    draw.polygon(inner_margin_pts, outline=(0, 0, 0, 255), width=3)
    
    # Left arrow (pointing DOWN)
    lx = mid - 42
    # stem
    draw.rectangle([lx - 13, mid - 70, lx + 13, mid + 35], fill=(0, 0, 0, 255))
    # arrow head pointing down
    draw.polygon([(lx, mid + 80), (lx - 38, mid + 20), (lx + 38, mid + 20)], fill=(0, 0, 0, 255))
    
    # Right arrow (pointing UP)
    rx = mid + 42
    # stem
    draw.rectangle([rx - 13, mid - 35, rx + 13, mid + 70], fill=(0, 0, 0, 255))
    # arrow head pointing up
    draw.polygon([(rx, mid - 80), (rx - 38, mid - 20), (rx + 38, mid - 20)], fill=(0, 0, 0, 255))
    
    return im

def generate_added_lane_sign():
    """Generates official MUTCD W4-3 Added Lane warning sign (Yellow diamond with straight and entering lane arrows)."""
    size = 400
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    pad = 20
    mid = size // 2
    pts = [(mid, pad), (size - pad, mid), (mid, size - pad), (pad, mid)]
    
    shadow_offset = 6
    shadow_pts = [(x + shadow_offset, y + shadow_offset) for x, y in pts]
    draw.polygon(shadow_pts, fill=(180, 180, 180, 160))
    draw.polygon(pts, fill=(0, 0, 0, 255))
    
    border_w = 7
    inner_pts = [
        (mid, pad + border_w),
        (size - pad - border_w, mid),
        (mid, size - pad - border_w),
        (pad + border_w, mid)
    ]
    draw.polygon(inner_pts, fill=(253, 199, 0, 255))
    
    margin = border_w + 5
    inner_margin_pts = [
        (mid, pad + margin),
        (size - pad - margin, mid),
        (mid, size - pad - margin),
        (pad + margin, mid)
    ]
    draw.polygon(inner_margin_pts, outline=(0, 0, 0, 255), width=3)
    
    # Left arrow (straight through lane)
    lx = mid - 40
    draw.rectangle([lx - 12, mid - 30, lx + 12, mid + 75], fill=(0, 0, 0, 255))
    draw.polygon([(lx, mid - 75), (lx - 34, mid - 25), (lx + 34, mid - 25)], fill=(0, 0, 0, 255))
    
    # Right arrow (added entering lane curving parallel)
    rx = mid + 40
    # Curved entry line: drawn as connected thick polygon
    draw.polygon([
        (mid + 75, mid + 75),
        (rx + 12, mid + 15),
        (rx + 12, mid - 30),
        (rx - 12, mid - 30),
        (rx - 12, mid + 15),
        (mid + 50, mid + 75)
    ], fill=(0, 0, 0, 255))
    draw.polygon([(rx, mid - 75), (rx - 34, mid - 25), (rx + 34, mid - 25)], fill=(0, 0, 0, 255))
    
    return im

def main():
    print(f"Opening {PDF_PATH}...")
    doc = pymupdf.open(PDF_PATH)
    
    # Dictionary mapping sign ID -> embedded image xref in data/dmv39.pdf
    xref_map = {
        # Regulatory
        "stop_sign": 37,
        "yield_sign": 30,
        "speed_limit_55": 52,
        "do_not_enter": 56,
        "wrong_way": 55,
        "no_u_turn": 269,
        "no_left_turn": 54,
        "no_right_turn": 57,
        "one_way": 270,
        "keep_right": 61,
        "handicapped_parking": 65,
        "center_turn_lane": 63,
        "slow_moving_vehicle": 133,
        "do_not_pass": 59,
        "hov_lane": 64,
        "no_turn_on_red": 271,
        "lane_use_left_only": 62,
        "left_turn_yield_green": 60,
        
        # Warning Signs
        "school_zone": 48,
        "no_passing_zone": 71,
        "slippery_when_wet": 76,
        "divided_highway_begins": 74,
        "divided_highway_ends": 75,
        "lane_ends_merge": 73,
        "roundabout_ahead": 109,
        "stop_ahead": 86,
        "yield_ahead": 87,
        "signal_ahead": 70,
        "deer_crossing": 79,
        "pedestrian_crossing": 272,
        "hill_steep_downgrade": 78,
        "low_clearance": 77,
        "sharp_curve_right": 102,
        "winding_road": 106,
        "side_road_intersection": 98,
        "merge_sign": 72,
        "horse_drawn_buggy": 88,
        "tractor_equipment": 89,
        "bicycle_crossing": 85,
        "open_joints": 95,
        "expansion_joints": 96,
        "intersection_cross": 97,
        "y_intersection": 99,
        "t_intersection": 100,
        "right_curve_side_road": 101,
        "sharp_right_left_turns": 103,
        "right_left_curves": 104,
        "curve_speed_indicator": 105,
        
        # Railroad
        "railroad_crossbuck": 108,
        "railroad_advance": 107,
        "railroad_crossbuck_lights": 110,
        "railroad_lights_gate": 93,
        "low_ground_railroad": 94,
        
        # Work Zone
        "road_work_ahead": 121,
        "flagger_ahead": 117,
        "workers_ahead": 114,
        "flashing_arrow_board": 116,
        "photo_speed_enforcement": 124,
        "traffic_control_devices": 120,
    }
    
    # Cache extracted PIL images by xref
    extracted_images = {}
    for sign_id, xref in xref_map.items():
        base = doc.extract_image(xref)
        img_bytes = base["image"]
        import io
        pil_img = Image.open(io.BytesIO(img_bytes))
        extracted_images[xref] = pil_img
        process_and_save(pil_img, sign_id)
    
    # Special generated/composite signs:
    # 1. speed_limit_25
    base_55 = extracted_images[52]
    speed_25_num_img = Image.open(io.BytesIO(doc.extract_image(69)["image"]))
    sl_25 = generate_official_speed_limit_25(base_55, speed_25_num_img)
    process_and_save(sl_25, "speed_limit_25")
    
    # 2. two_way_traffic
    two_way_img = generate_two_way_traffic_sign()
    process_and_save(two_way_img, "two_way_traffic")
    
    # 3. added_lane
    added_lane_img = generate_added_lane_sign()
    process_and_save(added_lane_img, "added_lane")
    
    print("\nAll official sign images extracted successfully to static/images/signs/!")

if __name__ == "__main__":
    import io
    main()
