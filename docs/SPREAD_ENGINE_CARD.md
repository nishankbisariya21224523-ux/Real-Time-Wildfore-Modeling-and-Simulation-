# Spread Engine Model Card: `spread-ca-v001`

## 1. Engine Overview

| Attribute | Details |
|---|---|
| **Engine Identifier** | `spread-ca-v001` |
| **Engine Type** | 2D Discrete Cellular Automata (CA) Simulation Engine |
| **Grid Neighborhood** | Moore Neighborhood (8-connected adjacent cells: N, NE, E, SE, S, SW, W, NW) |
| **Spatial Resolution** | Standardized 500 m × 500 m common spatial grid |
| **Temporal Resolution** | 1-hour discrete simulation steps (up to 12 hours total duration) |
| **Deterministic Guarantee** | Fully deterministic given identical initial active fire locations, terrain, weather, and fixed PRNG seed |
| **Implementation Language** | Python 3.11+ / NumPy / Shapely |

---

## 2. Theoretical Basis & Propagation Mechanics

The spread engine simulates wildland fire propagation across a discrete 2D raster grid. Each cell $c_{(x, y)}$ can occupy one of three states:
- **0: Unburned / Fuel Available**
- **1: Burning / Active Front**
- **2: Burned / Extinguished**

At each simulation hour $t \in [1, 12]$, for every burning cell, the ignition probability $P_{\text{spread}}(c \to n)$ to an adjacent unburned neighbor cell $n$ is computed via a multi-factor empirical propagation model:

$$P_{\text{spread}}(c \to n) = P_{\text{base}} \times K_{\text{wind}} \times K_{\text{slope}} \times K_{\text{fuel}} \times K_{\text{moisture}}$$

### 2.1 Propagation Factors

1. **Base Probability ($P_{\text{base}}$)**: Baseline probability of fire transmission across a 500m distance during a 1-hour interval under standard calm conditions ($P_{\text{base}} \approx 0.15$).
2. **Wind Factor ($K_{\text{wind}}$)**:
   $$\theta = |\theta_{\text{wind}} - \theta_{\text{propagation}}|$$
   $$K_{\text{wind}} = \exp\left(c_w \cdot v_{\text{wind}} \cdot \cos(\theta)\right)$$
   Where $v_{\text{wind}}$ is wind velocity (km/h) and $\theta$ is the angle between wind direction and direction to neighbor $n$. Downwind spread is exponentially amplified; upwind spread is suppressed.
3. **Slope Factor ($K_{\text{slope}}$)**:
   $$K_{\text{slope}} = \exp\left(c_s \cdot \tan(\alpha)\right)$$
   Where $\alpha$ is terrain slope in the direction of propagation. Fire spreads significantly faster upslope due to convective pre-heating of uphill fuels.
4. **Fuel Factor ($K_{\text{fuel}}$)**: Multiplier derived from fuel class (dense dry deciduous forest = 1.4, scrub/grassland = 1.1, moist evergreen = 0.7, non-burnable water/urban = 0.0).
5. **Fuel Moisture Factor ($K_{\text{moisture}}$)**: Derived from relative humidity and recent rainfall; drier fuels accelerate ignition probability.

---

## 3. Output Generation & Spatial Formatting

At each hourly step $t$, the engine outputs:
1. **Perimeter Polygons**: Shapely geometry dissolved union of all active and burned cells, transformed into standard GeoJSON MultiPolygon format.
2. **Burned Area**: Cumulative burned area in hectares ($1 \text{ cell} = 500\text{m} \times 500\text{m} = 25 \text{ hectares}$).
3. **Front Velocity**: Rate of perimeter advancement (km/h) measured as the maximum radial displacement of newly ignited cells over the elapsed hour.
4. **Active Front Count**: Count of active burning cells.
5. **Threat Level Assessment**: Heuristic rating (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`) based on burned area acceleration and front velocity.

---

## 4. Verification & Determinism Audit

Local verification on a $40 \times 40$ test grid (1,600 cells) initialized with 3 ignition points under $25 \text{ km/h}$ westerly winds produced identical results across multiple runs:

- **Run 1 Burned Area at t=12h**: 37,375.0 ha
- **Run 2 Burned Area at t=12h**: 37,375.0 ha
- **Maximum Velocity**: 1.40 km/h (identical across runs)
- **Hourly Perimeter GeoJSON**: Bit-for-bit identical coordinate arrays

---

## 5. Scientific Status & Limitations

> [!WARNING]
> **UNEVEN PHYSICAL CALIBRATION NOTICE**
> The current spread engine is an **engineering heuristic simulation MVP**, developed for interactive scenario planning and operational decision-support demonstration. It has **NOT** been empirically calibrated against observed historical wildland fire burn scars (such as Bandipur 2019 or Simlipal 2021).

### Key Limitations:
- **No Spotting / Firebrand Modeling**: Does not simulate ember lofting and spotting ahead of the main fire perimeter.
- **No Atmosphere-Fire Coupling**: Assumes static or externally forecasted meteorology without microscale fire-induced convective winds or pyrocumulonimbus clouds.
- **No Suppression Interaction**: Does not account for active fire suppression activities (fire lines, aerial retardant drops, backburning).
- **Scale Resolution**: 500m cells smooth over micro-topographical ravines, firebreaks, and local fuel discontinuity.

### Intended Use:
- Macroscopic tactical overview and risk directionality visualization.
- Scenario planning and resource staging exercises.
- **Not certified for tactical life-safety evacuation line drawing without ground reconnaissance.**
