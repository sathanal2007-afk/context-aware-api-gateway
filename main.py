from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import time
import random
from geopy.distance import geodesic

app = FastAPI(title="Sathana's Adaptive Security Gateway")
user_logs = {}  

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise MFA Gateway</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-white min-h-screen flex items-center justify-center p-4">
    <div class="bg-slate-800 p-6 rounded-2xl shadow-2xl w-full max-w-md border border-slate-700 text-center">
        <h1 class="text-2xl font-bold text-emerald-400 mb-2">🛡️ Context & MFA Gateway</h1>
        <p class="text-slate-400 text-sm mb-6">Adaptive location tracking with automated OTP recovery bypass.</p>
        
        <div class="mb-4 text-left">
            <label class="block text-xs font-semibold text-slate-400 uppercase mb-2">Username</label>
            <input type="text" id="username" value="sathana_l" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none">
        </div>

        <!-- Hacker Mode Simulation Checkbox -->
        <div class="mb-4 flex items-center justify-between p-3 bg-slate-900 rounded-xl border border-slate-700">
            <span class="text-xs font-semibold text-rose-400 uppercase tracking-wider">⚠️ Simulate Hacker Attack (US)</span>
            <input type="checkbox" id="hacker-mode" class="w-5 h-5 accent-rose-600 cursor-pointer">
        </div>

        <!-- 🔐 Dynamic MFA OTP Box (Hidden by default) -->
        <div id="mfa-box" class="mb-6 p-4 bg-amber-950/40 border border-amber-600/50 rounded-xl text-left hidden">
            <label class="block text-xs font-semibold text-amber-400 uppercase mb-2">🛡️ Multi-Factor Authentication Required</label>
            <p class="text-xs text-slate-400 mb-3">Impossible travel anomaly detected. Verify identity to unlock account.</p>
            <div class="flex gap-2">
                <input type="text" id="otp-input" placeholder="Enter 4-Digit OTP" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm font-mono focus:outline-none">
                <button onclick="verifyMFA()" class="bg-amber-600 hover:bg-amber-500 font-medium px-4 py-2 rounded-lg text-sm transition">Verify</button>
            </div>
            <p class="text-[11px] text-amber-500 mt-2 font-mono" id="mock-otp-display"></p>
        </div>

        <button onclick="triggerAutoLogin()" id="signin-btn" class="w-full bg-blue-600 hover:bg-blue-500 font-medium py-3 rounded-xl transition shadow-lg">
            Secure Sign In
        </button>

        <div id="status-box" class="mt-6 p-4 bg-slate-900 rounded-xl border border-slate-700 hidden text-sm font-mono text-left">
            Processing...
        </div>
    </div>

    <script>
        let lastGeneratedOTP = "";

        function triggerAutoLogin() {
            const statusBox = document.getElementById('status-box');
            const isHacker = document.getElementById('hacker-mode').checked;
            statusBox.classList.remove('hidden');
            statusBox.innerHTML = "Fetching device GPS coordinates...";

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(async (position) => {
                    let lat = position.coords.latitude;
                    let lon = position.coords.longitude;
                    const username = document.getElementById('username').value;
                    
                    if (isHacker) {
                        lat = 40.7128;
                        lon = -74.0060;
                    }

                    try {
                        const response = await fetch(`/api/gateway?username=${username}&lat=${lat}&lon=${lon}`);
                        const data = await response.json();
                        
                        if (response.status === 200) {
                            statusBox.className = "mt-6 p-4 bg-emerald-950/50 rounded-xl border border-emerald-500 text-emerald-400 font-mono text-left";
                            statusBox.innerHTML = `<b>ACCESS GRANTED ✅</b><br><pre>${JSON.stringify(data, null, 2)}</pre>`;
                            document.getElementById('mfa-box').classList.add('hidden');
                        } else if (response.status === 403) {
                            statusBox.className = "mt-6 p-4 bg-rose-950/50 rounded-xl border border-rose-500 text-rose-400 font-mono text-left";
                            statusBox.innerHTML = `<b>ACCESS DENIED ❌</b><br><pre>${JSON.stringify(data, null, 2)}</pre>`;
                            
                            if(data.otp_triggered) {
                                document.getElementById('mfa-box').classList.remove('hidden');
                                lastGeneratedOTP = data.otp_code;
                                document.getElementById('mock-otp-display').innerHTML = `[SIMULATION LOG]: System dispatched OTP: <b>${data.otp_code}</b> to registered phone.`;
                            }
                        }
                    } catch (e) {
                        statusBox.innerHTML = "Connection Error!";
                    }
                }, (error) => {
                    statusBox.innerHTML = "🛑 Error: Location access denied!";
                });
            }
        }

        async function verifyMFA() {
            const username = document.getElementById('username').value;
            const otpInput = document.getElementById('otp-input').value;
            const statusBox = document.getElementById('status-box');

            try {
                const response = await fetch(`/api/verify-mfa?username=${username}&otp=${otpInput}`);
                const data = await response.json();

                if (response.status === 200) {
                    statusBox.className = "mt-6 p-4 bg-emerald-950/50 rounded-xl border border-emerald-500 text-emerald-400 font-mono text-left";
                    statusBox.innerHTML = `<b>MFA SUCCESS ✅</b><br><pre>${JSON.stringify(data, null, 2)}</pre>`;
                    document.getElementById('mfa-box').classList.add('hidden');
                    document.getElementById('hacker-mode').checked = false;
                } else {
                    alert("Invalid OTP! Security lock sustained.");
                }
            } catch (e) {
                alert("MFA Verification Failed!");
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
    
    if username not in user_logs:
        user_logs[username] = {"last_lat": lat, "last_lon": lon, "last_time": current_time, "is_frozen": False, "active_otp": None}
        return {"status": "ALLOWED", "info": "Initial trusted coordinates established."}
        
    user_data = user_logs[username]
    if user_data["is_frozen"]:
        if not user_data["active_otp"]:
            user_data["active_otp"] = str(random.randint(1000, 9999))
        return JSONResponse(status_code=403, content={"detail": "Account locked. Authentication step-up layer invoked.", "otp_triggered": True, "otp_code": user_data["active_otp"]})

    # Speed calculation
    last_time = user_data["last_time"]
    last_location = (user_data["last_lat"], user_data["last_lon"])
    time_gap_hours = (current_time - last_time) / 3600.0
    
    if time_gap_hours > 0:
        distance_km = geodesic(last_location, (lat, lon)).km
        speed_kmh = distance_km / time_gap_hours
        
        if speed_kmh > 900.0 and distance_km > 1.0:
            user_data["is_frozen"] = True
            user_data["active_otp"] = str(random.randint(1000, 9999))
            return JSONResponse(status_code=403, content={"detail": f"CRITICAL ANOMALY: Velocity of {int(speed_kmh)} km/h breached travel constraints.", "otp_triggered": True, "otp_code": user_data["active_otp"]})

    user_data["last_lat"] = lat
    user_data["last_lon"] = lon
    user_data["last_time"] = current_time
    return {"status": "SUCCESS", "current_speed": "Stationary / Safe"}

@app.get("/api/verify-mfa")
def verify_mfa(username: str, otp: str):
    if username in user_logs and user_logs[username]["active_otp"] == otp:
        user_logs.pop(username) # Flushing cache logs completely
        return {"status": "UNLOCKED", "message": "Telemetry caches flushed. Identity verified via secondary factor authentication channel."}
    return JSONResponse(status_code=401, content={"detail": "Invalid token parameters."})