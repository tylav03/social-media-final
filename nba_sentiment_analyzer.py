# Import required libraries
import feedparser
import pandas as pd
from textblob import TextBlob
import re
from datetime import datetime, timedelta
from nba_api.stats.static import players
from newsapi import NewsApiClient

class NBAArticleAnalyzer:
    def __init__(self):
        # Set up API key and initialize the news API client
        self.news_api_key = 'd894bde817574c778ba0803b29872c03'
        self.news_api = NewsApiClient(self.news_api_key)
        self.player_names = self._load_player_names()
        
    def _load_player_names(self):
        # Get a list of all active NBA players
        all_players = players.get_active_players()
        return [player['full_name'] for player in all_players]
    
    def fetch_articles(self, days_back=28):
        # Calculate date range for article search
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        print(f"Fetching articles from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        articles = []
        # List of sports news sources to search from
        sources = ('espn,bleacher-report,fox-sports,sports-illustrated,'
                  'cbs-sports,nbc-sports,the-athletic,talksport,'
                  'espn-cric-info,four-four-two,marca,bbc-sport,'
                  'goal-com,sporting-news,yahoo-sports,sky-sports,'
                  'football-italia,sport,as,lequipe,kicker,'
                  'sports-mole,sportstar,the-score,fansided')
        
        try:
            # Make API request to get NBA articles
            response = self.news_api.get_everything(
                q='NBA',
                sources=sources,
                from_param=start_date.strftime('%Y-%m-%d'),
                to=end_date.strftime('%Y-%m-%d'),
                language='en',
                sort_by='publishedAt',
                page_size=100  # Max articles per request
            )
            
            # If request successful, store article details
            if response['status'] == 'ok':
                for article in response['articles']:
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'published': article.get('publishedAt', ''),
                        'link': article.get('url', '')
                    })
            
            print(f"Fetched {len(articles)} articles")
            return articles
            
        except Exception as e:
            print(f"Error fetching articles: {e}")
            return []
    
    def analyze_sentiment(self, text):
        # Analyze if text is positive or negative (-1 to 1 scale)
        blob = TextBlob(text)
        return blob.sentiment.polarity
    
    def find_player_mentions(self, text):
        # Find which NBA players are mentioned in the text
        mentions = {}
        for player in self.player_names:
            if player.lower() in text.lower():
                mentions[player] = True
        return mentions
    
    def analyze_articles(self):
        # Main function to analyze articles
        articles = self.fetch_articles()
        results = []
        
        # For each article, check sentiment and player mentions
        for article in articles:
            full_text = f"{article['title']} {article['description']}"
            sentiment = self.analyze_sentiment(full_text)
            player_mentions = self.find_player_mentions(full_text)
            
            # Store results for each player mentioned
            for player in player_mentions:
                results.append({
                    'player': player,
                    'sentiment': sentiment,
                    'article_title': article['title'],
                    'date': article['published'],
                    'url': article['link']
                })
                
        return pd.DataFrame(results)


if __name__ == "__main__":
    # Create analyzer object
    analyzer = NBAArticleAnalyzer()
    # Get results in a DataFrame
    results_df = analyzer.analyze_articles()
    
    print("\nDataFrame Info:")
    print(results_df.info())

    # Create visualizations if we have data
    if not results_df.empty:
        import matplotlib.pyplot as plt
        
        # Create first plot: sentiment by player
        plt.figure(figsize=(12, 6))
        avg_sentiment = results_df.groupby('player')['sentiment'].mean().sort_values(ascending=True)
        avg_sentiment.plot(kind='barh')
        plt.title('Average Sentiment Score by Player')
        plt.xlabel('Sentiment Score (-1 = Negative, 1 = Positive)')
        plt.ylabel('Player')
        plt.tight_layout()
        plt.show()
        
        # Create second plot: mention counts
        plt.figure(figsize=(12, 6))
        mention_counts = results_df['player'].value_counts()
        mention_counts.plot(kind='bar')
        plt.title('Number of Mentions by Player')
        plt.xlabel('Player')
        plt.ylabel('Number of Mentions')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    # Print summary statistics
    if not results_df.empty:
        print("\nTotal articles analyzed:", len(results_df))
        print("\nAverage Sentiment by Player:")
        print(results_df.groupby('player')['sentiment'].mean().sort_values(ascending=False))
        
        print("\nNumber of mentions per player:")
        print(results_df['player'].value_counts())
    else:
        print("\nNo player mentions found in the articles.")