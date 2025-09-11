#!/usr/bin/env python3
"""
Quick test to see what data is in the cached manager squads
"""

from player_combination_analysis import FPLCombinationAnalyzer
import sys
import os
import pickle
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def inspect_cache():
    analyzer = FPLCombinationAnalyzer()

    # Load from existing cache
    cache_loaded = analyzer.load_manager_squads_cache(13907, 3)

    if cache_loaded and analyzer.manager_squads:
        # Get first manager's data to inspect structure
        first_manager_id = list(analyzer.manager_squads.keys())[0]
        first_manager_data = analyzer.manager_squads[first_manager_id]

        print("=== Manager Squad Data Structure ===")
        print(f"Manager ID: {first_manager_id}")
        print("Available keys:", list(first_manager_data.keys()))
        print()

        for key, value in first_manager_data.items():
            print(f"{key}: {type(value)}")
            if key == 'picks' and isinstance(value, list) and len(value) > 0:
                print(f"  First pick: {value[0]}")
            elif key == 'entry_history' and isinstance(value, dict):
                print(f"  Entry history keys: {list(value.keys())}")
                print(f"  Entry history: {value}")
            else:
                print(f"  Value: {value}")
            print()
    else:
        print("No cache found or failed to load")


if __name__ == "__main__":
    inspect_cache()
