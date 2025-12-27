# 2_Player_Comparison.py
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Player Comparison", layout="wide")

# ------ Styling --------------------------------------------

st.markdown(
    """
    <style>
        .stApp {
            background-color: #303339;  /* light gray-blue background */
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
        h1{
            color: rgba(255, 255, 255, 0.5) !important;
        }
        h2{
            color: rgba(255, 255, 255, 0.5) !important;
        }
        h3{
            color: rgba(255, 255, 255, 0.5) !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    /* Make all widget labels white */
    .stSlider label, .stMultiSelect label {
        color: rgba(255, 255, 255, 0.5) !important;
    }

    /* Also adjust general label text in case of other widgets */
    .stSelectbox label, .stDateInput label {
        color: rgba(255, 255, 255, 1) !important;
    }

    /* If you want the options text inside multiselect to be white too */
    .stMultiSelect div[data-baseweb="select"] span {
        color: rgba(255, 255, 255, 1) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Data loading --------------------------------------------

st.title("Player Comparison")

from src.data import fetch_data, get_player_id, fetch_player_shot_data, fetch_team_match_data

leaguedata = fetch_data(2024)
leaguedata = leaguedata.loc[leaguedata["main_position"] != "Goalkeeper"].copy()

# Example source
players = sorted(leaguedata["player_name"].dropna().unique().tolist())

# --- Main page ---------------------------------------------

left_col, right_col = st.columns([1, 1], gap="large")  # wider left, narrower right


def goals_last_5(player_shots: pd.DataFrame,
                 team_matches: pd.DataFrame) -> int:
    
    tm = team_matches.copy()
    if not {'id','date'}.issubset(tm.columns):
        raise ValueError("team_matches must have columns: 'id' and 'date'")

    tm['date'] = pd.to_datetime(tm['date'], errors='coerce')

    if "forecast" in tm.columns:
        tm = tm[tm["forecast"].notna()].copy()
                     
    last5_ids = (
        tm.sort_values('date', ascending=False)
          .drop_duplicates(subset='id', keep='first')
          .head(5)['id'] # last 5 unique match ids
          .tolist()
    )

    if not last5_ids:
        return np.nan # team has no matches

    if len(last5_ids) < 5:
        return np.nan  # Not enough matches to determine last 5

    ps = player_shots.copy()

    if "date" in ps:
        ps["date"] = pd.to_datetime(ps["date"], errors="coerce")
    else:
        raise ValueError("Expected a 'date' column in player_shots")

    # goal flag
    if "is_goal" not in ps:
        if "result" in ps:
            ps["is_goal"] = ps["result"].astype(str).str.lower().eq("goal").astype(int)
        else:
            raise ValueError("Need either 'is_goal' or 'result' column")

    if "match_id" not in ps:
        raise ValueError("Expected a 'match_id' column to group by matches")

    # Goals per match, ordered by match date
    per_match = (
        ps.groupby("match_id")
        .agg(goals=("is_goal", "sum"), match_date=("date", "max"))
        .sort_values("match_date")
    )

    # Keep only the team’s last-5 match ids; 0 if player didn't shoot in that match
    total_goals = int(per_match["goals"].reindex(last5_ids).fillna(0).sum())

    return total_goals


with left_col:
    player1 = st.selectbox(
        "Select Player 1",
        players,
        index=None,                    
        placeholder="Player"  
    )

    if player1:
        player1 = get_player_id(leaguedata, player1)
        player1team = leaguedata[leaguedata["id"] == player1]["current_team"].values[0]

        player1stats = leaguedata[leaguedata["id"] == player1]

        player1shots = fetch_player_shot_data(player1)
        player1team_matches = fetch_team_match_data(player1team)

        if player1shots.empty:
                st.info("No shots data.")
                player1last5 = np.nan
        else:   
            player1last5 = goals_last_5(player1shots, player1team_matches)

        


with right_col:
    player2 = st.selectbox(
        "Select Player 2 ",
        players,
        index=None,                        
        placeholder="Player"   
    )

    if player2:
        player2 = get_player_id(leaguedata, player2)
        player2team = leaguedata[leaguedata["id"] == player2]["current_team"].values[0]

        player2stats = leaguedata[leaguedata["id"] == player2]

        player2shots = fetch_player_shot_data(player2)
        player2team_matches = fetch_team_match_data(player2team)

        if player2shots.empty:
                st.info("No shots data.")
                player2last5 = np.nan
        else:
            player2last5 = goals_last_5(player2shots, player2team_matches)


if player1 and player2:
    player1KPI = pd.DataFrame()
    player1KPI["Goals"] = [player1stats["goals"].values[0]]
    player1KPI["Assists"] = [player1stats["assists"].values[0]]
    player1KPI["xG"] =[round(player1stats["xG"].values[0],2)]
    player1KPI["xA"] = [round(player1stats["xA"].values[0],2)]
    player1KPI["Goals Last 5 Games"] = [player1last5] if player1last5 is not np.nan else ["N/A"]
    player1KPI["Minutes Played"] = [player1stats["time"].values[0]]
    player1KPI["xG/90"] = [round(player1stats["xG_per90"].values[0],2)]
    player1KPI["xA/90"] = [round(player1stats["xA_per90"].values[0],2)]



    player2KPI = pd.DataFrame() 
    player2KPI["Goals"] = [player2stats["goals"].values[0]]
    player2KPI["Assists"] = [player2stats["assists"].values[0]]     
    player2KPI["xG"] = [round(player2stats["xG"].values[0],2)]
    player2KPI["xA"] = [round(player2stats["xA"].values[0],2)]
    player2KPI["Goals Last 5 Games"] = [player2last5] if player2last5 is not np.nan else ["N/A"]
    player2KPI["Minutes Played"] = [player2stats["time"].values[0]]
    player2KPI["xG/90"] = [round(player2stats["xG_per90"].values[0],2)]
    player2KPI["xA/90"] = [round(player2stats["xA_per90"].values[0],2)]

col_radar, col_table = st.columns([3, 2], gap="large")

with col_table:
    st.subheader("Key Performance Indicators")
    if player1 and player2 and not player1KPI.empty and not player2KPI.empty:
        # Build comparison table
        comparison_df = pd.concat([player1KPI, player2KPI], axis=0)
        p1_name = player1stats["player_name"].values[0]
        p2_name = player2stats["player_name"].values[0]

        if p1_name == p2_name:
            p2_name = f"{p2_name} (2)" # Append (2) if same name

        comparison_df.index = [p1_name, p2_name]

        tbl = comparison_df.T.copy()  # rows = KPIs, cols = players
        tbl = tbl.reset_index().rename(columns={"index": "Stat"})

        # Plotly transparent table with white text
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(tbl.columns),
                fill_color="rgba(0,0,0,0)",
                font=dict(color="rgba(255,255,255,0.7)", size=14),
                align="left",
            ),
            cells=dict(
                values=[tbl[c] for c in tbl.columns],
                fill_color="rgba(0,0,0,0)",
                font=dict(color="rgba(255,255,255,0.7)", size=14),
                align="left",
                height=42,
            )

        )])

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",  # outside
            margin=dict(l=0, r=0, t=0, b=0)
        )

        # subtle grid lines
        fig.data[0].cells.line.color = "rgba(255,255,255,0.15)"
        fig.data[0].header.line.color = "rgba(255,255,255,0.25)"

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    else:
        st.info("Select two players to compare.")


radar_labels = ["Goals", "Assists", "xG", "xA", "xG/90", "xA/90"]


label_to_col = {
    "Goals":  "goals",
    "Assists":"assists",
    "xG":     "xG",
    "xA":     "xA",
    "xG/90":  "xG_per90",
    "xA/90":  "xA_per90",
}

# mins/maxs from league
mins  = pd.Series({lbl: pd.to_numeric(leaguedata[label_to_col[lbl]], errors="coerce").min()
                   for lbl in radar_labels})
maxs  = pd.Series({lbl: pd.to_numeric(leaguedata[label_to_col[lbl]], errors="coerce").max()
                   for lbl in radar_labels})
denom = (maxs - mins).replace(0, np.nan)
SCALE = 5

def normalized_vals(player_stats_row: pd.Series) -> list[float]:
    raw = pd.Series({lbl: float(player_stats_row[label_to_col[lbl]]) for lbl in radar_labels})
    norm = ((raw - mins) / denom).clip(0, 1).fillna(0) * SCALE
    return norm.tolist()



with col_radar:
    st.subheader("Radar Chart Comparison (Scored 0-5)")
    if player1 and player2 and not player1KPI.empty and not player2KPI.empty:
        p1_vals = normalized_vals(player1stats.squeeze())
        p2_vals = normalized_vals(player2stats.squeeze())
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=p1_vals, theta=radar_labels, fill="toself",
                                    name=player1stats["player_name"].values[0]))
        fig.add_trace(go.Scatterpolar(r=p2_vals, theta=radar_labels, fill="toself",
                                    name=player2stats["player_name"].values[0]))
        fig.update_layout(
            template="plotly_dark",
            showlegend=True, margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor="rgba(0,0,0,0)",   # transparent plot area
            paper_bgcolor="rgba(0,0,0,0)",   # transparent outside area 
            font=dict(color="rgba(255,255,255,0.5)"),
            legend=dict(
                title=dict(text="Players", font=dict(color="rgba(255,255,255,0.5)") ),
                font=dict(color="rgba(255,255,255,0.5)")),
            polar=dict(
            radialaxis=dict(visible=True, range=[0, (max(max(p1_vals), max(p2_vals))+0.1)],), 
            bgcolor="rgba(0, 0, 0, 0)")
            )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select two players to compare.")



