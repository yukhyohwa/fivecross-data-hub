# Data Platform Application

A professional Streamlit-based data platform for querying, analyzing, and predicting game data.

## Features

- **Query Tools**: 
  - Standardized ODPS queries for different projects (WINGS, JUMP, OP).
  - Advanced SQL execution tool for ODPS and Hologres.
- **Data Management**:
  - Secure data upload to ODPS.
  - JSON utility tools.
- **Analytics**:
  - KPI Dashboard with visualization.
  - Interactive Data Explorer.
- **Predictions**:
  - LTV, DAU, and MAU prediction models.
- **Utilities**:
  - SQL Code Generator.

## Setup & specific instructions

1. **Environment Setup**:
   Ensure you have Python 3.8+ installed.
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**:
   Create a `.env` file in the root directory (already created if using the assistant).
   This file should contain the following credentials:
   - `ODPS_DOMESTIC_...`
   - `ODPS_OVERSEAS_...`
   - `HOLO_DOMESTIC_...`
   - `HOLO_OVERSEAS_...`

   *Note: Sensitive credentials are not stored in the code repository.*

3. **Running the Application**:
   Run the main entry point:
   ```bash
   streamlit run main.py
   ```

## Directory Structure

- `main.py`: Application entry point.
- `app/`: Core application logic.
  - `config.py`: Configuration and environment variable management.
  - `auth.py`: User authentication.
  - `modules/`: Feature modules (Queries, Dashboard, Tools).
- `output/`: Directory for generated files.

## Notes

- Output files are saved to the `output` directory or downloaded directly via the browser.