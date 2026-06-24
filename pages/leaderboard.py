import streamlit as st
import pandas as pd

st.title("Leaderboard")

df = pd.read_csv("games.csv")

if df.empty:
    st.warning("No games logged yet.")
else:
    format_filter = st.selectbox("Format", ["All", "3v3", "4v4"])

    if format_filter != "All":
        df = df[df["format"] == format_filter]

    summary = df.groupby("player").agg(
        games   = ("game_id", "count"),
        wins    = ("win", "sum"),
        pts     = ("pts", "sum"),
        fgm     = ("fgm", "sum"),
        fga     = ("fga", "sum"),
        threepm = ("threepm", "sum"),
        threepa = ("threepa", "sum"),
        ast     = ("ast", "sum"),
        reb     = ("reb", "sum"),
        blk     = ("blk", "sum"),
        stl     = ("stl", "sum"),
        to      = ("to", "sum"),
    ).reset_index()

    summary["losses"]    = summary["games"] - summary["wins"]
    summary["win_pct"]   = (summary["wins"] / summary["games"] * 100).round(1)
    summary["ppg"]       = (summary["pts"]     / summary["games"]).round(1)
    summary["apg"]       = (summary["ast"]     / summary["games"]).round(1)
    summary["rpg"]       = (summary["reb"]     / summary["games"]).round(1)
    summary["bpg"]       = (summary["blk"]     / summary["games"]).round(1)
    summary["spg"]       = (summary["stl"]     / summary["games"]).round(1)
    summary["topg"]      = (summary["to"]      / summary["games"]).round(1)
    summary["fg_pct"]    = (summary["fgm"] / summary["fga"].replace(0, 1) * 100).round(1)
    summary["three_pct"] = (summary["threepm"] / summary["threepa"].replace(0, 1) * 100).round(1)

    st.subheader("Averages")
    sort_avg = st.selectbox("Sort by", ["win_pct", "ppg", "apg", "rpg", "bpg", "spg", "fg_pct", "three_pct", "topg"], key="sort_avg")

    avg_table = summary.sort_values(sort_avg, ascending=False).reset_index(drop=True)
    avg_table.index += 1
    st.dataframe(avg_table[[
        "player", "games", "wins", "losses", "win_pct",
        "ppg", "apg", "rpg", "bpg", "spg", "fg_pct", "three_pct", "topg"
    ]].rename(columns={
        "player":    "Player",
        "games":     "GP",
        "wins":      "W",
        "losses":    "L",
        "win_pct":   "Win%",
        "ppg":       "PPG",
        "apg":       "APG",
        "rpg":       "RPG",
        "bpg":       "BPG",
        "spg":       "SPG",
        "fg_pct":    "FG%",
        "three_pct": "3P%",
        "topg":      "TO/G",
    }), use_container_width=True)

    st.subheader("Totals")
    sort_tot = st.selectbox("Sort by", ["pts", "ast", "reb", "blk", "stl", "fgm", "fga", "threepm", "threepa", "to", "wins", "games"], key="sort_tot")

    tot_table = summary.sort_values(sort_tot, ascending=False).reset_index(drop=True)
    tot_table.index += 1
    st.dataframe(tot_table[[
        "player", "games", "wins", "pts", "ast", "reb", "blk", "stl", "fgm", "fga", "threepm", "threepa", "to"
    ]].rename(columns={
        "player":   "Player",
        "games":    "GP",
        "wins":     "W",
        "pts":      "PTS",
        "ast":      "AST",
        "reb":      "REB",
        "blk":      "BLK",
        "stl":      "STL",
        "fgm":      "FGM",
        "fga":      "FGA",
        "threepm":  "3PM",
        "threepa":  "3PA",
        "to":       "TO",
    }), use_container_width=True)
