#!/usr/bin/env python3
"""
generate_data.py
Builds authentic Virginia DMV Learner's Permit knowledge test data:
- signs.json: 36+ detailed road signs with SVG vector graphics, shapes, colors, official definitions
- questions_signs.json: 45 authentic Part 1 sign questions (100% passing required)
- questions_general.json: 75 authentic Part 2 general knowledge questions (80% passing required)
- cheat_sheet.json: Fast-recall tables of Virginia rules, numbers, distances, fines, and signals
"""
import json
import os

SIGNS = [
    {
        "id": "stop_sign",
        "name": "Stop Sign",
        "shape": "Octagon (8-sided)",
        "color": "Red with white letters and border",
        "category": "regulatory",
        "meaning": "Come to a complete stop at the stop line, crosswalk, or before entering the intersection. Yield right-of-way to pedestrians and oncoming traffic before proceeding.",
        "key_rule": "You must come to a COMPLETE stop. A rolling stop is illegal in Virginia.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="35,5 85,5 115,35 115,85 85,115 35,115 5,85 5,35" fill="#CC0000" stroke="#FFFFFF" stroke-width="4"/><polygon points="36,8 84,8 112,36 112,84 84,112 36,112 8,84 8,36" fill="none" stroke="#FFFFFF" stroke-width="2"/><text x="60" y="69" font-family="Arial Black, Impact, sans-serif" font-size="25" font-weight="900" fill="#FFFFFF" text-anchor="middle" letter-spacing="1">STOP</text></svg>'
    },
    {
        "id": "yield_sign",
        "name": "Yield Sign",
        "shape": "Equilateral Triangle (pointing down)",
        "color": "Red border and white interior with red text",
        "category": "regulatory",
        "meaning": "Slow down as you approach the intersection. Prepare to stop and yield right-of-way to all vehicles and pedestrians before proceeding.",
        "key_rule": "You must stop if necessary to avoid interfering with any traffic with right-of-way.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="10,15 110,15 60,105" fill="#CC0000"/><polygon points="26,24 94,24 60,86" fill="#FFFFFF"/><text x="60" y="47" font-family="Arial Black, Impact, sans-serif" font-size="16" font-weight="900" fill="#CC0000" text-anchor="middle" letter-spacing="1">YIELD</text></svg>'
    },
    {
        "id": "speed_limit_25",
        "name": "Speed Limit 25 MPH",
        "shape": "Vertical Rectangle",
        "color": "White background with black letters and border",
        "category": "regulatory",
        "meaning": "The maximum legal speed in this zone under ideal conditions is 25 MPH. Default limit in Virginia school, business, and residential areas.",
        "key_rule": "In Virginia, 25 MPH is the statutory speed limit for school, business, and residential areas unless otherwise posted.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><rect x="18" y="8" width="84" height="104" rx="8" fill="#FFFFFF" stroke="#000000" stroke-width="4"/><rect x="22" y="12" width="76" height="96" rx="6" fill="none" stroke="#000000" stroke-width="1.5"/><text x="60" y="36" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#000000" text-anchor="middle">SPEED</text><text x="60" y="54" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#000000" text-anchor="middle">LIMIT</text><text x="60" y="98" font-family="Arial Black, Impact, sans-serif" font-size="42" font-weight="900" fill="#000000" text-anchor="middle">25</text></svg>'
    },
    {
        "id": "speed_limit_55",
        "name": "Speed Limit 55 MPH",
        "shape": "Vertical Rectangle",
        "color": "White background with black letters and border",
        "category": "regulatory",
        "meaning": "Maximum legal speed on this highway under normal conditions is 55 MPH. Default limit for paved Virginia state highways.",
        "key_rule": "55 MPH is Virginia statutory maximum on non-interstate highways unless posted otherwise.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><rect x="18" y="8" width="84" height="104" rx="8" fill="#FFFFFF" stroke="#000000" stroke-width="4"/><rect x="22" y="12" width="76" height="96" rx="6" fill="none" stroke="#000000" stroke-width="1.5"/><text x="60" y="36" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#000000" text-anchor="middle">SPEED</text><text x="60" y="54" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#000000" text-anchor="middle">LIMIT</text><text x="60" y="98" font-family="Arial Black, Impact, sans-serif" font-size="42" font-weight="900" fill="#000000" text-anchor="middle">55</text></svg>'
    },
    {
        "id": "school_zone",
        "name": "School Zone / School Crossing",
        "shape": "Pentagon (5-sided, pointing up)",
        "color": "Fluorescent Yellow-Green (or Yellow) with black symbols",
        "category": "school",
        "meaning": "You are near a school or school crossing. Watch for children crossing the street and obey reduced school speed limits (typically 25 MPH when flashing).",
        "key_rule": "Pentagon shape is exclusively reserved for school zone and school crossing warnings in Virginia.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,8 112,46 112,110 8,110 8,46" fill="#CCFF00" stroke="#000000" stroke-width="4"/><polygon points="60,14 106,48 106,104 14,104 14,48" fill="none" stroke="#000000" stroke-width="2"/><circle cx="48" cy="45" r="7" fill="#000000"/><path d="M40,60 L56,60 L54,82 L42,82 Z" fill="#000000"/><rect x="42" y="82" width="4" height="16" fill="#000000"/><rect x="50" y="82" width="4" height="16" fill="#000000"/><circle cx="72" cy="52" r="6" fill="#000000"/><path d="M64,65 L80,65 L78,84 L66,84 Z" fill="#000000"/><rect x="66" y="84" width="3.5" height="14" fill="#000000"/><rect x="74" y="84" width="3.5" height="14" fill="#000000"/></svg>'
    },
    {
        "id": "no_passing_zone",
        "name": "No Passing Zone",
        "shape": "Pennant (isosceles triangle pointing right)",
        "color": "Yellow background with black border and letters",
        "category": "warning",
        "meaning": "Posted on the LEFT side of two-lane roads. Indicates the start of a zone where passing other vehicles is prohibited.",
        "key_rule": "Always posted on the LEFT side of the highway facing oncoming traffic.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="10,16 112,60 10,104" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="15,23 102,60 15,97" fill="none" stroke="#000000" stroke-width="2"/><text x="32" y="44" font-family="Arial Black, sans-serif" font-size="11" font-weight="bold" fill="#000000">NO</text><text x="30" y="64" font-family="Arial Black, sans-serif" font-size="10" font-weight="bold" fill="#000000">PASSING</text><text x="32" y="84" font-family="Arial Black, sans-serif" font-size="11" font-weight="bold" fill="#000000">ZONE</text></svg>'
    },
    {
        "id": "railroad_crossbuck",
        "name": "Railroad Crossing Crossbuck",
        "shape": "X-Shape (Crossbuck)",
        "color": "White background with black lettering",
        "category": "railroad",
        "meaning": "Identifies a railroad crossing. Treat as a yield sign; listen and look both ways for oncoming trains. Stop if a train is approaching.",
        "key_rule": "In Virginia, you must stop within 15 to 50 feet of the nearest rail when lights are flashing or a train is approaching.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><g transform="translate(60,60)"><line x1="-50" y1="-50" x2="50" y2="50" stroke="#FFFFFF" stroke-width="20" stroke-linecap="square"/><line x1="-50" y1="50" x2="50" y2="-50" stroke="#FFFFFF" stroke-width="20" stroke-linecap="square"/><line x1="-50" y1="-50" x2="50" y2="50" stroke="#000000" stroke-width="22" stroke-linecap="square" style="opacity:0.2"/><line x1="-50" y1="-50" x2="50" y2="50" stroke="#000000" stroke-width="1.5"/><line x1="-50" y1="50" x2="50" y2="-50" stroke="#000000" stroke-width="1.5"/><text transform="rotate(45)" x="0" y="4" font-family="Arial Black, sans-serif" font-size="9.5" font-weight="900" fill="#000000" text-anchor="middle">RAILROAD</text><text transform="rotate(-45)" x="0" y="4" font-family="Arial Black, sans-serif" font-size="9.5" font-weight="900" fill="#000000" text-anchor="middle">CROSSING</text></g></svg>'
    },
    {
        "id": "railroad_advance",
        "name": "Railroad Advance Warning",
        "shape": "Round (Circle)",
        "color": "Yellow background with black X and letters RR",
        "category": "railroad",
        "meaning": "Alerts drivers that a railroad crossing is ahead. Slow down, listen, and look both directions for approaching trains.",
        "key_rule": "The round shape is exclusively used for advance warning of railroad crossings.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><circle cx="60" cy="60" r="52" fill="#FFCC00" stroke="#000000" stroke-width="4"/><circle cx="60" cy="60" r="47" fill="none" stroke="#000000" stroke-width="2"/><line x1="26" y1="26" x2="94" y2="94" stroke="#000000" stroke-width="6"/><line x1="26" y1="94" x2="94" y2="26" stroke="#000000" stroke-width="6"/><text x="32" y="67" font-family="Arial Black, sans-serif" font-size="22" font-weight="900" fill="#000000" text-anchor="middle">R</text><text x="88" y="67" font-family="Arial Black, sans-serif" font-size="22" font-weight="900" fill="#000000" text-anchor="middle">R</text></svg>'
    },
    {
        "id": "do_not_enter",
        "name": "Do Not Enter",
        "shape": "Square with interior red circle",
        "color": "Red circle on white background with white bar and white text",
        "category": "regulatory",
        "meaning": "Do not drive onto this ramp, street, or lane. Traffic is moving in the opposite direction toward you.",
        "key_rule": "Commonly posted at freeway exit ramps and one-way streets to prevent head-on collisions.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><rect x="10" y="10" width="100" height="100" rx="8" fill="#FFFFFF" stroke="#000000" stroke-width="3"/><circle cx="60" cy="60" r="46" fill="#CC0000"/><rect x="22" y="52" width="76" height="16" fill="#FFFFFF"/><text x="60" y="38" font-family="Arial Black, sans-serif" font-size="11" font-weight="900" fill="#FFFFFF" text-anchor="middle">DO NOT</text><text x="60" y="87" font-family="Arial Black, sans-serif" font-size="12" font-weight="900" fill="#FFFFFF" text-anchor="middle">ENTER</text></svg>'
    },
    {
        "id": "wrong_way",
        "name": "Wrong Way",
        "shape": "Horizontal Rectangle",
        "color": "Red background with white letters and border",
        "category": "regulatory",
        "meaning": "You are driving in the wrong direction against oncoming traffic. Immediately pull off to the side, stop, and turn around when safe.",
        "key_rule": "Accompanies Do Not Enter signs on highway off-ramps.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><rect x="8" y="24" width="104" height="72" rx="6" fill="#CC0000" stroke="#FFFFFF" stroke-width="4"/><rect x="12" y="28" width="96" height="64" rx="4" fill="none" stroke="#FFFFFF" stroke-width="2"/><text x="60" y="53" font-family="Arial Black, sans-serif" font-size="14" font-weight="900" fill="#FFFFFF" text-anchor="middle">WRONG</text><text x="60" y="78" font-family="Arial Black, sans-serif" font-size="16" font-weight="900" fill="#FFFFFF" text-anchor="middle">WAY</text></svg>'
    },
    {
        "id": "no_u_turn",
        "name": "No U-Turn",
        "shape": "Square",
        "color": "White background, black U-turn arrow, red prohibition circle and slash",
        "category": "regulatory",
        "meaning": "Making a 180-degree turn (U-turn) to travel in the opposite direction is prohibited at this location.",
        "key_rule": "Red circle with a diagonal slash always signifies an action is strictly prohibited.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><rect x="10" y="10" width="100" height="100" rx="8" fill="#FFFFFF" stroke="#000000" stroke-width="3"/><path d="M42,80 L42,52 A18,18 0 0,1 78,52 L78,80" fill="none" stroke="#000000" stroke-width="8"/><polygon points="34,76 42,92 50,76" fill="#000000"/><circle cx="60" cy="60" r="42" fill="none" stroke="#CC0000" stroke-width="8"/><line x1="30" y1="30" x2="90" y2="90" stroke="#CC0000" stroke-width="8"/></svg>'
    },
    {
        "id": "no_left_turn",
        "name": "No Left Turn",
        "shape": "Square",
        "color": "White background, black arrow, red circle and slash",
        "category": "regulatory",
        "meaning": "You must not turn left at this intersection or entrance.",
        "key_rule": "Obey turn restrictions even when there is no cross traffic.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><rect x="10" y="10" width="100" height="100" rx="8" fill="#FFFFFF" stroke="#000000" stroke-width="3"/><path d="M70,82 L70,55 Q70,45 55,45 L38,45" fill="none" stroke="#000000" stroke-width="8"/><polygon points="40,36 24,45 40,54" fill="#000000"/><circle cx="60" cy="60" r="42" fill="none" stroke="#CC0000" stroke-width="8"/><line x1="30" y1="30" x2="90" y2="90" stroke="#CC0000" stroke-width="8"/></svg>'
    },
    {
        "id": "no_right_turn",
        "name": "No Right Turn",
        "shape": "Square",
        "color": "White background, black arrow, red circle and slash",
        "category": "regulatory",
        "meaning": "You must not make a right turn at this intersection or roadway.",
        "key_rule": "Includes right turn on red restrictions unless signs state otherwise.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><rect x="10" y="10" width="100" height="100" rx="8" fill="#FFFFFF" stroke="#000000" stroke-width="3"/><path d="M50,82 L50,55 Q50,45 65,45 L82,45" fill="none" stroke="#000000" stroke-width="8"/><polygon points="80,36 96,45 80,54" fill="#000000"/><circle cx="60" cy="60" r="42" fill="none" stroke="#CC0000" stroke-width="8"/><line x1="30" y1="30" x2="90" y2="90" stroke="#CC0000" stroke-width="8"/></svg>'
    },
    {
        "id": "one_way",
        "name": "One Way",
        "shape": "Horizontal Rectangle",
        "color": "Black background with white arrow and black text (or white with black arrow)",
        "category": "regulatory",
        "meaning": "Traffic is permitted to travel only in the direction indicated by the arrow.",
        "key_rule": "When turning onto a one-way street, turn into the nearest available lane.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><rect x="6" y="36" width="108" height="48" rx="4" fill="#000000" stroke="#FFFFFF" stroke-width="2"/><polygon points="12,50 82,50 82,40 108,60 82,80 82,70 12,70" fill="#FFFFFF"/><text x="48" y="65" font-family="Arial Black, sans-serif" font-size="11" font-weight="900" fill="#000000" text-anchor="middle">ONE WAY</text></svg>'
    },
    {
        "id": "slippery_when_wet",
        "name": "Slippery When Wet",
        "shape": "Diamond",
        "color": "Yellow background with black symbol",
        "category": "warning",
        "meaning": "The road surface becomes unusually slippery when wet. Slow down, avoid sudden turns or hard braking.",
        "key_rule": "Pavement is most slippery during the first 10-15 minutes after rain begins due to oil buildup.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><rect x="44" y="38" width="32" height="16" rx="4" fill="#000000"/><circle cx="50" cy="56" r="5" fill="#000000"/><circle cx="70" cy="56" r="5" fill="#000000"/><path d="M48,64 Q42,72 52,78 T46,92" fill="none" stroke="#000000" stroke-width="3" stroke-linecap="round"/><path d="M72,64 Q66,72 76,78 T70,92" fill="none" stroke="#000000" stroke-width="3" stroke-linecap="round"/></svg>'
    },
    {
        "id": "divided_highway_begins",
        "name": "Divided Highway Begins",
        "shape": "Diamond",
        "color": "Yellow background with black symbols",
        "category": "warning",
        "meaning": "The highway ahead splits into two separate one-way roadways separated by a physical median island. Keep to the right side of the divider.",
        "key_rule": "Median island is located between opposing traffic flows. Keep to the right.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><path d="M52,28 A8,8 0 0,1 68,28 L66,48 A6,6 0 0,1 54,48 Z" fill="#000000"/><path d="M40,88 L40,48 Q40,36 48,34" fill="none" stroke="#000000" stroke-width="5" stroke-linecap="round"/><polygon points="34,48 40,34 46,48" fill="#000000"/><path d="M80,34 L80,74 Q80,86 72,88" fill="none" stroke="#000000" stroke-width="5" stroke-linecap="round"/><polygon points="86,74 80,88 74,74" fill="#000000"/></svg>'
    },
    {
        "id": "divided_highway_ends",
        "name": "Divided Highway Ends",
        "shape": "Diamond",
        "color": "Yellow background with black symbols",
        "category": "warning",
        "meaning": "The physical median divider is ending ahead. The roadway transitions back to two-way traffic on an undivided roadway.",
        "key_rule": "Watch for opposing oncoming traffic sharing the same undivided pavement.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><path d="M52,92 A8,8 0 0,0 68,92 L66,72 A6,6 0 0,0 54,72 Z" fill="#000000"/><path d="M40,32 L40,72 Q40,84 48,86" fill="none" stroke="#000000" stroke-width="5" stroke-linecap="round"/><polygon points="34,46 40,32 46,46" fill="#000000"/><path d="M80,88 L80,48 Q80,36 72,34" fill="none" stroke="#000000" stroke-width="5" stroke-linecap="round"/><polygon points="86,74 80,88 74,74" fill="#000000"/></svg>'
    },
    {
        "id": "two_way_traffic",
        "name": "Two-Way Traffic",
        "shape": "Diamond",
        "color": "Yellow background with black opposing arrows",
        "category": "warning",
        "meaning": "You are leaving a one-way roadway and entering a roadway with traffic traveling in both opposing directions. Stay to the right.",
        "key_rule": "Opposing vehicles will be in the oncoming left lane.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><line x1="44" y1="84" x2="44" y2="36" stroke="#000000" stroke-width="6"/><polygon points="36,46 44,28 52,46" fill="#000000"/><line x1="76" y1="36" x2="76" y2="84" stroke="#000000" stroke-width="6"/><polygon points="68,74 76,92 84,74" fill="#000000"/></svg>'
    },
    {
        "id": "lane_ends_merge",
        "name": "Lane Ends / Merge Left",
        "shape": "Diamond",
        "color": "Yellow background with black symbols",
        "category": "warning",
        "meaning": "The right lane is ending ahead. Drivers in the right lane must merge safely into the left lane.",
        "key_rule": "Vehicles already in the continuous left lane have right-of-way; merging vehicles must adjust speed and yield.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><line x1="44" y1="28" x2="44" y2="92" stroke="#000000" stroke-width="6"/><path d="M76,92 L76,65 Q76,46 56,36" fill="none" stroke="#000000" stroke-width="6"/></svg>'
    },
    {
        "id": "roundabout_ahead",
        "name": "Roundabout Ahead",
        "shape": "Diamond",
        "color": "Yellow background with circular arrows",
        "category": "warning",
        "meaning": "Circular intersection (roundabout) ahead. Slow down, yield to pedestrians and traffic already inside the roundabout, and enter counter-clockwise.",
        "key_rule": "In Virginia roundabouts, entering vehicles must yield to traffic already circulating.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><path d="M60,34 A26,26 0 0,1 86,60" fill="none" stroke="#000000" stroke-width="5"/><polygon points="80,56 86,66 92,56" fill="#000000"/><path d="M86,60 A26,26 0 0,1 60,86" fill="none" stroke="#000000" stroke-width="5"/><polygon points="64,80 54,86 64,92" fill="#000000"/><path d="M60,86 A26,26 0 0,1 34,60" fill="none" stroke="#000000" stroke-width="5"/><polygon points="40,64 34,54 28,64" fill="#000000"/><path d="M34,60 A26,26 0 0,1 60,34" fill="none" stroke="#000000" stroke-width="5"/><polygon points="56,40 66,34 56,28" fill="#000000"/></svg>'
    },
    {
        "id": "stop_ahead",
        "name": "Stop Ahead",
        "shape": "Diamond",
        "color": "Yellow background with red octagon and upward arrow",
        "category": "warning",
        "meaning": "A stop sign is coming up ahead. Begin slowing down to ensure you can come to a complete stop before the intersection.",
        "key_rule": "Posted when the upcoming stop sign is hidden by curves, hills, or distance.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><line x1="60" y1="52" x2="60" y2="28" stroke="#000000" stroke-width="6"/><polygon points="50,38 60,24 70,38" fill="#000000"/><polygon points="48,58 72,58 84,70 84,82 72,94 48,94 36,82 36,70" fill="#CC0000" stroke="#FFFFFF" stroke-width="2"/><text x="60" y="80" font-family="Arial Black, sans-serif" font-size="8" font-weight="900" fill="#FFFFFF" text-anchor="middle">STOP</text></svg>'
    },
    {
        "id": "yield_ahead",
        "name": "Yield Ahead",
        "shape": "Diamond",
        "color": "Yellow background with red yield triangle and upward arrow",
        "category": "warning",
        "meaning": "A yield sign is coming up ahead. Prepare to slow down, check for cross traffic, and stop if required.",
        "key_rule": "Prepare to yield right-of-way ahead.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><line x1="60" y1="52" x2="60" y2="28" stroke="#000000" stroke-width="6"/><polygon points="50,38 60,24 70,38" fill="#000000"/><polygon points="40,62 80,62 60,94" fill="#CC0000"/><polygon points="48,66 72,66 60,86" fill="#FFFFFF"/></svg>'
    },
    {
        "id": "signal_ahead",
        "name": "Traffic Signal Ahead",
        "shape": "Diamond",
        "color": "Yellow background with red, yellow, green signal graphic",
        "category": "warning",
        "meaning": "A traffic signal controls the intersection ahead. Be prepared for red lights and stop if necessary.",
        "key_rule": "Often posted on high-speed roads or where sightlines to signals are limited.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><rect x="47" y="32" width="26" height="56" rx="4" fill="#000000"/><circle cx="60" cy="42" r="6" fill="#CC0000"/><circle cx="60" cy="60" r="6" fill="#FFCC00"/><circle cx="60" cy="78" r="6" fill="#00CC44"/></svg>'
    },
    {
        "id": "deer_crossing",
        "name": "Deer Crossing",
        "shape": "Diamond",
        "color": "Yellow background with leaping deer silhouette",
        "category": "warning",
        "meaning": "Deer frequently cross the roadway in this vicinity. Be especially alert at dusk, dawn, and night.",
        "key_rule": "Deer travel in groups; if you see one deer, expect others nearby.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><path d="M42,42 Q48,34 56,40 L64,48 L76,46 L82,40 L84,42 L80,50 L84,54 L80,56 L74,54 L66,66 L74,86 L68,88 L60,72 L50,72 L44,88 L38,86 L44,66 L38,62 Q34,54 42,42 Z" fill="#000000"/></svg>'
    },
    {
        "id": "pedestrian_crossing",
        "name": "Pedestrian Crossing",
        "shape": "Diamond",
        "color": "Fluorescent Yellow-Green or Yellow with walking pedestrian symbol",
        "category": "warning",
        "meaning": "Pedestrians may be crossing the street ahead. Yield right-of-way to all pedestrians in crosswalks.",
        "key_rule": "In Virginia, drivers must yield right-of-way to pedestrians crossing at any marked or unmarked intersection.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#CCFF00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><circle cx="62" cy="38" r="6" fill="#000000"/><path d="M52,54 L64,48 L72,58 L68,64 L62,56 L58,66 L70,84 L64,88 L52,70 L48,86 L42,84 L46,62 Q46,56 52,54 Z" fill="#000000"/><line x1="32" y1="92" x2="88" y2="92" stroke="#000000" stroke-width="3"/></svg>'
    },
    {
        "id": "hill_steep_downgrade",
        "name": "Hill / Steep Downgrade",
        "shape": "Diamond",
        "color": "Yellow background with truck on inclined triangle",
        "category": "warning",
        "meaning": "A steep downhill grade is ahead. Check brakes and shift to a lower gear before beginning your descent.",
        "key_rule": "Shift to a lower gear to let engine braking help control speed and prevent brake fade.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><polygon points="32,84 88,84 32,52" fill="#000000"/><g transform="translate(48,46) rotate(-28)"><rect x="-14" y="-8" width="22" height="12" fill="#000000"/><rect x="8" y="-4" width="8" height="8" fill="#000000"/><circle cx="-8" cy="6" r="3" fill="#000000"/><circle cx="2" cy="6" r="3" fill="#000000"/><circle cx="12" cy="6" r="3" fill="#000000"/></g></svg>'
    },
    {
        "id": "keep_right",
        "name": "Keep Right",
        "shape": "Vertical Rectangle",
        "color": "White background with black angled arrow passing barrier",
        "category": "regulatory",
        "meaning": "A traffic island, median, or obstruction is ahead. You must stay to the right of the divider.",
        "key_rule": "Never pass on the left side of this island unless directed by police or flagger.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><rect x="18" y="8" width="84" height="104" rx="8" fill="#FFFFFF" stroke="#000000" stroke-width="4"/><rect x="22" y="12" width="76" height="96" rx="6" fill="none" stroke="#000000" stroke-width="1.5"/><path d="M48,34 A10,10 0 0,1 68,34 L66,64 A8,8 0 0,1 50,64 Z" fill="#000000"/><path d="M40,94 L40,78 Q40,54 64,42 L72,42" fill="none" stroke="#000000" stroke-width="6"/><polygon points="68,34 82,42 68,50" fill="#000000"/></svg>'
    },
    {
        "id": "road_work_ahead",
        "name": "Road Work Ahead",
        "shape": "Diamond",
        "color": "Orange background with black letters and border",
        "category": "work_zone",
        "meaning": "Highway construction or maintenance work zone ahead. Slow down, obey flaggers, and watch for workers and machinery.",
        "key_rule": "In Virginia, speeding in a highway work zone carries an increased fine of up to $500.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FF7700" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><text x="60" y="48" font-family="Arial Black, sans-serif" font-size="11" font-weight="900" fill="#000000" text-anchor="middle">ROAD</text><text x="60" y="66" font-family="Arial Black, sans-serif" font-size="11" font-weight="900" fill="#000000" text-anchor="middle">WORK</text><text x="60" y="84" font-family="Arial Black, sans-serif" font-size="11" font-weight="900" fill="#000000" text-anchor="middle">AHEAD</text></svg>'
    },
    {
        "id": "flagger_ahead",
        "name": "Flagger Ahead",
        "shape": "Diamond",
        "color": "Orange background with flagger symbol",
        "category": "work_zone",
        "meaning": "Traffic flagger ahead directing traffic. You must follow the flagger's hand signals and paddle directions.",
        "key_rule": "A flagger's instructions override normal traffic signals or signs.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FF7700" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><circle cx="56" cy="38" r="6" fill="#000000"/><line x1="56" y1="44" x2="56" y2="70" stroke="#000000" stroke-width="5"/><line x1="56" y1="52" x2="34" y2="46" stroke="#000000" stroke-width="4"/><polygon points="34,36 34,56 22,46" fill="#CC0000"/><line x1="56" y1="70" x2="48" y2="92" stroke="#000000" stroke-width="4"/><line x1="56" y1="70" x2="64" y2="92" stroke="#000000" stroke-width="4"/></svg>'
    },
    {
        "id": "workers_ahead",
        "name": "Workers Ahead",
        "shape": "Diamond",
        "color": "Orange background with worker silhouette digging",
        "category": "work_zone",
        "meaning": "Workers are on or near the roadway. Stay alert, slow down, and provide extra clearance.",
        "key_rule": "Orange signs designate temporary traffic control and work zones.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FF7700" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><circle cx="48" cy="42" r="6" fill="#000000"/><path d="M48,48 L56,66 L46,84 L40,82 L48,66 L42,54 Z" fill="#000000"/><path d="M54,58 L68,70 L72,66 L58,54 Z" fill="#000000"/><line x1="44" y1="58" x2="82" y2="88" stroke="#000000" stroke-width="3"/><polygon points="80,84 88,90 82,94 76,88" fill="#000000"/></svg>'
    },
    {
        "id": "handicapped_parking",
        "name": "Handicapped Parking Only",
        "shape": "Vertical Rectangle",
        "color": "Blue and white with wheelchair symbol and fine notice",
        "category": "regulatory",
        "meaning": "Reserved strictly for vehicles displaying official disabled parking license plates or disabled placards.",
        "key_rule": "Illegal parking in disabled spaces in Virginia results in fines between $100 and $500.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><rect x="18" y="8" width="84" height="104" rx="8" fill="#FFFFFF" stroke="#0044AA" stroke-width="4"/><rect x="22" y="12" width="76" height="96" rx="6" fill="none" stroke="#0044AA" stroke-width="1.5"/><rect x="28" y="18" width="64" height="60" rx="4" fill="#0044AA"/><circle cx="62" cy="32" r="5" fill="#FFFFFF"/><path d="M58,40 L66,40 L64,54 L76,54" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/><circle cx="56" cy="56" r="10" fill="none" stroke="#FFFFFF" stroke-width="4"/><text x="60" y="92" font-family="Arial, sans-serif" font-size="9" font-weight="bold" fill="#0044AA" text-anchor="middle">RESERVED</text><text x="60" y="103" font-family="Arial, sans-serif" font-size="8" font-weight="bold" fill="#0044AA" text-anchor="middle">PARKING</text></svg>'
    },
    {
        "id": "low_clearance",
        "name": "Low Clearance (12'-6\")",
        "shape": "Diamond",
        "color": "Yellow background with clearance measurement and opposing vertical arrows",
        "category": "warning",
        "meaning": "Overpass or bridge ahead has limited vertical clearance. Vehicles taller than the posted height must not proceed.",
        "key_rule": "Do not enter if vehicle and load exceed the specified clearance height.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><polygon points="60,26 68,36 52,36" fill="#000000"/><polygon points="60,94 68,84 52,84" fill="#000000"/><text x="60" y="66" font-family="Arial Black, sans-serif" font-size="16" font-weight="900" fill="#000000" text-anchor="middle">12\'-6"</text></svg>'
    },
    {
        "id": "sharp_curve_right",
        "name": "Sharp Curve Right (90° Turn)",
        "shape": "Diamond",
        "color": "Yellow background with black sharp right arrow",
        "category": "warning",
        "meaning": "The road ahead makes a sharp 90-degree turn to the right. Reduce speed significantly before entering the turn.",
        "key_rule": "Brake before entering the curve, not while steering sharply through it.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><path d="M46,88 L46,54 L74,54" fill="none" stroke="#000000" stroke-width="8"/><polygon points="70,42 88,54 70,66" fill="#000000"/></svg>'
    },
    {
        "id": "winding_road",
        "name": "Winding Road Ahead",
        "shape": "Diamond",
        "color": "Yellow background with winding arrow curve",
        "category": "warning",
        "meaning": "A series of three or more consecutive curves begins ahead. Drive with caution and reduce speed.",
        "key_rule": "First curve bends in the direction shown at the bottom of the arrow.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><path d="M60,88 Q48,74 60,60 T60,34" fill="none" stroke="#000000" stroke-width="6"/><polygon points="50,42 60,26 70,42" fill="#000000"/></svg>'
    },
    {
        "id": "added_lane",
        "name": "Added Lane (Free Flowing)",
        "shape": "Diamond",
        "color": "Yellow background with continuous parallel lane arrow",
        "category": "warning",
        "meaning": "A new lane enters alongside your roadway without merging. Traffic entering does not need to merge immediately.",
        "key_rule": "Unlike merge signs, added lanes do not require immediate merging into an existing lane.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><line x1="44" y1="92" x2="44" y2="34" stroke="#000000" stroke-width="5"/><polygon points="36,44 44,28 52,44" fill="#000000"/><path d="M78,92 Q78,64 68,48 L68,34" fill="none" stroke="#000000" stroke-width="5"/><polygon points="60,44 68,28 76,44" fill="#000000"/></svg>'
    },
    {
        "id": "side_road_intersection",
        "name": "Side Road Intersection",
        "shape": "Diamond",
        "color": "Yellow background with cross intersection symbol",
        "category": "warning",
        "meaning": "Another road enters the highway from the side ahead. Watch for traffic entering or turning.",
        "key_rule": "Be alert for cross traffic and vehicles pulling onto the highway.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,6 114,60 60,114 6,60" fill="#FFCC00" stroke="#000000" stroke-width="4"/><polygon points="60,12 108,60 60,108 12,60" fill="none" stroke="#000000" stroke-width="1.5"/><line x1="60" y1="28" x2="60" y2="92" stroke="#000000" stroke-width="8"/><line x1="60" y1="60" x2="88" y2="60" stroke="#000000" stroke-width="8"/></svg>'
    },
    {
        "id": "slow_moving_vehicle",
        "name": "Slow-Moving Vehicle Emblem",
        "shape": "Triangle (reflective orange with red border)",
        "color": "Fluorescent orange triangle with dark red reflective border",
        "category": "regulatory",
        "meaning": "Mounted on the rear of vehicles traveling at 25 MPH or slower (such as farm equipment, tractors, road machinery).",
        "key_rule": "Be prepared to slow down rapidly when approaching a vehicle displaying this emblem.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><polygon points="60,12 110,98 10,98" fill="#CC0000"/><polygon points="60,26 98,90 22,90" fill="#FF5500"/></svg>'
    },
    {
        "id": "center_turn_lane",
        "name": "Center Two-Way Left Turn Lane",
        "shape": "Vertical Rectangle",
        "color": "White background with opposing curved turn arrows",
        "category": "regulatory",
        "meaning": "The center lane is reserved exclusively for left turns by traffic traveling in both directions. You must not use this lane for passing or travel.",
        "key_rule": "You may only drive in this center lane for a brief distance to prepare for a left turn.",
        "svg": '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><rect x="18" y="8" width="84" height="104" rx="8" fill="#FFFFFF" stroke="#000000" stroke-width="4"/><rect x="22" y="12" width="76" height="96" rx="6" fill="none" stroke="#000000" stroke-width="1.5"/><path d="M46,84 L46,62 Q46,48 34,48" fill="none" stroke="#000000" stroke-width="4"/><polygon points="36,42 26,48 36,54" fill="#000000"/><path d="M74,36 L74,58 Q74,72 86,72" fill="none" stroke="#000000" stroke-width="4"/><polygon points="84,66 94,72 84,78" fill="#000000"/><text x="60" y="65" font-family="Arial Black, sans-serif" font-size="10" font-weight="bold" fill="#000000" text-anchor="middle">ONLY</text></svg>'
    }
]

