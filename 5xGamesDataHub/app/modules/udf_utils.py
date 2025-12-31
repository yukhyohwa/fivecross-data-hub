from odps import ODPS
import psycopg2
import pandas as pd
import app.config as config

def get_odps_connection(region):
    # Map region 'domestic'/'overseas' to config keys
    # ensure we handle the keys correctly.
    creds = config.get_odps_credentials(region)
    if not creds:
        raise ValueError(f"No credentials for region {region}")
        
    return ODPS(
        creds['access_id'],
        creds['access_key'],
        creds['project'],
        creds['endpoint']
    )

def get_holo_connection(region):
    creds = config.get_hologres_credentials(region)
    if not creds:
         raise ValueError(f"No credentials for region {region}")

    return psycopg2.connect(
        host=creds['host'],
        port=creds['port'],
        dbname=creds['dbname'],
        user=creds['user'],
        password=creds['password']
    )

def execute_sql(engine, region, sql, config_ignored=None):
    """
    Execute SQL on ODPS or Holo.
    config_ignored: kept for backward compatibility with function signature if needed, but ignored.
    """
    if engine == 'odps':
        conn = get_odps_connection(region)
        with conn.execute_sql(sql).open_reader() as reader:
            column_names = [field.name for field in reader.schema.columns]
            data = [row.values for row in reader]
            df = pd.DataFrame(data, columns=column_names)
            return df
    elif engine == 'holo':
        conn = get_holo_connection(region)
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()
        df = pd.DataFrame(results, columns=column_names)
        return df
    else:
        raise ValueError(f"Unsupported engine: {engine}")
