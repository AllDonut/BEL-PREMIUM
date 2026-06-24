import streamlit as st
import pandas as pd
import plotly.express as px

st.title("League Scatter")

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
        pts     = ("pts", "mean"),
        ast     = ("ast", "mean"),
        reb     = ("reb", "mean"),
        blk     = ("blk", "mean"),
        stl     = ("stl", "mean"),
        to      = ("to", "mean"),
        fgm     = ("fgm", "sum"),
        fga     = ("fga", "sum"),
        threepm = ("threepm", "sum"),
        threepa = ("threepa", "sum"),
    ).reset_index()

    summary["win_pct"]   = (summary["wins"] / summary["games"] * 100).round(1)
    summary["ppg"]       = summary["pts"].round(1)
    summary["apg"]       = summary["ast"].round(1)
    summary["rpg"]       = summary["reb"].round(1)
    summary["bpg"]       = summary["blk"].round(1)
    summary["spg"]       = summary["stl"].round(1)
    summary["topg"]      = summary["to"].round(1)
    summary["fg_pct"]    = (summary["fgm"] / summary["fga"].replace(0, 1) * 100).round(1)
    summary["three_pct"] = (summary["threepm"] / summary["threepa"].replace(0, 1) * 100).round(1)

    stat_options = {
        "PPG": "ppg", "APG": "apg", "RPG": "rpg",
        "BPG": "bpg", "SPG": "spg", "TO/G": "topg",
        "FG%": "fg_pct", "3P%": "three_pct",
        "Win%": "win_pct", "Wins": "wins", "Games": "games"
    }

    col1, col2 = st.columns(2)
    with col1:
        x_label = st.selectbox("X axis", list(stat_options.keys()), index=0)
    with col2:
        y_label = st.selectbox("Y axis", list(stat_options.keys()), index=1)

    x_col = stat_options[x_label]
    y_col = stat_options[y_label]

    fig = px.scatter(
        summary,
        x=x_col,
        y=y_col,
        text="player",
        color="player",
        size="games",
        size_max=20,
        labels={x_col: x_label, y_col: y_label, "player": "Player"},
    )
    x_min = 0
    x_max = summary[x_col].max() * 1.2
    y_min = 0
    y_max = summary[y_col].max() * 1.2
    x_mid = x_max / 2
    y_mid = y_max / 2

    fig.update_traces(textposition="top center", textfont_size=11)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#888",
        showlegend=True,
        xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", range=[x_min, x_max]),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", range=[y_min, y_max]),
        height=550,
        shapes=[
            dict(type="line", x0=x_mid, x1=x_mid, y0=y_min, y1=y_max,
                 line=dict(color="rgba(255,255,255,0.15)", width=1.5, dash="dash")),
            dict(type="line", x0=x_min, x1=x_max, y0=y_mid, y1=y_mid,
                 line=dict(color="rgba(255,255,255,0.15)", width=1.5, dash="dash")),
            dict(type="rect", x0=x_mid, x1=x_max, y0=y_mid, y1=y_max,
                 fillcolor="rgba(50,102,173,0.07)", line_width=0),
            dict(type="rect", x0=x_min, x1=x_mid, y0=y_min, y1=y_mid,
                 fillcolor="rgba(169,79,79,0.07)", line_width=0),
            dict(type="rect", x0=x_mid, x1=x_max, y0=y_min, y1=y_mid,
                 fillcolor="rgba(128,128,128,0.05)", line_width=0),
            dict(type="rect", x0=x_min, x1=x_mid, y0=y_mid, y1=y_max,
                 fillcolor="rgba(128,128,128,0.05)", line_width=0),
        ],
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Bubble size = games played · Quadrants split at midpoint of range")
