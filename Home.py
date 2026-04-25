import streamlit as st

st.set_page_config(
    page_title="PL Attacking Intelligence",
    page_icon="⚽",
    layout="wide",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(90, 110, 160, 0.20), transparent 30%),
                linear-gradient(135deg, #25272d 0%, #303339 45%, #1f2228 100%);
            color: rgba(255,255,255,0.86);
        }

        [data-testid="stSidebar"] {
            background-color: rgba(20, 22, 27, 0.75);
        }

        .hero {
            padding: 3.5rem 2rem 2rem 2rem;
            border-radius: 28px;
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 20px 60px rgba(0,0,0,0.25);
            margin-bottom: 2rem;
        }

        .eyebrow {
            color: #9fb4ff;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.8rem;
        }

        .hero h1 {
            color: rgba(255,255,255,0.94) !important;
            font-size: 3.1rem;
            line-height: 1.05;
            margin-bottom: 1rem;
        }

        .hero p {
            max-width: 820px;
            color: rgba(255,255,255,0.68);
            font-size: 1.12rem;
            line-height: 1.7;
        }

        .feature-card {
            min-height: 260px;
            padding: 1.6rem;
            border-radius: 24px;
            background: rgba(255,255,255,0.055);
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 14px 35px rgba(0,0,0,0.20);
        }

        .feature-card h2 {
            color: rgba(255,255,255,0.90) !important;
            margin-bottom: 0.65rem;
            font-size: 1.45rem;
        }

        .feature-card p {
            color: rgba(255,255,255,0.65);
            line-height: 1.55;
            margin-bottom: 1.2rem;
        }

        .pill {
            display: inline-block;
            margin: 0.2rem 0.25rem 0.2rem 0;
            padding: 0.35rem 0.65rem;
            border-radius: 999px;
            background: rgba(159,180,255,0.12);
            border: 1px solid rgba(159,180,255,0.22);
            color: rgba(255,255,255,0.76);
            font-size: 0.82rem;
        }

        div[data-testid="stPageLink"] a {
            background: rgba(180,180,255,0.4);
            border: 1px solid rgba(159,180,255,0.28);
            border-radius: 14px;
            padding: 0.75rem 1rem;
            color: rgba(255,255,255,0.92) !important;
            font-weight: 700;
            text-decoration: none;
        }

        div[data-testid="stPageLink"] a:hover {
            background: rgba(159,180,255,0.24);
            border-color: rgba(159,180,255,0.45);
        }

        .footer-note {
            color: rgba(255,255,255,0.45);
            margin-top: 2rem;
            font-size: 0.95rem;
        }

        div[data-testid="stSidebarNav"] a {
            background: rgba(200,200,255,0.75);
            border: 1px solid rgba(159,180,255,0.28);
            border-radius: 5px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------


# ---------- Landing page ----------
st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">Premier League analytics</div>
        <h1>Attacking intelligence for player analysis.</h1>
        <p>
            Explore Premier League attacking output through xG, xA, shot quality,
            player comparison and performance trends. Choose a module below to start analysing.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(
        """
        <div class="feature-card">
            <h2>Attacking Dashboard</h2>
            <p>
                Explore league-wide attacking patterns using scatter plots, xG/xA views,
                shot quality and over/underperformance against expected goals.
            </p>
            <span class="pill">xG vs xA</span>
            <span class="pill">Shot quality</span>
            <span class="pill">Overperformance</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Attacking_Dashboard.py", label="Open Attacking Dashboard", icon="📊")

with col2:
    st.markdown(
        """
        <div class="feature-card">
            <h2>Player Comparison</h2>
            <p>
                Compare two players directly using KPI tables, normalised radar scores
                and recent goal output for their current team.
            </p>
            <span class="pill">Radar chart</span>
            <span class="pill">KPI table</span>
            <span class="pill">Last 5 games</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Player_Comparison.py", label="Open Player Comparison", icon="🆚")

