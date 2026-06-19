"""
Cinesis Good Fit Test - Part B: rank & match loads to the driver profile.

Pipeline: filter by the extracted driver profile (equipment, weight, min rate)
FIRST, then rank the eligible loads by effective rate per mile.

    effective rate/mile = price / (deadhead_to_origin + loaded_miles + deadhead_home)

All distances are straight-line haversine miles from the provided lat/long.
"""

from math import radians, sin, cos, asin, sqrt

# --- Driver profile (extracted in Part A) -----------------------------------
# Keep these in sync with the 'Part A Answer' tab.
DRIVER = {
    "current": (32.7767, -96.7970),          # Dallas, TX (truck's current location)
    "home":    (29.4241, -98.4936),          # San Antonio, TX (home base)
    "min_rate_per_mile": 2.00,               # "above $2 per mile, I'll consider it"
    "equipment": {"hotshot", "gooseneck"},   # "I run a hotshot gooseneck trailer"
    "weight_capacity_lb": 16500,             # not stated; inferred from hotshot/gooseneck class
}

# --- Load board -------------------------------------------------------------
# Missing critical data is stored as None so we flag the row instead of crashing.
LOADS = [
    {"id": "L01", "trailer": "van",       "weight": 42000, "price": 620,
     "origin": (32.7555, -97.3308), "dest": (35.4676, -97.5164)},   # Fort Worth -> Oklahoma City
    {"id": "L02", "trailer": "hotshot",   "weight": 11500, "price": 1600,
     "origin": (29.7604, -95.3698), "dest": (27.5306, -99.4803)},   # Houston -> Laredo
    {"id": "L03", "trailer": "gooseneck", "weight": 14200, "price": 1500,
     "origin": (30.2672, -97.7431), "dest": (27.8006, -97.3964)},   # Austin -> Corpus Christi
    {"id": "L04", "trailer": "van",       "weight": 38000, "price": 1500,
     "origin": (33.0198, -96.6989), "dest": (35.1495, -90.0490)},   # Plano -> Memphis
    {"id": "L05", "trailer": "flatbed",   "weight": 9800,  "price": 640,
     "origin": (31.5493, -97.1467), "dest": (29.4241, -98.4936)},   # Waco -> San Antonio
    {"id": "L06", "trailer": "van",       "weight": 46500, "price": None,
     "origin": (32.5252, -93.7502), "dest": (33.7490, -84.3880)},   # Shreveport -> Atlanta (no price)
    {"id": "L07", "trailer": "hotshot",   "weight": 13400, "price": 1100,
     "origin": (36.1540, -95.9928), "dest": None},                  # Tulsa -> ??? (no destination)
    {"id": "L08", "trailer": "hotshot",   "weight": 12600, "price": 1700,
     "origin": (32.7767, -96.7970), "dest": (26.2034, -98.2300)},   # Dallas -> McAllen
]


def haversine_miles(a, b):
    """Great-circle distance in miles between two (lat, lon) points."""
    R = 3958.8  # Earth radius in miles
    lat1, lon1, lat2, lon2 = map(radians, [a[0], a[1], b[0], b[1]])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(h))


def evaluate(load):
    """Return (eligible: bool, reason: str, effective_rate: float | None)."""
    # 1. Reject incomplete rows we cannot score (don't crash on them).
    if load["price"] is None:
        return False, "missing price", None
    if load["dest"] is None:
        return False, "missing destination", None

    # 2. Filter on the driver profile BEFORE ranking.
    if load["trailer"] not in DRIVER["equipment"]:
        return False, f"trailer '{load['trailer']}' not run by driver", None
    if load["weight"] > DRIVER["weight_capacity_lb"]:
        return False, f"weight {load['weight']} lb over capacity", None

    # 3. Effective rate across all three legs.
    deadhead_to_origin = haversine_miles(DRIVER["current"], load["origin"])
    loaded_miles       = haversine_miles(load["origin"], load["dest"])
    deadhead_home      = haversine_miles(load["dest"], DRIVER["home"])
    total_miles = deadhead_to_origin + loaded_miles + deadhead_home
    rate = load["price"] / total_miles

    # 4. Final filter: must meet the driver's minimum rate.
    if rate < DRIVER["min_rate_per_mile"]:
        return False, f"effective rate {rate:.3f} below minimum", rate
    return True, "eligible", rate


def main():
    eligible = []
    print("Per-load evaluation")
    print("-" * 64)
    for load in LOADS:
        ok, reason, rate = evaluate(load)
        rate_str = f"{rate:.3f}" if rate is not None else "  n/a"
        print(f"{load['id']}: rate={rate_str}  {'OK  ' if ok else 'skip'}  ({reason})")
        if ok:
            eligible.append((load["id"], rate))

    eligible.sort(key=lambda x: x[1], reverse=True)

    print("\nTop 3 eligible loads (by effective rate/mile)")
    print("-" * 64)
    for rank, (load_id, rate) in enumerate(eligible[:3], start=1):
        print(f"{rank}.  {load_id}   {rate:.3f}")


if __name__ == "__main__":
    main()
