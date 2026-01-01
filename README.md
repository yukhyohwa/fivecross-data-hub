# 5xGamesDataHub

**5xGamesDataHub** is a unified data operations platform designed for game analytics. It provides a suite of tools for SQL generation, data visualization, predictive modeling (MAU/DAU/LTV), and ad-hoc queries across multiple game projects (Domestic & Overseas).

## 🚀 Key Features

*   **KPI Dashboard**: High-level overview of global game performance (Revenue, MAU, NUU).
*   **Universal SQL Library**: A template-based query system. Select a game, choose a report type, and run. No SQL knowledge required for end-users.
*   **Predictive Analytics**: Tools to forecast MAU, DAU, and LTV based on historical retention and payment data.
*   **Data Tools**:
    *   **SQL Editor**: Run free-form ad-hoc queries on ODPS/Hologres.
    *   **Data Upload**: Upload Excel/CSV data directly to ODPS tables.
    *   **JSON Tool**: Utility for formatting and inspecting JSON.

## 📂 Project Structure

```
5xGamesDataHub/
├── app/
│   ├── modules/                 # Functional Python modules (Streamlit pages)
│   │   ├── universal_sql_query.py   # Core template engine
│   │   ├── kpi_dashboard.py         # Global dashboard
│   │   ├── mau_predict.py           # MAU forecasting
│   │   ├── ...
│   ├── sql_templates/           # SQL Template Library
│   │   ├── system/                  # Shared/Platform queries (e.g. KPI, MAU History)
│   │   ├── slamdunk_overseas/       # Project-specific templates
│   │   ├── onepiece_domestic/       # Project-specific templates
│   ├── games_config.py          # Central Registry for Game IDs & Envs
│   ├── config.py                # Credential management
├── main.py                      # Application Entry Point
├── split_sql.py                 # Utility to migrate legacy SQL files
├── requirements.txt             # Python dependencies
```

## ⚙️ Configuration & Adding New Games

The system uses a **Configuration-First** approach. You do not need to modify Python code to add a new game.

### 1. Add Game to `games_config.py`
Open `app/games_config.py` and register your game:

```python
    "new_game_key": {
        "label": "My New Game",
        "folder": "my_new_game_folder", # Matches folder in sql_templates
        "environment": "overseas",       # 'domestic' or 'overseas'
        "game_id": "g12345678",          # Automatically injected into SQL
        "odps_project": "project_name"
    }
```

### 2. Create Template Folder
Create a folder in `app/sql_templates/` matching the `folder` name above (e.g., `app/sql_templates/my_new_game_folder/`).

### 3. Add SQL Templates
Add `.sql` files to that folder.
*   **Filename**: Describes functionality (e.g., `daily_report.sql`).
*   **Header**: First line must be `-- Index. Title`.
*   **Placeholders**:
    *   `{game_id}`: Automatically filled from config.
    *   `{any_other_var}`: Will generate a user input box in the UI.

**Example SQL (`app/sql_templates/my_new_game_folder/active_users.sql`):**
```sql
-- 1. Active Users Report
-- Description: Query daily active users

SELECT day, COUNT(DISTINCT role_id)
FROM ods_log_login
WHERE game_id = '{game_id}'  -- Auto-filled
  AND day = '{target_day}'   -- Ask user for input
GROUP BY day;
```

## 🛠️ Usage

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run Application**:
    ```bash
    streamlit run main.py
    ```

## 🔧 Core Modules Explanation

*   **Universal SQL Query**: The primary tool for non-technical Ops teams. It reads from the `sql_templates` folder and provides a UI form for variables.
*   **KPI Dashboard**: Aggregates data from `dm_platform.monthly_lcx_user_info` to show company-wide trends.
*   **MAU/DAU/LTV Predict**: Mathematical models that fetch historical data via SQL and project future trends based on retention curves.