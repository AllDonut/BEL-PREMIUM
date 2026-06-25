import streamlit as st
import pandas as pd

st.title("Awards")

# All-time win% from the full league record book (includes untracked sessions)
ALL_TIME_WIN_PCT = {
    "Borgers Rodriguez":  18 / 30,
    "Ningwa Limbu":       14 / 30,
    "Nathan Cabral":      13 / 24,
    "Kanetho Sequira":    13 / 21,
    "Renick Fernandes":    9 / 23,
    "Clinton Camelo":      8 / 15,
    "Ashwin Rai":          7 / 16,
    "Mahdi Miah":          7 / 21,
    "Cameron":             4 / 11,
    "Savio Da Costa":      2 /  4,
}

df = pd.read_csv("games.csv")

if df.empty:
    st.warning("No games logged yet.")
else:
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

    summary["sample_win_pct"] = summary["wins"] / summary["games"]
    summary["fg_pct"] = (summary["fgm"] / summary["fga"] * 100).where(summary["fga"] > 0, 0).round(1)

    # Blend all-time win% (70%) with stats-sample win% (30%) for players in the record book
    def blended_win_pct(row):
        name = row["player"]
        if name in ALL_TIME_WIN_PCT:
            return ALL_TIME_WIN_PCT[name] * 0.70 + row["sample_win_pct"] * 0.30
        return row["sample_win_pct"]

    summary["win_pct"] = summary.apply(blended_win_pct, axis=1)

    def norm(col):
        mn, mx = col.min(), col.max()
        if mx == mn:
            return pd.Series([0.5] * len(col), index=col.index)
        return (col - mn) / (mx - mn)

    # MVP: all-time blended win% 30%, PPG 25%, APG 20%, RPG 15%, FG% 10%
    summary["mvp_score"] = (
        norm(summary["win_pct"]) * 0.30 +
        norm(summary["pts"])     * 0.25 +
        norm(summary["ast"])     * 0.20 +
        norm(summary["reb"])     * 0.15 +
        norm(summary["fg_pct"])  * 0.10
    )

    # DPOY: BPG 40%, SPG 40%, RPG 20%
    summary["dpoy_score"] = (
        norm(summary["blk"]) * 0.40 +
        norm(summary["stl"]) * 0.40 +
        norm(summary["reb"]) * 0.20
    )

    mvp_row  = summary.loc[summary["mvp_score"].idxmax()]
    dpoy_row = summary.loc[summary["dpoy_score"].idxmax()]

    # ── MVP card ──────────────────────────────────────────────────────────────
    st.markdown("## 🏆 Most Valuable Player")
    st.markdown(f"### {mvp_row['player']}")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("PPG",          round(mvp_row["pts"], 1))
    c2.metric("APG",          round(mvp_row["ast"], 1))
    c3.metric("RPG",          round(mvp_row["reb"], 1))
    c4.metric("All-Time Win%", f"{round(mvp_row['win_pct'] * 100, 1)}%")
    c5.metric("FG%",          f"{mvp_row['fg_pct']}%")

    all_time_gp = None
    if mvp_row["player"] in ALL_TIME_WIN_PCT:
        pct = ALL_TIME_WIN_PCT[mvp_row["player"]]
        # reverse-calculate from stored fractions
        lookup = {
            "Borgers Rodriguez": (18, 30), "Ningwa Limbu": (14, 30),
            "Nathan Cabral": (13, 24),     "Kanetho Sequira": (13, 21),
            "Renick Fernandes": (9, 23),   "Clinton Camelo": (8, 15),
            "Ashwin Rai": (7, 16),         "Mahdi Miah": (7, 21),
            "Cameron": (4, 11),            "Savio Da Costa": (2, 4),
        }
        w, gp = lookup[mvp_row["player"]]
        st.caption(f"All-time: {gp} GP · {w}W · {gp - w}L  |  Tracked sessions: {int(mvp_row['games'])} GP")
    else:
        st.caption(f"{int(mvp_row['games'])} tracked games")

    st.divider()

    # ── DPOY card ─────────────────────────────────────────────────────────────
    st.markdown("## 🛡️ Defensive Player of the Year")
    st.markdown(f"### {dpoy_row['player']}")
    d1, d2, d3 = st.columns(3)
    d1.metric("BPG", round(dpoy_row["blk"], 1))
    d2.metric("SPG", round(dpoy_row["stl"], 1))
    d3.metric("RPG", round(dpoy_row["reb"], 1))
    st.caption(f"{int(dpoy_row['games'])} tracked games")

    st.divider()

    # ── MVP standings ─────────────────────────────────────────────────────────
    st.subheader("MVP standings")
    st.caption("Win% is blended — 70% from all-time record book, 30% from tracked sessions.")
    mvp_table = summary.sort_values("mvp_score", ascending=False).reset_index(drop=True)
    mvp_table.index += 1
    st.dataframe(mvp_table[[
        "player", "games", "pts", "ast", "reb", "win_pct", "fg_pct", "mvp_score"
    ]].rename(columns={
        "player":    "Player",
        "games":     "Tracked GP",
        "pts":       "PPG",
        "ast":       "APG",
        "reb":       "RPG",
        "win_pct":   "Blended Win%",
        "fg_pct":    "FG%",
        "mvp_score": "Score",
    }).assign(**{
        "PPG":          lambda x: x["PPG"].round(1),
        "APG":          lambda x: x["APG"].round(1),
        "RPG":          lambda x: x["RPG"].round(1),
        "Blended Win%": lambda x: (x["Blended Win%"] * 100).round(1).astype(str) + "%",
        "Score":        lambda x: x["Score"].round(3),
    }), use_container_width=True)

    st.subheader("DPOY standings")
    dpoy_table = summary.sort_values("dpoy_score", ascending=False).reset_index(drop=True)
    dpoy_table.index += 1
    st.dataframe(dpoy_table[[
        "player", "games", "blk", "stl", "reb", "dpoy_score"
    ]].rename(columns={
        "player":     "Player",
        "games":      "Tracked GP",
        "blk":        "BPG",
        "stl":        "SPG",
        "reb":        "RPG",
        "dpoy_score": "Score",
    }).assign(**{
        "BPG":   lambda x: x["BPG"].round(1),
        "SPG":   lambda x: x["SPG"].round(1),
        "RPG":   lambda x: x["RPG"].round(1),
        "Score": lambda x: x["Score"].round(3),
    }), use_container_width=True)
