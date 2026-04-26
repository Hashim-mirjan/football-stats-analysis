import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

from src.data import fetch_data

st.set_page_config(
    page_title="Attacking Dashboard | PL Intelligence",
    page_icon="📊",
    layout="wide",
)

# ---------- Shared styling ----------
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
            background-color: rgba(20, 22, 27, 0.78);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        h1, h2, h3, h4, h5, h6 {
            color: rgba(255,255,255,0.92) !important;
        }

        .page-hero {
            padding: 2.2rem 2rem 1.8rem 2rem;
            border-radius: 28px;
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 20px 60px rgba(0,0,0,0.25);
            margin-bottom: 1.4rem;
        }

        .eyebrow {
            color: #9fb4ff;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.65rem;
        }

        .page-hero h1 {
            font-size: 2.65rem;
            line-height: 1.05;
            margin-bottom: 0.75rem;
        }

        .page-hero p {
            max-width: 860px;
            color: rgba(255,255,255,0.66);
            font-size: 1.04rem;
            line-height: 1.65;
            margin-bottom: 0;
        }

        .metric-card {
            padding: 1.05rem 1.2rem;
            border-radius: 20px;
            background: rgba(255,255,255,0.055);
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 12px 28px rgba(0,0,0,0.16);
        }

        .metric-label {
            color: rgba(255,255,255,0.52);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .metric-value {
            color: rgba(255,255,255,0.93);
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1.15;
        }

        .metric-sub {
            color: rgba(255,255,255,0.50);
            font-size: 0.86rem;
            margin-top: 0.3rem;
        }

        .chart-card {
            padding: 1.1rem 1.1rem 0.6rem 1.1rem;
            border-radius: 24px;
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 14px 35px rgba(0,0,0,0.18);
            margin-bottom: 1.2rem;
        }

        .section-title {
            color: rgba(255,255,255,0.88);
            font-size: 1.15rem;
            font-weight: 800;
            margin-bottom: 0.15rem;
        }

        .section-caption {
            color: rgba(255,255,255,0.52);
            font-size: 0.92rem;
            line-height: 1.45;
            margin-bottom: 0.85rem;
        }

        .stRadio label, .stMultiSelect label, .stSlider label {
            color: rgba(255,255,255,0.78) !important;
            font-weight: 650;
        }

        div[data-testid="stPageLink"] a {
            background: rgba(159,180,255,0.12);
            border: 1px solid rgba(159,180,255,0.24);
            border-radius: 14px;
            padding: 0.62rem 0.9rem;
            color: rgba(255,255,255,0.90) !important;
            font-weight: 700;
            text-decoration: none;
        }

        div[data-testid="stPageLink"] a:hover {
            background: rgba(159,180,255,0.22);
            border-color: rgba(159,180,255,0.42);
        }

        div[data-testid="stSidebarNav"] a {
            background: rgba(200,200,255,0.75);
            border: 1px solid rgba(159,180,255,0.28);
            border-radius: 5px;
        }

        html, body, [class*="css"]  {
        color: rgba(255,255,255,0.9) !important;
        }
    """,
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner=False)
def load_league_data(year: str) -> pd.DataFrame:
    return fetch_data(year)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("---")
    st.markdown("### Analysis filters")

    season_year = st.radio("Season", ["2024", "2025"], index=1)
    leaguedata = load_league_data(season_year)

    t_min = int(np.nanmin(leaguedata["time"])) if leaguedata["time"].notna().any() else 0
    t_max = int(np.nanmax(leaguedata["time"])) if leaguedata["time"].notna().any() else 3000
    default_min = max(t_min, min(int(0.6 * t_max), t_max))

    min_minutes = st.slider(
        "Minimum minutes played",
        min_value=t_min,
        max_value=t_max,
        value=default_min,
        step=30,
    )

    positions = sorted(leaguedata["main_position"].dropna().unique().tolist())
    default_positions = [p for p in ["Forward", "Midfielder"] if p in positions]
    sel_positions = st.multiselect("Positions", positions, default=default_positions)

    teams = sorted(leaguedata["current_team"].dropna().unique().tolist())
    sel_teams = st.multiselect("Team", teams, default=teams)

mask = (
    leaguedata["time"].notna()
    & (leaguedata["time"] >= min_minutes)
    & (leaguedata["main_position"].isin(sel_positions))
    & (leaguedata["current_team"].isin(sel_teams))
)
df = leaguedata.loc[mask].copy()

# ---------- Hero ----------
st.markdown(
    """
    <section class="page-hero">
        <div class="eyebrow">League-wide attacking view</div>
        <h1>Attacking Dashboard</h1>
        <p>
            Identify shot-volume threats, high-quality chance takers, creative players and xG over/underperformers.
            Use the filters to focus the analysis by season, position, team and minutes played.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

if df.empty:
    st.warning("No players match the selected filters. Try lowering the minutes threshold or broadening the position/team filters.")
    st.stop()

# ---------- KPI cards ----------
df["xG_diff"] = df["goals"] - df["xG"]
players_count = len(df)
teams_count = df["current_team"].nunique()
top_xg = df.sort_values("xG", ascending=False).iloc[0]
top_xa = df.sort_values("xA", ascending=False).iloc[0]

kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
with kpi1:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Players in view</div><div class="metric-value">{players_count}</div><div class="metric-sub">Across {teams_count} teams</div></div>""", unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Top xG</div><div class="metric-value">{top_xg['player_name']}</div><div class="metric-sub">{top_xg['xG']:.2f} expected goals</div></div>""", unsafe_allow_html=True)
with kpi3:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Top xA</div><div class="metric-value">{top_xa['player_name']}</div><div class="metric-sub">{top_xa['xA']:.2f} expected assists</div></div>""", unsafe_allow_html=True)
with kpi4:
    xg_leader = df.sort_values("xG_diff", ascending=False).iloc[0]
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Biggest xG overperformer</div><div class="metric-value">{xg_leader['player_name']}</div><div class="metric-sub">Goals - xG: {xg_leader['xG_diff']:.1f}</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------- Charts ----------
def scatter_shotsvsxG(df, x="shots_per90", y="xG_per_shot", title="xG Per Shot vs Shots Taken Per 90"):
    pos_colors = {
        "Goalkeeper": "#6b7280",
        "Defender": "#2e8467",
        "Midfielder": "#3b5070",
        "Forward": "#aa4242",
    }

    xlim = df[x].max() * 0.5 if df[x].notna().any() else 0
    ylim = df[y].max() * 0.5 if df[y].notna().any() else 0
    label_mask = (df[x] >= xlim) | (df[y] >= ylim)
    labels = np.where(label_mask, df["last_name"], None)

    fig = px.scatter(
        df,
        x=x,
        y=y,
        hover_name="player_name",
        color="main_position",
        color_discrete_map=pos_colors,
        title=title,
        height=430,
        text=labels,
    )

    fig.update_layout(
        template="plotly_dark",
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.68)"),
        title=dict(font=dict(size=18, color="rgba(255,255,255,0.78)"), x=0.02, xanchor="left"),
        margin=dict(l=10, r=10, t=52, b=10),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.09)", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.09)", zeroline=False),
    )
    fig.update_traces(textposition="top center", marker=dict(size=9, opacity=0.82, line=dict(width=0)))
    return fig


def top10_bar(df, metric="xG_diff", title="xG Over and Underperformers (Goals - xG)"):
    num_players = len(df)
    top10 = df.sort_values(by=metric, ascending=False).head(min(10, num_players // 2 + num_players % 2))
    bottom10 = df.sort_values(by=metric, ascending=True).head(min(10, num_players // 2)).iloc[::-1]
    plot_df = pd.concat([top10, bottom10]).copy()
    plot_df[metric] = plot_df[metric].round(1)

    fig = px.bar(
        plot_df,
        x=metric,
        y="player_name",
        orientation="h",
        text=metric,
        title=title,
        height=880,
    )

    fig.update_traces(marker_line_width=0, textposition="outside")
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.68)"),
        title=dict(font=dict(size=18, color="rgba(255,255,255,0.78)"), x=0.02, xanchor="left"),
        margin=dict(l=10, r=10, t=52, b=10),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.09)", zeroline=True, zerolinecolor="rgba(255,255,255,0.22)"),
        yaxis=dict(showgrid=False),
    )
    return fig

left_col, right_col = st.columns([3, 2], gap="large")

with left_col:
    st.markdown('<div class="chart-card"><div class="section-title">Shot volume vs shot quality</div><div class="section-caption">Top-right players combine frequent shooting with strong average chance quality.</div>', unsafe_allow_html=True)
    st.plotly_chart(scatter_shotsvsxG(df, "shots_per90", "xG_per_shot", "xG Per Shot vs Shots Taken Per 90"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="section-title">Finishing threat vs creativity</div><div class="section-caption">Use this to separate pure finishers, creators and dual-threat attackers.</div>', unsafe_allow_html=True)
    st.plotly_chart(scatter_shotsvsxG(df, "xG_per90", "xA_per90", "xA Per 90 vs xG Per 90"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="chart-card"><div class="section-title">Performance against xG</div><div class="section-caption">Positive values indicate finishing above expected goals; negative values suggest underperformance.</div>', unsafe_allow_html=True)
    st.plotly_chart(top10_bar(df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
