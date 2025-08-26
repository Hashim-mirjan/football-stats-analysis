# Players_Dashboard.py
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="FPL Attacking Dashboard", layout="wide")

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
    </style>
    """,
    unsafe_allow_html=True
)

# --- Data loading --------------------------------------------

from src.Data import fetch_data

leaguedata = fetch_data(2024)

# ---------------- Sidebar (filters) -----------------------------

with st.sidebar:
    st.header("Filters")
    t_min = int(np.nanmin(leaguedata["time"])) if leaguedata["time"].notna().any() else 0
    t_max = int(np.nanmax(leaguedata["time"])) if leaguedata["time"].notna().any() else 3000
    # Default = 60% of max minutes
    default_min = int(0.6 * t_max)
    default_min = max(t_min, min(default_min, t_max))

    min_minutes = st.slider(
        "Minimum minutes played",
        min_value=t_min, max_value=t_max, value=default_min, step=30
    )


    positions = sorted(leaguedata["main_position"].dropna().unique().tolist())
    sel_positions = st.multiselect("Positions", positions, default=['Forward','Midfielder']) 

    teams = sorted(leaguedata["current_team"].dropna().unique().tolist())
    sel_teams = st.multiselect("Team", teams, default=teams)  

    mask = (
    leaguedata["time"].notna()
    & (leaguedata["time"] >= min_minutes)
    & (leaguedata["main_position"].isin(sel_positions))
    & (leaguedata["current_team"].isin(sel_teams))
    )
    df = leaguedata.loc[mask].copy()

# --- Main page ---------------------------------------------

st.title("Premier League Attacking Dashboard")


left_col, right_col = st.columns([3, 2], gap="large")  # wider left, narrower right


def scatter_shotsvsxG(df, x = 'shots_per90', y = 'xG_per_shot',title="xG Per Shot vs Shots Taken Per 90"):
    
    POS_ORDER = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
    POS_COLORS = {
        "Goalkeeper": "#6b7280",  
        "Defender":   "#2e8467", 
        "Midfielder": "#3b5070",  
        "Forward":    "#aa4242",  
    }
    
    xlim = df[x].max() * 0.5
    ylim = df[y].max() * 0.5
    label_mask = (df[x] >= xlim) | (df[y] >= ylim)
    
    labels = np.where(label_mask, df["last_name"], None)
    # Scatter plot
    fig = px.scatter(df,x=x, 
                     y=y, 
                     hover_name="player_name",
                     color="main_position",
                     color_discrete_map=POS_COLORS,
                     title=title,height=420,
                     text=labels
                     )
    
    
    fig.update_layout(showlegend=False)
    fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",   # transparent plot area
    paper_bgcolor="rgba(0,0,0,0)",   # transparent outside area  
    xaxis=dict(
        showgrid=True, gridcolor="rgba(255,255,255,0.1)", gridwidth=1,
        zeroline=False, showline=False, linecolor="grey", linewidth=1,
        ticks="outside", ticklen=6
    ),
    yaxis=dict(
        showgrid=True, gridcolor="rgba(255,255,255,0.1)", gridwidth=1,
        zeroline=False, showline=False, linecolor="grey", linewidth=1,
        ticks="outside", ticklen=6
    ),
    title=dict(
            font=dict(size=20, color = "rgba(255,255,255,0.5)"), 
            x=0.5, 
            xanchor="center"
        )
    )

    return fig

def xGunderover(df):
    df['xG_diff'] = df['goals'] - df['xG']
    df_sorted = df.sort_values(by='xG_diff', ascending=False)
    return df_sorted

fig_scatter1 = scatter_shotsvsxG(df,'shots_per90','xG_per_shot',title="xG Per Shot vs Shots Taken Per 90")
fig_scatter2 = scatter_shotsvsxG(df,'xG_per90','xA_per90',title="xA Per 90 vs xG Per 90")

with left_col:
    st.plotly_chart(fig_scatter1, use_container_width=True)
    st.plotly_chart(fig_scatter2, use_container_width=True)



def top10_bar(df, metric="xG_diff", title="Top 10 Players by xG per 90"):
    # Plot horizontal bar chart
    num_players = len(df)
    top10 = df.sort_values(by=metric, ascending=False).head(min(10,num_players//2 + num_players%2))
    bottom10 = df.sort_values(by=metric, ascending=True).head(min(10,num_players//2))
    bottom10 = bottom10.iloc[::-1]
    top10andbottom10 = pd.concat([top10, bottom10])
    top10andbottom10["xG_diff"] = top10andbottom10["xG_diff"].round(1)

    fig = px.bar(
        top10andbottom10,  
        x=metric,                  
        y="player_name",           
        orientation="h",           
        text=metric,               
        title=title,
        height=850
    )

    fig.update_traces(marker_line_width=0)

    fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",   # transparent plot area
    paper_bgcolor="rgba(0,0,0,0)",   # transparent outside area 
        xaxis=dict(
        showgrid=True, gridcolor="rgba(255,255,255,0.1)", gridwidth=1,
        zeroline=False, showline=False, linecolor="grey", linewidth=1,
        ticks="outside", ticklen=6
    ),
    yaxis=dict(
        showgrid=True, gridcolor="rgba(255,255,255,0.1)", gridwidth=1,
        zeroline=False, showline=False, linecolor="grey", linewidth=1,
        ticks="outside", ticklen=6
    ), 
    title=dict(
            font=dict(size=20, color = "rgba(255,255,255,0.5)"), 
            x=0.5, 
            xanchor="center"
        )
    )


    return fig

fig_xgoverperformers = top10_bar(df, metric="xG_diff", title="xG Over and Under performers "
"(Goals - xG)")


with right_col:
    st.plotly_chart(fig_xgoverperformers, use_container_width=True)



