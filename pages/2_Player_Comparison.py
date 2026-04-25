import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from src.data import fetch_data, get_player_id, fetch_player_shot_data, fetch_team_match_data

st.set_page_config(
    page_title="Player Comparison | PL Intelligence",
    page_icon="🆚",
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
            max-width: 900px;
            color: rgba(255,255,255,0.66);
            font-size: 1.04rem;
            line-height: 1.65;
            margin-bottom: 0;
        }

        .selector-card, .chart-card {
            padding: 1.15rem;
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

        .comparison-pill {
            display: inline-block;
            padding: 0.45rem 0.75rem;
            border-radius: 999px;
            background: rgba(159,180,255,0.12);
            border: 1px solid rgba(159,180,255,0.22);
            color: rgba(255,255,255,0.78);
            font-size: 0.86rem;
            margin-right: 0.35rem;
            margin-bottom: 0.4rem;
        }

        .stSelectbox label {
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
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("---")
    st.markdown("### Module notes")
    st.caption("Radar values are normalised from 0–5 against all non-goalkeepers in the selected season.")

# ---------- Data loading ----------
@st.cache_data(show_spinner=False)
def load_league_data(year: str) -> pd.DataFrame:
    return fetch_data(year)

leaguedata = load_league_data("2025")
leaguedata = leaguedata.loc[leaguedata["main_position"] != "Goalkeeper"].copy()
players = sorted(leaguedata["player_name"].dropna().unique().tolist())

# ---------- Hero ----------
st.markdown(
    """
    <section class="page-hero">
        <div class="eyebrow">Head-to-head player analysis</div>
        <h1>Player Comparison</h1>
        <p>
            Compare two Premier League players using headline output, expected metrics, recent goals and a normalised radar profile.
            This page is designed for fast scouting-style comparisons.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

# ---------- Helpers ----------
def goals_last_5(player_shots: pd.DataFrame, team_matches: pd.DataFrame) -> float:
    tm = team_matches.copy()
    if not {"id", "date"}.issubset(tm.columns):
        raise ValueError("team_matches must have columns: 'id' and 'date'")

    tm["date"] = pd.to_datetime(tm["date"], errors="coerce")
    if "forecast" in tm.columns:
        tm = tm[tm["forecast"].notna()].copy()

    last5_ids = (
        tm.sort_values("date", ascending=False)
        .drop_duplicates(subset="id", keep="first")
        .head(5)["id"]
        .tolist()
    )

    if len(last5_ids) < 5:
        return np.nan

    ps = player_shots.copy()
    if "date" not in ps:
        raise ValueError("Expected a 'date' column in player_shots")

    ps["date"] = pd.to_datetime(ps["date"], errors="coerce")

    if "is_goal" not in ps:
        if "result" in ps:
            ps["is_goal"] = ps["result"].astype(str).str.lower().eq("goal").astype(int)
        else:
            raise ValueError("Need either 'is_goal' or 'result' column")

    if "match_id" not in ps:
        raise ValueError("Expected a 'match_id' column to group by matches")

    per_match = (
        ps.groupby("match_id")
        .agg(goals=("is_goal", "sum"), match_date=("date", "max"))
        .sort_values("match_date")
    )

    return int(per_match["goals"].reindex(last5_ids).fillna(0).sum())


def build_player_context(player_name: str):
    if not player_name:
        return None

    player_id = get_player_id(leaguedata, player_name)
    stats = leaguedata[leaguedata["id"] == player_id]
    team = stats["current_team"].values[0]
    shots = fetch_player_shot_data(player_id)
    team_matches = fetch_team_match_data(team, 2025)

    if shots.empty:
        last5 = np.nan
    else:
        last5 = goals_last_5(shots, team_matches)

    return {
        "id": player_id,
        "name": stats["player_name"].values[0],
        "team": team,
        "stats": stats,
        "last5": last5,
    }


def player_kpi(ctx: dict) -> pd.DataFrame:
    stats = ctx["stats"]
    last5 = ctx["last5"]
    return pd.DataFrame({
        "Goals": [stats["goals"].values[0]],
        "Assists": [stats["assists"].values[0]],
        "xG": [round(stats["xG"].values[0], 2)],
        "xA": [round(stats["xA"].values[0], 2)],
        "Goals Last 5 Games (Current Team)": ["N/A" if pd.isna(last5) else int(last5)],
        "Minutes Played": [stats["time"].values[0]],
        "xG/90": [round(stats["xG_per90"].values[0], 2)],
        "xA/90": [round(stats["xA_per90"].values[0], 2)],
    })

# ---------- Selectors ----------
st.markdown('<div class="selector-card"><div class="section-title">Choose two players</div><div class="section-caption">Select any two outfield players from the 2025 Premier League dataset.</div>', unsafe_allow_html=True)
left_select, right_select = st.columns([1, 1], gap="large")
with left_select:
    player1_name = st.selectbox("Select Player 1", players, index=None, placeholder="Player")
with right_select:
    player2_name = st.selectbox("Select Player 2", players, index=None, placeholder="Player")
st.markdown('</div>', unsafe_allow_html=True)

player1_ctx = build_player_context(player1_name) if player1_name else None
player2_ctx = build_player_context(player2_name) if player2_name else None

if player1_ctx and player2_ctx:
    st.markdown(
        f"""
        <span class="comparison-pill">{player1_ctx['name']} · {player1_ctx['team']}</span>
        <span class="comparison-pill">{player2_ctx['name']} · {player2_ctx['team']}</span>
        """,
        unsafe_allow_html=True,
    )

# ---------- KPI table ----------
radar_labels = ["Goals", "Assists", "xG", "xA", "xG/90", "xA/90"]
label_to_col = {
    "Goals": "goals",
    "Assists": "assists",
    "xG": "xG",
    "xA": "xA",
    "xG/90": "xG_per90",
    "xA/90": "xA_per90",
}

mins = pd.Series({lbl: pd.to_numeric(leaguedata[label_to_col[lbl]], errors="coerce").min() for lbl in radar_labels})
maxs = pd.Series({lbl: pd.to_numeric(leaguedata[label_to_col[lbl]], errors="coerce").max() for lbl in radar_labels})
denom = (maxs - mins).replace(0, np.nan)
SCALE = 5


def percentile_vals(player_stats_row: pd.Series, reference_df: pd.DataFrame) -> list[float]:
    vals = []

    for lbl in radar_labels:
        col = label_to_col[lbl]

        reference = pd.to_numeric(reference_df[col], errors="coerce").dropna()
        player_value = float(player_stats_row[col])

        percentile = (reference < player_value).mean() * 100
        vals.append(round(percentile, 1))

    return vals

col_radar, col_table = st.columns([3, 2], gap="large")

with col_radar:
    st.markdown('<div class="chart-card"><div class="section-title">Radar profile</div><div class="section-caption">Each stat is presented as a percentile across all league players.</div>', unsafe_allow_html=True)
    if player1_ctx and player2_ctx:
        p1_vals = percentile_vals(player1_ctx["stats"].squeeze(), leaguedata)
        p2_vals = percentile_vals(player2_ctx["stats"].squeeze(), leaguedata)

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=p1_vals, theta=radar_labels, fill="toself", name=player1_ctx["name"]))
        fig.add_trace(go.Scatterpolar(r=p2_vals, theta=radar_labels, fill="toself", name=player2_ctx["name"]))
        fig.update_layout(
            template="plotly_dark",
            showlegend=True,
            margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.68)"),
            legend=dict(
                title=dict(text="Players", font=dict(color="rgba(255,255,255,0.64)")),
                font=dict(color="rgba(255,255,255,0.68)")
            ),
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickvals=[0, 25, 50, 75, 100]
                )
            ),
            height=560
            )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select two players to compare.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_table:
    st.markdown('<div class="chart-card"><div class="section-title">Key Stats</div></div>',unsafe_allow_html=True)
    if player1_ctx and player2_ctx:
        player1_kpi = player_kpi(player1_ctx)
        player2_kpi = player_kpi(player2_ctx)
        comparison_df = pd.concat([player1_kpi, player2_kpi], axis=0)

        p1_name = player1_ctx["name"]
        p2_name = player2_ctx["name"] if player2_ctx["name"] != p1_name else f"{player2_ctx['name']} (2)"
        comparison_df.index = [p1_name, p2_name]

        tbl = comparison_df.T.reset_index().rename(columns={"index": "Stat"})

        fig = go.Figure(data=[go.Table(
            columnwidth=[1.4, 1, 1],

            header=dict(
                values=[
                    "<b>Metric</b>",
                    f"<b>{p1_name}</b>",
                    f"<b>{p2_name}</b>",
                ],
                fill_color="rgba(255,255,255,0.06)",
                font=dict(color="white", size=17),
                align=["left", "center", "center"],
                height=46,
                line=dict(width=0)
            ),

            cells=dict(
                values=[tbl[c] for c in tbl.columns],
                fill_color=[
                    ["rgba(255,255,255,0.06)" if i % 2 == 0 else "rgba(255,255,255,0.02)" for i in range(len(tbl))],
                    ["rgba(255,255,255,0.02)"] * len(tbl),
                    ["rgba(255,255,255,0.02)"] * len(tbl),
                ],
                font=dict(color="rgba(255,255,255,0.76)", size=14),
                align=["left", "center", "center"],
                height=46,
                line=dict(width=0)
            ),
        )])

        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",margin=dict(l=0, r=0, t=4, b=0),height=520)
        fig.data[0].cells.line.color = "rgba(255,255,255,0.11)"
        fig.data[0].header.line.color = "rgba(255,255,255,0.18)"
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Select two players to compare.")
    st.markdown('</div>', unsafe_allow_html=True)

