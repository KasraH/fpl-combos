# FPL Player Combination Web App

A user-friendly web interface for analyzing player combinations across FPL league managers. This web app makes the powerful command-line FPL analysis tool accessible to non-technical users through a modern, intuitive interface.

## ✨ Features

- **🌐 Web-based interface** - No command line knowledge required
- **🔍 Player search** - Easy player selection with autocomplete
- **📊 Visual results** - Clean, organized display of analysis results
- **💾 Smart caching** - Reuses existing cache data for fast subsequent searches
- **📱 Mobile friendly** - Works on desktop, tablet, and mobile devices
- **⚡ Real-time search** - Instant player suggestions as you type

## 🚀 Quick Start

### For Non-Technical Users

1. **Download the files** to your computer
2. **Open Terminal** (Mac/Linux) or **Command Prompt** (Windows)
3. **Navigate** to the webapp folder:
   ```bash
   cd path/to/fpl_player_combination/webapp
   ```
4. **Run the setup script**:
   - **Mac/Linux**: `bash setup.sh`
   - **Windows**: Double-click `setup.bat`
5. **Start the web app**:
   ```bash
   python3 app.py
   ```
6. **Open your browser** and go to: http://localhost:5001

### Manual Installation

If the setup script doesn't work, install manually:

```bash
# Install Python packages
pip install flask requests pandas

# Start the web app
python3 app.py
```

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

## 🔧 Technical Details

### System Requirements

- Python 3.7 or higher
- Web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for FPL API)

### Dependencies

- Flask 2.3.3 - Web framework
- Requests 2.31.0 - HTTP library
- Pandas 2.1.1 - Data analysis

### Port and Access

- Default port: 5000
- Local access: http://localhost:5001
- Network access: http://YOUR_IP:5001 (accessible to other devices on your network)

## 📁 File Structure

```
webapp/
├── app.py              # Main Flask application
├── templates/
│   └── index.html      # Web interface
├── requirements.txt    # Python dependencies
├── setup.sh           # Mac/Linux setup script
├── setup.bat          # Windows setup script
└── README.md          # This file
```

## 🔄 Cache Integration

The web app automatically uses the existing cache system from the command-line tool:

- Cache files are stored in `../fpl_cache/`
- Previously loaded leagues are instantly available
- Cache information is displayed at the bottom of the page

## 🚨 Troubleshooting

### "Flask not found" Error

```bash
pip install flask
# or
pip3 install flask
```

### "Port already in use" Error

- Close other applications using port 5001
- Or change the port in `app.py`: `app.run(port=5002)`

### League Loading Fails

- Check your internet connection
- Verify the League ID is correct
- Try a smaller league first to test

### Players Not Found

- Use common player names (e.g., "Salah" not "Mohamed Salah")
- Try partial names (e.g., "Haal" for Haaland)
- Check spelling

## 🔒 Security Note

This web app is designed for local use. If sharing with others:

- Only share with trusted users on your local network
- The app runs on your computer and accesses FPL data using your connection
- No personal FPL data is collected or stored

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Try restarting the web app
4. Check the terminal/command prompt for error messages

## 🔗 Related Files

This web app uses the core analysis engine from:

- `../player_combination_analysis.py` - Main analysis logic
- `../cache_manager.py` - Cache management
- `../fpl_cache/` - Cached league data
