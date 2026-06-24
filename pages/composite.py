import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Composite Score & Tier")

# ── Weights (only adjust here) ──────────────────────────────────────────────
WEIGHTS = {
    "win_pct": 0.20,
    "ppg":     0.15,
    "apg":     0.15,
    "rpg":     0.15,
    "bpg":     0.10,
    "spg":     0.10,
    "to_inv":  0.05,   # inverted turnovers (fewer = better)
}
MIN_GAMES = 1
# ────────────────────────────────────────────────────────────────────────────

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
    ).reset_index()

    summary = summary[summary["games"] >= MIN_GAMES].copy()

    if summary.empty:
        st.warning(f"No players with {MIN_GAMES}+ games yet.")
    else:
        summary["ppg"]     = summary["pts"].round(2)
        summary["apg"]     = summary["ast"].round(2)
        summary["rpg"]     = summary["reb"].round(2)
        summary["bpg"]     = summary["blk"].round(2)
        summary["spg"]     = summary["stl"].round(2)
        summary["topg"]    = summary["to"].round(2)
        summary["win_pct"] = (summary["wins"] / summary["games"] * 100).round(1)

        def norm(col):
            mn, mx = col.min(), col.max()
            if mx == mn:
                return pd.Series([0.5] * len(col), index=col.index)
            return (col - mn) / (mx - mn)

        summary["to_inv"] = 1 - norm(summary["topg"])

        score = sum(WEIGHTS[s] * norm(summary[s]) for s in ["ppg","apg","rpg","bpg","spg","win_pct"]) \
              + WEIGHTS["to_inv"] * summary["to_inv"]
        summary["score"] = (score * 100).round(1)

        mean_s = summary["score"].mean()
        sd_s   = summary["score"].std()

        def tier(s):
            if s >= mean_s + sd_s:  return "Elite"
            if s >= mean_s:         return "Contender"
            if s >= mean_s - sd_s:  return "Mid"
            return "Bottom"

        summary["tier"] = summary["score"].apply(tier)

        tier_order  = ["Elite", "Contender", "Mid", "Bottom"]
        tier_colors = {
            "Elite":     "#f0c040",
            "Contender": "#3266ad",
            "Mid":       "#5a9e6f",
            "Bottom":    "#888888",
        }

        summary = summary.sort_values("score", ascending=False).reset_index(drop=True)
        summary.index += 1

        # ── Bar chart ───────────────────────────────────────────────────────
        fig = px.bar(
            summary,
            x="score",
            y="player",
            color="tier",
            orientation="h",
            color_discrete_map=tier_colors,
            category_orders={"tier": tier_order},
            labels={"score": "Composite Score", "player": "Player", "tier": "Tier"},
            text="score",
        )
        fig.update_traces(textposition="outside", textfont_size=11)
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#888",
            yaxis=dict(autorange="reversed", title=""),
            xaxis=dict(range=[0, summary["score"].max() * 1.2], title="Score (0–100)", gridcolor="rgba(128,128,128,0.15)"),
            legend=dict(orientation="h", y=-0.15, title_text=""),
            height=max(350, len(summary) * 45),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            f"Mean: {mean_s:.1f} · SD: {sd_s:.1f} — "
            "Elite ≥ mean+SD · Contender ≥ mean · Mid ≥ mean−SD · Bottom below"
        )

        st.divider()

        # ── Scatter: score vs win% ───────────────────────────────────────────
        st.subheader("Score vs Win% — tier map")
        fig_sc = px.scatter(
            summary,
            x="score",
            y="win_pct",
            color="player",
            text="player",
            size="games",
            size_max=22,
            labels={"score": "Composite Score", "win_pct": "Win %", "player": "Player", "games": "GP"},
        )
        sc_x_max = summary["score"].max() * 1.2
        fig_sc.update_traces(textposition="top center", textfont_size=11, marker=dict(opacity=0.85, line=dict(width=1, color="rgba(255,255,255,0.3)")))
        fig_sc.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#888",
            xaxis=dict(range=[0, sc_x_max], title="Composite Score", gridcolor="rgba(128,128,128,0.15)"),
            yaxis=dict(range=[0, 105], title="Win %", gridcolor="rgba(128,128,128,0.15)"),
            legend=dict(
                orientation="v",
                x=1.02,
                y=1,
                title_text="Player",
                bgcolor="rgba(0,0,0,0)",
            ),
            height=500,
        )
        st.plotly_chart(fig_sc, use_container_width=True)
        st.caption("Bubble size = games played · Click a tier in the legend to hide/show · Double-click to isolate")

        st.divider()

        # ── Score over time ──────────────────────────────────────────────────
        st.subheader("Composite score over time")
        st.caption("Average per-game performance score per session — win counts as +20 pts toward score.")

        raw = df.copy()

        def norm_col(col):
            mn, mx = col.min(), col.max()
            if mx == mn:
                return pd.Series([0.5] * len(col), index=col.index)
            return (col - mn) / (mx - mn)

        raw["game_score"] = (
            norm_col(raw["win"])  * 0.20 +
            norm_col(raw["pts"])  * 0.15 +
            norm_col(raw["ast"])  * 0.15 +
            norm_col(raw["reb"])  * 0.15 +
            norm_col(raw["blk"])  * 0.10 +
            norm_col(raw["stl"])  * 0.10 +
            (1 - norm_col(raw["to"])) * 0.05
        ) * 100

        time_df = raw.groupby(["player", "date"])["game_score"].mean().reset_index()
        time_df.columns = ["player", "date", "score"]
        time_df = time_df.sort_values("date")

        all_players = sorted(time_df["player"].unique().tolist())
        selected_t = st.multiselect("Players", all_players, default=all_players)
        time_filtered = time_df[time_df["player"].isin(selected_t)]

        if time_filtered.empty:
            st.info("No data for selected players.")
        else:
            fig_time = px.line(
                time_filtered,
                x="date",
                y="score",
                color="player",
                markers=True,
                labels={"date": "Session", "score": "Score", "player": "Player"},
            )
            fig_time.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#888",
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
                legend=dict(orientation="v", x=1.02, y=1, title_text="Player", bgcolor="rgba(0,0,0,0)"),
                height=420,
            )
            st.plotly_chart(fig_time, use_container_width=True)

        st.divider()

        # ── Tier table ──────────────────────────────────────────────────────
        st.subheader("Player rankings")
        display = summary[[
            "player","tier","score","games","wins","win_pct",
            "ppg","apg","rpg","bpg","spg","topg"
        ]].rename(columns={
            "player":  "Player",
            "tier":    "Tier",
            "score":   "Score",
            "games":   "GP",
            "wins":    "W",
            "win_pct": "Win%",
            "ppg":     "PPG",
            "apg":     "APG",
            "rpg":     "RPG",
            "bpg":     "BPG",
            "spg":     "SPG",
            "topg":    "TO/G",
        })
        st.dataframe(display, hide_index=False, use_container_width=True)

        st.divider()

        # ── Weight breakdown (read-only reference) ──────────────────────────
        with st.expander("How the score is calculated"):
            st.markdown("""
| Stat | Weight |
|------|--------|
| Win% | 20% |
| PPG | 15% |
| APG | 15% |
| RPG | 15% |
| BPG | 10% |
| SPG | 10% |
| TO (inverted) | 5% |

Each stat is **min-max normalised** across all qualifying players before weighting,
so the score reflects relative standing — not raw numbers.
Minimum **{} games** required to appear.
""".format(MIN_GAMES))
