# End-to-End System Demonstration Walkthrough

## 1. Overview

This document provides a guided walkthrough for demonstrating the core capabilities of the **Forest Fire Prediction & Spread Simulation Platform** end-to-end.

---

## 2. Launching the Platform

### Option A: Local Development Mode

Ensure the Python virtual environment and Node packages are ready:

```bash
# Terminal 1: Launch Backend API
source .venv/bin/activate
uvicorn services.api.app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Launch Frontend Development Server
cd apps/web
npm run dev
```

### Option B: Docker Compose

```bash
docker compose up -d
```

Open your browser to: **`http://localhost:5173`**

---

## 3. Step-by-Step Demonstration Script

### Step 1: System Health Verification
1. Direct your browser or terminal to:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
2. Verify response confirms backend operational status, database connectivity, and active version `1.0.0`.

### Step 2: Operational Dashboard & Region Selection
1. Open the web interface at `http://localhost:5173`.
2. Notice the **Operational Attention Banner** at the top:
   - Displays real-time counts of active thermal hotspots.
   - Highlights critical risk alerts for operational commanders.
3. In the left navigation header, use the **Region Selector** dropdown:
   - Switch between **Uttarakhand Forest Division** (`reg-01`) and **Western Ghats Conservation Zone** (`reg-02`).
   - Observe the Leaflet map automatically pan and re-center on the selected region boundary.

### Step 3: Inspect Active Hotspots & Risk Choropleth
1. In the **Layer Catalog** panel on the left, ensure the **Active Hotspots** toggle is enabled:
   - Active satellite detections (MODIS/VIIRS) appear as glowing thermal markers.
   - Click on an active hotspot marker to view its satellite sensor, acquisition timestamp, and FRP (Fire Radiative Power).
2. Toggle on the **24-Hour Fire Susceptibility** layer:
   - The map renders the 500m × 500m risk grid choropleth.
   - Examine the **Risk Legend** in the lower-right corner (Low: Green $\to$ Moderate: Yellow $\to$ High: Orange $\to$ Extreme: Red).
3. In the right analytics drawer, view the **Risk Distribution Histogram**:
   - Displays the percentage breakdown of grid cells across each risk tier.

### Step 4: Configure & Launch 12-Hour Spread Simulation
1. Switch to the **Fire Spread Simulation** tab or drawer panel.
2. Configure environmental simulation inputs:
   - **Wind Speed**: Adjust slider to $25\text{ km/h}$.
   - **Wind Direction**: Set compass heading to $270^\circ$ (Westerly wind pushing east).
   - **Fuel Moisture**: Set to dry conditions ($8\%$).
3. Select an Ignition Source:
   - Choose **From Active Hotspot** (selects the highest FRP detection in the region), or
   - Choose **Custom Map Click** and click directly on a high-risk forest compartment on the map.
4. Click **Launch 12-Hour Simulation**:
   - The frontend immediately dispatches a request to `/api/v1/simulations`.
   - A toast notification confirms task dispatch and displays the asynchronous task ID.
   - The UI enters a non-blocking polling state while the Celery background worker processes the 12-hour Cellular Automata propagation.

### Step 5: Timeline Playback & Spread Analytics
1. Once the simulation completes (typically under 400 milliseconds), the **12-Hour Timeline Scrubber** appears at the bottom.
2. Click the **Play** button:
   - Watch the animated fire perimeter expand across the terrain hour-by-hour ($t = 1\text{h}$ to $t = 12\text{h}$).
   - Notice that spread propagates faster downwind and up steep slopes.
3. Use the timeline slider to scrub manually to specific hours (e.g., $t = 3\text{h}$, $t = 6\text{h}$, $t = 12\text{h}$).
4. Inspect the **Spread Analytics Panel**:
   - **Cumulative Burned Area Chart**: Tracks exponential hectares burned over time.
   - **Front Velocity Chart**: Highlights peak perimeter expansion speed (km/h).
   - **Threat Assessment**: Displays dynamic operational severity rating.

---

## 4. Concluding the Demo

Point out the decoupling of components:
- The ML risk model operates independently on standardized 500m features.
- The 12-hour simulation is completely deterministic, allowing operators to run "what-if" scenarios with varying wind and moisture projections.
- The entire system operates without blocking the interactive UI.
