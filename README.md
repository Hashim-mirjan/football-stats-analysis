# Premier League Player Dashboard

An interactive Streamlit app for exploring player performance using scatter plots, filters, and a two-player comparison (radar + KPI table). Scatter points are currently colored by position.

> **Season notice:** The dashboard currently shows **2024** season data. I plan to add a **season selector** once more weeks have been played in the new season.

## Preview

<img width="600" height="265" alt="Screenshot 2025-08-26 193214" src="https://github.com/user-attachments/assets/94cbdfc6-1cad-4976-814c-0069b00adfe6" />  <img width="600" height="265" alt="Screenshot 2025-08-26 193258" src="https://github.com/user-attachments/assets/658e962a-8eb5-4947-beef-0fcb061933f8" />

<img width="600" height="265" alt="Screenshot 2025-08-26 203541" src="https://github.com/user-attachments/assets/9873268e-75c5-4212-875d-3c29ac0308d4" />


## Features
- **Filters:** minutes threshold, position, team, player search (typeahead). To narrow search down for player selection.
- **Two key scatters:**
  - Shooting Data: `xG/shot` vs `Shots/90`. Measures quality of shots vs quantity of shots. Top right is players who shoot a lot and shoot from good positions.
  - Expected Goal Involvements: `xA/90` vs `xG/90`. Measures goalscoring and assisting chances. Top right is players who are most likely to have high goals and assists.
- **Color by position** (Forward / Midfielder / Defender / Goalkeeper).
- **Player vs Player** comparison:
  - **Radar** (league min–max normalized to a 0–5 scale)
  - **KPI table** comparing goals, assists, xG, xA, goals last 5 games, minutes played, xG/90, xA/90.
- **Dark theme** and responsive layout.

## Data
- Source: **Understat** via `understatapi`.
Metrics shown:
- xG / xA: expected goals/assists from shot/pass quality
- Per-90 stats: rates scaled to 90 minutes (fair vs. different playing time)
- xG per shot: average chance quality per attempt
- xG diff: Goals − xG (over/under-performance)
- Goals in last 5: used in comparisons when available (shows “not enough data” if <5 matches)

## How to run

```bash
# 1) Clone the repo
git clone https://github.com/Hashim-mirjan/football-stats-analysis.git
cd football-stats-analysis

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the app (from the repo folder)
streamlit run Players_Dashboard.py

This will open a web app dashboard in your browser. The home page is the main dashbaord. Open the sidebar on the left to access the filters and the player comparison page.  
