import streamlit as st
import pandas as pd
from datetime import date

st.title("Buckhurst Egoist League")

password = st.text_input("Enter admin password", type="password")
authenticated = password == "yourpassword"

if not authenticated:
    st.error("Enter password to access the game logger.")
else:
    players_df = pd.read_csv("players.csv")
    player_list = players_df["name"].tolist()

    st.header("Log a game")

    col1, col2 = st.columns(2)
    with col1:
        game_date = st.date_input("Date", value=date.today())
    with col2:
        game_format = st.selectbox("Format", ["3v3", "4v4"])

    col3, col4 = st.columns(2)
    with col3:
        team_a = st.multiselect("Team A players", player_list)
    with col4:
        team_b = st.multiselect("Team B players", player_list)

    winner = st.selectbox("Winner", ["Team A", "Team B"])

    all_players = team_a + team_b
    st.subheader("Stats per player")

    stats = {}
    if all_players:
        for player in all_players:
            st.markdown(f"**{player}**")
            c1,c2,c3,c4,c5,c6,c7,c8,c9 = st.columns(9)
            safe = player.replace(" ", "_")
            stats[player] = {
                "fgm":     c1.number_input("FGM", min_value=0, key=f"fgm_{safe}"),
                "fga":     c2.number_input("FGA", min_value=0, key=f"fga_{safe}"),
                "threepm": c3.number_input("3PM", min_value=0, key=f"3pm_{safe}"),
                "threepa": c4.number_input("3PA", min_value=0, key=f"3pa_{safe}"),
                "ast":     c5.number_input("AST", min_value=0, key=f"ast_{safe}"),
                "reb":     c6.number_input("REB", min_value=0, key=f"reb_{safe}"),
                "blk":     c7.number_input("BLK", min_value=0, key=f"blk_{safe}"),
                "stl":     c8.number_input("STL", min_value=0, key=f"stl_{safe}"),
                "to":      c9.number_input("TO",  min_value=0, key=f"to_{safe}"),
            }

    if st.button("Save game"):
        if not team_a or not team_b:
            st.error("Please select players for both teams.")
        else:
            df = pd.read_csv("games.csv")
            new_id = int(df["game_id"].max() + 1) if len(df) > 0 else 1

            rows = []
            for player in all_players:
                s = stats[player]
                pts = (s["fgm"] - s["threepm"]) * 2 + s["threepm"] * 4
                fg_pct = round(s["fgm"] / s["fga"] * 100, 1) if s["fga"] > 0 else 0
                three_pct = round(s["threepm"] / s["threepa"] * 100, 1) if s["threepa"] > 0 else 0
                team = "A" if player in team_a else "B"
                win = 1 if (winner == "Team A" and team == "A") or (winner == "Team B" and team == "B") else 0

                rows.append({
                    "game_id":   new_id,
                    "date":      str(game_date),
                    "format":    game_format,
                    "player":    player,
                    "team":      team,
                    "win":       win,
                    "fgm":       s["fgm"],
                    "fga":       s["fga"],
                    "threepm":   s["threepm"],
                    "threepa":   s["threepa"],
                    "pts":       pts,
                    "fg_pct":    fg_pct,
                    "three_pct": three_pct,
                    "ast":       s["ast"],
                    "reb":       s["reb"],
                    "blk":       s["blk"],
                    "stl":       s["stl"],
                    "to":        s["to"],
                })

            new_df = pd.DataFrame(rows)
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv("games.csv", index=False)
            st.success(f"Game {new_id} saved successfully!")
            st.dataframe(new_df[["player","team","win","pts","fg_pct","three_pct","ast","reb","blk","stl","to"]])
