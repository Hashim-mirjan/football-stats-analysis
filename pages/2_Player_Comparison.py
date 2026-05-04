import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

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
            background-color: rgba(120,160,230, 0.8);
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
        .stRadio label,
        .stMultiSelect label,
        .stSlider label,
        .stSelectbox label {
            color: rgba(255,255,255,0.78) !important;
            font-weight: 650;
        }
        .stRadio div[role="radiogroup"] label p {
            color: rgba(255,255,255,0.85) !important;
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
    else:
        last5_ids = pd.DataFrame(last5_ids, columns=["match_id"])

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
        .reset_index()
        .sort_values("match_date")
    )

    last5 = last5_ids.merge(per_match)

    return int(sum(last5["goals"])) if not last5.empty else np.nan



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
        "shots" : shots,
    }


def player_kpi(ctx: dict) -> pd.DataFrame:
    stats = ctx["stats"]
    last5 = ctx["last5"]
    return pd.DataFrame({
        "Goals": [int(stats["goals"].values[0])],
        "Assists": [int(stats["assists"].values[0])],
        "Goals (non-penalty)": [int(stats["npg"].values[0])],
        "xG": [round(stats["xG"].values[0], 2)],
        "xA": [round(stats["xA"].values[0], 2)],
        "Goals Last 5 Games (Current Team)": ["N/A" if pd.isna(last5) else int(last5)],
        "Minutes Played": [int(stats["time"].values[0])],
        "xG/90": [round(stats["xG_per90"].values[0], 2)],
        "xA/90": [round(stats["xA_per90"].values[0], 2)],
        "KP/90": [round(stats["KP_per90"].values[0], 2)]
    })


def create_shot_map(shots: pd.DataFrame, time_window: str = "All time"):
    if shots.empty:
        return None

    pitch_length = 95
    pitch_width = 60

    shots = shots.copy()
    shots["date"] = pd.to_datetime(shots["date"], errors="coerce")

    if time_window == "Last 6 months":
        cutoff_date = pd.Timestamp.today() - pd.DateOffset(months=6)
        shots = shots[shots["date"] >= cutoff_date].copy()

    elif time_window == "Last 12 months":
        cutoff_date = pd.Timestamp.today() - pd.DateOffset(months=12)
        shots = shots[shots["date"] >= cutoff_date].copy()
    
    if shot_type == "Open play":
        shots = shots[shots["situation"] == "OpenPlay"].copy()

    if shots.empty:
        return None

    shots["open/set play"] = np.where(
        shots["situation"].isin(["DirectFreekick", "Penalty"]),
        "set-piece",
        "open-play"
    )

    shotsmap = shots.copy()
    shotsmap["x"] = shotsmap["X"] * pitch_length
    shotsmap["y"] = pitch_width - shotsmap["Y"] * pitch_width

    fig = px.scatter(
        shotsmap,
        x="y",
        y="x",
        size="xG",
        size_max=10,
        hover_data=["xG", "shotType", "minute", "date"],
    )

    fig.update_xaxes(range=[0, 60])
    fig.update_yaxes(range=[60, 95], scaleanchor="x", scaleratio=1)

    box_depth = 16.5
    box_width = 40.3
    box_left = (pitch_width - box_width) / 2
    box_right = (pitch_width + box_width) / 2

    fig.add_shape(
        type="rect",
        x0=box_left,
        x1=box_right,
        y0=pitch_length - box_depth,
        y1=pitch_length,
        line=dict(color="white", width=2)
    )

    six_yard_depth = 5.5
    six_yard_width = 18.3
    six_left = (pitch_width - six_yard_width) / 2
    six_right = (pitch_width + six_yard_width) / 2

    fig.add_shape(
        type="rect",
        x0=six_left,
        x1=six_right,
        y0=pitch_length - six_yard_depth,
        y1=pitch_length,
        line=dict(color="white", width=2)
    )

    penalty_spot_x = pitch_width / 2
    penalty_spot_y = pitch_length - 11
    arc_radius = 9.15

    theta = np.linspace(0, 2 * np.pi, 300)
    arc_x = penalty_spot_x + arc_radius * np.cos(theta)
    arc_y = penalty_spot_y + arc_radius * np.sin(theta)

    box_line_y = pitch_length - 16.5
    mask = arc_y < box_line_y

    fig.add_trace(
        go.Scatter(
            x=arc_x[mask],
            y=arc_y[mask],
            mode="lines",
            line=dict(color="white", width=2),
            showlegend=False,
            hoverinfo="skip"
        )
    )

    fig.update_layout(
        width=420,
        height=350,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False,
        xaxis_title=None,
        yaxis_title=None,
        )
    
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False, visible=False)

    fig.update_yaxes(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        visible=False,
        scaleanchor="x",
        scaleratio=1
    )

    fig.add_shape(
        type="rect",
        x0=0,
        x1=pitch_width,
        y0=60,
        y1=pitch_length,
        line=dict(color="white", width=2)
    )


    return fig

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

