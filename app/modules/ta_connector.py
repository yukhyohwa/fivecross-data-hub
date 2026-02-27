import requests
import pandas as pd
import json

def execute_sql(sql, url, token):
    """
    Executes a SQL query against the ThinkingData Open API.

    Args:
        sql (str): The SQL query string.
        url (str): The base URL for the ThinkingData API (e.g., https://<cluster>/querySql).
        token (str): The authentication token.

    Returns:
        pd.DataFrame: A DataFrame containing the query results.
    """
    if not url or not token:
        raise ValueError("ThinkingData URL and Token must be provided.")

    # Ensure URL ends with the query endpoint if not already provided
    if not url.endswith('/querySql'):
        # Handles cases where base URL is provided without trailing slash
        base = url.rstrip('/')
        api_endpoint = f"{base}/querySql"
    else:
        api_endpoint = url

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'token': token,
        'sql': sql,
        'format': 'json',
        'timeoutSeconds': 60
    }

    try:
        response = requests.post(api_endpoint, headers=headers, data=data, timeout=70)
        response.raise_for_status()

        # Determine format: Single JSON object or Line-delimited JSON
        # If response content starts with '{', it's likely JSON.
        # But both formats start with '{'.
        # Try to parse as single JSON first.

        try:
             result = response.json()
             # If successful, check if it has 'return_code' and 'data'
             if isinstance(result, dict) and 'return_code' in result:
                 if result['return_code'] != 0:
                     raise Exception(f"ThinkingData API Error: {result.get('return_message')}")

                 # It's a single object response (standard JSON format as per doc Option 1)
                 columns = result.get('data', {}).get('headers', [])
                 rows = result.get('data', {}).get('rows', []) # Some versions use 'rows'

                 # If rows are empty here, it might be because `format=json` with large data returns line-delimited
                 # and `requests.json()` parsed only the first line? NO.
                 # requests.json() parses the WHOLE body. If it succeeded, then the body is valid JSON.
                 # If the body is line-delimited JSON (multiple objects), requests.json() fails.

                 # However, if the server returns a valid JSON object AND extra lines, requests.json() might parse the first object
                 # if the library allows trailing garbage (standard json module does NOT).
                 # requests uses simplejson or json. Neither allow trailing non-whitespace.

                 # So if we are here, it's a SINGLE JSON OBJECT.
                 # If 'rows' key exists, use it.
                 if rows:
                     return pd.DataFrame(rows, columns=columns)

                 # If no 'rows' key, maybe it relies on line-delimited but somehow parsed as one obj? Unlikely.
                 # Proceed to line split logic if rows are empty but maybe we expect data?
                 # Actually, let's just fall through to line logic if we don't find data rows here,
                 # BUT we need to be careful not to re-read stream if it's consumed.
                 # response.text is safe.

        except (json.JSONDecodeError, ValueError):
             pass # Not a single JSON blob, proceed to line split

        lines = response.text.strip().split('\n')
        if not lines:
            return pd.DataFrame()

        # Parse Metadata (First Line)
        try:
            meta = json.loads(lines[0])
        except json.JSONDecodeError:
             raise Exception("Invalid response format from ThinkingData API")

        if meta.get('return_code') != 0:
             raise Exception(f"ThinkingData API Error: {meta.get('return_message')}")

        columns = meta.get('data', {}).get('headers', [])

        # Parse Data Rows (Subsequent Lines)
        data_rows = []
        for line in lines[1:]:
            if line.strip():
                try:
                    data_rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue # Skip invalid lines

        return pd.DataFrame(data_rows, columns=columns)

    except Exception as e:
        raise Exception(f"Failed to execute TA SQL: {str(e)}")