# Generate questions_signs.json (Part 1 Questions - exactly 10 are chosen for the exam, 100% required)
QUESTIONS_SIGNS = [
    {
        "id": "sq1",
        "signId": "stop_sign",
        "question": "What must you do when you see this eight-sided red sign?",
        "options": [
            "Slow down and proceed if no other vehicles are approaching.",
            "Come to a complete stop at the stop line or crosswalk and yield right-of-way.",
            "Stop only if pedestrians or oncoming cars are in the intersection.",
            "Slow down to 5 mph and roll through if the road is clear."
        ],
        "answerIndex": 1,
        "explanation": "An octagon always indicates a STOP sign. In Virginia, you must come to a COMPLETE stop at the stop line, marked crosswalk, or edge of the intersection before yielding and proceeding."
    },
    {
        "id": "sq2",
        "signId": "yield_sign",
        "question": "What is the meaning of this downward-pointing triangular sign?",
        "options": [
            "You have the right-of-way over cross traffic.",
            "Slow down, prepare to stop, and yield the right-of-way to vehicles and pedestrians.",
            "You must come to a complete stop at all times.",
            "Do not enter the roadway under any circumstance."
        ],
        "answerIndex": 1,
        "explanation": "A downward-pointing triangle is exclusively used for YIELD signs. You must slow down, yield to any traffic or pedestrians, and stop if necessary to let them proceed."
    },
    {
        "id": "sq3",
        "signId": "school_zone",
        "question": "What does this five-sided (pentagon) fluorescent yellow-green sign indicate?",
        "options": [
            "Pedestrian crosswalk on a multi-lane highway.",
            "School zone or school crossing ahead; watch for children.",
            "Public park or recreation area entrance.",
            "Construction zone with flaggers present."
        ],
        "answerIndex": 1,
        "explanation": "A five-sided pentagon pointing up is uniquely reserved for School Zones and School Crossings. Be alert for children and observe posted school speed limits (typically 25 MPH)."
    },
    {
        "id": "sq4",
        "signId": "no_passing_zone",
        "question": "Where will you find this yellow pennant-shaped sign, and what does it mean?",
        "options": [
            "Posted on the right side indicating a passing zone begins.",
            "Posted on the left side of the road indicating the start of a No-Passing Zone.",
            "Posted at school zones indicating no stopping.",
            "Posted on multi-lane highways indicating lane reduction."
        ],
        "answerIndex": 1,
        "explanation": "A pennant-shaped sign is always posted on the LEFT side of the roadway facing drivers, marking the beginning of a zone where passing other vehicles is strictly prohibited."
    },
    {
        "id": "sq5",
        "signId": "railroad_crossbuck",
        "question": "When approaching this white crossbuck sign, what is required of Virginia drivers?",
        "options": [
            "Treat it as a yield sign; look, listen, and stop if a train is approaching.",
            "Speed up to clear the tracks before the gate lowers.",
            "Always come to a mandatory complete stop, even if no train is coming.",
            "Sound your horn twice before crossing the tracks."
        ],
        "answerIndex": 0,
        "explanation": "A railroad crossbuck sign indicates a railroad crossing and must be treated as a yield sign. If lights are flashing, gates are down, or a train is visible, you must stop between 15 and 50 feet of the nearest rail."
    },
    {
        "id": "sq6",
        "signId": "railroad_advance",
        "question": "What does this round yellow sign with a black 'X' and 'RR' warn drivers about?",
        "options": [
            "Rest area ahead on the interstate.",
            "Roundabout intersection ahead.",
            "Advance warning of a railroad crossing ahead.",
            "Road repairs and lane closures ahead."
        ],
        "answerIndex": 2,
        "explanation": "A circular sign is exclusively reserved for railroad advance warning. It tells you a railroad crossing is ahead so you can slow down and look both ways."
    },
    {
        "id": "sq7",
        "signId": "do_not_enter",
        "question": "What should you do if you see this red and white square sign?",
        "options": [
            "Proceed cautiously with your hazard lights on.",
            "Do not drive onto this ramp or roadway; you are facing oncoming traffic.",
            "Authorized government vehicles only may enter.",
            "Entry is prohibited only between 10 PM and 6 AM."
        ],
        "answerIndex": 1,
        "explanation": "DO NOT ENTER signs are posted at freeway exit ramps and one-way streets to notify drivers that traffic is traveling in the opposite direction."
    },
    {
        "id": "sq8",
        "signId": "wrong_way",
        "question": "If you drive past this red sign, what emergency action must you take?",
        "options": [
            "Accelerate to reach the next exit as quickly as possible.",
            "Pull over to the side immediately, stop, and turn around when it is safe.",
            "Continue driving on the left shoulder.",
            "Sound your horn continuously to warn oncoming vehicles."
        ],
        "answerIndex": 1,
        "explanation": "WRONG WAY signs indicate you are traveling against traffic on a one-way street or ramp. Pull over immediately to the side of the road, stop, and turn around safely."
    },
    {
        "id": "sq9",
        "signId": "no_u_turn",
        "question": "What does a red circle with a diagonal slash across a symbol mean?",
        "options": [
            "The indicated action is recommended during off-peak hours.",
            "The indicated action is strictly prohibited.",
            "Caution is advised when performing the action.",
            "The action is permitted only for emergency vehicles."
        ],
        "answerIndex": 1,
        "explanation": "A red circle with a diagonal slash across a symbol always means that the maneuver shown is prohibited by law. Here, U-turns are illegal."
    },
    {
        "id": "sq10",
        "signId": "slippery_when_wet",
        "question": "What does this diamond warning sign indicate?",
        "options": [
            "Winding mountain road with hairpin curves ahead.",
            "Road surface becomes slippery when wet; reduce speed and avoid sudden maneuvers.",
            "Vehicles may experience strong crosswinds on this bridge.",
            "Rough road surface with gravel or unpaved pavement."
        ],
        "answerIndex": 1,
        "explanation": "This sign warns that the pavement is slick and slippery when wet. Roads are especially slippery during the first 10-15 minutes of a rain shower due to accumulated oil."
    },
    {
        "id": "sq11",
        "signId": "divided_highway_begins",
        "question": "What does this diamond sign with a divider at the top mean?",
        "options": [
            "Divided highway ends ahead; prepare for two-way undivided traffic.",
            "Divided highway begins ahead; keep to the right of the physical median divider.",
            "Two-way traffic ahead with no passing permitted.",
            "Steep downhill grade ahead; shift to a lower gear."
        ],
        "answerIndex": 1,
        "explanation": "When the median island symbol is at the TOP of the sign between opposing arrows, it warns that a divided highway begins and you must keep right of the median."
    },
    {
        "id": "sq12",
        "signId": "divided_highway_ends",
        "question": "What does this diamond sign with the median divider at the bottom mean?",
        "options": [
            "Divided highway ends ahead; oncoming traffic will no longer be separated by a median.",
            "Divided highway begins ahead; move into the right lane immediately.",
            "Dual turn lanes are ending ahead.",
            "Freeway ramp merging onto an interstate highway."
        ],
        "answerIndex": 0,
        "explanation": "When the median island symbol is at the BOTTOM of the sign, it indicates the divided highway is ending and traffic will be traveling both ways on an undivided roadway."
    },
    {
        "id": "sq13",
        "signId": "two_way_traffic",
        "question": "What does this sign with two opposing vertical arrows warn you about?",
        "options": [
            "Passing is allowed in both directions.",
            "You are on or approaching a two-way street with traffic traveling in opposite directions.",
            "Express lanes are open in both directions.",
            "Dual left turn lanes ahead at the intersection."
        ],
        "answerIndex": 1,
        "explanation": "This warning sign alerts you that you are leaving a one-way street or divided roadway and entering a two-way roadway where traffic travels in opposite directions."
    },
    {
        "id": "sq14",
        "signId": "lane_ends_merge",
        "question": "What action should you take when you see this lane ends / merge sign?",
        "options": [
            "Drivers in the continuous left lane must yield to merging vehicles.",
            "The right lane is ending; drivers in that lane must safely merge left and yield right-of-way.",
            "Stop at the end of the lane before entering traffic.",
            "Drive onto the shoulder until traffic clears."
        ],
        "answerIndex": 1,
        "explanation": "The right lane is ending ahead. Vehicles in the ending lane must merge left into the continuous lane, yielding to traffic already established in that lane."
    },
    {
        "id": "sq15",
        "signId": "roundabout_ahead",
        "question": "What are the rules when approaching a roundabout marked with this sign?",
        "options": [
            "Vehicles entering the roundabout have the right-of-way.",
            "Enter in a clockwise direction at high speed to match circulating traffic.",
            "Slow down, yield to traffic already in the circle and pedestrians, and travel counter-clockwise.",
            "Always come to a mandatory complete stop before entering the roundabout."
        ],
        "answerIndex": 2,
        "explanation": "When approaching a roundabout, slow down and yield to pedestrians and vehicles already inside the circle. Always travel to the right in a counter-clockwise direction."
    },
    {
        "id": "sq16",
        "signId": "stop_ahead",
        "question": "Why is this 'Stop Ahead' warning sign posted?",
        "options": [
            "To let drivers know they must stop immediately at this exact sign.",
            "To alert drivers that a stop sign is upcoming and may be hidden from early view.",
            "To warn of a red traffic signal light ahead.",
            "To indicate a mandatory brake inspection station."
        ],
        "answerIndex": 1,
        "explanation": "A Stop Ahead sign gives drivers early warning that a stop sign is located ahead, typically where hills, curves, or obstacles obstruct direct view of the stop sign."
    },
    {
        "id": "sq17",
        "signId": "yield_ahead",
        "question": "What should you prepare to do when you observe this 'Yield Ahead' sign?",
        "options": [
            "Prepare to slow down and yield right-of-way at the upcoming yield sign.",
            "Speed up to pass vehicles before the intersection.",
            "Make an immediate U-turn before the yield sign.",
            "Honk your horn to claim right-of-way."
        ],
        "answerIndex": 0,
        "explanation": "A Yield Ahead sign warns that a yield sign is ahead so you can begin slowing down and scanning for approaching cross traffic."
    },
    {
        "id": "sq18",
        "signId": "signal_ahead",
        "question": "What does this yellow diamond sign with a traffic light graphic tell you?",
        "options": [
            "A traffic signal is ahead; be prepared to stop if the light is red.",
            "Traffic signals are currently malfunctioning ahead.",
            "Flashing yellow caution lights only are present ahead.",
            "Emergency vehicle dispatch station ahead."
        ],
        "answerIndex": 0,
        "explanation": "This sign indicates a traffic control signal is approaching at the next intersection. Be prepared to stop if the light changes to yellow or red."
    },
    {
        "id": "sq19",
        "signId": "deer_crossing",
        "question": "What must you keep in mind when driving through an area marked with this sign?",
        "options": [
            "Deer are only active during broad daylight.",
            "Deer frequently cross here; watch roadside shoulders, especially at dusk and dawn.",
            "Sound your horn continuously to scare animals away.",
            "Deer always travel alone so only watch for one."
        ],
        "answerIndex": 1,
        "explanation": "Deer crossing signs are posted where deer frequently cross roads. Deer are most active at dawn and dusk, and frequently travel in groups."
    },
    {
        "id": "sq20",
        "signId": "pedestrian_crossing",
        "question": "What does this fluorescent yellow-green diamond sign mean?",
        "options": [
            "Pedestrians are prohibited from crossing this street.",
            "A pedestrian crosswalk is ahead; drivers must yield right-of-way to pedestrians.",
            "Jogging path parallel to the highway.",
            "Hitchhiking pickup zone ahead."
        ],
        "answerIndex": 1,
        "explanation": "This sign alerts drivers to a pedestrian crossing ahead. In Virginia, motorists must yield to pedestrians in marked crosswalks and intersections."
    },
    {
        "id": "sq21",
        "signId": "hill_steep_downgrade",
        "question": "What should drivers do when seeing this truck on an incline sign?",
        "options": [
            "Shift into neutral to save fuel down the grade.",
            "Check brakes and shift into a lower gear to control speed before starting downhill.",
            "Pump the brakes hard and rapidly throughout the descent.",
            "Speed up to maintain highway momentum."
        ],
        "answerIndex": 1,
        "explanation": "This sign warns of a steep downhill slope ahead. Drivers (especially heavy vehicles) should downshift to use engine braking and avoid riding the brakes."
    },
    {
        "id": "sq22",
        "signId": "keep_right",
        "question": "What does this white regulatory sign with an angled arrow instruct drivers to do?",
        "options": [
            "Make an immediate right turn at the intersection.",
            "Keep to the right of an upcoming traffic island, divider, or obstruction.",
            "Only vehicles in the right lane may continue straight.",
            "Right turn on red is prohibited."
        ],
        "answerIndex": 1,
        "explanation": "The Keep Right sign directs traffic to stay to the right of a traffic island, median, or highway obstruction."
    },
    {
        "id": "sq23",
        "signId": "road_work_ahead",
        "question": "In Virginia, what is the maximum fine for speeding in a highway work zone marked with orange signs?",
        "options": [
            "Up to $100.",
            "Up to $250.",
            "Up to $500.",
            "Up to $1,000."
        ],
        "answerIndex": 2,
        "explanation": "Under Virginia law, speeding in a designated highway work zone when workers are present carries an increased penalty of up to a $500 fine."
    },
    {
        "id": "sq24",
        "signId": "flagger_ahead",
        "question": "What must you do when approaching a work zone with a flagger?",
        "options": [
            "Follow the flagger's hand signals and paddle commands above other signs.",
            "Ignore the flagger if the traffic light is green.",
            "Sound your horn to indicate you are passing the flagger.",
            "Proceed at standard posted highway speed."
        ],
        "answerIndex": 0,
        "explanation": "A flagger's directions take legal precedence over existing signs and traffic signals in a work zone. Always follow the flagger's instructions."
    },
    {
        "id": "sq25",
        "signId": "workers_ahead",
        "question": "What color is universally used on signs to identify temporary construction and maintenance work zones?",
        "options": [
            "Yellow",
            "Orange",
            "Fluorescent Yellow-Green",
            "Brown"
        ],
        "answerIndex": 1,
        "explanation": "Orange is exclusively designated for temporary traffic control, construction, and maintenance work zones."
    },
    {
        "id": "sq26",
        "signId": "handicapped_parking",
        "question": "Who is legally allowed to park in a space designated with this blue wheelchair sign?",
        "options": [
            "Anyone picking up a senior citizen.",
            "Any vehicle making a quick delivery under 5 minutes.",
            "Only vehicles displaying official disabled license plates or disabled parking placards.",
            "Any vehicle with hazard flashers turned on."
        ],
        "answerIndex": 2,
        "explanation": "In Virginia, disabled parking spaces are reserved strictly for individuals with valid disabled parking license plates or disabled placards. Fines range from $100 to $500."
    },
    {
        "id": "sq27",
        "signId": "low_clearance",
        "question": "What does a sign stating '12\'-6\"' with top and bottom arrows mean?",
        "options": [
            "The bridge or overpass ahead has a maximum height clearance of 12 feet, 6 inches.",
            "The roadway width is restricted to 12 feet, 6 inches.",
            "Maximum vehicle length allowed on this roadway is 12.6 feet.",
            "The distance to the nearest fuel station is 12.6 miles."
        ],
        "answerIndex": 0,
        "explanation": "This warning sign alerts drivers that the overhead structure has limited vertical clearance (12 feet 6 inches). Vehicles exceeding this height must seek an alternate route."
    },
    {
        "id": "sq28",
        "signId": "sharp_curve_right",
        "question": "What does a diamond sign with a sharp 90-degree arrow indicate?",
        "options": [
            "A sharp right turn ahead; slow down substantially before the turn.",
            "Right lane must exit onto the freeway.",
            "Road detour to the right ahead.",
            "Side street intersection on the right."
        ],
        "answerIndex": 0,
        "explanation": "A sharp 90-degree arrow warns of an impending sharp curve or turn. You should brake to a safe speed before entering the curve."
    },
    {
        "id": "sq29",
        "signId": "winding_road",
        "question": "What does a winding arrow sign warn you about?",
        "options": [
            "A steep mountain descent ahead.",
            "A series of three or more consecutive curves ahead in the road.",
            "A slippery bridge surface in freezing temperatures.",
            "A detour through a residential neighborhood."
        ],
        "answerIndex": 1,
        "explanation": "A winding road sign indicates a series of curves ahead (at least three). Reduce your speed and maintain your lane position."
    },
    {
        "id": "sq30",
        "signId": "added_lane",
        "question": "How does an 'Added Lane' sign differ from a 'Merge' sign?",
        "options": [
            "In an added lane, drivers must come to a complete stop before continuing.",
            "An added lane provides a new separate travel lane, so merging into traffic is not immediately required.",
            "In an added lane, you must merge immediately into the left lane.",
            "Added lanes are reserved strictly for high-occupancy vehicles."
        ],
        "answerIndex": 1,
        "explanation": "An Added Lane sign shows two parallel arrows, meaning a new lane is formed alongside the existing road and entering vehicles do not have to merge immediately."
    },
    {
        "id": "sq31",
        "signId": "slow_moving_vehicle",
        "question": "What does a triangular orange emblem with a dark red border mounted on a vehicle mean?",
        "options": [
            "The vehicle is transporting hazardous materials.",
            "The vehicle is designed to travel at 25 MPH or less.",
            "The vehicle is an emergency first-responder vehicle.",
            "The vehicle is oversized and requires a police escort."
        ],
        "answerIndex": 1,
        "explanation": "A reflective orange triangle with a red border is the Slow-Moving Vehicle emblem, required on vehicles that travel at speeds of 25 MPH or less (such as tractors and road machinery)."
    },
    {
        "id": "sq32",
        "signId": "center_turn_lane",
        "question": "What is the proper use of a center lane marked with opposing turn arrows and 'ONLY'?",
        "options": [
            "Use it as a passing lane to overtake slow drivers.",
            "Use it only to make left turns from either direction or enter traffic after turning left.",
            "Use it as a continuous travel lane when traffic is heavy.",
            "Use it for emergency stopping and parking."
        ],
        "answerIndex": 1,
        "explanation": "The center two-way left turn lane is strictly for turning left from either direction. It must never be used for through travel or passing."
    },
    {
        "id": "sq33",
        "signId": "speed_limit_25",
        "question": "Unless otherwise posted, what is the default legal speed limit in Virginia residential areas?",
        "options": [
            "15 MPH",
            "20 MPH",
            "25 MPH",
            "35 MPH"
        ],
        "answerIndex": 2,
        "explanation": "In Virginia, the default statutory speed limit in school, business, and residential areas is 25 MPH unless a different limit is posted."
    },
    {
        "id": "sq34",
        "signId": "speed_limit_55",
        "question": "In Virginia, what is the maximum speed limit on non-interstate highways if not otherwise posted?",
        "options": [
            "45 MPH",
            "50 MPH",
            "55 MPH",
            "65 MPH"
        ],
        "answerIndex": 2,
        "explanation": "Unless posted otherwise, 55 MPH is the maximum legal speed limit on all secondary and primary paved highways in Virginia other than school/business/residential areas."
    },
    {
        "id": "sq35",
        "signId": "side_road_intersection",
        "question": "What does this yellow diamond sign with a cross intersection warn of?",
        "options": [
            "A hospital entrance is ahead.",
            "A side road enters the highway from the right ahead; watch for entering traffic.",
            "Railroad tracks crossing the highway ahead.",
            "Four-way stop intersection ahead."
        ],
        "answerIndex": 1,
        "explanation": "A side road sign warns of an upcoming side street intersecting from the side shown. Drivers should watch for vehicles entering or turning."
    },
    {
        "id": "sq36",
        "signId": "stop_sign",
        "question": "What shape is exclusively used for STOP signs across the United States and Virginia?",
        "options": [
            "Hexagon (6 sides)",
            "Octagon (8 sides)",
            "Pentagon (5 sides)",
            "Diamond (4 sides)"
        ],
        "answerIndex": 1,
        "explanation": "The 8-sided Octagon shape is exclusively used for STOP signs so it can be identified even when covered by snow or viewed from behind."
    },
    {
        "id": "sq37",
        "signId": "yield_sign",
        "question": "What shape is exclusively used for YIELD signs?",
        "options": [
            "Equilateral triangle pointing down",
            "Isosceles triangle pointing right",
            "Diamond pointing up",
            "Vertical rectangle"
        ],
        "answerIndex": 0,
        "explanation": "An equilateral triangle pointing downwards is exclusively used for YIELD signs."
    },
    {
        "id": "sq38",
        "signId": "school_zone",
        "question": "What sign shape is exclusively reserved for School Zones and School Crossings in Virginia?",
        "options": [
            "Round (Circle)",
            "Diamond",
            "Pentagon (5-sided, pointing up)",
            "Pennant (pointing right)"
        ],
        "answerIndex": 2,
        "explanation": "The 5-sided Pentagon pointing upwards is uniquely reserved for School Zone and School Crossing signs."
    },
    {
        "id": "sq39",
        "signId": "no_passing_zone",
        "question": "What shape is the No Passing Zone warning sign?",
        "options": [
            "Pennant (three-sided pointing right)",
            "Octagon (eight-sided)",
            "Crossbuck (X-shape)",
            "Horizontal rectangle"
        ],
        "answerIndex": 0,
        "explanation": "The pennant shape (pointing right) is exclusively used for No Passing Zone signs and is posted on the left side of the road."
    },
    {
        "id": "sq40",
        "signId": "railroad_advance",
        "question": "What shape is exclusively reserved for advance warning of railroad crossings?",
        "options": [
            "Square",
            "Octagon",
            "Round (Circle)",
            "Downward triangle"
        ],
        "answerIndex": 2,
        "explanation": "A circular round sign is exclusively used for advance warnings of upcoming railroad crossings."
    }
]

