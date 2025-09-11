# FPL Player Combination Analysis

A powerful web application for analyzing player combinations across Fantasy Premier League (FPL) leagues. Discover which managers in your league have specific player combinations and analyze ownership patterns.

## ✨ Features

- **🌐 Modern web interface** - Clean, responsive design that works on all devices
- **🔍 Smart player search** - Intelligent autocomplete with fuzzy matching
- **📊 Detailed analytics** - Comprehensive results with manager details and statistics
- **💾 Intelligent caching** - Lightning-fast performance with advanced caching system
- **📱 Mobile optimized** - Perfect experience on desktop, tablet, and mobile
- **⚡ Instant analysis** - Real-time search and immediate results
- **🚀 Production ready** - Docker containerized with CDN support

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/KasraH/fpl-combos.git
cd fpl-combos/webapp

# Install dependencies
pip install -r requirements.txt

# Start the application
python3 app.py
```

Visit http://localhost:5001 in your browser.

### Production Deployment

This application is designed for VPS deployment with Docker and CDN support:

```bash
# Deploy to VPS
./deploy.sh

# Or manually with Docker
docker-compose up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) and [CDN_SETUP.md](CDN_SETUP.md) for detailed deployment instructions.

## 📖 How to Use

### Step 1: Load League Data

1. Enter your FPL League ID in the first section
2. Click "Load League" button
3. Wait for the data to load (first time may take a few minutes for large leagues)

**Finding your League ID:**

- Go to your FPL league page
- Look at the URL: `fantasy.premierleague.com/leagues/123456/standings/c`
- The League ID is `123456`

### Step 2: Select Players

1. Type a player name in the search box (e.g., "Salah", "Haaland")
2. Click on players from the dropdown suggestions
3. Selected players will appear as tags below
4. Remove players by clicking the X on their tag

### Step 3: Analyze

1. Click "Find Managers with These Players"
2. View the results showing:
   - How many managers have this combination
   - Percentage of league with this combination
   - List of specific managers with their points and rank

## 💡 Tips

- **Cache Benefits**: After loading a league once, subsequent searches are much faster
- **Multiple Searches**: You can search different combinations without reloading league data
- **Player Names**: Use common player names (web names) like "Salah" instead of "Mohamed Salah"
- **Large Leagues**: The tool works with leagues of any size, but larger leagues take longer to load initially

## 🏗️ Architecture

### Technology Stack

- **Backend**: Flask (Python 3.11+)
- **Frontend**: Modern HTML5/CSS3/JavaScript
- **Caching**: Intelligent disk-based caching with automatic upgrades
- **Deployment**: Docker + Docker Compose
- **Reverse Proxy**: Nginx with CDN optimization
- **SSL/CDN**: Namespace CDN integration

### Performance Features

- **Smart Caching**: Eliminates redundant API calls for cached leagues
- **Batch Processing**: Efficient concurrent manager data fetching  
- **CDN Integration**: Global content delivery for optimal performance
- **Resource Optimization**: Memory-efficient data processing for large leagues

## 📁 Project Structure

```
├── player_combination_analysis.py   # Core analysis engine
├── webapp/
│   ├── app.py                      # Flask web application
│   ├── wsgi.py                     # Production WSGI entry point
│   ├── templates/
│   │   └── index.html              # Web interface
│   ├── docker-compose.yml          # Docker orchestration
│   ├── Dockerfile                  # Container configuration
│   ├── nginx-fpl.conf             # Nginx reverse proxy config
│   ├── deploy.sh                   # Automated deployment script
│   ├── requirements.txt            # Python dependencies
│   ├── DEPLOYMENT.md              # Deployment guide
│   └── CDN_SETUP.md               # CDN configuration guide
└── fpl_cache/                      # Cached league data
```

## 🔄 Intelligent Caching System

Advanced caching ensures optimal performance:

- **Automatic Cache Detection**: Instantly recognizes available cached leagues
- **Zero API Calls**: Cached leagues load without any external requests  
- **Cache Upgrades**: Seamlessly upgrades legacy cache formats
- **Memory Optimization**: Efficient in-memory caching for analysis operations
- **Cache Management**: Built-in cache information and cleanup tools

## 🚨 Common Issues

### Player Search Tips
- Use common names: "Salah" instead of "Mohamed Salah"  
- Try partial matches: "Haal" for Haaland
- Names are case-insensitive and fuzzy-matched

### Performance Notes  
- First-time league loading requires API calls (may take 1-2 minutes for large leagues)
- Subsequent loads from cache are instant
- Analysis operations are always fast regardless of league size

## 🔒 Security & Privacy

- **No Data Storage**: No personal FPL credentials required or stored
- **Public API Only**: Uses official FPL public API endpoints  
- **Local Caching**: All data cached locally, not shared externally
- **Production Security**: Includes security headers and proper SSL configuration

## 🌟 Key Benefits

- **⚡ Performance**: Intelligent caching eliminates repeated API calls
- **📊 Analytics**: Deep insights into league player ownership patterns  
- **🔍 Discovery**: Find unique player combinations and ownership trends
- **📱 Accessibility**: Works on any device with a modern web browser
- **🚀 Scalability**: Handles leagues of any size efficiently

## 📄 License

This project is open source. Feel free to use, modify, and distribute.
