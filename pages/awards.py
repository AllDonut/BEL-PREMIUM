import streamlit as st
import pandas as pd

st.title("Awards")

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

    summary["win_pct"] = summary["wins"] / summary["games"]
    summary["fg_pct"]  = (summary["fgm"] / summary["fga"] * 100).where(summary["fga"] > 0, 0).round(1)

    # ── MVP ──────────────────────────────────────────────────────────────────
    # Weighted score: win% 30%, PPG 25%, APG 20%, RPG 15%, efficiency 10%
    def norm(col):
        mn, mx = col.min(), col.max()
        if mx == mn:
            return pd.Series([0.5] * len(col), index=col.index)
        return (col - mn) / (mx - mn)

    summary["mvp_score"] = (
        norm(summary["win_pct"]) * 0.30 +
        norm(summary["pts"])     * 0.25 +
        norm(summary["ast"])     * 0.20 +
        norm(summary["reb"])     * 0.15 +
        norm(summary["fg_pct"])  * 0.10
    )

    # ── DPOY ─────────────────────────────────────────────────────────────────
    # Weighted score: BPG 40%, SPG 40%, RPG 20%
    summary["dpoy_score"] = (
        norm(summary["blk"]) * 0.40 +
        norm(summary["stl"]) * 0.40 +
        norm(summary["reb"]) * 0.20
    )

    mvp_row  = summary.loc[summary["mvp_score"].idxmax()]
    dpoy_row = summary.loc[summary["dpoy_score"].idxmax()]

    # ── MVP card ─────────────────────────────────────────────────────────────
    st.markdown("## 🏆 Most Valuable Player")
    st.markdown(f"### {mvp_row['player']}")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("PPG",   round(mvp_row["pts"], 1))
    c2.metric("APG",   round(mvp_row["ast"], 1))
    c3.metric("RPG",   round(mvp_row["reb"], 1))
    c4.metric("Win%",  f"{round(mvp_row['win_pct'] * 100, 1)}%")
    c5.metric("FG%",   f"{mvp_row['fg_pct']}%")
    st.caption(f"{int(mvp_row['games'])} games played · {int(mvp_row['wins'])}W / {int(mvp_row['games'] - mvp_row['wins'])}L")

    st.divider()

    # ── DPOY card ─────────────────────────────────────────────────────────────
    st.markdown("## 🛡️ Defensive Player of the Year")
    st.markdown(f"### {dpoy_row['player']}")
    d1, d2, d3 = st.columns(3)
    d1.metric("BPG",  round(dpoy_row["blk"], 1))
    d2.metric("SPG",  round(dpoy_row["stl"], 1))
    d3.metric("RPG",  round(dpoy_row["reb"], 1))
    st.caption(f"{int(dpoy_row['games'])} games played")

    st.divider()

    # ── Full standings ────────────────────────────────────────────────────────
    st.subheader("MVP standings")
    mvp_table = summary.sort_values("mvp_score", ascending=False).reset_index(drop=True)
    mvp_table.index += 1
    st.dataframe(mvp_table[[
        "player", "games", "pts", "ast", "reb", "win_pct", "fg_pct", "mvp_score"
    ]].rename(columns={
        "player":    "Player",
        "games":     "GP",
        "pts":       "PPG",
        "ast":       "APG",
        "reb":       "RPG",
        "win_pct":   "Win%",
        "fg_pct":    "FG%",
        "mvp_score": "Score",
    }).assign(**{
        "PPG":   lambda x: x["PPG"].round(1),
        "APG":   lambda x: x["APG"].round(1),
        "RPG":   lambda x: x["RPG"].round(1),
        "Win%":  lambda x: (x["Win%"] * 100).round(1).astype(str) + "%",
        "Score": lambda x: x["Score"].round(3),
    }), use_container_width=True)

    st.subheader("DPOY standings")
    dpoy_table = summary.sort_values("dpoy_score", ascending=False).reset_index(drop=True)
    dpoy_table.index += 1
    st.dataframe(dpoy_table[[
        "player", "games", "blk", "stl", "reb", "dpoy_score"
    ]].rename(columns={
        "player":     "Player",
        "games":      "GP",
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
