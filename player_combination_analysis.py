#!/usr/bin/env python3
"""
FPL Player Combination Analysis Tool

A robust Python script for analyzing player combinations across FPL league managers.
Designed to handle large leagues efficiently without memory issues.

Usage:
    python player_combination_analysis.py

Features:
- Interactive league code input
- Player name search and selection
- Multiple combination analysis without re-fetching data
- Progress tracking and error handling
- Optimized for large leagues (tested up to 32k+ managers)
"""

import requests
import pandas as pd
import time
import gc
import json
import pickle
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Set, Tuple, Optional
import sys
import os

# Create a session for reusing connections
session = requests.Session()
session.headers.update({'User-Agent': 'FPL League Analysis Tool'})


class FPLCombinationAnalyzer:
    def __init__(self):
        self.bootstrap_data = None
        self.players_df = None
        self.league_data = None
        self.manager_squads = {}
        self.current_league_id = None
        self.cache_dir = "fpl_cache"

        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_cache_filename(self, league_id: int, gameweek: int = None) -> str:
        """Generate cache filename for a specific league and gameweek."""
        if gameweek is None:
            if self.bootstrap_data:
                events = self.bootstrap_data.get('events', [])
                gameweek = next((gw['id']
                                for gw in events if gw['is_current']), 1)
            else:
                gameweek = 1
        return os.path.join(self.cache_dir, f"league_{league_id}_gw_{gameweek}.pkl")

    def get_cache_info_filename(self, league_id: int, gameweek: int = None) -> str:
        """Generate cache info filename for metadata."""
        if gameweek is None:
            if self.bootstrap_data:
                events = self.bootstrap_data.get('events', [])
                gameweek = next((gw['id']
                                for gw in events if gw['is_current']), 1)
            else:
                gameweek = 1
        return os.path.join(self.cache_dir, f"league_{league_id}_gw_{gameweek}_info.json")

    def cache_exists(self, league_id: int, gameweek: int = None) -> bool:
        """Check if cache files exist for the given league and gameweek."""
        cache_file = self.get_cache_filename(league_id, gameweek)
        info_file = self.get_cache_info_filename(league_id, gameweek)
        return os.path.exists(cache_file) and os.path.exists(info_file)

    def save_manager_squads_cache(self, league_id: int, gameweek: int = None):
        """Save manager squads and league data to cache file."""
        try:
            cache_file = self.get_cache_filename(league_id, gameweek)
            info_file = self.get_cache_info_filename(league_id, gameweek)

            # Save the squads data along with league data
            cache_data = {
                'manager_squads': self.manager_squads,
                'league_data': self.league_data
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)

            # Save metadata
            cache_info = {
                'league_id': league_id,
                'gameweek': gameweek,
                'manager_count': len(self.manager_squads),
                'cached_at': datetime.now().isoformat(),
                'total_managers_in_league': len(self.league_data['standings']['results']) if self.league_data else 0
            }

            with open(info_file, 'w') as f:
                json.dump(cache_info, f, indent=2)

            print(
                f"💾 Cached {len(self.manager_squads)} manager squads and league data to {cache_file}")
            return True

        except Exception as e:
            print(f"❌ Error saving cache: {e}")
            return False

    def load_manager_squads_cache(self, league_id: int, gameweek: int = None, skip_prompt: bool = False) -> bool:
        """Load manager squads and league data from cache file."""
        try:
            cache_file = self.get_cache_filename(league_id, gameweek)
            info_file = self.get_cache_info_filename(league_id, gameweek)

            if not os.path.exists(cache_file) or not os.path.exists(info_file):
                return False

            # Load metadata
            with open(info_file, 'r') as f:
                cache_info = json.load(f)

            # Check if cache is recent (within 1 hour for same gameweek)
            cached_time = datetime.fromisoformat(cache_info['cached_at'])
            if datetime.now() - cached_time > timedelta(hours=1):
                print(f"⚠️  Cache is older than 1 hour, might be stale")
                if not skip_prompt:
                    use_cache = input(
                        "Use cached data anyway? (y/n, default: y): ").lower()
                    if use_cache == 'n':
                        return False
                else:
                    # In web app context, use cache anyway since user expects speed
                    print("📱 Web app context: using cache anyway for performance")

            # Load the cached data
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)

            # Handle both old format (just manager squads) and new format (dict with both)
            if isinstance(cached_data, dict) and 'manager_squads' in cached_data:
                # New format with both manager squads and league data
                self.manager_squads = cached_data['manager_squads']
                self.league_data = cached_data.get('league_data')
                print(f"📂 Loaded {len(self.manager_squads)} cached manager squads and league data (NEW FORMAT)")
            else:
                # Old format - just manager squads
                self.manager_squads = cached_data
                self.league_data = None
                print(f"📂 Loaded {len(self.manager_squads)} cached manager squads (legacy format)")

            print(f"🕒 Cached at: {cache_info['cached_at']}")
            print(
                f"📊 Coverage: {len(self.manager_squads)}/{cache_info['total_managers_in_league']} managers")

            return True

        except Exception as e:
            print(f"❌ Error loading cache: {e}")
            return False

    def list_available_caches(self):
        """List all available cache files."""
        if not os.path.exists(self.cache_dir):
            print("📂 No cache directory found")
            return []

        cache_files = []
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('_info.json'):
                try:
                    info_file = os.path.join(self.cache_dir, filename)
                    with open(info_file, 'r') as f:
                        cache_info = json.load(f)
                    cache_files.append(cache_info)
                except Exception:
                    continue

        if cache_files:
            print(f"\n📂 Available cached leagues:")
            print("-" * 60)
            for cache in sorted(cache_files, key=lambda x: x['cached_at'], reverse=True):
                cached_time = datetime.fromisoformat(cache['cached_at'])
                time_ago = datetime.now() - cached_time
                print(
                    f"League {cache['league_id']} (GW {cache['gameweek']}) - {cache['manager_count']} managers")
                print(
                    f"   Cached: {time_ago.seconds//3600}h {(time_ago.seconds//60) % 60}m ago")
        else:
            print("📂 No cached leagues found")

        return cache_files

    def get_bootstrap_data(self):
        """Fetch FPL bootstrap data with players, teams, etc."""
        try:
            url = "https://fantasy.premierleague.com/api/bootstrap-static/"
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(
                    f"❌ Error fetching bootstrap data: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Exception fetching bootstrap data: {e}")
            return None

    def get_league_data(self, league_id: int):
        """Fetch league standings data with pagination support for large leagues."""
        try:
            all_managers = []
            page = 1
            has_next = True

            print(f"🔄 Fetching league {league_id} data (with pagination)...")

            while has_next:
                url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?page_standings={page}"
                response = session.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    standings = data.get('standings', {})
                    results = standings.get('results', [])

                    if results:
                        all_managers.extend(results)
                        print(
                            f"📄 Page {page}: {len(results)} managers (Total: {len(all_managers)})")

                        # Check if there's a next page
                        has_next = standings.get('has_next', False)
                        page += 1

                        # Brief pause between pages to be respectful to the API
                        time.sleep(0.5)
                    else:
                        has_next = False
                else:
                    print(
                        f"❌ Error fetching league data page {page}: {response.status_code}")
                    if page == 1:  # If first page fails, return None
                        return None
                    else:  # If later page fails, return what we have
                        break

            # Return data in the same format as single page
            return {
                'standings': {
                    'results': all_managers
                }
            }

        except Exception as e:
            print(f"❌ Exception fetching league data: {e}")
            return None

    def get_manager_squad(self, manager_id: int, gameweek: int = None):
        """Fetch a manager's squad for a specific gameweek."""
        try:
            if gameweek is None:
                # Get current gameweek from bootstrap data
                if self.bootstrap_data:
                    events = self.bootstrap_data.get('events', [])
                    current_gw = next(
                        (gw['id'] for gw in events if gw['is_current']), 1)
                else:
                    current_gw = 1
            else:
                current_gw = gameweek

            url = f"https://fantasy.premierleague.com/api/entry/{manager_id}/event/{current_gw}/picks/"
            response = session.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                print(
                    f"❌ Error fetching squad for manager {manager_id}: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Exception fetching squad for manager {manager_id}: {e}")
            return None

    def initialize_data(self):
        """Initialize bootstrap data and player information."""
        print("🔄 Fetching FPL bootstrap data...")
        try:
            self.bootstrap_data = self.get_bootstrap_data()
            if not self.bootstrap_data:
                raise Exception("Failed to fetch bootstrap data")

            # Create players DataFrame
            players = self.bootstrap_data['elements']
            self.players_df = pd.DataFrame(players)
            self.players_df['full_name'] = self.players_df['first_name'] + \
                ' ' + self.players_df['second_name']

            print(f"✅ Loaded {len(self.players_df)} players")
            return True

        except Exception as e:
            print(f"❌ Error initializing data: {e}")
            return False

    def search_players(self, search_term: str, limit: int = 10) -> pd.DataFrame:
        """Search for players by name."""
        if self.players_df is None:
            print("❌ Player data not initialized")
            return pd.DataFrame()

        mask = self.players_df['full_name'].str.contains(
            search_term, case=False, na=False)
        results = self.players_df[mask][[
            'full_name', 'web_name', 'team', 'element_type']].head(limit)
        return results

    def get_league_info(self, league_id: int) -> bool:
        """Fetch league information and manager list."""
        print(f"🔄 Fetching league {league_id} information...")
        try:
            self.league_data = self.get_league_data(league_id)
            if not self.league_data:
                raise Exception(f"Failed to fetch league {league_id}")

            managers_count = len(self.league_data['standings']['results'])
            print(f"✅ League loaded: {managers_count} managers")
            self.current_league_id = league_id
            return True

        except Exception as e:
            print(f"❌ Error fetching league: {e}")
            return False

    def get_manager_squad_safe(self, manager_id: int, max_retries: int = 3) -> Optional[Dict]:
        """Safely fetch a manager's squad with retries."""
        for attempt in range(max_retries):
            try:
                squad = self.get_manager_squad(manager_id)
                if squad:
                    return squad
                time.sleep(0.5)  # Brief pause between retries
            except Exception as e:
                if attempt == max_retries - 1:
                    print(
                        f"❌ Failed to fetch manager {manager_id} after {max_retries} attempts")
                time.sleep(1)  # Longer pause on error
        return None

    def fetch_manager_squads_batch(self, manager_ids: List[int], batch_size: int = 200,
                                   max_workers: int = 5, speed_mode: str = 'conservative') -> Dict[int, Dict]:
        """Fetch manager squads in batches with different speed settings."""
        print(
            f"🔄 Fetching squads for {len(manager_ids)} managers in {speed_mode} mode...")

        # Speed mode configurations
        speed_configs = {
            'conservative': {'batch_size': 200, 'max_workers': 3, 'delay': 1.0, 'retry_delay': 1.0},
            'moderate': {'batch_size': 500, 'max_workers': 8, 'delay': 0.5, 'retry_delay': 0.5},
            'aggressive': {'batch_size': 1000, 'max_workers': 15, 'delay': 0.1, 'retry_delay': 0.2},
            'maximum': {'batch_size': 2000, 'max_workers': 25, 'delay': 0.0, 'retry_delay': 0.1}
        }

        if speed_mode in speed_configs:
            config = speed_configs[speed_mode]
            batch_size = config['batch_size']
            max_workers = config['max_workers']
            batch_delay = config['delay']
            retry_delay = config['retry_delay']
        else:
            # Use provided parameters
            batch_delay = 1.0
            retry_delay = 1.0

        print(
            f"⚙️  Settings: {batch_size} managers/batch, {max_workers} workers, {batch_delay}s delay")

        all_squads = {}
        total_batches = (len(manager_ids) + batch_size - 1) // batch_size
        start_time = time.time()

        for batch_num, i in enumerate(range(0, len(manager_ids), batch_size)):
            batch_ids = manager_ids[i:i + batch_size]
            batch_start = time.time()

            print(
                f"📦 Batch {batch_num + 1}/{total_batches} ({len(batch_ids)} managers)")

            # Process batch with threading
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_id = {
                    executor.submit(self.get_manager_squad_safe, manager_id, retry_delay): manager_id
                    for manager_id in batch_ids
                }

                for future in as_completed(future_to_id):
                    manager_id = future_to_id[future]
                    try:
                        squad = future.result()
                        if squad:
                            all_squads[manager_id] = squad
                    except Exception as e:
                        print(f"❌ Error processing manager {manager_id}: {e}")

            # Performance metrics
            batch_time = time.time() - batch_start
            total_time = time.time() - start_time
            success_rate = len(all_squads) / ((batch_num + 1) * batch_size) * \
                100 if batch_num == 0 else len(
                    all_squads) / len(manager_ids[:i + len(batch_ids)]) * 100
            avg_time_per_manager = total_time / \
                len(all_squads) if all_squads else 0

            print(
                f"✅ Batch {batch_num + 1} complete in {batch_time:.1f}s | Total: {len(all_squads)} | Success: {success_rate:.1f}%")
            print(
                f"⏱️  Avg: {avg_time_per_manager:.2f}s/manager | ETA: {(len(manager_ids) - len(all_squads)) * avg_time_per_manager / 60:.1f} min")

            # Memory cleanup and pause between batches
            gc.collect()
            if batch_num < total_batches - 1 and batch_delay > 0:
                time.sleep(batch_delay)

        total_time = time.time() - start_time
        self.manager_squads = all_squads
        print(
            f"🎉 Completed in {total_time:.1f}s | {len(all_squads)}/{len(manager_ids)} squads ({len(all_squads)/len(manager_ids)*100:.1f}%)")
        return all_squads

    def get_manager_squad_safe(self, manager_id: int, retry_delay: float = 1.0, max_retries: int = 3) -> Optional[Dict]:
        """Safely fetch a manager's squad with configurable retry delays."""
        for attempt in range(max_retries):
            try:
                squad = self.get_manager_squad(manager_id)
                if squad:
                    return squad
                time.sleep(retry_delay * 0.5)  # Brief pause between retries
            except Exception as e:
                if attempt == max_retries - 1:
                    print(
                        f"❌ Failed to fetch manager {manager_id} after {max_retries} attempts")
                time.sleep(retry_delay)  # Configurable pause on error
        return None

    def find_player_combinations(self, player_names: List[str]) -> Tuple[List[int], Dict[str, any]]:
        """Find managers who have all specified players."""
        if not self.manager_squads:
            print("❌ No manager squads loaded")
            return [], {}

        # Find player IDs
        player_ids = []
        for name in player_names:
            matches = self.search_players(name, limit=1)
            if matches.empty:
                print(f"❌ Player '{name}' not found")
                return [], {}

            # Get the player ID (assuming exact match from search)
            player_id = self.players_df[
                self.players_df['full_name'].str.contains(
                    name, case=False, na=False)
            ].iloc[0]['id']
            player_ids.append(player_id)
            print(f"✅ Found {name} (ID: {player_id})")

        print(
            f"🔍 Searching for managers with all {len(player_ids)} players...")

        matching_managers = []
        for manager_id, squad_data in self.manager_squads.items():
            try:
                squad_player_ids = [pick['element']
                                    for pick in squad_data['picks']]
                if all(pid in squad_player_ids for pid in player_ids):
                    matching_managers.append(manager_id)
            except (KeyError, TypeError):
                continue

        # Prepare results
        results = {
            'player_names': player_names,
            'player_ids': player_ids,
            'matching_managers': matching_managers,
            'total_managers_checked': len(self.manager_squads),
            'combination_count': len(matching_managers)
        }

        return matching_managers, results

    def print_results(self, results: Dict[str, any]):
        """Print formatted results."""
        print("\n" + "="*60)
        print("🎯 COMBINATION ANALYSIS RESULTS")
        print("="*60)

        print(f"👥 Players searched: {', '.join(results['player_names'])}")
        print(
            f"📊 Total managers analyzed: {results['total_managers_checked']:,}")
        print(
            f"✅ Managers with this combination: {results['combination_count']:,}")

        if results['combination_count'] > 0:
            percentage = (results['combination_count'] /
                          results['total_managers_checked']) * 100
            print(f"📈 Percentage: {percentage:.2f}%")

            print(f"\n📋 Manager IDs with this combination:")
            manager_ids = results['matching_managers']

            # Print in rows of 10 for readability
            for i in range(0, len(manager_ids), 10):
                row = manager_ids[i:i+10]
                print("   " + ", ".join(map(str, row)))

        print("="*60)

    def interactive_analysis(self):
        """Run interactive analysis session."""
        print("🚀 FPL Player Combination Analysis Tool")
        print("="*50)

        # Initialize data
        if not self.initialize_data():
            return

        # Get league ID and check cache first
        while True:
            try:
                league_id = int(input("\n📋 Enter FPL League ID: "))

                # Get current gameweek for cache check
                current_gw = None
                if self.bootstrap_data:
                    events = self.bootstrap_data.get('events', [])
                    current_gw = next((gw['id']
                                      for gw in events if gw['is_current']), 1)

                print(
                    f"\n💾 Checking for cached data (League {league_id}, GW {current_gw})...")

                # Show available caches
                self.list_available_caches()

                # Try to load cache for this league FIRST
                cache_loaded = self.load_manager_squads_cache(
                    league_id, current_gw)

                if cache_loaded:
                    print(f"✅ Found cached data for league {league_id}!")
                    use_cache = input(
                        "Use cached data? (y/n, default: y): ").lower()
                    if use_cache != 'n':
                        print("🎉 Using cached data - no API fetching needed!")
                        self.current_league_id = league_id
                        # We still need basic league info, but can get it from cache metadata
                        try:
                            # Try to load league info from cache metadata
                            cache_info_file = self.get_cache_info_filename(
                                league_id, current_gw)
                            if os.path.exists(cache_info_file):
                                with open(cache_info_file, 'r') as f:
                                    cache_info = json.load(f)
                                    # Reconstruct league_data from cache info
                                    manager_count = cache_info.get(
                                        'manager_count', len(self.manager_squads))
                                    print(
                                        f"✅ League loaded from cache: {manager_count} managers")
                                    # Create minimal league_data structure
                                    self.league_data = {
                                        'standings': {
                                            'results': [{'entry': manager_id} for manager_id in self.manager_squads.keys()]
                                        }
                                    }
                                    break
                            else:
                                # Fallback: get league info normally but keep the cached squads
                                if self.get_league_info(league_id):
                                    break
                        except Exception as e:
                            print(f"⚠️  Cache metadata issue: {e}")
                            if self.get_league_info(league_id):
                                break
                    else:
                        # User chose not to use cache, clear it and fetch fresh
                        self.manager_squads = {}
                        if self.get_league_info(league_id):
                            break
                else:
                    # No cache found, get league info normally
                    if self.get_league_info(league_id):
                        break

            except ValueError:
                print("❌ Please enter a valid league ID (numbers only)")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                return

        # Get manager IDs from league data
        manager_ids = [entry['entry']
                       for entry in self.league_data['standings']['results']]

        # Determine if we need to fetch squads
        skip_fetch = False
        if self.manager_squads:
            # We have squads (either from cache or user chose to fetch fresh)
            cached_count = len(self.manager_squads)
            total_count = len(manager_ids)

            if cached_count >= total_count * 0.95:  # 95% coverage is good enough
                print(
                    f"✅ Ready with {cached_count}/{total_count} manager squads ({cached_count/total_count*100:.1f}%)")
                skip_fetch = True
            else:
                # Partial cache - offer to fetch missing
                print(
                    f"⚠️  Only have {cached_count}/{total_count} managers ({cached_count/total_count*100:.1f}%)")
                extend_cache = input(
                    "Fetch missing managers? (y/n, default: y): ").lower()
                if extend_cache != 'n':
                    # Find missing managers
                    cached_manager_ids = set(self.manager_squads.keys())
                    missing_manager_ids = [
                        mid for mid in manager_ids if mid not in cached_manager_ids]
                    manager_ids = missing_manager_ids  # Only fetch missing ones
                    print(
                        f"📥 Will fetch {len(missing_manager_ids)} missing managers")
                    skip_fetch = False
                else:
                    skip_fetch = True
        else:
            # No squads available, need to fetch
            skip_fetch = False

        # Fetch manager squads if needed
        if not skip_fetch:
            # Speed mode selection
            print(
                f"\n⚡ Choose processing speed for {len(manager_ids):,} managers:")
            print("1. Conservative (200/batch, 3 workers, 1s delay) - Safest, slower")
            print("2. Moderate (500/batch, 8 workers, 0.5s delay) - Balanced")
            print(
                "3. Aggressive (1000/batch, 15 workers, 0.1s delay) - Fast, may hit limits")
            print("4. Maximum (2000/batch, 25 workers, no delay) - Fastest, risky")
            print("5. Custom settings")

            speed_modes = {
                '1': 'conservative',
                '2': 'moderate',
                '3': 'aggressive',
                '4': 'maximum'
            }

            while True:
                choice = input(
                    "\nSelect speed mode (1-5, default: 1): ").strip() or '1'
                if choice in speed_modes:
                    speed_mode = speed_modes[choice]
                    break
                elif choice == '5':
                    try:
                        batch_size = int(
                            input("Batch size (default 200): ") or "200")
                        max_workers = int(
                            input("Max workers (default 5): ") or "5")
                        speed_mode = 'custom'
                        break
                    except ValueError:
                        print("❌ Invalid input. Using conservative settings.")
                        speed_mode = 'conservative'
                        break
                else:
                    print("❌ Invalid choice. Please select 1-5.")

            # Fetch squads with selected speed mode
            if speed_mode == 'custom':
                new_squads = self.fetch_manager_squads_batch(
                    manager_ids, batch_size, max_workers, 'conservative')
            else:
                new_squads = self.fetch_manager_squads_batch(
                    manager_ids, speed_mode=speed_mode)

            if not new_squads:
                print("❌ Failed to fetch manager squads")
                return

            # If we were extending cache, merge new data
            if cache_loaded and 'missing_manager_ids' in locals():
                self.manager_squads.update(new_squads)
                print(
                    f"🔄 Extended cache: {len(self.manager_squads)} total managers")

            # Save to cache
            print(f"\n💾 Saving data to cache...")
            self.save_manager_squads_cache(league_id, current_gw)

        # Interactive combination search
        print("\n🔍 Now you can search for player combinations!")
        print("💡 Tip: You can run multiple searches without re-fetching the league data")

        while True:
            try:
                print("\n" + "-"*40)

                # Get player names
                print("Enter player names (one per line, empty line to finish):")
                player_names = []
                while True:
                    name = input(f"Player {len(player_names) + 1}: ").strip()
                    if not name:
                        break
                    player_names.append(name)

                if not player_names:
                    print("❌ No players entered")
                    continue

                # Search for combination
                matching_managers, results = self.find_player_combinations(
                    player_names)
                self.print_results(results)

                # Ask for another search
                another = input(
                    "\n🔄 Search for another combination? (y/n): ").lower()
                if another != 'y':
                    break

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break


def main():
    """Main entry point."""
    analyzer = FPLCombinationAnalyzer()
    analyzer.interactive_analysis()


if __name__ == "__main__":
    main()