# ---------- Stats table & Radar chart ----------
radar_labels = ["Goals", "Assists", "xG", "xA", "xG/90", "xA/90"]
label_to_col = {
    "Goals": "goals",
    "Assists": "assists",
    "Goals (non-penalty)": "npg",
    "xG": "xG",
    "xA": "xA",
    "xG/90": "xG_per90",
    "xA/90": "xA_per90",
    "KP/90": "KP_per90",
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
    st.markdown("<div style='height: 2.0rem;'></div>", unsafe_allow_html=True)
    if player1_ctx and player2_ctx:
        player1_kpi = player_kpi(player1_ctx)
        player2_kpi = player_kpi(player2_ctx)
        comparison_df = pd.concat([player1_kpi, player2_kpi], axis=0)

        p1_name = player1_ctx["name"]
        p2_name = player2_ctx["name"] if player2_ctx["name"] != p1_name else f"{player2_ctx['name']} (2)"
        comparison_df.index = [p1_name, p2_name]

        tbl = comparison_df.T.reset_index().rename(columns={"index": "Metric"})

        tbl = tbl[[p1_name, "Metric", p2_name]]

        int_metrics = [
            "Goals",
            "Assists",
            "Goals (non-penalty)",
            "Goals Last 5 Games (Current Team)",
            "Minutes Played"
        ]

        # Player 1 column
        tbl[p1_name] = [
            str(int(v)) if m in int_metrics else f"{float(v):.2f}"
            for m, v in zip(tbl["Metric"], tbl[p1_name])
        ]

        # Player 2 column
        tbl[p2_name] = [
            str(int(v)) if m in int_metrics else f"{float(v):.2f}"
            for m, v in zip(tbl["Metric"], tbl[p2_name])
        ]

        # fig = go.Figure(data=[go.Table(
        #     columnwidth=[1, 1.3, 1],

        #     header=dict(
        #         values=[
        #             f"{p1_name}",
        #             "",
        #             f"{p2_name}",
        #         ],
        #         fill_color="rgba(0,0,0,0)",   # no header background
        #         font=dict(color="white", size=15),
        #         align=["center", "center", "center"],
        #         height=40,
        #         line=dict(width=0)
        #     ),

        #     cells=dict(
        #         values=[tbl[c] for c in tbl.columns],
        #         fill_color="rgba(0,0,0,0)",
        #         font=dict(
        #             color=[
        #                 "rgba(255,255,255,0.90)",
        #                 "rgba(255,255,255,0.55)",
        #                 "rgba(255,255,255,0.90)",
        #             ],
        #             size=[16, 13, 16]
        #         ),
        #         align=["center", "center", "center"],
        #         height=52,
        #         line=dict(width=0)
        #     ),
        # )])

        # fig.update_layout(
        #     paper_bgcolor="rgba(0,0,0,0)",
        #     plot_bgcolor="rgba(0,0,0,0)",
        #     margin=dict(l=0, r=0, t=0, b=0),
        #     height=500
        # )

        # st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        rows_html = ""

        for _, row in tbl.iterrows():
            rows_html += f"""
            <div style="
                display:grid;
                grid-template-columns: 1fr 1.25fr 1fr;
                align-items:center;
                padding: 0.65rem 0;
                border-bottom: 1px solid rgba(255,255,255,0.18);
            ">
                <div style="text-align:center; color:rgba(255,255,255,0.92); font-size:1.18rem; font-weight:800;">
                    {row[p1_name]}
                </div>
                <div style="text-align:center; color:rgba(255,255,255,0.48); font-size:0.82rem; font-weight:800; letter-spacing:0.08em; text-transform:uppercase;">
                    {row["Metric"]}
                </div>
                <div style="text-align:center; color:rgba(255,255,255,0.92); font-size:1.18rem; font-weight:800;">
                    {row[p2_name]}
                </div>
            </div>
            """

        st.markdown(
            f"""
            <div style="padding: 0.7rem 0.2rem 0.2rem 0.2rem;">
                <div style="
                    display:grid;
                    grid-template-columns: 1fr 1.25fr 1fr;
                    align-items:center;
                    margin-bottom:0.75rem;
                ">
                    <div style="text-align:center; color:rgba(255,255,255,0.92); font-size:1rem; font-weight:850;">
                        {p1_name}
                    </div>
                    <div></div>
                    <div style="text-align:center; color:rgba(255,255,255,0.92); font-size:1rem; font-weight:850;">
                        {p2_name}
                    </div>
                </div>

                {rows_html}
            </div>
            """,
            unsafe_allow_html=True
        )


    else:
        st.info("Select two players to compare.")
    st.markdown('</div>', unsafe_allow_html=True)



radio_col1, radio_col2, radio_col3 = st.columns([3, 2, 3], gap="large")

with radio_col1:
    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    shot_time_window = st.radio(
        "Shot map time period",
        ["Last 6 months", "Last 12 months", "All time"],
        horizontal=True
    )

with radio_col2:
    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    shot_type = st.radio(
        "Shot type",
        ["All shots", "Open play"],
        horizontal=True
    )


# ---------- Shot maps ----------
shot_col1, shot_col2 = st.columns([1, 1], gap="large")

with shot_col1:
    
    if player1_ctx and player2_ctx:
        st.markdown(
        f'<div class="chart-card"><div class="section-title">{player1_ctx["name"]} Shot Map',
        unsafe_allow_html=True
        )

        fig1 = create_shot_map(player1_ctx["shots"],shot_time_window)

        if fig1 is not None:
            st.plotly_chart(fig1, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})
        else:
            st.info("No shot data available for this player.")
    else:
        st.info("Select Player 1 to view shot map.")

    st.markdown("</div>", unsafe_allow_html=True)

with shot_col2:
    

    if player2_ctx and player1_ctx:
        st.markdown(
        f'<div class="chart-card"><div class="section-title">{player2_ctx["name"]} Shot Map</div></div>',
        unsafe_allow_html=True
        )
        fig2 = create_shot_map(player2_ctx["shots"], shot_time_window)

        if fig2 is not None:
            st.plotly_chart(fig2, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})
            
        else:
            st.info("No shot data available for this player.")
    else:
        st.info("Select Player 2 to view shot map.")

    st.markdown("</div>", unsafe_allow_html=True)