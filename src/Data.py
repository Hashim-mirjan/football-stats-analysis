import numpy as np
import pandas as pd
import understatapi as ustat
import streamlit as st

# Reuse the API client across pages/reruns
@st.cache_resource
def get_client():
    return ustat.UnderstatClient()

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(season='2024'):
    season = str(season)
    client = get_client()
    leaguedata = client.league(league='EPL').get_player_data(season=season)
    leaguedata = pd.DataFrame(leaguedata)

    leaguedata = leaguedata.dropna(subset=["player_name"])

    leaguedata["xG"] = pd.to_numeric(leaguedata["xG"], errors="coerce")
    leaguedata["goals"] = pd.to_numeric(leaguedata["goals"], errors="coerce")
    leaguedata["shots"] = pd.to_numeric(leaguedata["shots"], errors="coerce")
    leaguedata["key_passes"] = pd.to_numeric(leaguedata["key_passes"], errors="coerce")
    leaguedata["time"] = pd.to_numeric(leaguedata["time"], errors="coerce")
    leaguedata["assists"] = pd.to_numeric(leaguedata["assists"], errors="coerce")
    leaguedata["xA"] = pd.to_numeric(leaguedata["xA"], errors="coerce")

    nineties = (leaguedata["time"] / 90).replace(0, np.nan)
    leaguedata["shots_per90"]   = leaguedata["shots"].div(nineties)
    leaguedata["xG_per_shot"]   = leaguedata["xG"].div(leaguedata["shots"]).replace([np.inf, -np.inf], np.nan)
    leaguedata["xG_per90"]      = leaguedata["xG"].div(nineties)
    leaguedata["xA_per90"]      = leaguedata["xA"].div(nineties)
    leaguedata["goals_per90"]   = leaguedata["goals"].div(nineties)
    leaguedata["assists_per90"] = leaguedata["assists"].div(nineties)
    leaguedata["xG_diff"]       = leaguedata["goals"] - leaguedata["xG"]

    leaguedata["last_name"] = leaguedata["player_name"].str.split().str[-1] 
    leaguedata["current_team"] = leaguedata["team_title"].str.split(",").str[0].str.strip()

    leaguedata["main_position"] = np.where(
    leaguedata["position"].str.strip().str[-1] == "S",
    leaguedata["position"].str.strip().str[-3],
    leaguedata["position"].str.strip().str[-1]
    )

    leaguedata["main_position"] = leaguedata["main_position"].replace({
        "F": "Forward", 
        "M": "Midfielder", 
        "D": "Defender",
        "K": "Goalkeeper"
    })

    return leaguedata

def get_player_id(leaguedata, player_name):
    player_row = leaguedata[leaguedata["player_name"] == player_name]
    if not player_row.empty:
        return str(player_row.iloc[0]["id"])
    else:
        return None

def fetch_player_shot_data(player_id):
    client = get_client()
    player = client.player(player_id)
    shot_data = player.get_shot_data()
    shot_data = pd.DataFrame(shot_data)
    if shot_data.empty:
        return shot_data
    # Convert relevant columns to numeric types
    numeric_cols = ["xG", "minute", "X", "Y"]
    for col in numeric_cols:
        shot_data[col] = pd.to_numeric(shot_data[col], errors="coerce")

    if "date" in shot_data:
        shot_data["date"] = pd.to_datetime(shot_data["date"], errors="coerce")
    
    return shot_data

def fetch_team_match_data(team_name, season='2024'):
    client = get_client()
    match_data = client.team(team_name).get_match_data(season=season)
    match_data = pd.DataFrame(match_data)
    match_data.rename(columns={"datetime": "date"}, inplace=True)
    
    return match_data
