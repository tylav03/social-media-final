# NBA PlayerSentiment and Valuation Analysis Application

This application analyzes NBA player sentiment from news articles and compares it with their recent performance statistics. It then assigns a player with a valuation of OVERVALUED, UNDERVALUED, or NEUTRAL.

## Make sure you have these installed:

- Python 3.8 or higher
- Node.js and npm
- Git

To install:

1. Clone the repository:

```bash
git clone https://github.com/tylav03/social-media-final
cd social-media-final
```

2. Create and activate a Python virtual environment if you want to:
```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install our Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install React dependencies:
```bash
cd nba-sentiment-frontend
npm install
cd ..
```

## Running the Application

### Option 1: Using the start script (Only works on mac and linux we think)

1. Make the start script executable:
```bash
chmod +x start_app.sh
```

2. Run the start script:
```bash
./start_app.sh
```

### Option 2: Manual startup

1. Start the Flask backend (from the root directory):
```bash
python app.py
```

2. In a new terminal, start the React frontend:
```bash
cd nba-sentiment-frontend
npm start
```

## Accessing the Application

- The frontend will be running on: http://localhost:3000
- The backend API will be running on: http://localhost:5001

## Features

- Real-time sentiment analysis of NBA players from news articles
- Player performance statistics from the last 30 days
- Visual representation of sentiment scores
- Player valuation analysis (OVERVALUED/UNDERVALUED/NEUTRAL) based on sentiment and performance metrics

## Problems we ran into

1. If player stats aren't loading:
   - The NBA API has rate limits. The code has retry logic, but you might need to wait a few between requests

2. If the frontend fails to start:
   - Make sure all npm dependencies are installed
   - Check if port 3000 is available on your computer

3. If the backend fails to start:
   - Make sure port 5001 is available on your computer
   - Look and see if all Python libraries are installed correctly

## Stopping the Application

- If using the start script: Press Ctrl+C in the terminal running the script
- If running manually: Press Ctrl+C in both terminal windows