# Generate questions_general.json (Part 2 Questions - 30 chosen for exam, 80% / 24 correct required)
QUESTIONS_GENERAL = [
    # Topic 1: Speed Limits & Reckless Driving
    {
        "id": "gq1",
        "category": "Speed Limits & Reckless Driving",
        "question": "Unless otherwise posted, what is the maximum speed limit on unpaved secondary roads in Virginia?",
        "options": [
            "25 MPH",
            "35 MPH",
            "45 MPH",
            "55 MPH"
        ],
        "answerIndex": 1,
        "explanation": "In Virginia, the statutory speed limit on unpaved roads is 35 MPH unless a different speed is posted."
    },
    {
        "id": "gq2",
        "category": "Speed Limits & Reckless Driving",
        "question": "Under Virginia law, driving at or above which speed is automatically considered reckless driving, regardless of the posted limit?",
        "options": [
            "75 MPH",
            "80 MPH",
            "85 MPH",
            "90 MPH"
        ],
        "answerIndex": 2,
        "explanation": "In Virginia, driving faster than 85 MPH—regardless of the posted speed limit—or driving 20 MPH or more over the speed limit is classified as Reckless Driving, a Class 1 misdemeanor."
    },
    {
        "id": "gq3",
        "category": "Speed Limits & Reckless Driving",
        "question": "Driving 20 MPH or more over the posted speed limit in Virginia is considered:",
        "options": [
            "A standard civil traffic infraction with no points.",
            "Reckless Driving, which is a criminal misdemeanor.",
            "A warning offense for first-time drivers.",
            "An automatic 1-year jail sentence."
        ],
        "answerIndex": 1,
        "explanation": "Exceeding the posted speed limit by 20 MPH or more is Reckless Driving under Virginia law, carrying criminal misdemeanor penalties."
    },
    {
        "id": "gq4",
        "category": "Speed Limits & Reckless Driving",
        "question": "What is the statutory speed limit in Virginia school zones when flashing warning lights are active?",
        "options": [
            "15 MPH",
            "25 MPH (or as posted)",
            "30 MPH",
            "35 MPH"
        ],
        "answerIndex": 1,
        "explanation": "The maximum speed in school zones during indicated hours or when lights are flashing is 25 MPH unless a lower limit is specifically posted."
    },

    # Topic 2: Following Distance & Stopping
    {
        "id": "gq5",
        "category": "Following Distance & Stopping",
        "question": "According to the Virginia Driver's Manual, what following distance should you maintain at speeds under 35 MPH on dry pavement?",
        "options": [
            "At least 1 second",
            "At least 2 seconds",
            "At least 4 seconds",
            "At least 6 seconds"
        ],
        "answerIndex": 1,
        "explanation": "Virginia uses the 2-, 3-, and 4-Second Rule: maintain at least 2 seconds following distance at speeds under 35 MPH."
    },
    {
        "id": "gq6",
        "category": "Following Distance & Stopping",
        "question": "Under the Virginia 2-, 3-, and 4-Second Rule, what following distance is required for speeds between 35 and 45 MPH?",
        "options": [
            "2 seconds",
            "3 seconds",
            "4 seconds",
            "5 seconds"
        ],
        "answerIndex": 1,
        "explanation": "At speeds between 35 and 45 MPH on dry roads, you should allow a minimum of 3 seconds following distance."
    },
    {
        "id": "gq7",
        "category": "Following Distance & Stopping",
        "question": "What following distance is recommended by Virginia DMV for speeds from 46 to 70 MPH?",
        "options": [
            "2 seconds",
            "3 seconds",
            "At least 4 seconds",
            "5 seconds"
        ],
        "answerIndex": 2,
        "explanation": "At higher speeds between 46 and 70 MPH, you should allow at least 4 seconds following distance."
    },
    {
        "id": "gq8",
        "category": "Following Distance & Stopping",
        "question": "How do you measure following distance using the seconds rule?",
        "options": [
            "Count your car lengths from the car in front.",
            "Pick a fixed landmark ahead; when the vehicle ahead passes it, count seconds until you reach the same landmark.",
            "Watch your odometer while maintaining pace.",
            "Calculate your stopping distance in feet divided by 10."
        ],
        "answerIndex": 1,
        "explanation": "Choose a stationary object (sign, overpass, tree). When the vehicle ahead passes it, count 'one-thousand-one, one-thousand-two...' You should not reach that object before finishing the required seconds."
    },
    {
        "id": "gq9",
        "category": "Following Distance & Stopping",
        "question": "When following large trucks or commercial buses, why should you increase your following distance?",
        "options": [
            "Trucks always drive slower than the speed limit.",
            "To see around the truck and allow the truck driver to see you in their side mirrors.",
            "Trucks cannot make right turns.",
            "To draft behind the truck and save fuel."
        ],
        "answerIndex": 1,
        "explanation": "Increasing following distance behind large trucks ensures you stay out of their rear blind spot ('No-Zone') and gives you a clear view of the road ahead."
    },

    # Topic 3: Right of Way & Intersections
    {
        "id": "gq10",
        "category": "Right of Way & Intersections",
        "question": "When two vehicles arrive at a 4-way stop at the exact same time, which driver has the right-of-way?",
        "options": [
            "The driver on the left has the right-of-way.",
            "The driver on the right has the right-of-way.",
            "The larger vehicle always goes first.",
            "The driver intending to turn left has priority."
        ],
        "answerIndex": 1,
        "explanation": "When two vehicles arrive simultaneously at an all-way stop or uncontrolled intersection, the driver on the left must yield to the driver on the right."
    },
    {
        "id": "gq11",
        "category": "Right of Way & Intersections",
        "question": "At an uncontrolled intersection (no signs or signals), who must you yield to?",
        "options": [
            "Yield to any vehicle already in the intersection and vehicles approaching from your right.",
            "Yield only to vehicles moving faster than you.",
            "You never have to yield if you are going straight.",
            "Yield only to commercial delivery trucks."
        ],
        "answerIndex": 0,
        "explanation": "At uncontrolled intersections, you must yield to traffic already in the intersection and to vehicles on your right."
    },
    {
        "id": "gq12",
        "category": "Right of Way & Intersections",
        "question": "When making a left turn at a green traffic light (solid green circle), what must you do?",
        "options": [
            "You have automatic right-of-way over oncoming vehicles.",
            "Yield to oncoming traffic and pedestrians before completing the turn.",
            "Honk your horn and turn immediately.",
            "Wait for the light to turn red before completing the turn."
        ],
        "answerIndex": 1,
        "explanation": "A solid green light gives you permission to turn left only after yielding to oncoming vehicles moving straight or turning right, as well as pedestrians in the crosswalk."
    },
    {
        "id": "gq13",
        "category": "Right of Way & Intersections",
        "question": "What does a flashing yellow traffic arrow mean for drivers turning left?",
        "options": [
            "Stop and wait for a green arrow.",
            "Turns are allowed, but you must yield to oncoming traffic and pedestrians.",
            "You have protected right-of-way; oncoming traffic must stop.",
            "The traffic light is out of order."
        ],
        "answerIndex": 1,
        "explanation": "A flashing yellow arrow means left turns are permitted, but oncoming traffic has a green light. You must yield before turning."
    },
    {
        "id": "gq14",
        "category": "Right of Way & Intersections",
        "question": "In Virginia, can you make a right turn on red?",
        "options": [
            "No, right turns on red are never legal in Virginia.",
            "Yes, after coming to a complete stop and yielding to traffic and pedestrians, unless a 'No Turn On Red' sign is posted.",
            "Yes, without stopping if the cross street is empty.",
            "Only between sunrise and sunset."
        ],
        "answerIndex": 1,
        "explanation": "You may turn right on red in Virginia only after coming to a COMPLETE stop and yielding to all traffic and pedestrians, provided no sign prohibits the turn."
    },
    {
        "id": "gq15",
        "category": "Right of Way & Intersections",
        "question": "Can you legally turn left on red in Virginia?",
        "options": [
            "Never under any circumstances.",
            "Only from a one-way street onto another one-way street, after coming to a complete stop and yielding.",
            "At any intersection as long as cross traffic is clear.",
            "Only on Sundays and holidays."
        ],
        "answerIndex": 1,
        "explanation": "In Virginia, left turns on red are permitted ONLY when turning from a one-way street onto another one-way street, after coming to a full stop and yielding."
    },
    {
        "id": "gq16",
        "category": "Right of Way & Intersections",
        "question": "When approaching a roundabout, who has the right-of-way?",
        "options": [
            "Vehicles entering the roundabout.",
            "Vehicles already circulating inside the roundabout.",
            "The vehicle driving at the highest speed.",
            "Vehicles entering from the left."
        ],
        "answerIndex": 1,
        "explanation": "Traffic already circulating inside the roundabout has right-of-way. Entering traffic must yield before joining the circle."
    },
    {
        "id": "gq17",
        "category": "Right of Way & Intersections",
        "question": "What must drivers do regarding funeral processions in Virginia?",
        "options": [
            "Funeral processions must yield to all standard traffic.",
            "Funeral processions have the right-of-way; other drivers must not cut through or join the procession.",
            "Pass the procession on the right shoulder.",
            "Sound your horn as you pass."
        ],
        "answerIndex": 1,
        "explanation": "Virginia law grants funeral processions the right-of-way. It is illegal to join, cut through, or pass a funeral procession."
    },

    # Topic 4: School Buses
    {
        "id": "gq18",
        "category": "School Buses",
        "question": "When approaching a stopped school bus with flashing red lights and an extended stop sign on an undivided roadway, what must you do?",
        "options": [
            "Only traffic traveling behind the bus must stop.",
            "Drivers approaching from either direction must stop and remain stopped until children are clear and the bus resumes motion.",
            "Slow down to 10 MPH and pass cautiously.",
            "Stop only if children are actively in the roadway."
        ],
        "answerIndex": 1,
        "explanation": "On any undivided road, drivers traveling in BOTH directions must stop for a school bus with flashing red lights and extended stop arm."
    },
    {
        "id": "gq19",
        "category": "School Buses",
        "question": "When are you NOT required to stop for a stopped school bus with flashing red lights?",
        "options": [
            "When driving in the opposite direction on a roadway separated by a physical median or unpaved barrier.",
            "When traveling on any 4-lane highway.",
            "When there are double yellow lines separating lanes.",
            "When the speed limit is 45 MPH or higher."
        ],
        "answerIndex": 0,
        "explanation": "You do not need to stop if you are traveling in the opposite direction on a divided highway separated by a physical barrier or unpaved median."
    },
    {
        "id": "gq20",
        "category": "School Buses",
        "question": "Does a continuous painted turn lane count as a physical barrier exempting you from stopping for a school bus?",
        "options": [
            "Yes, any painted lane is considered a barrier.",
            "No, only a physical median barrier or unpaved space exempts opposite-direction traffic.",
            "Yes, if the turn lane is wider than 10 feet.",
            "Yes, between the hours of 8 AM and 3 PM."
        ],
        "answerIndex": 1,
        "explanation": "A painted median or center turn lane is NOT a physical barrier. All lanes in both directions must stop."
    },

    # Topic 5: Move Over Law & Emergency Vehicles
    {
        "id": "gq21",
        "category": "Move Over Law & Emergency Vehicles",
        "question": "What does Virginia's 'Move Over' law require you to do when approaching stationary emergency vehicles with flashing lights?",
        "options": [
            "Maintain speed and sound your horn.",
            "Change into an adjacent lane not next to the emergency vehicle if safe, or slow down with caution.",
            "Come to a dead stop in your travel lane.",
            "Accelerate past the emergency vehicle quickly."
        ],
        "answerIndex": 1,
        "explanation": "Virginia's Move Over law requires drivers on multi-lane highways to move over at least one lane away from stopped emergency/utility/hazard vehicles, or slow down significantly if changing lanes is unsafe."
    },
    {
        "id": "gq22",
        "category": "Move Over Law & Emergency Vehicles",
        "question": "What must you do when an emergency vehicle with flashing red/blue lights and sirens approaches you from behind?",
        "options": [
            "Speed up to reach the nearest exit.",
            "Immediately pull over to the right edge of the road, clear of any intersection, and stop until it passes.",
            "Stop immediately in the middle of your lane.",
            "Move onto the left shoulder and stop."
        ],
        "answerIndex": 1,
        "explanation": "Yield right-of-way by immediately driving to the right edge of the road, stopping clear of intersections, until emergency vehicles have passed."
    },

    # Topic 6: Headlights & Lighting Laws
    {
        "id": "gq23",
        "category": "Headlights & Lighting Laws",
        "question": "Virginia law requires you to use your headlights:",
        "options": [
            "From sunset to sunrise, whenever wipers are in use, and when visibility is reduced to 500 feet or less.",
            "Only between 9 PM and 5 AM.",
            "Only on dark rural highways.",
            "Only when driving in snow or heavy fog."
        ],
        "answerIndex": 0,
        "explanation": "Virginia requires headlights from sunset to sunrise, whenever windshield wipers are in use (rain, fog, snow, sleet), and whenever visibility is reduced to 500 feet or less."
    },
    {
        "id": "gq24",
        "category": "Headlights & Lighting Laws",
        "question": "When driving at night, when must you dim your high beams for oncoming vehicles in Virginia?",
        "options": [
            "Within 200 feet of an oncoming vehicle.",
            "Within 500 feet of an oncoming vehicle.",
            "Within 1,000 feet of an oncoming vehicle.",
            "Only when the oncoming driver flashes their lights."
        ],
        "answerIndex": 1,
        "explanation": "Virginia law requires dimming your high beams whenever you come within 500 feet of an oncoming vehicle."
    },
    {
        "id": "gq25",
        "category": "Headlights & Lighting Laws",
        "question": "When following another vehicle from behind at night, when must you dim your high beams?",
        "options": [
            "Within 100 feet.",
            "Within 200 feet.",
            "Within 400 feet.",
            "Within 500 feet."
        ],
        "answerIndex": 1,
        "explanation": "Virginia law requires dimming high beams when within 200 feet of the vehicle you are following."
    },
    {
        "id": "gq26",
        "category": "Headlights & Lighting Laws",
        "question": "When driving in dense fog or heavy snow, which headlights should you use?",
        "options": [
            "High beam headlights for maximum penetration.",
            "Low beam headlights (or fog lights), because high beams reflect off water droplets back into your eyes.",
            "Parking lights only.",
            "Emergency hazard flashers only."
        ],
        "answerIndex": 1,
        "explanation": "Use low beams in fog, rain, or snow. High beams reflect off droplets/crystals and create blinding glare."
    },

    # Topic 7: Turn Signals & Hand Signals
    {
        "id": "gq27",
        "category": "Turn Signals & Hand Signals",
        "question": "In Virginia, how many feet before making a turn or lane change must you signal your intention?",
        "options": [
            "At least 25 feet",
            "At least 50 feet",
            "At least 100 feet",
            "At least 200 feet"
        ],
        "answerIndex": 2,
        "explanation": "Virginia law requires signaling your intention to turn or change lanes at least 100 feet ahead."
    },
    {
        "id": "gq28",
        "category": "Turn Signals & Hand Signals",
        "question": "What is the proper hand signal for a LEFT turn?",
        "options": [
            "Left arm extended straight out horizontally.",
            "Left arm bent upward at 90 degrees.",
            "Left arm bent downward at 90 degrees.",
            "Right arm pointed across the dashboard."
        ],
        "answerIndex": 0,
        "explanation": "To signal a left turn with hand signals, extend your left arm and hand straight out horizontally."
    },
    {
        "id": "gq29",
        "category": "Turn Signals & Hand Signals",
        "question": "What is the hand signal for a RIGHT turn?",
        "options": [
            "Left arm extended straight out.",
            "Left arm bent upward at a 90-degree angle.",
            "Left arm bent downward at a 90-degree angle.",
            "Right hand waving out the passenger window."
        ],
        "answerIndex": 1,
        "explanation": "To signal a right turn, hold your left arm out and bent upwards at a 90-degree angle."
    },
    {
        "id": "gq30",
        "category": "Turn Signals & Hand Signals",
        "question": "What is the hand signal to indicate you are SLOWING DOWN or STOPPING?",
        "options": [
            "Left arm extended straight out.",
            "Left arm bent upward at 90 degrees.",
            "Left arm bent downward at a 90-degree angle with palm facing rear.",
            "Pointing down toward the ground with your index finger."
        ],
        "answerIndex": 2,
        "explanation": "To signal slow down or stop, hold your left arm out and bent downwards at a 90-degree angle with your palm facing rearward."
    },

    # Topic 8: Parking Distances & Rules
    {
        "id": "gq31",
        "category": "Parking Distances & Rules",
        "question": "In Virginia, you may NOT park within how many feet of a fire hydrant?",
        "options": [
            "10 feet",
            "15 feet",
            "20 feet",
            "25 feet"
        ],
        "answerIndex": 1,
        "explanation": "You may not park within 15 feet of any fire hydrant to ensure emergency fire crews have immediate unobstructed access."
    },
    {
        "id": "gq32",
        "category": "Parking Distances & Rules",
        "question": "You may NOT park within how many feet of an intersection or crosswalk?",
        "options": [
            "10 feet",
            "15 feet",
            "20 feet",
            "30 feet"
        ],
        "answerIndex": 2,
        "explanation": "You may not park within 20 feet of an intersection or marked crosswalk so that visibility for pedestrians and approaching drivers is maintained."
    },
    {
        "id": "gq33",
        "category": "Parking Distances & Rules",
        "question": "In Virginia, you may NOT park within how many feet of a railroad crossing?",
        "options": [
            "20 feet",
            "30 feet",
            "50 feet",
            "100 feet"
        ],
        "answerIndex": 2,
        "explanation": "Parking is prohibited within 50 feet of the nearest rail of a railroad crossing."
    },
    {
        "id": "gq34",
        "category": "Parking Distances & Rules",
        "question": "When parking downhill on a two-way street WITH a curb, which way should you turn your front wheels?",
        "options": [
            "Turn wheels away from the curb (to the left).",
            "Turn wheels toward the curb (to the right).",
            "Keep wheels pointing straight ahead.",
            "It does not matter if the parking brake is set."
        ],
        "answerIndex": 1,
        "explanation": "When parking downhill with a curb, turn wheels toward the curb (to the right) so if brakes fail, the car rolls into the curb."
    },
    {
        "id": "gq35",
        "category": "Parking Distances & Rules",
        "question": "When parking UPHILL on a street WITH a curb, which direction should you turn your wheels?",
        "options": [
            "Turn wheels toward the curb (to the right).",
            "Turn wheels away from the curb (to the left) so the back of the front tire rests against the curb.",
            "Keep wheels pointing straight.",
            "Turn wheels to the right into the roadway."
        ],
        "answerIndex": 1,
        "explanation": "When parking uphill WITH a curb, turn your front wheels away from the curb (to the left) and let the vehicle roll back gently until the tire touches the curb."
    },
    {
        "id": "gq36",
        "category": "Parking Distances & Rules",
        "question": "When parking on a hill (uphill or downhill) WITHOUT a curb, how should your wheels be turned?",
        "options": [
            "Toward the center of the road.",
            "Toward the edge of the road (to the right).",
            "Straight ahead.",
            "Toward the oncoming lane."
        ],
        "answerIndex": 1,
        "explanation": "Without a curb, always turn your wheels toward the edge of the road (to the right) so the vehicle rolls off the roadway rather than into traffic."
    },

    # Topic 9: Alcohol, Drugs & Virginia DUI Laws
    {
        "id": "gq37",
        "category": "Alcohol, Drugs & Virginia DUI Laws",
        "question": "In Virginia, what is the legal Blood Alcohol Concentration (BAC) limit for drivers age 21 and older?",
        "options": [
            "0.04%",
            "0.05%",
            "0.08%",
            "0.10%"
        ],
        "answerIndex": 2,
        "explanation": "Drivers age 21 and older are legally considered driving under the influence (DUI) at a BAC of 0.08% or higher."
    },
    {
        "id": "gq38",
        "category": "Alcohol, Drugs & Virginia DUI Laws",
        "question": "Under Virginia's 'Zero Tolerance' law for drivers UNDER age 21, what BAC can result in criminal DUI penalties and license suspension?",
        "options": [
            "0.02% or higher",
            "0.05% or higher",
            "0.08% or higher",
            "0.10% or higher"
        ],
        "answerIndex": 0,
        "explanation": "Under Virginia's Zero Tolerance law, anyone under age 21 operating a motor vehicle with a BAC of 0.02% to less than 0.08% faces driver's license suspension for one year, minimum $500 fine, or 50 hours of community service."
    },
    {
        "id": "gq39",
        "category": "Alcohol, Drugs & Virginia DUI Laws",
        "question": "What does Virginia's 'Implied Consent' law mean?",
        "options": [
            "You give consent for police to search your trunk at any time.",
            "By driving on Virginia roads, you agree to take a chemical test (breath or blood) if arrested for suspected DUI.",
            "You consent to automatic vehicle impoundment upon any speeding ticket.",
            "You agree to purchase commercial auto insurance."
        ],
        "answerIndex": 1,
        "explanation": "Implied Consent means that by operating a motor vehicle in Virginia, you agree to submit to a chemical test if suspected of DUI. Refusal results in an immediate automatic 7-day administrative license suspension plus court penalties."
    },
    {
        "id": "gq40",
        "category": "Alcohol, Drugs & Virginia DUI Laws",
        "question": "If you refuse a chemical breath or blood test after being arrested for DUI in Virginia for the first time, your driver's license will be immediately suspended for:",
        "options": [
            "24 hours",
            "7 days by the magistrate, and 1 year by the court upon conviction of unreasonable refusal",
            "30 days",
            "90 days"
        ],
        "answerIndex": 1,
        "explanation": "Under Virginia law, unreasonable refusal of a breath test results in an immediate 7-day administrative suspension, and the court will suspend your license for 1 full year upon conviction."
    },
    {
        "id": "gq41",
        "category": "Alcohol, Drugs & Virginia DUI Laws",
        "question": "What is the only effective way to sober up and remove alcohol from your body?",
        "options": [
            "Drinking several cups of strong black coffee",
            "Taking a cold shower",
            "Giving your body sufficient time to metabolize the alcohol",
            "Vigorous physical exercise"
        ],
        "answerIndex": 2,
        "explanation": "Only time metabolizes alcohol. Coffee, cold showers, and exercise do not reduce blood alcohol concentration."
    },

    # Topic 10: Teen Driving Laws & Learner's Permit Rules
    {
        "id": "gq42",
        "category": "Teen Driving Laws & Learner's Permit Rules",
        "question": "Under Virginia law, what curfew applies to drivers under age 18?",
        "options": [
            "10:00 PM to 6:00 AM",
            "11:00 PM to 5:00 AM",
            "Midnight to 4:00 AM",
            "1:00 AM to 5:00 AM"
        ],
        "answerIndex": 2,
        "explanation": "Virginia law prohibits licensed drivers under age 18 from driving between Midnight and 4:00 AM, with narrow exceptions for work, school events, or medical emergencies."
    },
    {
        "id": "gq43",
        "category": "Teen Driving Laws & Learner's Permit Rules",
        "question": "While driving with a Virginia learner's permit, who must accompany you in the front passenger seat?",
        "options": [
            "Any friend who is at least 18 years old.",
            "A licensed driver who is at least 21 years old (or an immediate family member who is a licensed driver at least 18 years old).",
            "Any licensed driver regardless of age.",
            "Nobody, if driving during daylight hours."
        ],
        "answerIndex": 1,
        "explanation": "A permit holder must be accompanied by a licensed driver who is at least 21 years old, or an immediate family member who is at least 18 years old and licensed."
    },
    {
        "id": "gq44",
        "category": "Teen Driving Laws & Learner's Permit Rules",
        "question": "How many non-family passengers under age 21 may a Virginia driver under 18 carry during their first year of licensure?",
        "options": [
            "Only one non-family passenger",
            "Up to two passengers",
            "Up to three passengers",
            "No restrictions if everyone wears a seat belt"
        ],
        "answerIndex": 0,
        "explanation": "Virginia passenger restriction allows drivers under 18 to transport only ONE non-family passenger under age 21 for the first year of having a license."
    },
    {
        "id": "gq45",
        "category": "Teen Driving Laws & Learner's Permit Rules",
        "question": "Under Virginia law, what is the rule on cell phone usage for drivers under age 18?",
        "options": [
            "Hands-free calling is allowed, but texting is banned.",
            "All cell phone use (both handheld AND hands-free) is strictly prohibited while driving, except in emergencies.",
            "Cell phones may be used when stopped at red lights.",
            "Only GPS navigation apps are allowed."
        ],
        "answerIndex": 1,
        "explanation": "Virginia law completely bans any cell phone use (handheld or hands-free) for drivers under age 18 while operating a vehicle, except for a genuine emergency."
    },
    {
        "id": "gq46",
        "category": "Teen Driving Laws & Learner's Permit Rules",
        "question": "If you fail the Virginia learner's permit knowledge test 3 times, what must you do before you can test again?",
        "options": [
            "Wait 6 months.",
            "Complete the classroom portion of a Virginia-approved driver education program.",
            "Pay a $250 penalty fee.",
            "Submit a formal appeal to the DMV Commissioner."
        ],
        "answerIndex": 1,
        "explanation": "Under Virginia's 3-Failure Rule, if you fail the knowledge test 3 times, you must complete the classroom component of driver education before you are permitted to test a fourth time."
    },

    # Topic 11: Seat Belts & Child Safety Seats
    {
        "id": "gq47",
        "category": "Seat Belts & Child Safety Seats",
        "question": "Under Virginia law, who is legally required to wear a seat belt in a passenger vehicle?",
        "options": [
            "Only the driver.",
            "The driver and all front-seat passengers, as well as anyone under age 18 anywhere in the vehicle.",
            "Only passengers seated in the rear.",
            "Only occupants under age 21."
        ],
        "answerIndex": 1,
        "explanation": "Virginia law requires the driver, all front-seat occupants, and all passengers under age 18 (regardless of seating position) to wear properly secured safety belts."
    },
    {
        "id": "gq48",
        "category": "Seat Belts & Child Safety Seats",
        "question": "In Virginia, children must be secured in an approved child safety seat or booster seat until what age?",
        "options": [
            "Age 4",
            "Age 6",
            "Age 8",
            "Age 10"
        ],
        "answerIndex": 2,
        "explanation": "Virginia law requires all children under age 8 to be properly secured in an approved child safety seat or booster seat."
    },
    {
        "id": "gq49",
        "category": "Seat Belts & Child Safety Seats",
        "question": "Under Virginia law, until what age must infants be secured in a REAR-FACING child restraint seat?",
        "options": [
            "Until at least age 1",
            "Until at least age 2",
            "Until age 4",
            "Until weight exceeds 20 pounds"
        ],
        "answerIndex": 1,
        "explanation": "Virginia law requires children under age 2 to ride in a rear-facing child restraint seat unless the child meets minimum weight requirements approved by the manufacturer."
    },

    # Topic 12: Weather, Emergencies & Hazardous Driving
    {
        "id": "gq50",
        "category": "Weather, Emergencies & Hazardous Driving",
        "question": "What is hydroplaning, and at what speed can it begin in heavy rain?",
        "options": [
            "Tires floating on a film of water with total loss of traction, possible at speeds as low as 35 MPH.",
            "Brakes overheating from water intrusion.",
            "Engine flooding from deep puddles.",
            "Windshield fogging that reduces visibility."
        ],
        "answerIndex": 0,
        "explanation": "Hydroplaning occurs when water creates a film between your tires and the road surface, causing complete loss of steering and braking. It can happen at speeds as low as 35 MPH."
    },
    {
        "id": "gq51",
        "category": "Weather, Emergencies & Hazardous Driving",
        "question": "If your vehicle begins to hydroplane, what should you do?",
        "options": [
            "Slam on the brakes immediately.",
            "Ease your foot off the gas pedal gradually and steer straight until the tires regain traction.",
            "Turn the steering wheel vigorously back and forth.",
            "Pull the emergency handbrake."
        ],
        "answerIndex": 1,
        "explanation": "If your vehicle hydroplanes, do NOT slam on the brakes. Gently ease off the accelerator and steer straight until your tires make contact with the pavement again."
    },
    {
        "id": "gq52",
        "category": "Weather, Emergencies & Hazardous Driving",
        "question": "If your vehicle begins to skid, what is the proper recovery technique?",
        "options": [
            "Brake hard and steer in the opposite direction of the skid.",
            "Ease off the accelerator and steer gently in the direction you want the front of the vehicle to go.",
            "Accelerate rapidly to power out of the skid.",
            "Turn off the vehicle ignition."
        ],
        "answerIndex": 1,
        "explanation": "To recover from a skid, take your foot off the accelerator and gently steer in the direction you want the front wheels to travel. Avoid slamming on brakes."
    },
    {
        "id": "gq53",
        "category": "Weather, Emergencies & Hazardous Driving",
        "question": "Why are bridges and overpasses especially dangerous in freezing weather?",
        "options": [
            "Salt is not allowed on bridges.",
            "They freeze before normal road surfaces because cold air circulates both above and below the bridge deck.",
            "They have lower speed limits.",
            "Bridge pavements are smoother than highway roads."
        ],
        "answerIndex": 1,
        "explanation": "Bridges and ramps freeze before other roadway surfaces because cold air circulates underneath and around the bridge deck."
    },
    {
        "id": "gq54",
        "category": "Weather, Emergencies & Hazardous Driving",
        "question": "If you experience a sudden tire blowout while driving at highway speed, what should you do?",
        "options": [
            "Hit the brakes as hard as possible immediately.",
            "Hold the steering wheel firmly, keep the vehicle straight, ease off the gas, and brake gently only after the vehicle slows down.",
            "Yank the steering wheel to pull off the road abruptly.",
            "Shift into reverse."
        ],
        "answerIndex": 1,
        "explanation": "In a tire blowout, hold the wheel tightly to maintain control, take your foot off the accelerator, and let the car decelerate naturally before braking gently to pull over."
    },
    {
        "id": "gq55",
        "category": "Weather, Emergencies & Hazardous Driving",
        "question": "If your accelerator pedal gets stuck while driving, what should you do first?",
        "options": [
            "Turn off the ignition and remove the key immediately.",
            "Shift into neutral, apply steady brake pressure, and steer safely off the roadway.",
            "Pump the gas pedal repeatedly at full power.",
            "Jump out of the vehicle."
        ],
        "answerIndex": 1,
        "explanation": "Shift into NEUTRAL. This disconnects the engine from the wheels. Then apply steady brakes and steer safely to the shoulder before turning off the engine."
    },

    # Topic 13: Pavement Markings & Lane Usage
    {
        "id": "gq56",
        "category": "Pavement Markings & Lane Usage",
        "question": "What does a solid double yellow line down the center of a two-way road signify?",
        "options": [
            "Passing is permitted from both directions.",
            "Passing is prohibited from both directions.",
            "Passing is permitted only during daylight hours.",
            "The left lane is reserved for bicycles."
        ],
        "answerIndex": 1,
        "explanation": "A double solid yellow line indicates that passing is prohibited in both directions for traffic on either side."
    },
    {
        "id": "gq57",
        "category": "Pavement Markings & Lane Usage",
        "question": "What does a broken yellow line alongside a solid yellow line mean?",
        "options": [
            "You may pass only if the broken yellow line is on your side of the road and it is safe.",
            "Passing is forbidden from both directions.",
            "Both directions may pass at any time.",
            "You must turn around immediately."
        ],
        "answerIndex": 0,
        "explanation": "When a broken line is on your side, you may pass if the way ahead is clear. If the solid line is on your side, passing is prohibited."
    },
    {
        "id": "gq58",
        "category": "Pavement Markings & Lane Usage",
        "question": "What do broken white lines painted on the roadway indicate?",
        "options": [
            "Traffic is traveling in opposite directions.",
            "Traffic is moving in the same direction, and lane changes are permitted when safe.",
            "Lane changes are prohibited at all times.",
            "Pedestrian crosswalk zone."
        ],
        "answerIndex": 1,
        "explanation": "Broken white lines separate lanes of traffic traveling in the same direction. Drivers may cross these lines to change lanes when safe."
    },
    {
        "id": "gq59",
        "category": "Pavement Markings & Lane Usage",
        "question": "What do solid white lines separating lanes of traffic moving in the same direction mean?",
        "options": [
            "Lane changes are encouraged.",
            "Lane changes are discouraged or restricted; drivers should stay in their lane.",
            "Passing is permitted at any time.",
            "The lane is closing in 100 feet."
        ],
        "answerIndex": 1,
        "explanation": "Solid white lines discourage lane changes and signify areas where changing lanes is hazardous (such as near intersections or freeway merges)."
    },
    {
        "id": "gq60",
        "category": "Pavement Markings & Lane Usage",
        "question": "What does a diamond symbol painted on a highway lane designate?",
        "options": [
            "The lane is reserved for High Occupancy Vehicles (HOV), buses, or carpools.",
            "Passing is allowed in this lane only.",
            "Speed limit is 10 MPH higher in this lane.",
            "Emergency stopping only."
        ],
        "answerIndex": 0,
        "explanation": "A painted white diamond marks an HOV (High Occupancy Vehicle) lane, restricted during specified hours to buses, carpools, or vehicles meeting passenger minimums (e.g., HOV-2 or HOV-3)."
    },
    {
        "id": "gq61",
        "category": "Pavement Markings & Lane Usage",
        "question": "What does a painted bicycle symbol with two chevrons ('Sharrow') on the pavement mean?",
        "options": [
            "Bicycles must ride on the sidewalk.",
            "Shared lane marking indicating motorists and bicyclists share the full travel lane.",
            "Motorists are prohibited from using this lane.",
            "Bicycles must yield to all automobiles."
        ],
        "answerIndex": 1,
        "explanation": "Shared Lane Markings (Sharrows) alert road users that bicyclists may use the full travel lane and remind motorists to share the road safely."
    },

    # Topic 14: Sharing the Road (Bicycles, Pedestrians, Motorcycles)
    {
        "id": "gq62",
        "category": "Sharing the Road",
        "question": "When passing a bicyclist in Virginia, how much clearance must you legally provide?",
        "options": [
            "At least 1 foot",
            "At least 2 feet",
            "At least 3 feet",
            "At least 5 feet"
        ],
        "answerIndex": 2,
        "explanation": "Virginia law requires motorists to pass bicyclists with at least 3 feet of clearance. If unable to give 3 feet safely, the driver must wait until it is safe."
    },
    {
        "id": "gq63",
        "category": "Sharing the Road",
        "question": "Under Virginia law, are bicyclists entitled to the full travel lane when necessary for safety?",
        "options": [
            "No, bicycles must always ride on the sidewalk.",
            "Yes, bicycles are vehicles under the law and may use the full travel lane when passing, turning, or avoiding hazards.",
            "Only on residential streets with speed limits under 15 MPH.",
            "Only when escorted by a pilot vehicle."
        ],
        "answerIndex": 1,
        "explanation": "Bicycles are legal vehicles on Virginia roads and have the right to use the full lane to avoid hazards, make turns, or when the lane is too narrow to share side-by-side."
    },
    {
        "id": "gq64",
        "category": "Sharing the Road",
        "question": "What is the 'No-Zone' around large commercial trucks and buses?",
        "options": [
            "The area where trucks are not permitted to drive.",
            "The large blind spots around the front, rear, and both sides of commercial trucks where cars cannot be seen.",
            "The weight-station inspection zone.",
            "The distance between two semi-trucks."
        ],
        "answerIndex": 1,
        "explanation": "The 'No-Zone' refers to the expansive blind spots directly behind, in front of, and along both sides of large trucks. If you cannot see the driver in their mirror, they cannot see you."
    },
    {
        "id": "gq65",
        "category": "Sharing the Road",
        "question": "Why should you allow extra following distance when trailing behind a motorcycle?",
        "options": [
            "Motorcycles can stop much more quickly than passenger cars, and road hazards affect them more severely.",
            "Motorcycles accelerate very slowly.",
            "Motorcycles frequently drop objects on the road.",
            "Motorcycle brake lights are optional."
        ],
        "answerIndex": 0,
        "explanation": "Motorcycles are lighter and can stop in much shorter distances. Following too closely drastically increases the risk of rear-ending the motorcyclist."
    },

    # Topic 15: General Virginia Rules, Accidents & Penalties
    {
        "id": "gq66",
        "category": "General Virginia Rules & Penalties",
        "question": "What is Virginia's law regarding holding a handheld mobile phone while operating a vehicle?",
        "options": [
            "Holding a phone is legal if using speakerphone.",
            "Holding any handheld personal communications device while driving is completely illegal in Virginia.",
            "It is legal only when stopped at red traffic lights.",
            "It is permitted on interstate highways only."
        ],
        "answerIndex": 1,
        "explanation": "Virginia law bans holding a handheld mobile device while operating a motor vehicle on any Virginia highway. First violation carries a $125 fine."
    },
    {
        "id": "gq67",
        "category": "General Virginia Rules & Penalties",
        "question": "If you are involved in a traffic crash resulting in injury, death, or property damage, what must you do immediately?",
        "options": [
            "Drive home and report it online the following business day.",
            "Stop at once, help any injured persons, and report the accident to police immediately.",
            "Exchange business cards and leave the scene immediately.",
            "Call your insurance agent before contacting law enforcement."
        ],
        "answerIndex": 1,
        "explanation": "Virginia law requires stopping immediately at the scene of any crash involving injury, death, or property damage, rendering aid, and notifying law enforcement."
    },
    {
        "id": "gq68",
        "category": "General Virginia Rules & Penalties",
        "question": "In Virginia, aggressive driving is defined as committing a hazard with intent to:",
        "options": [
            "Harass, intimidate, injure, or obstruct another driver.",
            "Arrive at your destination on time.",
            "Pass an oversized vehicle.",
            "Test vehicle acceleration."
        ],
        "answerIndex": 0,
        "explanation": "Virginia law classifies aggressive driving as operating a vehicle with the intent to harass, intimidate, injure, or obstruct other drivers."
    },
    {
        "id": "gq69",
        "category": "General Virginia Rules & Penalties",
        "question": "When must you report a crash to the DMV in Virginia?",
        "options": [
            "If police do not investigate and the crash results in death, injury, or property damage of $1,500 or more.",
            "Whenever any fender bender occurs.",
            "Only when cited for a moving violation.",
            "Within 90 days of any incident."
        ],
        "answerIndex": 0,
        "explanation": "If law enforcement does not investigate the accident, drivers must file a crash report with DMV within 10 days if damage exceeds $1,500 or involves injury or death."
    },
    {
        "id": "gq70",
        "category": "General Virginia Rules & Penalties",
        "question": "What should you do if an aggressive driver tailgates you or flashes their high beams?",
        "options": [
            "Brake check them to teach them a lesson.",
            "Stay calm, do not make eye contact, safely move to the right lane, and let them pass.",
            "Match their speed and refuse to let them overtake.",
            "Honk your horn and wave angrily."
        ],
        "answerIndex": 1,
        "explanation": "Never engage with aggressive drivers. Safely change lanes to the right, allow them to pass, and maintain your distance."
    },
    {
        "id": "gq71",
        "category": "General Virginia Rules & Penalties",
        "question": "What does a flashing RED traffic light mean in Virginia?",
        "options": [
            "Slow down and proceed with caution without stopping.",
            "Treat it exactly like a STOP sign: come to a complete stop, yield right-of-way, and proceed when clear.",
            "The intersection is closed to traffic.",
            "Pedestrians only may cross."
        ],
        "answerIndex": 1,
        "explanation": "A flashing red traffic signal has the exact same legal meaning as a stop sign. You must come to a full stop and yield to traffic before proceeding."
    },
    {
        "id": "gq72",
        "category": "General Virginia Rules & Penalties",
        "question": "What does a flashing YELLOW traffic light mean in Virginia?",
        "options": [
            "Come to a mandatory complete stop.",
            "Slow down and proceed through the intersection with caution.",
            "The light is about to turn red within 2 seconds.",
            "Right turns only are permitted."
        ],
        "answerIndex": 1,
        "explanation": "A flashing yellow light warns drivers to slow down and proceed with heightened caution."
    },
    {
        "id": "gq73",
        "category": "General Virginia Rules & Penalties",
        "question": "What does a steady yellow light indicate?",
        "options": [
            "Speed up to clear the intersection before the red light.",
            "The red light is about to appear; come to a stop if you can safely do so without risking a rear-end collision.",
            "You have guaranteed right-of-way over all vehicles.",
            "You may make a U-turn."
        ],
        "answerIndex": 1,
        "explanation": "A steady yellow signal warns that the green signal has ended and red is imminent. Stop if you can do so safely; do not accelerate into the intersection."
    },
    {
        "id": "gq74",
        "category": "General Virginia Rules & Penalties",
        "question": "When entering an expressway or interstate from an on-ramp, what is the correct procedure?",
        "options": [
            "Stop at the beginning of the acceleration lane and wait for a gap.",
            "Use the acceleration lane to match expressway speed, scan your mirrors and blind spots, and merge smoothly into a gap.",
            "Immediately merge across all lanes into the left express lane.",
            "Force expressway drivers to yield to you."
        ],
        "answerIndex": 1,
        "explanation": "Use the acceleration lane to build speed matching expressway traffic, signal, check blind spots, and merge when there is a safe gap."
    },
    {
        "id": "gq75",
        "category": "General Virginia Rules & Penalties",
        "question": "If you miss your exit on a highway or interstate, what should you do?",
        "options": [
            "Stop on the shoulder and back up to the ramp.",
            "Make an immediate U-turn across the grass median.",
            "Continue to the next exit and safely turn around there.",
            "Honk your horn and cut across exit lanes."
        ],
        "answerIndex": 2,
        "explanation": "Never back up or make a U-turn on an interstate highway. Proceed to the next exit and navigate back safely."
    }
]

