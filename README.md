# Premier League Player Analysis

**Live App:** [https://your-app.streamlit.app](https://premstats.streamlit.app/)

An interactive Streamlit application for analysing Premier League attacking performance using expected metrics and shot/pass data.

The tool is designed to support direct player comparison, league-wide player analysis and to reveal undervalued/overvalued players based on their stats.

Player, Match and Shots data were collected separately via the Understat API, then cleaned and mapped to create a useful dataset.

> **Season notice:** The dashboard now shows data for the current **2025/26** season as well as the previous **2024/25** season.

## Features

### League-wide Dashbaord

Interactive scatter plots to explore league-wide trends
Key views include:
- **Shot Quality vs Shot Volume** (xG/shot vs Shots/90). Top right is players who shoot a lot and shoot from good positions.
- **Chance Creation vs Goal Threat** (xA/90 vs xG/90). Top right is players who are most likely to have high goals and assists.
- All scatters are coloured by position (DEF, MID, FWD)
Filters: Minutes played, Position, Team

### Player Comparison

Page to compare any two players head to head.
Key views include:
- **Radar Plot** - Both player's profiles are plotted on the radar axis to compare their profiles. Scores are normalized as league-wide percetiles to offer a fair comparison.
- **Key Stats** - Key stats such as goals and assists are displayed side by side for each player.
- **Shot Maps** - View showing every shot from a player built from shot event data. Markers are sized by xG.

## Data
- Source: **Understat** via `understatapi`.
Metrics shown:
- xG / xA: expected goals/assists from shot/pass quality
- Per-90 stats: rates scaled to 90 minutes (fair vs. different playing time)
- xG per shot: average chance quality per attempt
- xG diff: Goals − xG (over/under-performance)
- Goals in last 5: used in comparisons when available (shows “not enough data” if <5 matches)
  - Constructed using shot data from club's last 5 matches

## Preview

<img width="1764" height="783" alt="image" src="https://github.com/user-attachments/assets/1ed32306-be93-4d5d-82a2-4a89238dc62c" />
<br>
<img width="1824" height="819" alt="image" src="https://github.com/user-attachments/assets/8dc390c9-3c34-4d5e-ae89-de18a9918357" />
<br>
<img width="1784" height="816" alt="image" src="https://github.com/user-attachments/assets/2b37ffee-d797-48d3-b485-4167f914c49f" />
<br>
<img width="1799" height="816" alt="image" src="https://github.com/user-attachments/assets/92bcdf13-7700-4010-94d5-1af0bce269b2" />


## How to run


### 1) Clone the repo
```bash
git clone https://github.com/Hashim-mirjan/football-stats-analysis.git
cd football-stats-analysis
```
### 2) Install dependencies
```bash
pip install -r requirements.txt
```
### 3) Run the app (from the repo folder)
```bash
streamlit run Players_Dashboard.py
```
This will open a web app dashboard in your browser. The home page is the main dashbaord. Open the sidebar on the left to access the filters and the player comparison page.

### Troubleshooting
ModuleNotFoundError (e.g., No module named 'src'):
Make sure you ran streamlit run app.py from the repo folder (after cd <REPO_NAME>).

AttributeError: 'Options' object has no attribute 'set_headless':
Make sure you are have selenium v3 installed, as shown in requirements.
