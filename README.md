# FPL Player Combination Analysis

🏆 **Analyze player combinations across Fantasy Premier League leagues with lightning speed**

A powerful web application that helps you discover which managers in your FPL league have specific player combinations. Perfect for analyzing ownership patterns, finding unique strategies, and understanding league dynamics.

## ✨ Key Features

- 🚀 **Lightning Fast**: Intelligent caching system eliminates redundant API calls
- 🔍 **Smart Search**: Fuzzy player name matching with autocomplete
- 📊 **Deep Analytics**: Comprehensive manager statistics and ownership data
- 💻 **Modern UI**: Responsive design that works on all devices
- 🐳 **Production Ready**: Docker containerized with CDN support
- ⚡ **Instant Results**: Real-time analysis without page reloads

## 🎯 Use Cases

- **League Analysis**: See which players are popular in your mini-league
- **Strategy Research**: Find managers with similar team structures
- **Ownership Trends**: Discover unique player combinations
- **Performance Tracking**: Compare strategies with league standings

## 🚀 Quick Demo

1. **Enter League ID** → Load your FPL league data
2. **Search Players** → Select players using smart autocomplete
3. **Analyze** → Instantly see which managers have those players
4. **Explore Results** → View detailed manager information and statistics

## 🛠️ Installation & Usage

### Local Development

```bash
git clone https://github.com/KasraH/fpl-combos.git
cd fpl-combos/webapp
pip install -r requirements.txt
python3 app.py
```

Visit http://localhost:5001

### Production Deployment

- 🐳 **Docker Ready**: Complete containerization with docker-compose
- 🌐 **CDN Optimized**: Namespace CDN integration for global performance
- 🔒 **SSL Included**: Automatic HTTPS with security headers
- 📋 **Full Documentation**: Step-by-step deployment guides

## 🏗️ Architecture

- **Backend**: Flask with intelligent caching system
- **Frontend**: Modern HTML5/CSS3/JavaScript
- **Data Source**: Official FPL API
- **Deployment**: Docker + Nginx + CDN
- **Caching**: Advanced disk-based caching with auto-upgrades

## 📊 Performance

- ⚡ **Cache Hits**: Zero API calls for previously loaded leagues
- 🔄 **Batch Processing**: Concurrent data fetching for large leagues
- 💾 **Smart Storage**: Efficient cache format with backward compatibility
- 🌍 **CDN Delivery**: Global content distribution for optimal speed

## 📁 Project Structure

```
├── player_combination_analysis.py   # Core analysis engine
├── webapp/                          # Web application
│   ├── app.py                      # Flask server
│   ├── templates/                  # UI templates
│   ├── Dockerfile & docker-compose # Container setup
│   └── deploy.sh                   # Deployment automation
└── fpl_cache/                      # Intelligent caching system
```

## 🔧 Advanced Features

- **Cache Management**: Built-in cache inspection and cleanup tools
- **Health Monitoring**: Application health checks for production
- **Error Handling**: Graceful error recovery and user feedback
- **Security**: Production-grade security headers and SSL support

## 📈 Scalability

Tested and optimized for:

- ✅ Leagues up to 32,000+ managers
- ✅ Concurrent user access
- ✅ High-frequency analysis requests
- ✅ Mobile and desktop traffic

## 🤝 Contributing

This project is open source! Contributions are welcome:

- 🐛 Bug reports and feature requests via Issues
- 🔧 Pull requests for improvements
- 📚 Documentation enhancements
- 🧪 Testing and performance optimization

## 📄 License

Open source - feel free to use, modify, and distribute.

---

**Built with ❤️ for the FPL community**
