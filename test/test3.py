import jwt
from datetime import datetime, timedelta
def sign_token(payload,key):
    """
    Genera un JWT con el payload proporcionado.
    
    Args:
        payload (dict): Información de la sesión, incluyendo usuario, rol, expiración y jwt.
    
    Returns:
        str: Token JWT firmado.
    """
    payload_copy = payload.copy()
    payload_copy["iat"] = datetime.utcnow()  
    payload_copy["exp"] = datetime.utcnow() + timedelta(weeks=1)  # Expiración en 1 semana
    
    token = jwt.encode(payload_copy, key, algorithm="HS256")
    return token

token_response="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiZW1haWwiOiJqaG9uZG9lQGVtYWlsLmNvbSIsImFjY291bnRfdHlwZSI6eyJpZCI6MSwibmFtZSI6IkFkbWluaXN0cmFkb3IiLCJzdGF0dXMiOjF9LCJpYXQiOjE3Mzk2NzE1MjAsImV4cCI6MTc0MDI3NjMyMH0.zLaKTyKrTjzC7s54VIjHTTcG8cftStcDW3lqQO-bh1U"
iso_date = '2025-02-22T02:54:40.134Z'
payload = {'user': {'id':1}, "role":1,"expires":iso_date,'jwt':token_response}
key  = 'd2a933ae55573c187971fde0ac38603adbc708d22402d76e403b2109f1efe33e'

token = sign_token(payload,key)
print(token)