from flask import Flask, jsonify, request
from flask_cors import CORS
from nba_sentiment_analyzer import NBAArticleAnalyzer
import logging
from datetime import datetime, timedelta
from get_stats import getPlayerStats

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for /api/*

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Get current date and date 28 days ago using UTC
end_date = datetime.utcnow().strftime('%Y-%m-%d')
start_date = (datetime.utcnow() - timedelta(days=28)).strftime('%Y-%m-%d')

# Add debug logging
app.logger.debug(f"Start date: {start_date}")
app.logger.debug(f"End date: {end_date}")

# Use these dates in your NewsAPI request
params = {
    'q': 'NBA',
    'sources': 'espn,bleacher-report,...',  # your existing sources
    'from': start_date,
    'to': end_date,
    'language': 'en',
    'sortBy': 'publishedAt',
    'pageSize': 100
}

@app.route('/api/sentiment', methods=['GET'])
def get_sentiment_data():
    app.logger.debug(f"Received request: {request.method} {request.url}")
    
    analyzer = NBAArticleAnalyzer()
    results_df = analyzer.analyze_articles()
    
    app.logger.debug(f"Returning {len(results_df)} records")
    return jsonify(results_df.to_dict(orient='records'))

@app.route('/api/player-stats/<player_name>', methods=['GET'])
def get_player_stats(player_name):
    try:
        app.logger.debug(f"Received request for player stats: {player_name}")
        
        stats = getPlayerStats()
        stats._get_player_game_stats(player_name)
        
        # Check if player was found
        if player_name not in stats.player_stats_dict:
            return jsonify({
                "error": "Player not found",
                "message": f"Could not find stats for player: {player_name}"
            }), 404
        
        return jsonify(stats.player_stats_dict[player_name])
        
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "An error occurred while processing your request"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 