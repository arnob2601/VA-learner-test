#!/usr/bin/env bash
# Virginia DMV Learner's Permit Exam Simulator Launcher
cd "$(dirname "$0")"

echo "============================================================"
echo " 🚗 Starting Virginia DMV Learner's Permit Exam Simulator..."
echo "============================================================"

# Ensure data is generated
if [ ! -f "data/signs.json" ]; then
  python3 generate_data.py
fi

# Run the local server
python3 server.py "$@"