# Quick cheat sheet numbers and rules for rapid review before test
CHEAT_SHEET = {
    "speed_limits": [
        {"zone": "School, Business, Residential", "speed": "25 MPH", "notes": "Unless otherwise posted"},
        {"zone": "Unpaved Secondary Roads", "speed": "35 MPH", "notes": "Statutory limit in Virginia"},
        {"zone": "Non-Interstate Paved Highways", "speed": "55 MPH", "notes": "Unless otherwise posted"},
        {"zone": "Interstate Highways", "speed": "55 - 70 MPH", "notes": "As posted by VDOT"},
        {"zone": "Reckless Driving Threshold", "speed": "85+ MPH or 20+ MPH over limit", "notes": "Class 1 Misdemeanor in VA"}
    ],
    "following_distances": [
        {"speed_range": "Under 35 MPH", "seconds": "2 Seconds", "notes": "On dry, clean pavement"},
        {"speed_range": "35 to 45 MPH", "seconds": "3 Seconds", "notes": "Allows reaction + braking space"},
        {"speed_range": "46 to 70 MPH", "seconds": "4 Seconds", "notes": "High speed highway rule"},
        {"speed_range": "Rain, Ice, Snow, Fog", "seconds": "Double or Triple", "notes": "Add buffer when following trucks or motorcycles"}
    ],
    "parking_distances": [
        {"location": "Fire Hydrant", "distance": "15 Feet", "rule": "Never park within 15 ft"},
        {"location": "Intersection / Crosswalk", "distance": "20 Feet", "rule": "Maintain sight lines for pedestrians"},
        {"location": "Railroad Crossing", "distance": "50 Feet", "rule": "From nearest rail"},
        {"location": "Fire Station Entrance", "distance": "15 Feet", "rule": "Same side (75 ft on opposite side)"},
        {"location": "Emergency Vehicle with flashing lights", "distance": "500 Feet", "rule": "Do not follow closer than 500 ft"}
    ],
    "lighting_and_signals": [
        {"requirement": "Headlights Required", "rule": "Sunset to Sunrise, AND whenever wipers are in use, AND anytime visibility < 500 ft"},
        {"requirement": "Dim High Beams (Approaching)", "rule": "Within 500 Feet of oncoming traffic"},
        {"requirement": "Dim High Beams (Following)", "rule": "Within 200 Feet of vehicle ahead"},
        {"requirement": "Turn Signal Distance", "rule": "At least 100 Feet before turning or changing lanes"},
        {"requirement": "Bicycle Clearance", "rule": "At least 3 Feet passing buffer"}
    ],
    "alcohol_and_teen_laws": [
        {"topic": "Adult BAC Limit (21+)", "detail": "0.08% or higher is illegal (DUI)"},
        {"topic": "Under 21 Zero Tolerance", "detail": "0.02% to 0.08% BAC leads to 1-yr license suspension & $500 fine"},
        {"topic": "Implied Consent Law", "detail": "Refusal of breath test = immediate 7-day administrative suspension + 1-yr court revocation"},
        {"topic": "Teen Curfew (under 18)", "detail": "Midnight to 4:00 AM"},
        {"topic": "Teen Cell Phone Ban", "detail": "100% prohibited (both handheld & hands-free) for drivers under 18"},
        {"topic": "Child Safety Seats", "detail": "Required under age 8; rear-facing required until age 2"}
    ],
    "sign_shapes_colors": [
        {"shape": "Octagon (8 sides)", "meaning": "STOP only", "color": "Red with white letters"},
        {"shape": "Triangle (pointing down)", "meaning": "YIELD only", "color": "Red and white"},
        {"shape": "Pentagon (5 sides)", "meaning": "School Zone / School Crossing", "color": "Fluorescent Yellow-Green"},
        {"shape": "Pennant (pointing right)", "meaning": "No Passing Zone", "color": "Yellow with black letters (posted on left)"},
        {"shape": "Round (Circle)", "meaning": "Railroad Advance Warning", "color": "Yellow with black RXR"},
        {"shape": "Crossbuck (X)", "meaning": "Railroad Crossing", "color": "White with black letters"},
        {"shape": "Diamond", "meaning": "Warning / Hazard Ahead", "color": "Yellow or Orange (Work Zone)"},
        {"shape": "Vertical Rectangle", "meaning": "Regulatory (Speed, lane rules)", "color": "White with black letters"},
        {"shape": "Horizontal Rectangle", "meaning": "Guide / Direction / Information", "color": "Green, Blue, Brown, or Red (Wrong Way)"}
    ]
}

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    with open(os.path.join(data_dir, "signs.json"), "w", encoding="utf-8") as f:
        json.dump(SIGNS, f, indent=2)
    print(f"Generated data/signs.json ({len(SIGNS)} signs)")

    with open(os.path.join(data_dir, "questions_signs.json"), "w", encoding="utf-8") as f:
        json.dump(QUESTIONS_SIGNS, f, indent=2)
    print(f"Generated data/questions_signs.json ({len(QUESTIONS_SIGNS)} questions)")

    with open(os.path.join(data_dir, "questions_general.json"), "w", encoding="utf-8") as f:
        json.dump(QUESTIONS_GENERAL, f, indent=2)
    print(f"Generated data/questions_general.json ({len(QUESTIONS_GENERAL)} questions)")

    with open(os.path.join(data_dir, "cheat_sheet.json"), "w", encoding="utf-8") as f:
        json.dump(CHEAT_SHEET, f, indent=2)
    print("Generated data/cheat_sheet.json")

if __name__ == "__main__":
    main()
