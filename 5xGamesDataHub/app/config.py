import os
from dotenv import load_dotenv

load_dotenv()

def get_odps_credentials(location):
    """
    Get ODPS credentials based on location ('domestic' or 'overseas').
    Returns a dictionary of credentials.
    """
    if location == 'domestic' or location == '国内':
        return {
            'access_id': os.getenv('ODPS_DOMESTIC_ACCESS_ID'),
            'access_key': os.getenv('ODPS_DOMESTIC_ACCESS_KEY'),
            'project': os.getenv('ODPS_DOMESTIC_PROJECT'),
            'endpoint': os.getenv('ODPS_DOMESTIC_ENDPOINT')
        }
    elif location == 'overseas' or location == '海外':
        # Defaulting to the 'easy_query' version
        return {
            'access_id': os.getenv('ODPS_OVERSEAS_ACCESS_ID'),
            'access_key': os.getenv('ODPS_OVERSEAS_ACCESS_KEY'),
            'project': os.getenv('ODPS_OVERSEAS_PROJECT'),
            'endpoint': os.getenv('ODPS_OVERSEAS_ENDPOINT')
        }
    elif location == 'overseas_v2':
        return {
            'access_id': os.getenv('ODPS_OVERSEAS_V2_ACCESS_ID'),
            'access_key': os.getenv('ODPS_OVERSEAS_V2_ACCESS_KEY'),
            'project': os.getenv('ODPS_OVERSEAS_V2_PROJECT'),
            'endpoint': os.getenv('ODPS_OVERSEAS_ENDPOINT')
        }
    return None

def get_hologres_credentials(location):
    if location == 'domestic' or location == '国内环境':
        return {
            'host': os.getenv('HOLO_DOMESTIC_HOST'),
            'port': os.getenv('HOLO_DOMESTIC_PORT'),
            'dbname': os.getenv('HOLO_DOMESTIC_DB'),
            'user': os.getenv('HOLO_DOMESTIC_USER'),
            'password': os.getenv('HOLO_DOMESTIC_PASSWORD')
        }
    elif location == 'overseas' or location == '海外环境':
        return {
            'host': os.getenv('HOLO_OVERSEAS_HOST'),
            'port': os.getenv('HOLO_OVERSEAS_PORT'),
            'dbname': os.getenv('HOLO_OVERSEAS_DB'),
            'user': os.getenv('HOLO_OVERSEAS_USER'),
            'password': os.getenv('HOLO_OVERSEAS_PASSWORD')
        }
    return None
