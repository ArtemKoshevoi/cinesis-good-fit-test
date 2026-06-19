# Cinesis — Good Fit Test

Match a driver to the best loads on the board. **Part A** extracts a structured driver
profile from a raw call transcript; **Part B** filters loads against that profile, then
ranks the eligible ones by effective rate per mile:

```
effective rate/mile = price / (deadhead_to_origin + loaded_miles + deadhead_home)
```

All distances are straight-line haversine miles from the provided lat/long.

## Profile

- **Current location:** Dallas, TX — driver is usually around San Antonio but is in Dallas now.
- **Home base:** San Antonio, TX.
- **Minimum rate:** 2.00/mile — "above $2 per mile, I'll consider it."
- **Equipment:** hotshot, gooseneck — "I run a hotshot gooseneck trailer." Flatbed was only
  asked about, not run, so it is excluded.

## Assumptions

The driver never states a weight capacity, so I inferred **16,500 lb** from the
hotshot/gooseneck class. The 44,000 figure comes from the dispatcher, not the driver.
Dallas and San Antonio coordinates were reused from the Loads tab.

## Incomplete rows

L06 (no price) and L07 (no destination) cannot be scored, so they are flagged and skipped
with a reason — never dropped silently and never crashing.

## Rejected

L06 (Shreveport → Atlanta, 46,500 lb) looks attractive but fails on trailer type, weight,
and missing price.

## Run

```bash
python3 solution.py
```

No dependencies beyond the standard library.
