import streamlit as st
import pandas as pd
import plotly.express as px

st.title("All-Time Records")
st.caption("Full league history — including sessions before stat tracking began.")

# ── All-time leaderboard (manual from Buckhurst_Egoist_League_Leaderboard.xlsx) ──
records = [
    {"Player": "Borgers Rodriguez",  "GP": 30, "W": 18, "L": 12, "Yen": 180_000_000},
    {"Player": "Ningwa Limbu",       "GP": 30, "W": 14, "L": 16, "Yen": 140_000_000},
    {"Player": "Nathan Cabral",      "GP": 24, "W": 13, "L": 11, "Yen": 130_000_000},
    {"Player": "Kanetho Sequira",    "GP": 21, "W": 13, "L":  8, "Yen": 130_000_000},
    {"Player": "Renick Fernandes",   "GP": 23, "W":  9, "L": 14, "Yen":  90_000_000},
    {"Player": "Clinton Camelo",     "GP": 15, "W":  8, "L":  7, "Yen":  80_000_000},
    {"Player": "Ashwin Rai",         "GP": 16, "W":  7, "L":  9, "Yen":  70_000_000},
    {"Player": "Mahdi Miah",         "GP": 21, "W":  7, "L": 14, "Yen":  70_000_000},
    {"Player": "Cameron",            "GP": 11, "W":  4, "L":  7, "Yen":  40_000_000},
    {"Player": "Savio Da Costa",     "GP":  4, "W":  2, "L":  2, "Yen":  20_000_000},
]

df = pd.DataFrame(records)
df["Win%"] = (df["W"] / df["GP"] * 100).round(1)
df = df.sort_values("Win%", ascending=False).reset_index(drop=True)
df.index += 1

# ── Session history (W-L per session per player) ──────────────────────────────
# Scores read directly from Excel via openpyxl (date-formatted cells decoded as M-D = wins-losses)
sessions_raw = {
    "Player":      ["Mahdi", "Ningwa", "Borgers", "Nathan", "Kanetho", "Renick", "Ashwin", "Clinton", "Savio", "Cameron", "Aben", "Pter", "Oliver", "Paras", "Tristan"],
    "29/05/26":    ["3-3",  "2-4",  "4-2",  "3-3",  "5-1",  "1-5",  None,   None,   None,   None,   None,   None,   None,   None,   None],
    "09/06/26":    ["1-3",  "4-0",  "2-2",  "0-4",  None,   "3-1",  "0-4",  "4-0",  "2-2",  None,   None,   None,   None,   None,   None],
    "14/06/26":    ["1-4",  "3-2",  "1-4",  "4-1",  None,   None,   "3-2",  "1-4",  None,   "3-2",  "3-2",  "2-0",  None,   None,   None],
    "13/06":       [None,   "1-3",  "3-1",  None,   "2-2",  "2-2",  None,   "3-1",  None,   "1-3",  None,   None,   None,   None,   None],
    "15/06":       ["2-2",  "1-3",  "3-1",  "3-1",  "2-2",  "1-3",  None,   None,   None,   None,   None,   "0-1",  "1-0",  None,   None],
    "18/06/26":    [None,   "3-2",  "3-2",  "3-2",  "2-3",  "2-3",  "2-3",  None,   None,   None,   None,   None,   None,   "1-0",  "1-2"],
    "22/06/26":    ["0-2",  "0-2",  "2-0",  None,   "2-0",  None,   "2-0",  "0-2",  None,   "0-2",  None,   None,   None,   None,   None],
}
sessions_df = pd.DataFrame(sessions_raw).set_index("Player")

# ── Top section: rank cards ───────────────────────────────────────────────────
st.subheader("Win % ranking — all time")

medals = {1: "🥇", 2: "🥈", 3: "🥉"}
cols = st.columns(3)
for i, row in df.head(3).iterrows():
    with cols[i - 1]:
        st.markdown(f"### {medals[i]} {row['Player']}")
        st.metric("Win%", f"{row['Win%']}%")
        st.caption(f"{row['GP']} GP · {row['W']}W · {row['L']}L")

st.divider()

# ── Bar chart ─────────────────────────────────────────────────────────────────
fig = px.bar(
    df.sort_values("Win%"),
    x="Win%",
    y="Player",
    orientation="h",
    text="Win%",
    color="Win%",
    color_continuous_scale=["#d94f4f", "#e07b39", "#5a9e6f"],
    range_color=[30, 70],
    labels={"Win%": "Win %", "Player": ""},
)
fig.update_traces(texttemplate="%{text}%", textposition="outside")
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="#888",
    coloraxis_showscale=False,
    xaxis=dict(range=[0, 80], gridcolor="rgba(128,128,128,0.15)"),
    yaxis=dict(showgrid=False),
    height=380,
    margin=dict(r=60),
)
st.plotly_chart(fig, use_container_width=True)

# ── Full table ────────────────────────────────────────────────────────────────
st.subheader("Full standings")
display_df = df.copy()
display_df["Yen Valuation"] = display_df["Yen"].apply(lambda x: f"¥{x:,.0f}")
st.dataframe(display_df[["Player", "GP", "W", "L", "Win%", "Yen Valuation"]],
             use_container_width=True)

st.divider()

# ── Yen valuation ─────────────────────────────────────────────────────────────
st.subheader("Yen valuation")
st.caption("Player market value as tracked in the league spreadsheet.")
yen_df = df.sort_values("Yen", ascending=False).reset_index(drop=True)
fig_yen = px.bar(
    yen_df.sort_values("Yen"),
    x="Yen",
    y="Player",
    orientation="h",
    text="Yen",
    color="Yen",
    color_continuous_scale=["#3266ad", "#a855b5"],
    labels={"Yen": "Yen Valuation", "Player": ""},
)
fig_yen.update_traces(
    texttemplate=[f"¥{v:,.0f}" for v in yen_df.sort_values("Yen")["Yen"]],
    textposition="outside",
)
fig_yen.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="#888",
    coloraxis_showscale=False,
    xaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
    yaxis=dict(showgrid=False),
    height=380,
    margin=dict(r=120),
)
st.plotly_chart(fig_yen, use_container_width=True)

st.divider()

# ── Session history table ─────────────────────────────────────────────────────
st.subheader("Session history")
st.caption("W-L record per session. Blank = did not play.")
st.dataframe(sessions_df.fillna("—"), use_container_width=True)
