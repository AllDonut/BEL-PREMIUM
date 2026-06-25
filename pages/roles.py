import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("Role Contribution")

df = pd.read_csv("games.csv")

if df.empty:
    st.warning("No games logged yet.")
else:
    format_filter = st.selectbox("Format", ["All", "3v3", "4v4"])

    if format_filter != "All":
        df = df[df["format"] == format_filter]

    summary = df.groupby("player").agg(
        games   = ("game_id", "count"),
        pts     = ("pts", "mean"),
        ast     = ("ast", "mean"),
        reb     = ("reb", "mean"),
        blk     = ("blk", "mean"),
        stl     = ("stl", "mean"),
    ).reset_index()

    summary["ppg"] = summary["pts"].round(2)
    summary["apg"] = summary["ast"].round(2)
    summary["rpg"] = summary["reb"].round(2)
    summary["bpg"] = summary["blk"].round(2)
    summary["spg"] = summary["stl"].round(2)

    summary["scoring"]    = summary["ppg"]
    summary["playmaking"] = summary["apg"] * 2
    summary["rebounding"] = summary["rpg"]
    summary["defending"]  = (summary["bpg"] + summary["spg"]) * 2
    summary["total"]      = summary["scoring"] + summary["playmaking"] + summary["rebounding"] + summary["defending"]

    summary["scoring_pct"]    = (summary["scoring"]    / summary["total"] * 100).round(1)
    summary["playmaking_pct"] = (summary["playmaking"] / summary["total"] * 100).round(1)
    summary["rebounding_pct"] = (summary["rebounding"] / summary["total"] * 100).round(1)
    summary["defending_pct"]  = (summary["defending"]  / summary["total"] * 100).round(1)

    st.subheader("Role breakdown — stacked bar")
    st.caption("What % of each player's contribution comes from scoring, playmaking, rebounding and defending.")

    fig_bar = px.bar(
        summary,
        y="player",
        x=["scoring_pct", "playmaking_pct", "rebounding_pct", "defending_pct"],
        orientation="h",
        labels={
            "value": "%", "player": "Player", "variable": "Role",
        },
        color_discrete_map={
            "scoring_pct":    "#3266ad",
            "playmaking_pct": "#e07b39",
            "rebounding_pct": "#5a9e6f",
            "defending_pct":  "#a855b5",
        },
    )
    fig_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#888",
        barmode="stack",
        xaxis=dict(title="%", gridcolor="rgba(128,128,128,0.15)"),
        yaxis=dict(title=""),
        legend=dict(
            orientation="h",
            y=-0.2,
            title_text="",
        ),
        height=420,
    )
    newnames = {
        "scoring_pct": "Scoring",
        "playmaking_pct": "Playmaking",
        "rebounding_pct": "Rebounding",
        "defending_pct": "Defending",
    }
    fig_bar.for_each_trace(lambda t: t.update(name=newnames[t.name]))
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    st.subheader("Role breakdown — radar chart")
    st.caption("Compare player shapes across all four roles.")

    selected_players = st.multiselect(
        "Select players to compare", summary["player"].tolist(),
        default=summary["player"].tolist()[:3]
    )

    categories = ["Scoring", "Playmaking", "Rebounding", "Defending"]
    colors = ["#3266ad","#e07b39","#5a9e6f","#a855b5","#d94f4f","#2eb8c2","#c9a227","#7b6cf6","#e85d8a"]

    def norm_role(col):
        mn, mx = col.min(), col.max()
        if mx == mn:
            return pd.Series([50.0] * len(col), index=col.index)
        return (col - mn) / (mx - mn) * 100

    summary["scoring_norm"]    = norm_role(summary["scoring"])
    summary["playmaking_norm"] = norm_role(summary["playmaking"])
    summary["rebounding_norm"] = norm_role(summary["rebounding"])
    summary["defending_norm"]  = norm_role(summary["defending"])

    fig_radar = go.Figure()
    for i, player in enumerate(selected_players):
        row = summary[summary["player"] == player].iloc[0]
        values = [
            row["scoring_norm"],
            row["playmaking_norm"],
            row["rebounding_norm"],
            row["defending_norm"],
        ]
        values += [values[0]]
        cats = categories + [categories[0]]
        hex_color = colors[i % len(colors)]
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        fill_color = f"rgba({r},{g},{b},0.15)"
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=cats,
            fill="toself",
            name=player,
            line_color=hex_color,
            fillcolor=fill_color,
            opacity=0.8,
        ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, gridcolor="rgba(128,128,128,0.2)"),
            angularaxis=dict(gridcolor="rgba(128,128,128,0.2)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#888",
        showlegend=True,
        height=500,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()

    st.subheader("Raw role scores")
    st.caption("Normalised contribution per role before converting to %.")
    st.dataframe(summary[[
        "player", "scoring_pct", "playmaking_pct", "rebounding_pct", "defending_pct"
    ]].rename(columns={
        "player":          "Player",
        "scoring_pct":     "Scoring %",
        "playmaking_pct":  "Playmaking %",
        "rebounding_pct":  "Rebounding %",
        "defending_pct":   "Defending %",
    }).sort_values("Scoring %", ascending=False).reset_index(drop=True),
    hide_index=True, use_container_width=True)
