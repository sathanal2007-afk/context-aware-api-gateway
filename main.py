from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import time
from geopy.distance import geodesic

app = FastAPI(title="Sathana's Production-Ready Gateway")
user_logs = {}  

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Production Gateway Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-white min-h-screen flex items-center justify-center p-4">
    <div class="bg-slate-800 p-6 rounded-2xl shadow-2xl w-full max-w-md border border-slate-700 text-center">
        <h1 class="text-2xl font-bold text-emerald-400 mb-2">🛡️ Live Enterprise Gateway</h1>
        <p class="text-slate-400 text-sm mb-6">No buttons. Automatic background location tracking verification.</p>
        
        <div class="mb-4 text-left">
            <label class="block text-xs font-semibold text-slate-400 uppercase mb-2">Username</label>
            <input type="text" id="username" value="sathana_l" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none">
        </div>

        <button onclick="triggerAutoLogin()" class="w-full bg-blue-600 hover:bg-blue-500 font-medium py-3 rounded-xl transition shadow-lg">
            Secure Sign In
        </button>

        <div id="status-box" class="mt-6 p-4 bg-slate-900 rounded-xl border border-slate-700 hidden text-sm font-mono">
            Processing...
        </div>
    </div>

    <script>
        function triggerAutoLogin() {
            const statusBox = document.getElementById('status-box');
            statusBox.classList.remove('hidden');
            statusBox.innerHTML = "Fetching device GPS coordinates...";

            // 🤖 ஆட்டோமேட்டிக்கா பிரவுசர் மூலமா லொகேஷன் எடுக்குறோம்!
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(async (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const username = document.getElementById('username').value;
                    
                    statusBox.innerHTML = `GPS Loaded: (${lat}, ${lon})\\nSending to Firewall Gateway...`;

                    try {
                        const response = await fetch(`/api/gateway?username=${username}&lat=${lat}&lon=${lon}`);
                        const data = await response.json();
                        
                        if (response.status === 200) {
                            statusBox.className = "mt-6 p-4 bg-emerald-950/50 rounded-xl border border-emerald-500 text-emerald-400 text-left font-mono";
                            statusBox.innerHTML = `<b>ACCESS GRANTED ✅</b><br><pre>${JSON.stringify(data, null, 2)}</pre>`;
                        } else {
                            statusBox.className = "mt-6 p-4 bg-rose-950/50 rounded-xl border border-rose-500 text-rose-400 text-left font-mono";
                            statusBox.innerHTML = `<b>ACCESS DENIED ❌</b><br><pre>${JSON.stringify(data, null, 2)}</pre>`;
                        }
                    } catch (e) {
                        statusBox.innerHTML = "Connection Error!";
                    }
                }, (error) => {
                    statusBox.innerHTML = "🛑 Error: Location access denied by browser! Please allow location permission.";
                });
            } else {
                statusBox.innerHTML = "Browser does not support geolocation.";
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return HTML_TEMPLATE

@app.get("/api/gateway")
def gateway(username: str, lat: float, lon: float):
    current_time = time.time()
    current_location = (lat, lon)
    
    if username not in user_logs:
        user_logs[username] = {"hits": [], "last_lat": lat, "last_lon": lon, "last_time": current_time, "is_frozen": False}
        return {"status": "ALLOWED", "info": "Initial login location verified and cached securely."}
        
    user_data = user_logs[username]
    if user_data["is_frozen"]:
        raise HTTPException(status_code=403, detail="Account locked. Anomaly state cached in security node.")

    # Impossible Travel Validation Engine
    last_time = user_data["last_time"]
    last_location = (user_data["last_lat"], user_data["last_lon"])
    time_gap_hours = (current_time - last_time) / 3600.0
    
    if time_gap_hours > 0:
        distance_km = geodesic(last_location, current_location).km
        speed_kmh = distance_km / time_gap_hours
        
        # ரியல் வேர்ல்டுல லொகேஷன் மாறாம அடுத்தடுத்து கிளிக் பண்ணா ஸ்பீடு ஏறாம இருக்க 0.1 கிமீ செக் வச்சிருக்கோம்
        if speed_kmh > 900.0 and distance_km > 0.1:
            user_data["is_frozen"] = True
            raise HTTPException(status_code=403, detail=f"CRITICAL: Impossible travel detected at {int(speed_kmh)} km/h!")

    # Rate Limiter
    user_data["hits"] = [t for t in user_data["hits"] if current_time - t < 60]
    if len(user_data["hits"]) >= 5:
        raise HTTPException(status_code=429, detail="Too many rapid requests.")
        
    user_data["hits"].append(current_time)
    user_data["last_lat"] = lat
    user_data["last_lon"] = lon
    user_data["last_time"] = current_time
    
    return {"status": "SUCCESS", "current_speed": "Normal / Stationary", "tracked_rpm": len(user_data["hits"])}