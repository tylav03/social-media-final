from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import time
from requests.exceptions import Timeout, RequestException
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
        Method for finding a specific NBA players statistics, given their name. Will populate the self.player_stats_dict

        Parameters:
            player_name: The full name of an nba player, as a string
        """
        for attempt in range(max_retries):
            try:
                # shortening keywords that will be used calling game data
                regular_season = self.gamelog.SeasonTypeAllStar.regular 
                current_season = self.gamelog.Season.current_season

                try:
                    # translate the NBA players name into its 'id' variant. if the player cannot be found, return
                    player_id = (self.players.find_players_by_full_name(player_name)[0])['id']
                except(IndexError):
                    print(f"Player not found: {player_name}")
                    return

                # add delay between requests to avoid rate limiting
                time.sleep(1)
                
                player_recent_games = self.gamelog.PlayerGameLog(
                    player_id, 
                    season=current_season, 
                    season_type_all_star=regular_season,
                    timeout=45  
                ).get_normalized_dict()
                
                player_recent_game = (player_recent_games['PlayerGameLog'])[0]

                # parse for the game date, points, rebounds, assists, and plus minus of that game
                game_date = player_recent_game['GAME_DATE']
                game_points = player_recent_game['PTS']
                game_rebounds = player_recent_game['REB']
                game_assists = player_recent_game['AST']
                game_plusminus = player_recent_game['PLUS_MINUS']

                self.player_stats_dict.update({
                    player_name: {
                        'date': str(game_date), 
                        'pts': game_points, 
                        'reb': game_rebounds,
                        'ast': game_assists, 
                        'plus_minus': game_plusminus
                    }
                })
                return

            except (Timeout, RequestException) as e:
                if attempt == max_retries - 1:  # Last attempt
                    print(f"Failed to get stats for {player_name} after {max_retries} attempts")
                    raise
                time.sleep(2 * (attempt + 1))  # Exponential backoff

# left the main in the code for testing should this file be edited, commented out
"""
if __name__ == "__main__":

    stats = getPlayerStats()
    player_name_list = ["Lebron James", "Jrue Holiday", "Brandon Ingram", "Frank Ocean", "Kendrick Lamar", "Giannis Antetokounmpo"]

    for player_name in player_name_list:
        stats._get_player_game_stats(player_name)

    print(stats.player_stats_dict)
"""
