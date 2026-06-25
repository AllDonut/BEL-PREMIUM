import streamlit as st

pg = st.navigation([
    st.Page("pages/logger.py",         title="Log Game",          icon="📝"),
    st.Page("pages/leaderboard.py",    title="Leaderboard",       icon="🏆"),
    st.Page("pages/player_profile.py", title="Player Profile",    icon="👤"),
    st.Page("pages/scatter.py",        title="Scatter",           icon="📊"),
    st.Page("pages/roles.py",          title="Role Contribution", icon="🎭"),
    st.Page("pages/composite.py",      title="Composite Score",   icon="⭐"),
    st.Page("pages/awards.py",         title="Awards",            icon="🏅"),
    st.Page("pages/all_time.py",       title="All-Time Records",  icon="📜"),
])
pg.run()
