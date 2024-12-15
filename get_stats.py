from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import time
from requests.exceptions import Timeout, RequestException
from datetime import datetime, timedelta
"""
IMPORTS
"""


class getPlayerStats:
    """
    Class for finding the statistics of specific players

    Methods: 
        _get_player_game_stats(): given a players name, will pull the game date, points, rebound, assists, and plus/minus statistics

    Attributes:
        players: a reference to the nba_api.stats.static module, 'players'
        gamelog: a reference to the nba_api.stats.endpoints module, 'playergamelog'
        player_stats_dict: a dictionary that will hold the names, dates, points, rebounds, assists, and plus/minus statistics of players
    """

    def __init__(self):
        """
        Initializes the class; Only a default constructor is used

        players: a reference to the nba_api.stats.static module, 'players'
        gamelog: a reference to the nba_api.stats.endpoints module, 'playergamelog'
        self.player_stats_dict: {{}}
            initialized as {}, ends as {playername: {'date': date, 'pts': points, 'reb': rebounds, 'assists': rebounds, 'plus_minus': plus/minus},...}
        """

        self.players = players
        self.gamelog = playergamelog
        self.player_stats_dict = {}
    
    def _get_player_game_stats(self, player_name: str, max_retries=3):
        """
        Method for finding a specific NBA player's average statistics over the past 30 days
        """
        for attempt in range(max_retries):
            try:
                regular_season = self.gamelog.SeasonTypeAllStar.regular 
                current_season = self.gamelog.Season.current_season

                try:
                    player_id = (self.players.find_players_by_full_name(player_name)[0])['id']
                except(IndexError):
                    print(f"Player not found: {player_name}")
                    return

                time.sleep(1)
                
                player_games = self.gamelog.PlayerGameLog(
                    player_id, 
                    season=current_season, 
                    season_type_all_star=regular_season,
                    timeout=45  
                ).get_normalized_dict()
                
                # Get games from last 30 days
                thirty_days_ago = datetime.now() - timedelta(days=30)
                recent_games = []
                
                for game in player_games['PlayerGameLog']:
                    # Parse date in the format "MMM DD, YYYY"
                    try:
                        game_date = datetime.strptime(game['GAME_DATE'], '%b %d, %Y')
                    except ValueError:
                        # Try alternative format if first attempt fails
                        game_date = datetime.strptime(game['GAME_DATE'], '%B %d, %Y')
                        
                    if game_date >= thirty_days_ago:
                        recent_games.append(game)

                if not recent_games:
                    print(f"No games found in the last 30 days for: {player_name}")
                    return

                # Calculate averages
                num_games = len(recent_games)
                avg_points = sum(game['PTS'] for game in recent_games) / num_games
                avg_rebounds = sum(game['REB'] for game in recent_games) / num_games
                avg_assists = sum(game['AST'] for game in recent_games) / num_games
                avg_plusminus = sum(game['PLUS_MINUS'] for game in recent_games) / num_games

                self.player_stats_dict.update({
                    player_name: {
                        'games_played': num_games,
                        'avg_pts': round(avg_points, 1),
                        'avg_reb': round(avg_rebounds, 1),
                        'avg_ast': round(avg_assists, 1),
                        'avg_plus_minus': round(avg_plusminus, 1),
                        'last_30_days': True
                    }
                })
                return

            except (Timeout, RequestException) as e:
                if attempt == max_retries - 1:
                    print(f"Failed to get stats for {player_name} after {max_retries} attempts")
                    raise
                time.sleep(2 * (attempt + 1))

# left the main in the code for testing should this file be edited, commented out
"""
if __name__ == "__main__":

    stats = getPlayerStats()
    player_name_list = ["Lebron James", "Jrue Holiday", "Brandon Ingram", "Frank Ocean", "Kendrick Lamar", "Giannis Antetokounmpo"]

    for player_name in player_name_list:
        stats._get_player_game_stats(player_name)

    print(stats.player_stats_dict)
"""
