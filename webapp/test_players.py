#!/usr/bin/env python3
"""
Quick test script to check player names in FPL database
"""

from player_combination_analysis import FPLCombinationAnalyzer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create analyzer and load data
analyzer = FPLCombinationAnalyzer()
analyzer.initialize_data()

print("Searching for Salah...")
salah_matches = analyzer.players_df[analyzer.players_df['web_name'].str.contains(
    'Salah', case=False, na=False)]
print("Salah matches by web_name:")
for _, player in salah_matches.iterrows():
    print(
        f"  ID: {player['id']}, Web: {player['web_name']}, Full: {player['full_name']}")

print("\nSearching for Mohamed...")
mohamed_matches = analyzer.players_df[analyzer.players_df['first_name'].str.contains(
    'Mohamed', case=False, na=False)]
print("Mohamed matches by first_name:")
for _, player in mohamed_matches.iterrows():
    print(
        f"  ID: {player['id']}, Web: {player['web_name']}, Full: {player['full_name']}")

print("\nSearching for Bruno...")
bruno_matches = analyzer.players_df[analyzer.players_df['first_name'].str.contains(
    'Bruno', case=False, na=False)]
print("Bruno matches by first_name:")
for _, player in bruno_matches.iterrows():
    print(
        f"  ID: {player['id']}, Web: {player['web_name']}, Full: {player['full_name']}")

print("\nSearching for Fernandes...")
fernandes_matches = analyzer.players_df[analyzer.players_df['second_name'].str.contains(
    'Fernandes', case=False, na=False)]
print("Fernandes matches by second_name:")
for _, player in fernandes_matches.iterrows():
    print(
        f"  ID: {player['id']}, Web: {player['web_name']}, Full: {player['full_name']}")
