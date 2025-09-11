#!/usr/bin/env python3
"""
FPL Player Combination Web App

A Flask web application for analyzing player combinations across FPL league managers.
Built on top of the existing FPL analysis tool with caching capabilities.
"""

import sys
import os
import json
from flask import Flask, render_template, request, jsonify, flash
from datetime import datetime

# Add parent directory to path to import the analysis module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from player_combination_analysis import FPLCombinationAnalyzer

app = Flask(__name__)
app.secret_key = 'fpl_analyzer_secret_key_change_in_production'

# Global analyzer instance
analyzer = FPLCombinationAnalyzer()

# Cache for league standings to avoid repeated fetching
league_standings_cache = {}
cache_timestamps = {}

# Cache settings
CACHE_EXPIRY_MINUTES = 1440  # Clear cache after 1 day (24 hours * 60 minutes)
MAX_CACHED_LEAGUES = 5       # Keep max 5 leagues in memory


def cleanup_expired_cache():
    """Remove expired cache entries and limit cache size."""
    current_time = datetime.now()
    expired_keys = []

    # Find expired entries
    for cache_key, timestamp in cache_timestamps.items():
        if (current_time - timestamp).total_seconds() > CACHE_EXPIRY_MINUTES * 60:
            expired_keys.append(cache_key)

    # Remove expired entries
    for key in expired_keys:
        league_standings_cache.pop(key, None)
        cache_timestamps.pop(key, None)

    # If still too many entries, remove oldest ones
    if len(league_standings_cache) > MAX_CACHED_LEAGUES:
        # Sort by timestamp and keep only the newest entries
        sorted_items = sorted(cache_timestamps.items(),
                              key=lambda x: x[1], reverse=True)
        keys_to_keep = [item[0] for item in sorted_items[:MAX_CACHED_LEAGUES]]

        # Remove excess entries
        keys_to_remove = set(league_standings_cache.keys()) - set(keys_to_keep)
        for key in keys_to_remove:
            league_standings_cache.pop(key, None)
            cache_timestamps.pop(key, None)

    if expired_keys:
        print(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")


def is_cache_valid(cache_key):
    """Check if a cache entry is still valid (not expired)."""
    if cache_key not in cache_timestamps:
        return False

    current_time = datetime.now()
    cache_time = cache_timestamps[cache_key]
    is_valid = (current_time -
                cache_time).total_seconds() <= CACHE_EXPIRY_MINUTES * 60

    return is_valid

# Global analyzer instance


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/api/load_league', methods=['POST'])
def load_league():
    """Load league data."""
    try:
        data = request.get_json()
        league_id = data.get('league_id')

        if not league_id:
            return jsonify({'error': 'League ID is required'}), 400

        try:
            league_id = int(league_id)
        except ValueError:
            return jsonify({'error': 'League ID must be a number'}), 400

        # Check if data is already loaded for this league
        if analyzer.current_league_id == league_id and analyzer.manager_squads:
            return jsonify({
                'success': True,
                'message': f'League {league_id} data already loaded',
                'manager_count': len(analyzer.manager_squads),
                'from_cache': True
            })

        # Initialize bootstrap data if not already done
        if not analyzer.bootstrap_data:
            success = analyzer.initialize_data()
            if not success:
                return jsonify({'error': 'Failed to initialize FPL data'}), 500

        # Get current gameweek for cache check
        current_gw = None
        if analyzer.bootstrap_data:
            events = analyzer.bootstrap_data.get('events', [])
            current_gw = next((gw['id']
                              for gw in events if gw['is_current']), 1)

        # Check if cache exists before attempting to load
        cache_available = analyzer.cache_exists(league_id, current_gw)
        
        if cache_available:
            print(f"🚀 Cache found for league {league_id}, gameweek {current_gw} - loading immediately...")
            # Try to load cache first (skip_prompt=True for web app)
            cache_loaded = analyzer.load_manager_squads_cache(
                league_id, current_gw, skip_prompt=True)
        else:
            print(f"📥 No cache found for league {league_id}, gameweek {current_gw} - will fetch fresh data")
            cache_loaded = False

        if cache_loaded:
            # Set the current league ID so the analyzer knows which league is loaded
            analyzer.current_league_id = league_id

            # Check if we have league data from cache (new format) or need to fetch it (old format)
            cache_key = f"{league_id}_{current_gw}"
            if analyzer.league_data and 'standings' in analyzer.league_data:
                # New cache format - league data is available
                league_standings = analyzer.league_data.get(
                    'standings', {}).get('results', [])
                league_standings_cache[cache_key] = league_standings
                cache_timestamps[cache_key] = datetime.now()
                print(f"⚡ League data loaded from cache for {cache_key}")
            else:
                # Old cache format or missing league data - fetch it once and cache it
                print(f"📊 Fetching league standings for cached league {league_id} (one-time upgrade)...")
                if analyzer.get_league_info(league_id):
                    # Cache the league standings in memory
                    if analyzer.league_data and 'standings' in analyzer.league_data:
                        league_standings = analyzer.league_data.get(
                            'standings', {}).get('results', [])
                        league_standings_cache[cache_key] = league_standings
                        cache_timestamps[cache_key] = datetime.now()
                        print(f"💾 Cached league standings for {cache_key}")
                        
                        # Update the cache file with the new format for next time
                        analyzer.save_manager_squads_cache(league_id, current_gw)
                        print(f"🔄 Updated cache to new format with league data")

            return jsonify({
                'success': True,
                'message': f'Successfully loaded league {league_id} from cache (fast)',
                'manager_count': len(analyzer.manager_squads),
                'from_cache': True
            })

        # No cache found, fetch fresh data
        if not analyzer.get_league_info(league_id):
            return jsonify({'error': 'Failed to load league data. Please check the league ID.'}), 400

        # Cache the league standings in memory immediately after fetching
        cache_key = f"{league_id}_{current_gw}"
        if analyzer.league_data and 'standings' in analyzer.league_data:
            league_standings = analyzer.league_data.get(
                'standings', {}).get('results', [])
            league_standings_cache[cache_key] = league_standings
            cache_timestamps[cache_key] = datetime.now()
            print(f"💾 Cached league standings during load for {cache_key}")

        # Get manager IDs and fetch squads
        manager_ids = [entry['entry']
                       for entry in analyzer.league_data['standings']['results']]

        try:
            # Fetch manager squads
            analyzer.fetch_manager_squads_batch(manager_ids)

            # Save to cache for future use
            analyzer.save_manager_squads_cache(league_id, current_gw)

            return jsonify({
                'success': True,
                'message': f'Successfully loaded league {league_id}',
                'manager_count': len(analyzer.manager_squads),
                'from_cache': False
            })

        except Exception as e:
            return jsonify({'error': f'Error fetching manager squads: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/api/search_players', methods=['POST'])
def search_players():
    """Search for players by name."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'players': []})

        # Make sure bootstrap data is loaded
        if analyzer.players_df is None:
            if not analyzer.initialize_data():
                return jsonify({'error': 'Failed to initialize player data'}), 500

        query_lower = query.lower()

        # Multiple search strategies
        matches = []

        # 1. Exact web_name match (highest priority)
        exact_web = analyzer.players_df[analyzer.players_df['web_name'].str.lower(
        ) == query_lower]
        matches.extend(exact_web.to_dict('records'))

        # 2. Web_name starts with query
        starts_web = analyzer.players_df[analyzer.players_df['web_name'].str.lower(
        ).str.startswith(query_lower)]
        matches.extend(starts_web.to_dict('records'))

        # 3. Web_name contains query
        contains_web = analyzer.players_df[analyzer.players_df['web_name'].str.lower(
        ).str.contains(query_lower, na=False)]
        matches.extend(contains_web.to_dict('records'))

        # 4. Full name contains query
        contains_full = analyzer.players_df[analyzer.players_df['full_name'].str.lower(
        ).str.contains(query_lower, na=False)]
        matches.extend(contains_full.to_dict('records'))

        # 5. First or last name contains query
        contains_first = analyzer.players_df[analyzer.players_df['first_name'].str.lower(
        ).str.contains(query_lower, na=False)]
        matches.extend(contains_first.to_dict('records'))

        contains_second = analyzer.players_df[analyzer.players_df['second_name'].str.lower(
        ).str.contains(query_lower, na=False)]
        matches.extend(contains_second.to_dict('records'))

        # Remove duplicates while preserving order
        seen_ids = set()
        unique_matches = []
        for match in matches:
            if match['id'] not in seen_ids:
                seen_ids.add(match['id'])
                unique_matches.append(match)

        # Limit results
        unique_matches = unique_matches[:20]

        players = []
        for player in unique_matches:
            # Get team and position names from bootstrap data
            team_name = "Unknown"
            position_name = "Unknown"

            if analyzer.bootstrap_data:
                # Get team name
                teams = analyzer.bootstrap_data.get('teams', [])
                team_data = next(
                    (t for t in teams if t['id'] == player['team']), None)
                if team_data:
                    team_name = team_data['name']

                # Get position name
                element_types = analyzer.bootstrap_data.get(
                    'element_types', [])
                pos_data = next(
                    (p for p in element_types if p['id'] == player['element_type']), None)
                if pos_data:
                    position_name = pos_data['singular_name']

            players.append({
                'id': int(player['id']),
                'name': str(player['web_name']),
                'full_name': str(player['full_name']),
                'team': team_name,
                'position': position_name
            })

        return jsonify({'players': players})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


def find_player_by_name(name):
    """Find a player by name with flexible matching."""
    if analyzer.players_df is None:
        return None

    name_lower = name.lower().strip()

    # Try exact web_name match first
    exact_match = analyzer.players_df[analyzer.players_df['web_name'].str.lower(
    ) == name_lower]
    if not exact_match.empty:
        return exact_match.iloc[0]

    # Try web_name contains
    web_name_match = analyzer.players_df[analyzer.players_df['web_name'].str.lower(
    ).str.contains(name_lower, na=False)]
    if not web_name_match.empty:
        return web_name_match.iloc[0]

    # Try full_name contains
    full_name_match = analyzer.players_df[analyzer.players_df['full_name'].str.lower(
    ).str.contains(name_lower, na=False)]
    if not full_name_match.empty:
        return full_name_match.iloc[0]

    # Try first_name or second_name contains
    first_name_match = analyzer.players_df[analyzer.players_df['first_name'].str.lower(
    ).str.contains(name_lower, na=False)]
    if not first_name_match.empty:
        return first_name_match.iloc[0]

    second_name_match = analyzer.players_df[analyzer.players_df['second_name'].str.lower(
    ).str.contains(name_lower, na=False)]
    if not second_name_match.empty:
        return second_name_match.iloc[0]

    return None


@app.route('/api/analyze_combination', methods=['POST'])
def analyze_combination():
    """Analyze player combinations."""
    try:
        data = request.get_json()
        player_names = data.get('player_names', [])

        if not player_names:
            return jsonify({'error': 'At least one player name is required'}), 400

        if not analyzer.manager_squads:
            return jsonify({'error': 'No league data loaded. Please load a league first.'}), 400

        # Make sure bootstrap data is loaded
        if analyzer.players_df is None:
            if not analyzer.initialize_data():
                return jsonify({'error': 'Failed to initialize player data'}), 500

        # Find player IDs using our improved search
        player_ids = []
        found_players = []

        for name in player_names:
            player = find_player_by_name(name)
            if player is None:
                return jsonify({'error': f"Player '{name}' not found. Try using the exact name from the search suggestions."}), 400

            player_ids.append(int(player['id']))
            found_players.append(player['web_name'])

        # Find managers with all these players
        matching_managers = []
        for manager_id, squad_data in analyzer.manager_squads.items():
            try:
                squad_player_ids = [pick['element']
                                    for pick in squad_data['picks']]
                if all(pid in squad_player_ids for pid in player_ids):
                    matching_managers.append(manager_id)
            except (KeyError, TypeError):
                continue

        # Get current gameweek for the FPL link
        current_gw = 1  # Default fallback
        if analyzer.bootstrap_data:
            events = analyzer.bootstrap_data.get('events', [])
            current_gw = next((gw['id']
                              for gw in events if gw['is_current']), 1)

        # Get detailed manager information from league data
        formatted_results = []

        # Check if we have league standings cached in memory for this league
        cache_key = f"{analyzer.current_league_id}_{current_gw}"

        print(f"🔍 Debug: Looking for cache key: {cache_key}")
        print(
            f"🔍 Debug: Available cache keys: {list(league_standings_cache.keys())}")
        print(f"🔍 Debug: Cache exists: {cache_key in league_standings_cache}")
        print(f"🔍 Debug: Cache valid: {is_cache_valid(cache_key)}")

        if cache_key in league_standings_cache and is_cache_valid(cache_key):
            print(f"⚡ Using cached league standings for {cache_key}")
            # Use cached league standings - no need to fetch
            league_standings = league_standings_cache[cache_key]
        else:
            # Cache miss or expired - need to fetch league standings
            if cache_key in league_standings_cache:
                print(f"🔄 Cache expired! Fetching fresh league standings...")
            else:
                print(f"🔄 Cache miss! Fetching league standings for manager details...")

            analyzer.get_league_info(analyzer.current_league_id)

            # Cache the league standings in memory with timestamp
            if analyzer.league_data:
                league_standings = analyzer.league_data.get(
                    'standings', {}).get('results', [])
                league_standings_cache[cache_key] = league_standings
                cache_timestamps[cache_key] = datetime.now()
                print(f"💾 Cached league standings for {cache_key}")
            else:
                league_standings = []

        # Clean up expired cache entries AFTER using the cache
        cleanup_expired_cache()

        if league_standings and matching_managers:

            # Limit to first 50 for performance
            for manager_id in matching_managers[:50]:
                # Find manager in league standings
                manager_info = next(
                    (m for m in league_standings if m['entry'] == manager_id), None)

                # Get gameweek points from the manager's squad data
                gw_points = 0
                if manager_id in analyzer.manager_squads:
                    squad_data = analyzer.manager_squads[manager_id]
                    # Try to get points from different possible locations in the data
                    if 'entry_history' in squad_data and squad_data['entry_history']:
                        gw_points = squad_data['entry_history'].get(
                            'points', 0)
                    elif 'current_event_points' in squad_data:
                        gw_points = squad_data.get('current_event_points', 0)
                    # If still 0, we might need to calculate from picks
                    if gw_points == 0 and 'picks' in squad_data:
                        # This is a fallback - actual GW points calculation would be complex
                        gw_points = 0  # Keep as 0 for now since we don't have live points

                if manager_info:
                    formatted_results.append({
                        'manager_id': manager_id,
                        'manager_name': manager_info.get('player_name', f'Manager {manager_id}'),
                        'team_name': manager_info.get('entry_name', f'Team {manager_id}'),
                        'total_points': manager_info.get('total', 0),
                        'gw_points': gw_points,
                        'fpl_url': f'https://fantasy.premierleague.com/entry/{manager_id}/event/{current_gw}',
                        'players_found': found_players,
                        'missing_players': []
                    })
                else:
                    # Fallback if manager not found in standings
                    formatted_results.append({
                        'manager_id': manager_id,
                        'manager_name': f'Manager {manager_id}',
                        'team_name': f'Team {manager_id}',
                        'total_points': 0,
                        'gw_points': gw_points,
                        'fpl_url': f'https://fantasy.premierleague.com/entry/{manager_id}/event/{current_gw}',
                        'players_found': found_players,
                        'missing_players': []
                    })
        else:
            # Fallback when no league data available
            for manager_id in matching_managers[:50]:
                # Get gameweek points from the manager's squad data
                gw_points = 0
                if manager_id in analyzer.manager_squads:
                    squad_data = analyzer.manager_squads[manager_id]
                    if 'entry_history' in squad_data and squad_data['entry_history']:
                        gw_points = squad_data['entry_history'].get(
                            'points', 0)
                    elif 'current_event_points' in squad_data:
                        gw_points = squad_data.get('current_event_points', 0)

                formatted_results.append({
                    'manager_id': manager_id,
                    'manager_name': f'Manager {manager_id}',
                    'team_name': f'Team {manager_id}',
                    'total_points': 0,
                    'gw_points': gw_points,
                    'fpl_url': f'https://fantasy.premierleague.com/entry/{manager_id}/event/{current_gw}',
                    'players_found': found_players,
                    'missing_players': []
                })

        return jsonify({
            'success': True,
            'total_managers': len(analyzer.manager_squads),
            'matching_managers': len(matching_managers),
            'percentage': (len(matching_managers) / len(analyzer.manager_squads)) * 100 if analyzer.manager_squads else 0,
            'results': formatted_results,
            'current_gameweek': current_gw
        })

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/api/league_info')
def league_info():
    """Get current league information."""
    try:
        if not analyzer.current_league_id:
            return jsonify({'loaded': False})

        return jsonify({
            'loaded': True,
            'league_id': analyzer.current_league_id,
            'manager_count': len(analyzer.manager_squads) if analyzer.manager_squads else 0,
            'league_name': analyzer.league_data.get('name', 'Unknown') if analyzer.league_data else 'Unknown'
        })

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/api/cache_info')
def cache_info():
    """Get cache information."""
    try:
        cache_files = analyzer.list_available_caches()

        cache_info = []
        for cache_file in cache_files:
            cache_info.append({
                'league_id': cache_file['league_id'],
                'gameweek': cache_file['gameweek'],
                'manager_count': cache_file['manager_count'],
                'cached_at': cache_file['cached_at'],
                'total_managers': cache_file['total_managers_in_league']
            })

        return jsonify({'cache_files': cache_info})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    import os

    # Get configuration from environment variables
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5001))
    host = os.getenv('HOST', '0.0.0.0')

    if debug_mode:
        print("🚀 Starting FPL Player Combination Web App (Development)...")
        print(f"📱 Open http://localhost:{port} in your browser")
        print("🔄 Press Ctrl+C to stop the server")
    else:
        print("🚀 Starting FPL Player Combination Web App (Production)...")
        print(f"🌐 Running on {host}:{port}")

    app.run(debug=debug_mode, host=host, port=port)
