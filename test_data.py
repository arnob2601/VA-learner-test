#!/usr/bin/env python3
"""
test_data.py: Validates JSON datasets for Virginia DMV quiz application.
"""
import json
import os
import sys

def test_datasets():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    
    with open(os.path.join(data_dir, "signs.json")) as f:
        signs = json.load(f)
    with open(os.path.join(data_dir, "questions_signs.json")) as f:
        q_signs = json.load(f)
    with open(os.path.join(data_dir, "questions_general.json")) as f:
        q_general = json.load(f)
    with open(os.path.join(data_dir, "cheat_sheet.json")) as f:
        cheat_sheet = json.load(f)

    sign_ids = {s["id"] for s in signs}
    print(f"Loaded {len(signs)} signs, {len(q_signs)} sign questions, {len(q_general)} general questions.")

    # Validate signs
    for sign in signs:
        assert "id" in sign, "Sign missing id"
        assert "name" in sign, "Sign missing name"
        assert "shape" in sign, "Sign missing shape"
        assert "color" in sign, "Sign missing color"
        assert "meaning" in sign, "Sign missing meaning"
        assert "svg" in sign and sign["svg"].startswith("<svg"), f"Invalid SVG for {sign['id']}"

    # Validate sign questions
    for q in q_signs:
        assert "id" in q, "Sign question missing id"
        assert "question" in q, "Sign question missing text"
        assert "options" in q and len(q["options"]) >= 3, f"Sign question {q['id']} has < 3 options"
        assert "answerIndex" in q and 0 <= q["answerIndex"] < len(q["options"]), f"Invalid answerIndex in {q['id']}"
        assert "explanation" in q, f"Missing explanation in {q['id']}"
        if "signId" in q:
            assert q["signId"] in sign_ids, f"Sign ID {q['signId']} not found in signs.json"

    # Validate general questions
    for q in q_general:
        assert "id" in q, "General question missing id"
        assert "category" in q, "General question missing category"
        assert "question" in q, "General question missing text"
        assert "options" in q and len(q["options"]) >= 3, f"General question {q['id']} has < 3 options"
        assert "answerIndex" in q and 0 <= q["answerIndex"] < len(q["options"]), f"Invalid answerIndex in {q['id']}"
        assert "explanation" in q, f"Missing explanation in {q['id']}"

    print("All dataset tests passed successfully!")

if __name__ == "__main__":
    test_datasets()
