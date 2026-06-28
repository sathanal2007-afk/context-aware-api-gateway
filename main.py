from fastapi import FastAPI, HTTPException
import time
from geopy.distance import geodesic
import redis # Redis டூலை இம்போர்ட் பண்றோம்

app = FastAPI(title="Sathana's Distributed Security Gateway")

# 🔗 Connect to Redis (By default, local host 6379 போர்ட்ல கனெக்ட் ஆகும்)
# ரியல் டைம்ல கம்பெனிகள்ல இப்படித்தான் கிளவுட் டேட்டாபேஸை கனெக்ட் பண்ணுவாங்க
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.get("/")
def home():
    return {"status": "Online", "gateway": "Enterprise Redis Security Gateway Live!"}

@app.get("/api/gateway")
def gateway(username: str, lat: float, lon: float):
    current_time = time.time()
    
    # 1. Unique Redis Key ஃபார்மேட் (ஒவ்வொரு யூசருக்கும் தனி கீ)
    frozen_key = f"user:{username}:frozen"
    geo_key = f"user:{username}:geo"
    rate_key = f"user:{username}:rate"
    
    # 2. Check: யூசர் அக்கவுண்ட் ஆல்ரெடி ஃப்ரீஸ் ஆகிருக்கான்னு Redis-ல செக் பண்றோம்
    if r.get(frozen_key) == "true":
        raise HTTPException(status_code=403, detail="CRITICAL: Account frozen due to profile anomaly in Redis state!")

    # 3. ADVANCED SECURITY: GEOSPATIAL VELOCITY CHECK
    last_geo = r.hgetall(geo_key) # Redis hash-ல இருந்து பழைய லொகேஷன் எடுக்குறோம்
    
    if last_geo:
        last_lat = float(last_geo["lat"])
        last_lon = float(last_geo["lon"])
        last_time = float(last_geo["time"])
        
        time_gap_hours = (current_time - last_time) / 3600.0
        
        if time_gap_hours > 0:
            distance_km = geodesic((last_lat, last_lon), (lat, lon)).km
            speed_kmh = distance_km / time_gap_hours
            
            if speed_kmh > 900.0:
                r.set(frozen_key, "true") # Redis-ல நிரந்தரமா அக்கவுண்ட்டை லாக் பண்றோம்
                raise HTTPException(status_code=403, detail=f"SECURITY ALERT: Impossible Travel! Speed: {int(speed_kmh)} km/h. Frozen in Database.")

    # 4. TRADITIONAL SECURITY: SLIDING-WINDOW RATE LIMITER (Using Redis Sorted Sets)
    pipe = r.pipeline()
    # 1 நிமிஷத்துக்கு முந்துன பழைய ரெக்வஸ்ட்டை டெலீட் பண்றோம்
    pipe.zremrangebyscore(rate_key, 0, current_time - 60)
    # இப்போ வந்த ஹிட்டை டைம்ஸ்டேம்போட ஆட் பண்றோம்
    pipe.zadd(rate_key, {str(current_time): current_time})
    # மொத்த ஹிட்ஸ் எவ்ளோன்னு கவுண்ட் எடுக்குறோம்
    pipe.zcard(rate_key)
    # மெமரி வேஸ்ட் ஆகாம இருக்க 60 செகண்ட்ல எக்ஸ்பைரி செட் பண்றோம்
    pipe.expire(rate_key, 60)
    
    results = pipe.execute()
    request_count = results[2] # zcard-ஓட அவுட்புட் இன்டெக்ஸ் 2-ல வரும்
    
    if request_count > 5:
        raise HTTPException(status_code=429, detail="RATE LIMIT EXCEEDED: Too many distributed hits.")

    # 5. லேட்டஸ்ட் லொகேஷனை Redis Hash-ல அப்டேட் பண்றோம்
    r.hmset(geo_key, {"lat": lat, "lon": lon, "time": current_time})
    
    return {
        "status": "ALLOWED",
        "message": "Access granted safely via Redis validation.",
        "active_rpm": request_count
    }