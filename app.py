from flask import Flask, jsonify, request
from flask_cors import CORS
from nba_sentiment_analyzer import NBAArticleAnalyzer
import logging
from datetime import datetime, timedelta
from get_stats import getPlayerStats

# Flask app
app = Flask(__name__)
# Turn on CORS for all routes under /api/* to allow cross origin requests
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Turn on basic logging for debug
logging.basicConfig(level=logging.DEBUG)

# Route for getting sentiment analysis data
@app.route('/api/sentiment', methods=['GET'])
def get_sentiment_data():

    app.logger.debug(f"Received request: {request.method} {request.url}")
    
    # Create analyzer and process articles
    analyzer = NBAArticleAnalyzer()
    results_df = analyzer.analyze_articles()
    
    app.logger.debug(f"Returning {len(results_df)} records")

    # Convert DataFrame to dictionary and return as JSON
    return jsonify(results_df.to_dict(orient='records'))

# Route for getting specific player statistics
@app.route('/api/player-stats/<player_name>', methods=['GET'])
def get_player_stats(player_name):
    try:

        app.logger.debug(f"Received request for player stats: {player_name}")
        
        # Create stats object and get player game statistics
        stats = getPlayerStats()
        stats._get_player_game_stats(player_name)
        
        # Check if the requested player exists in the stats
        if player_name not in stats.player_stats_dict:
            # Return 404 error if player not found
            return jsonify({
                "error": "Player not found",
                "message": f"Could not find stats for player: {player_name}"
            }), 404
        
        # Return the player's statistics as JSON
        return jsonify(stats.player_stats_dict[player_name])
        
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "An error occurred while processing your request"
        }), 500

# Run the application if this file is executed directly
if __name__ == '__main__':
    # Start Flask server
    app.run(debug=True, port=5001) 