from discord_bots.models import FinishedGame, FinishedGamePlayer, Player, Session

session = Session()

finished_games: list[FinishedGame] = (
    session.query(FinishedGame)
    .order_by(FinishedGame.finished_at.desc())
    .limit(200)
    .all()
)

with open("./csv/match_history.csv", "w") as file_object:
    print(
        (
            "timestamp,"
            "winning_team,"
            "team0_win%,"
            "team1_win%,"
            "is_upset,"
            "t0player0,"
            "t0player1,"
            "t0player2,"
            "t0player3,"
            "t0player4,"
            "t1player0,"
            "t1player1,"
            "t1player2,"
            "t1player3,"
            "t1player4"
        ),
        file=file_object,
    )
    for finished_game in finished_games:
        winning_team = ""
        if finished_game.winning_team == -1:
            winning_team = "tie"
        elif finished_game.winning_team == 0:
            winning_team = "be"
        elif finished_game.winning_team == 1:
            winning_team = "ds"
        team0_players: list[Player] = (
            session.query(Player)
            .join(
                FinishedGamePlayer,
                Player.id == FinishedGamePlayer.player_id,
            )
            .filter(
                FinishedGamePlayer.finished_game_id == finished_game.id,
                FinishedGamePlayer.team == 0,
            )
        )
        team1_players: list[Player] = (
            session.query(Player)
            .join(
                FinishedGamePlayer,
                Player.id == FinishedGamePlayer.player_id,
            )
            .filter(
                FinishedGamePlayer.finished_game_id == finished_game.id,
                FinishedGamePlayer.team == 1,
            )
        )

        team0_ids: str = ",".join([str(player.id) for player in team0_players])
        team1_ids: str = ",".join([str(player.id) for player in team1_players])

        is_upset = False
        if finished_game.win_probability > 0.5 and finished_game.winning_team == 1:
            is_upset = True
        if finished_game.win_probability < 0.5 and finished_game.winning_team == 0:
            is_upset = True

        print(
            (
                f"{finished_game.finished_at},"
                f"{winning_team},"
                f"{round(finished_game.win_probability,2)},"
                f"{round(1-finished_game.win_probability,2)},"
                f"{is_upset},"
                f"{team0_ids},"
                f"{team1_ids}"
            ),
            file=file_object,
        )
