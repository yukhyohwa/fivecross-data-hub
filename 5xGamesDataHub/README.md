# Data Platform Application (5xGamesDataHub)

A comprehensive, Streamlit-based data engineering and analytics platform designed for game projects. It provides a suite of tools for SQL execution, data management, visualization, and prediction.

## 🚀 Key Features

### 1. Game SQL Library (Universal Query Tool)
*   **Multi-Game Support**: Dynamically loads SQL templates for different games (e.g., Slam Dunk, One Piece) from the `app/sql_templates/` directory.
*   **Smart Parsing**: Automatically identifies query parameters (like `{day1}`, `{start_date}`).
*   **Cross-Environment**: Supports both Domestic and Overseas ODPS environments.
*   **Flexible Export**: Export results to **CSV**, **Excel**, or **TXT**.

### 2. KPI Dashboard
*   **High-Performance**: Cached data fetching for instant report loading.
*   **Visual Analytics**: Interactive charts (Altair) and sparklines showing Revenue, MAU, and NUU trends.
*   **Global View**: Aggregates data from multiple regions (Domestic/Overseas).

### 3. Data Tools
*   **Data Upload**: 
    *   Supports **Excel (.xlsx)**, **CSV**, and **TXT** formats.
    *   Features smart partition handling and table name inference.
*   **JSON Toolkit**: 
    *   Real-time JSON validation, formatting (Pretty Print), and compression.
*   **SQL Generator**: 
    *   Quickly generates standard SQL queries from field definitions.

### 4. Legacy Modules
*   **ODPS Query**: Standardized queries for legacy projects (WINGS, JUMP, OP).
*   **Prediction Models**: LTV, DAU, and MAU prediction (ML modules).

---

## 📂 Project Structure

```text
5xGamesDataHub/
├── app/
│   ├── modules/              # Core Application Logic
│   │   ├── universal_sql_query.py  # Generic SQL Runner
│   │   ├── kpi_dashboard.py        # Dashboard with Charts
│   │   ├── data_upload.py          # Data Uploader
│   │   └── ...
│   ├── sql_templates/        # SQL Template Repository
│   │   ├── slamdunk_overseas/      # e.g. Project Folder
│   │   │   ├── g33002013_weeklyreport_vip.sql
│   │   │   └── ...
│   │   └── [new_game]_[loc]/       # Add new game folders here
│   ├── config.py             # Environment Configuration
│   └── ...
├── output/                   # Temp folder for outputs
├── requirements.txt          # Python Dependencies
└── main.py                   # Application Entry Point
```

---

## 🛠️ Usage Guide

### Installation
1.  Ensure Python 3.8+ is installed.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration
Ensure your `.env` file (or environment variables) is configured with ODPS credentials:
*   `ODPS_DOMESTIC_ACCESS_ID`, `ODPS_DOMESTIC_ACCESS_KEY`...
*   `ODPS_OVERSEAS_ACCESS_ID`, `ODPS_OVERSEAS_ACCESS_KEY`...

### Running the App
```bash
streamlit run main.py
```

### Adding a New Game Project
To add SQL templates for a new game:
1.  Create a folder in `app/sql_templates/`.
    *   Naming convention: `[game_name]_[location]` (e.g., `naruto_domestic`).
2.  Add `.sql` files to that folder.
    *   Files are automatically detected and added to the "Game SQL Library" menu.

---

## 📝 Notes
*   **Performance**: Major dashboards use caching (`ttl=3600s`). To refresh data immediately, clear the Streamlit cache (Press `C`).
*   **Security**: Credentials are never stored in the code; strictly use environment variables or local `.env`.