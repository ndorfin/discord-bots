from discord_bots.models import FinishedGame, FinishedGamePlayer, Player, Session

session = Session()
total_games = 0
players = session.query(Player).order_by(Player.rated_trueskill_mu.desc()).all()

with open("./csv/players.csv", "w") as file_object:
    print(
        ("id," "name," "games," "rated_ts_mu," "rated_ts_sigma," "last_activity_at"),
        file=file_object,
    )

    for i, player in enumerate(players):
        total_games = 0
        wins = 0
        losses = 0
        ties = 0
        finished_game: FinishedGame
        finished_games = (
            session.query(FinishedGame)
            .join(
                FinishedGamePlayer,
                FinishedGame.id == FinishedGamePlayer.finished_game_id,
            )
            .filter(FinishedGamePlayer.player_id == player.id)
            .all()
        )
        total_games += len(finished_games)

        print(
            (
                f"{player.id},"
                f"{player.name},"
                f"{total_games},"
                f"{player.rated_trueskill_mu},"
                f"{player.rated_trueskill_sigma},"
                f"{player.last_activity_at}"
            ),
            file=file_object,
        )
