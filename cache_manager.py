#!/usr/bin/env python3
"""
FPL Cache Management Tool

Manage cached league data for the FPL Player Combination Analysis Tool.
"""

import os
import json
import shutil
from datetime import datetime
from player_combination_analysis import FPLCombinationAnalyzer


def format_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"


def manage_cache():
    """Interactive cache management."""
    print("🗄️  FPL Cache Management Tool")
    print("="*50)

    analyzer = FPLCombinationAnalyzer()

    if not os.path.exists(analyzer.cache_dir):
        print("📂 No cache directory found")
        return

    while True:
        print("\n📋 Cache Management Options:")
        print("1. List all cached leagues")
        print("2. View cache details")
        print("3. Delete specific cache")
        print("4. Clear all cache")
        print("5. Cache statistics")
        print("6. Exit")

        choice = input("\nSelect option (1-6): ").strip()

        if choice == '1':
            list_caches(analyzer)
        elif choice == '2':
            view_cache_details(analyzer)
        elif choice == '3':
            delete_specific_cache(analyzer)
        elif choice == '4':
            clear_all_cache(analyzer)
        elif choice == '5':
            cache_statistics(analyzer)
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-6.")


def list_caches(analyzer):
    """List all available caches."""
    print("\n📂 Listing all cached leagues...")
    cache_files = analyzer.list_available_caches()

    if not cache_files:
        return

    print(f"\nTotal: {len(cache_files)} cached leagues")


def view_cache_details(analyzer):
    """View detailed information about a specific cache."""
    cache_files = []
    for filename in os.listdir(analyzer.cache_dir):
        if filename.endswith('_info.json'):
            try:
                info_file = os.path.join(analyzer.cache_dir, filename)
                with open(info_file, 'r') as f:
                    cache_info = json.load(f)
                cache_files.append(cache_info)
            except Exception:
                continue

    if not cache_files:
        print("📂 No cached leagues found")
        return

    print("\n📋 Select a cache to view details:")
    for i, cache in enumerate(cache_files, 1):
        print(
            f"{i}. League {cache['league_id']} (GW {cache['gameweek']}) - {cache['manager_count']} managers")

    try:
        choice = int(input(f"\nSelect cache (1-{len(cache_files)}): "))
        if 1 <= choice <= len(cache_files):
            cache = cache_files[choice - 1]

            # Get file sizes
            cache_file = analyzer.get_cache_filename(
                cache['league_id'], cache['gameweek'])
            info_file = analyzer.get_cache_info_filename(
                cache['league_id'], cache['gameweek'])

            cache_size = os.path.getsize(
                cache_file) if os.path.exists(cache_file) else 0
            info_size = os.path.getsize(
                info_file) if os.path.exists(info_file) else 0
            total_size = cache_size + info_size

            print(f"\n📄 Cache Details:")
            print(f"League ID: {cache['league_id']}")
            print(f"Gameweek: {cache['gameweek']}")
            print(f"Managers: {cache['manager_count']}")
            print(
                f"Total managers in league: {cache['total_managers_in_league']}")
            print(
                f"Coverage: {cache['manager_count']/cache['total_managers_in_league']*100:.1f}%")
            print(f"Cached at: {cache['cached_at']}")
            print(f"Data file size: {format_size(cache_size)}")
            print(f"Info file size: {format_size(info_size)}")
            print(f"Total size: {format_size(total_size)}")
        else:
            print("❌ Invalid selection")
    except ValueError:
        print("❌ Invalid input")


def delete_specific_cache(analyzer):
    """Delete a specific cache."""
    cache_files = []
    for filename in os.listdir(analyzer.cache_dir):
        if filename.endswith('_info.json'):
            try:
                info_file = os.path.join(analyzer.cache_dir, filename)
                with open(info_file, 'r') as f:
                    cache_info = json.load(f)
                cache_files.append(cache_info)
            except Exception:
                continue

    if not cache_files:
        print("📂 No cached leagues found")
        return

    print("\n🗑️  Select a cache to delete:")
    for i, cache in enumerate(cache_files, 1):
        cached_time = datetime.fromisoformat(cache['cached_at'])
        time_ago = datetime.now() - cached_time
        print(
            f"{i}. League {cache['league_id']} (GW {cache['gameweek']}) - {time_ago.days}d {time_ago.seconds//3600}h ago")

    try:
        choice = int(
            input(f"\nSelect cache to delete (1-{len(cache_files)}): "))
        if 1 <= choice <= len(cache_files):
            cache = cache_files[choice - 1]

            confirm = input(
                f"Delete League {cache['league_id']} GW {cache['gameweek']} cache? (y/n): ").lower()
            if confirm == 'y':
                cache_file = analyzer.get_cache_filename(
                    cache['league_id'], cache['gameweek'])
                info_file = analyzer.get_cache_info_filename(
                    cache['league_id'], cache['gameweek'])

                try:
                    if os.path.exists(cache_file):
                        os.remove(cache_file)
                    if os.path.exists(info_file):
                        os.remove(info_file)
                    print(
                        f"✅ Deleted cache for League {cache['league_id']} GW {cache['gameweek']}")
                except Exception as e:
                    print(f"❌ Error deleting cache: {e}")
            else:
                print("❌ Deletion cancelled")
        else:
            print("❌ Invalid selection")
    except ValueError:
        print("❌ Invalid input")


def clear_all_cache(analyzer):
    """Clear all cached data."""
    if not os.path.exists(analyzer.cache_dir):
        print("📂 No cache directory found")
        return

    file_count = len([f for f in os.listdir(analyzer.cache_dir)
                     if f.endswith('.pkl') or f.endswith('.json')])

    if file_count == 0:
        print("📂 No cache files found")
        return

    confirm = input(
        f"⚠️  Delete ALL {file_count//2} cached leagues? This cannot be undone! (y/n): ").lower()
    if confirm == 'y':
        try:
            shutil.rmtree(analyzer.cache_dir)
            os.makedirs(analyzer.cache_dir)
            print("✅ All cache data cleared")
        except Exception as e:
            print(f"❌ Error clearing cache: {e}")
    else:
        print("❌ Clear cancelled")


def cache_statistics(analyzer):
    """Show cache statistics."""
    if not os.path.exists(analyzer.cache_dir):
        print("📂 No cache directory found")
        return

    cache_files = []
    total_size = 0
    total_managers = 0

    for filename in os.listdir(analyzer.cache_dir):
        filepath = os.path.join(analyzer.cache_dir, filename)
        total_size += os.path.getsize(filepath)

        if filename.endswith('_info.json'):
            try:
                with open(filepath, 'r') as f:
                    cache_info = json.load(f)
                cache_files.append(cache_info)
                total_managers += cache_info['manager_count']
            except Exception:
                continue

    print(f"\n📊 Cache Statistics:")
    print(f"Number of cached leagues: {len(cache_files)}")
    print(f"Total managers cached: {total_managers:,}")
    print(f"Total cache size: {format_size(total_size)}")
    print(
        f"Average managers per league: {total_managers//len(cache_files) if cache_files else 0:,}")

    if cache_files:
        oldest = min(cache_files, key=lambda x: x['cached_at'])
        newest = max(cache_files, key=lambda x: x['cached_at'])

        oldest_time = datetime.fromisoformat(oldest['cached_at'])
        newest_time = datetime.fromisoformat(newest['cached_at'])

        print(f"Oldest cache: {(datetime.now() - oldest_time).days} days ago")
        print(
            f"Newest cache: {(datetime.now() - newest_time).seconds//3600} hours ago")


if __name__ == "__main__":
    manage_cache()
