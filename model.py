import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
from nba_sentiment_analyzer import NBAArticleAnalyzer

class PlayerPerformancePredictor:
    def __init__(self):
        self.sentiment_analyzer = NBAArticleAnalyzer()
        self.scaler = StandardScaler()
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def _get_player_stats(self, player_name, days_back=60):
        """Fetch recent game statistics for a player"""
        player_info = [p for p in players.get_players() if p['full_name'] == player_name][0]
        game_log = playergamelog.PlayerGameLog(player_id=player_info['id'])
        df = game_log.get_data_frames()[0]
        
        # Calculate rolling averages for key statistics
        df['PTS_AVG_5'] = df['PTS'].rolling(window=5).mean()
        df['AST_AVG_5'] = df['AST'].rolling(window=5).mean()
        df['REB_AVG_5'] = df['REB'].rolling(window=5).mean()
        
        return df

    def _prepare_features(self, stats_df, sentiment_df):
        """Combine player statistics with sentiment analysis"""
        features = []
        labels = []
        
        for i in range(len(stats_df) - 5):  # Need 5 games for rolling averages
            current_stats = {
                'pts_avg': stats_df['PTS_AVG_5'].iloc[i],
                'ast_avg': stats_df['AST_AVG_5'].iloc[i],
                'reb_avg': stats_df['REB_AVG_5'].iloc[i],
                'sentiment': sentiment_df['sentiment'].mean()  # Average sentiment
            }
            
            # Compare next game performance to current averages
            next_game = stats_df.iloc[i]
            performance_label = self._get_performance_label(
                next_game['PTS'], 
                current_stats['pts_avg']
            )
            
            features.append(current_stats)
            labels.append(performance_label)
            
        return pd.DataFrame(features), np.array(labels)

    def _get_performance_label(self, actual_points, average_points):
        """Classify performance as better (2), same (1), or worse (0)"""
        diff_percentage = ((actual_points - average_points) / average_points) * 100
        
        if diff_percentage > 15:  # More than 15% better
            return 2
        elif diff_percentage < -15:  # More than 15% worse
            return 0
        else:
            return 1

    def train(self, player_name):
        """Train the model for a specific player"""
        # Get sentiment analysis
        sentiment_df = self.sentiment_analyzer.analyze_articles()
        player_sentiment = sentiment_df[sentiment_df['player'] == player_name]
        
        # Get player statistics
        stats_df = self._get_player_stats(player_name)
        
        # Prepare features and labels
        X, y = self._prepare_features(stats_df, player_sentiment)
        
        if len(X) == 0:
            raise ValueError("Not enough data to train the model")
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Return test accuracy
        return self.model.score(X_test_scaled, y_test)

    def predict_performance(self, player_name):
        """Predict if a player will perform better, same, or worse"""
        # Get current sentiment
        sentiment_df = self.sentiment_analyzer.analyze_articles()
        player_sentiment = sentiment_df[sentiment_df['player'] == player_name]
        
        # Get current stats
        stats_df = self._get_player_stats(player_name)
        
        # Prepare current features
        current_features = pd.DataFrame([{
            'pts_avg': stats_df['PTS_AVG_5'].iloc[0],
            'ast_avg': stats_df['AST_AVG_5'].iloc[0],
            'reb_avg': stats_df['REB_AVG_5'].iloc[0],
            'sentiment': player_sentiment['sentiment'].mean()
        }])
        
        # Scale and predict
        features_scaled = self.scaler.transform(current_features)
        prediction = self.model.predict(features_scaled)[0]
        
        # Return prediction and confidence
        prediction_proba = self.model.predict_proba(features_scaled)[0]
        confidence = max(prediction_proba)
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'current_sentiment': player_sentiment['sentiment'].mean()
        }

    def predict_multiple_players(self):
        """Predict performance for all players in sentiment analysis"""
        # Get current sentiment for all players
        sentiment_df = self.sentiment_analyzer.analyze_articles()
        unique_players = sentiment_df['player'].unique()
        
        predictions = {}
        prediction_map = {0: "worse", 1: "same", 2: "better"}
        
        for player_name in unique_players:
            try:
                # Train model for this player
                accuracy = self.train(player_name)
                
                # Get prediction
                result = self.predict_performance(player_name)
                
                predictions[player_name] = {
                    'expected_performance': prediction_map[result['prediction']],
                    'confidence': result['confidence'],
                    'sentiment': result['current_sentiment'],
                    'model_accuracy': accuracy
                }
            except Exception as e:
                print(f"Could not process player {player_name}: {str(e)}")
                continue
                
        return predictions

# Update the usage example
if __name__ == "__main__":
    predictor = PlayerPerformancePredictor()
    
    try:
        # Get predictions for all players
        all_predictions = predictor.predict_multiple_players()
        
        # Display results
        print("\nPredictions for all players:")
        for player, data in all_predictions.items():
            print(f"\n{player}:")
            print(f"Expected to perform: {data['expected_performance']}")
            print(f"Confidence: {data['confidence']:.2f}")
            print(f"Current sentiment: {data['sentiment']:.2f}")
            print(f"Model accuracy: {data['model_accuracy']:.2f}")
            
    except Exception as e:
        print(f"Error: {e}")
