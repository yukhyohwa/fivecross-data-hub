from odps import ODPS
import app.config as config

def create_odps_instance(location, project_override=None):
    """
    Creates an ODPS instance based on the location.
    Optionally allows overriding the project name (e.g. for different games in the same environment).
    """
    # Defensive mapping: If the string 'overseas' is passed, 
    # we decide if we mean the default overseas or v2.
    # Looking at sql_tool.py, it maps 'overseas' -> 'overseas_v2'.
    # We will try to follow that pattern for consistency if needed,
    # OR we rely on config.get_odps_credentials to handle it.
    
    # Actually, config.get_odps_credentials has explicit 'overseas' and 'overseas_v2'.
    # Let's try to be smart. If 'overseas' fails, maybe v2 is needed.
    # But for now, let's trust the input or map it if we are sure.
    
    # In universal_sql_query.py, it gets location from GAMES_CONFIG.
    # Let's assume GAMES_CONFIG has correct keys or needs mapping.
    
    creds = config.get_odps_credentials(location)
        
    if not creds:
        return None
    
    project = project_override if project_override else creds['project']
        
    return ODPS(
        creds['access_id'], 
        creds['access_key'], 
        project, 
        creds['endpoint']
    )
