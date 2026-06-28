from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import time
from geopy.distance import geodesic

app = FastAPI(title="Sathana's Adaptive Mobile Firewall")

# Global memory to track users
user_logs = {}  

# HTML UI Template for Mobile View
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Context-Aware Gateway</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-white font-sans min-h-screen flex items-center justify-center p-4">
    <div class="bg-slate-800 p-6 rounded-2xl shadow-2xl w-full max-w-md border border-slate-700">
        <!-- Header -->
        <div class="text-center mb-6">
            <h1 class="text-2xl font-bold text-emerald-400">🛡️ Security Gateway</h1>
            <p class="text-slate-400 text-sm mt-1">Context-Aware Real-time Mitigation Dashboard</p>
        </div>

        <!-- Status Card -->
        <div id="status-card" class="bg-slate-700 p-4 rounded-xl text-center mb-6 border border-slate-600 transition-all duration-300">
            <span class="text-xs font-semibold uppercase tracking-wider text-slate-400 block">System Status</span>
            <span id="status-text" class="text-xl font-bold text-blue-400 mt-1 block">READY FOR TESTING</span>
        </div>

        <!-- Simulator Buttons -->
        <div class="space-y-4">
            <div>
                <label class="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">1. Profile Target</label>
                <input type="text" id="username" value="sathana_l" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500">
            </div>

            <div class="pt-2">
                <label class="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">2. Simulate Scenarios</label>
                <div class="grid grid-cols-1 gap-3">
                    <button onclick="sendTelemetry(13.08, 80.27)" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-3 px-4 rounded-xl transition duration-200 shadow-lg flex items-center justify-center gap-2">
                        📍 Hit 1: Login from Chennai
                    </button>
                    <button onclick="sendTelemetry(40.71, -74.00)" class="w-full bg-rose-600 hover:bg-rose-500 text-white font-medium py-3 px-4 rounded-xl transition duration-200 shadow-lg flex items-center justify-center gap-2">
                        🚀 Hit 2: Instant Login from US (Hack Attempt)
                    </button>
                </div>
            </div>
        </div>

        <!-- Analytics Output -->
        <div class="mt-6 bg-slate-900 rounded-xl p-4 border border-slate-700">
            <span class="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-2">Live Server Response logs</span>
            <pre id="log-output" class="text-xs text-slate-300 whitespace-pre-wrap font-mono bg-black/30 p-2 rounded max-h-40 overflow-y-auto">Click any scenario button above to trigger baseline firewall verification pipeline...</pre>
        </div>
    </div>

    <script>
        async function sendTelemetry(lat, lon) {
            const username = document.getElementById('username').value;
            const logBox = document.getElementById('log-output');
            const statusCard = document.getElementById('status-card');
            const statusText = document.getElementById('status-text');

            try {
                const response = await fetch(`/api/gateway?username=${username}&lat=${lat}&lon=${lon}`);
                const data = await response.json();

                if (response.status === 200) {
                    logBox.textContent = JSON.stringify(data, null, 2);
                    statusCard.className = "bg-emerald-950/50 p-4 rounded-xl text-center mb-6 border border-emerald-500 transition-all duration-300";
                    statusText.className = "text-xl font-bold text-emerald-400 mt-1 block";
                    statusText.textContent = "ACCESS ALLOWED ✅";
                } else {
                    logBox.textContent = JSON.stringify(data, null, 2);
                    statusCard.className = "bg-rose-950/50 p-4 rounded-xl text-center mb-6 border border-rose-500 transition-all duration-300";
                    statusText.className = "text-xl font-bold text-rose-400 mt-1 block";
                    statusText.textContent = "ACCESS DENIED ❌";
                }
            } catch (error) {
                logBox.textContent = "Connection Error or Security Constraint Breached!";
                statusCard.className = "bg-rose-950/50 p-4 rounded-xl text-center mb-6 border border-rose-500 transition-all duration-300";
                statusText.className = "text-xl font-bold text-rose-400 mt-1 block";
                statusText.textContent = "BLOCKED 🛑";
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
        return {"status": "ALLOWED", "message": "Telemetry profile initialized smoothly."}
        
    user_data = user_logs[username]
    
    if user_data["is_frozen"]:
        raise HTTPException(status_code=403, detail="CRITICAL: Account locked permanently due to travel anomaly.")

    # Impossible Travel Detection Engine
    last_time = user_data["last_time"]
    last_location = (user_data["last_lat"], user_data["last_lon"])
    time_gap_hours = (current_time - last_time) / 3600.0
    
    if time_gap_hours > 0:
        distance_km = geodesic(last_location, current_location).km
        speed_kmh = distance_km / time_gap_hours
        
        if speed_kmh > 900.0:
            user_data["is_frozen"] = True
            raise HTTPException(status_code=403, detail=f"ALERT: Impossible travel at {int(speed_kmh)} km/h detected! Session frozen.")

    # Rate Limiter
    user_data["hits"] = [t for t in user_data["hits"] if current_time - t < 60]
    if len(user_data["hits"]) >= 5:
        raise HTTPException(status_code=429, detail="LIMIT BREACHED: Request queue dropped.")
        
    user_data["hits"].append(current_time)
    user_data["last_lat"] = lat
    user_data["last_lon"] = lon
    user_data["last_time"] = current_time
    
    return {"status": "ALLOWED", "active_rpm": len(user_data["hits"]), "velocity_status": "Normal"}