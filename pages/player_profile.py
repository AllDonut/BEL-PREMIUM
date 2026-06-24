import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Player Profile")

df = pd.read_csv("games.csv")

if df.empty:
    st.warning("No games logged yet.")
else:
    players = sorted(df["player"].unique().tolist())
    selected = st.selectbox("Select player", players)

    p = df[df["player"] == selected].copy()
    p3 = p[p["format"] == "3v3"]
    p4 = p[p["format"] == "4v4"]

    def safe_avg(series):
        return round(series.mean(), 1) if len(series) > 0 else 0.0

    def fg(made, att):
        return round(made.sum() / att.sum() * 100, 1) if att.sum() > 0 else 0.0

    games_all  = len(p)
    wins_all   = int(p["win"].sum())
    losses_all = games_all - wins_all
    win_pct    = round(wins_all / games_all * 100, 1) if games_all > 0 else 0.0

    last5 = p.sort_values("game_id").tail(5)["win"].tolist()
    form  = " ".join(["W" if w == 1 else "L" for w in last5])

    st.markdown(f"### {selected}")
    st.markdown(f"**{games_all} GP · {wins_all}W · {losses_all}L · {win_pct}% Win**")
    st.markdown(f"Last 5: `{form}`")

    st.divider()

    st.subheader("Averages")
    stats_table = pd.DataFrame({
        "Format": ["All", "3v3", "4v4"],
        "PPG":  [safe_avg(p["pts"]),  safe_avg(p3["pts"]),  safe_avg(p4["pts"])],
        "APG":  [safe_avg(p["ast"]),  safe_avg(p3["ast"]),  safe_avg(p4["ast"])],
        "RPG":  [safe_avg(p["reb"]),  safe_avg(p3["reb"]),  safe_avg(p4["reb"])],
        "BPG":  [safe_avg(p["blk"]),  safe_avg(p3["blk"]),  safe_avg(p4["blk"])],
        "SPG":  [safe_avg(p["stl"]),  safe_avg(p3["stl"]),  safe_avg(p4["stl"])],
        "TO/G": [safe_avg(p["to"]),   safe_avg(p3["to"]),   safe_avg(p4["to"])],
        "FG%":  [fg(p["fgm"],p["fga"]), fg(p3["fgm"],p3["fga"]), fg(p4["fgm"],p4["fga"])],
        "3P%":  [fg(p["threepm"],p["threepa"]), fg(p3["threepm"],p3["threepa"]), fg(p4["threepm"],p4["threepa"])],
    })
    st.dataframe(stats_table, hide_index=True, use_container_width=True)

    st.subheader("Totals")
    totals_table = pd.DataFrame({
        "Format": ["All", "3v3", "4v4"],
        "PTS":  [int(p["pts"].sum()),    int(p3["pts"].sum()),    int(p4["pts"].sum())],
        "AST":  [int(p["ast"].sum()),    int(p3["ast"].sum()),    int(p4["ast"].sum())],
        "REB":  [int(p["reb"].sum()),    int(p3["reb"].sum()),    int(p4["reb"].sum())],
        "BLK":  [int(p["blk"].sum()),    int(p3["blk"].sum()),    int(p4["blk"].sum())],
        "STL":  [int(p["stl"].sum()),    int(p3["stl"].sum()),    int(p4["stl"].sum())],
        "TO":   [int(p["to"].sum()),     int(p3["to"].sum()),     int(p4["to"].sum())],
        "FGM":  [int(p["fgm"].sum()),    int(p3["fgm"].sum()),    int(p4["fgm"].sum())],
        "FGA":  [int(p["fga"].sum()),    int(p3["fga"].sum()),    int(p4["fga"].sum())],
        "3PM":  [int(p["threepm"].sum()), int(p3["threepm"].sum()), int(p4["threepm"].sum())],
        "3PA":  [int(p["threepa"].sum()), int(p3["threepa"].sum()), int(p4["threepa"].sum())],
    })
    st.dataframe(totals_table, hide_index=True, use_container_width=True)

    st.divider()

    st.subheader("Stat over time")
    stat_options = {
        "Points": "pts", "Assists": "ast", "Rebounds": "reb",
        "Blocks": "blk", "Steals": "stl", "Turnovers": "to",
        "FG%": "fg_pct", "3P%": "three_pct"
    }
    selected_stat = st.selectbox("Stat", list(stat_options.keys()))
    stat_col = stat_options[selected_stat]

    session_3v3 = p3.groupby("date")[stat_col].mean().reset_index()
    session_3v3["format"] = "3v3"
    session_4v4 = p4.groupby("date")[stat_col].mean().reset_index()
    session_4v4["format"] = "4v4"
    session_df = pd.concat([session_3v3, session_4v4]).sort_values("date")

    if session_df.empty:
        st.info("Not enough data yet.")
    else:
        fig = px.line(
            session_df,
            x="date",
            y=stat_col,
            color="format",
            markers=True,
            color_discrete_map={"3v3": "#3266ad", "4v4": "#e07b39"},
            labels={"date": "Session", stat_col: selected_stat, "format": "Format"},
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#888",
            legend_title_text="",
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Full game log")
    log = p.sort_values("game_id", ascending=False).reset_index(drop=True)
    log.index += 1
    log["result"] = log["win"].map({1: "W", 0: "L"})
    st.dataframe(log[[
        "game_id", "date", "format", "result",
        "pts", "fg_pct", "three_pct", "ast", "reb", "blk", "stl", "to"
    ]].rename(columns={
        "game_id":   "Game",
        "date":      "Date",
        "format":    "Format",
        "result":    "Result",
        "pts":       "PTS",
        "fg_pct":    "FG%",
        "three_pct": "3P%",
        "ast":       "AST",
        "reb":       "REB",
        "blk":       "BLK",
        "stl":       "STL",
        "to":        "TO",
    }), use_container_width=True)
