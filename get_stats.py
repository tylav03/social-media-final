from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
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
    
    def _get_player_game_stats(self, player_name: str):
        """
        Method for finding a specific NBA players statistics, given their name. Will populate the self.player_stats_dict

        Parameters:
            player_name: The full name of an nba player, as a string
        """

        # shortening keywords that will be used calling game data
        regular_season = self.gamelog.SeasonTypeAllStar.regular 
        current_season = self.gamelog.Season.current_season

        # translate the NBA players name into its 'id' variant. if the player cannot be found, return
        try:
            player_id = (self.players.find_players_by_full_name(player_name)[0])['id']
        except(IndexError):
            print("NAME DOES NOT EXIST IN DATA BASE... RETURNING")
            return

        # request a normalized dictionary of the NBA players games played this season, during the regular season
        player_recent_games = self.gamelog.PlayerGameLog(player_id, season=current_season, season_type_all_star=regular_season).get_normalized_dict()
        
        # get the most recent game from the gamelog
        player_recent_game = (player_recent_games['PlayerGameLog'])[0]

        # parse for the game date, points, rebounds, assists, and plus minus of that game
        game_date = player_recent_game['GAME_DATE']
        game_points = player_recent_game['PTS']
        game_rebounds = player_recent_game['REB']
        game_assists = player_recent_game['AST']
        game_plusminus = player_recent_game['PLUS_MINUS']

        # update the player_stats_dict to add a new key: value pair into the dictionary
        self.player_stats_dict.update({player_name: {'date': str(game_date), 'pts': game_points, 'reb': game_rebounds,
                                                      'ast': game_assists, 'plus_minus': game_plusminus}})
        
        # print(self.player_stats_dict)

# left the main in the code for testing should this file be edited, commented out
"""
if __name__ == "__main__":

    stats = getPlayerStats()
    player_name_list = ["Lebron James", "Jrue Holiday", "Brandon Ingram", "Frank Ocean", "Kendrick Lamar", "Giannis Antetokounmpo"]

    for player_name in player_name_list:
        stats._get_player_game_stats(player_name)

    print(stats.player_stats_dict)
"""
