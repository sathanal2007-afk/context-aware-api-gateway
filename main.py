from fastapi import FastAPI, HTTPException
import time
from geopy.distance import geodesic # Distances calculate panna library use panrom

app = FastAPI(title="Sathana's Advanced Security Gateway")

# Global tracking database proxy (Single object dictionary)
user_logs = {}  
# Inside Memory Structure: 
# { "username": { "hits": [timestamps], "last_lat": lat, "last_lon": lon, "last_time": timestamp, "is_frozen": bool } }

@app.get("/")
def home():
    return {"status": "Online", "gateway": "AI-Powered Context Aware Firewall Live!"}

@app.get("/api/gateway")
def gateway(username: str, lat: float, lon: float):
    current_time = time.time()
    current_location = (lat, lon)
    
    # 1. User pudhusa varaanga na, profile tracking space assign pannu
    if username not in user_logs:
        user_logs[username] = {
            "hits": [], 
            "last_lat": lat, 
            "last_lon": lon, 
            "last_time": current_time,
            "is_frozen": False
        }
        return {"status": "ALLOWED", "message": "First time telemetry profile initialized!"}
        
    user_data = user_logs[username]
    
    # 2. Check: Profile already anomalous attack vector aagi freeze account checking
    if user_data["is_frozen"]:
        raise HTTPException(status_code=403, detail="CRITICAL ERROR: Account frozen due to impossible travel profile detection!")

    # 3. ADVANCED SECURITY LAYER: IMPOSSIBLE TRAVEL DETECTION
    last_time = user_data["last_time"]
    last_location = (user_data["last_lat"], user_data["last_lon"])
    
    # Time gap-ah seconds-la irundhu Hours-ku mathurorom
    time_gap_hours = (current_time - last_time) / 3600.0
    
    if time_gap_hours > 0:
        # Geodesic method accurate KM track vector yield pannum
        distance_km = geodesic(last_location, current_location).km
        speed_kmh = distance_km / time_gap_hours
        
        # Scenario Check: Flight speed (900 KM/hr) thandina transaction freeze
        if speed_kmh > 900.0:
            user_data["is_frozen"] = True # Account permanent freeze inside state block
            raise HTTPException(
                status_code=403, 
                detail=f"SECURITY ALERT: Impossible Travel Detected! Calculated Speed: {int(speed_kmh)} km/h. Device Access Blocked."
            )

    # 4. TRADITIONAL SECURITY LAYER: RATE LIMITER
    # Clean up hits older than 60 seconds
    user_data["hits"] = [t for t in user_data["hits"] if current_time - t < 60]
    
    if len(user_data["hits"]) >= 5:
        raise HTTPException(status_code=429, detail="RATE LIMIT EXCEEDED: Too many requests from single profile node.")
        
    # Updates parameters to tracking cache state
    user_data["hits"].append(current_time)
    user_data["last_lat"] = lat
    user_data["last_lon"] = lon
    user_data["last_time"] = current_time
    
    return {
        "status": "ALLOWED",
        "message": "Access granted under adaptive secure evaluation.",
        "active_rpm": len(user_data["hits"]),
        "calculated_speed": "Normal"
    }