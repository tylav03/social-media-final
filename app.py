from flask import Flask, jsonify, request
from flask_cors import CORS
from nba_sentiment_analyzer import NBAArticleAnalyzer
import logging

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for /api/*

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/api/sentiment', methods=['GET'])
def get_sentiment_data():
    app.logger.debug(f"Received request: {request.method} {request.url}")
    
    analyzer = NBAArticleAnalyzer()
    results_df = analyzer.analyze_articles()
    
    app.logger.debug(f"Returning {len(results_df)} records")
    return jsonify(results_df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True, port=5001) 