# gravitymap

`gravitymap` is an interactive visualization tool for comparing how fast clocks tick across the solar system relative to a reference observer on Earth.

It renders a "time heatmap" using a weak-field general relativity approximation: at each sampled point, it estimates the local proper-time rate and divides it by the proper-time rate of a configurable Earth-surface observer.

The project is meant to be physically grounded, visually explorable, and honest about its limits. It is a solar-system timing visualization, not a precision ephemeris or mission-navigation tool.

## What It Shows

For each point in space, `gravitymap` computes:

```text
H(x) = dτ(x) / dτ_ref
```

where:

- `dτ(x)` is the local proper-time rate at the sampled point
- `dτ_ref` is the proper-time rate of the chosen Earth reference observer

The displayed plots use:

```text
(H - 1) × 10^9
```

so colors are shown in parts per billion relative to the Earth reference clock.

Interpretation:

- negative values: time runs slower than the Earth reference
- zero: same rate as the Earth reference
- positive values: time runs faster than the Earth reference

## What The Project Includes

- An interactive Streamlit UI for exploring the solar-system clock-rate field
- A CLI for exporting static PNG heatmaps and raw `.npz` field data
- A first post-Newtonian `1PN` timing model
- Date-dependent solar-system body states
- Sourced masses, radii, and orbital elements for:
  - Sun
  - Moon
  - Mercury through Neptune
  - Pluto

## Physics Summary

The core approximation is:

```text
dτ/dt ≈ 1 + Φ/c² - v²/(2c²)
```

where:

- `Φ` is the summed Newtonian gravitational potential
- `v` is the speed in the chosen coordinate frame
- `c` is the speed of light

This means the map reflects two effects:

- clocks deeper in gravitational wells tick more slowly
- clocks moving faster tick more slowly

The app compares all clocks at a common barycentric coordinate time and normalizes the result to a chosen Earth observer.

For a fuller explanation, see:

- [docs/physics-overview.md](docs/physics-overview.md)
- [docs/math-model.md](docs/math-model.md)

## Data Sources

The current implementation is based on NASA, JPL, and NIST references.

Primary sources used in the code:

- JPL Approximate Positions of the Planets
  <https://ssd.jpl.nasa.gov/planets/approx_pos.html>
- JPL Planetary Physical Parameters
  <https://ssd.jpl.nasa.gov/planets/phys_par.html>
- JPL Planetary Satellite Physical Parameters
  <https://ssd.jpl.nasa.gov/sats/phys_par/>
- JPL Planetary Satellite Mean Elements
  <https://ssd.jpl.nasa.gov/sats/elem/>
- NASA Sun Fact Sheet
  <https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html?level=1>
- NASA Pluto Fact Sheet
  <https://nssdc.gsfc.nasa.gov/planetary/factsheet/plutofact.html?level=1>
- NIST: A Relativistic Framework to Establish Coordinate Time on the Moon and Beyond
  <https://www.nist.gov/publications/relativistic-framework-establish-coordinate-time-moon-and-beyond>
- Ashby and Nelson, *Relativity in Fundamental Astronomy*
  <https://tf.nist.gov/general/pdf/2444.pdf>

For implementation notes and caveats, see:

- [docs/data-and-sources.md](docs/data-and-sources.md)

## Current Accuracy Envelope

This project is designed for exploratory visualization, not precision astrodynamics.

Reasonable uses:

- visualizing the large-scale solar-system proper-time field
- comparing the broad influence of the Sun and major planets
- exploring how gravitational and velocity terms change the heatmap

Important limitations:

- The planetary propagation uses JPL's approximate element series, intended for dates from `1800-01-01` through `2050-12-31`.
- The Moon uses JPL mean orbital elements, which JPL explicitly does not present as high-accuracy ephemerides.
- Pluto is propagated from fact-sheet elements and an inferred mean motion, which is weaker than using a modern ephemeris.
- The model is `1PN` only and does not include higher-order relativistic corrections, multipole gravity fields, light-time effects, or full worldline integration.

## Installation

This project uses `uv`.

```bash
uv sync
```

## Running The Interactive UI

Launch the app with:

```bash
uv run gravitymap-ui
```

This starts a local Streamlit server. In the sidebar you can change:

- UTC date and hour
- field of view
- slice height `z`
- grid resolution
- velocity model
- Earth reference latitude
- local solar time
- altitude
- Moon and Pluto inclusion

## Exporting Static Heatmaps

You can also generate files directly from the CLI:

```bash
uv run python -m gravitymap --output outputs/gravitymap.png --data-output outputs/gravitymap.npz
```

Example:

```bash
uv run python -m gravitymap \
  --date 2026-04-05 \
  --utc-hour 12 \
  --width-au 90 \
  --height-au 90 \
  --resolution 700 \
  --velocity-model stationary-barycentric \
  --output outputs/full-system.png \
  --data-output outputs/full-system.npz
```

Useful flags:

- `--date YYYY-MM-DD`
- `--utc-hour 12`
- `--width-au 90`
- `--height-au 90`
- `--z-au 0`
- `--resolution 700`
- `--velocity-model stationary-barycentric`
- `--velocity-model circular-solar-orbit`
- `--latitude-deg 0`
- `--solar-time-hours 12`
- `--altitude-m 0`
- `--no-moon`
- `--no-pluto`

## Velocity Models

The current grid supports two comparison modes:

### `stationary-barycentric`

Each sampled point is treated as stationary in the barycentric frame.

This is the cleaner choice if you want to isolate gravitational structure relative to the moving Earth reference clock.

### `circular-solar-orbit`

Each sampled point is assigned the speed of a circular orbit around the Sun at that radius.

This is a comparison model, not a claim that every sampled location is occupied by an object on a physically realized orbit.

## Project Structure

- [gravitymap/app.py](gravitymap/app.py): Streamlit UI
- [gravitymap/ui.py](gravitymap/ui.py): UI launcher
- [gravitymap/cli.py](gravitymap/cli.py): static export CLI
- [gravitymap/physics.py](gravitymap/physics.py): timing field calculations
- [gravitymap/solar_system.py](gravitymap/solar_system.py): body-state generation
- [gravitymap/catalog.py](gravitymap/catalog.py): sourced body constants and references
- [docs/physics-overview.md](docs/physics-overview.md): conceptual explanation
- [docs/math-model.md](docs/math-model.md): equations and approximations
- [docs/data-and-sources.md](docs/data-and-sources.md): sources and caveats

## Development

Run the tests with:

```bash
uv run python -m unittest discover -s tests -v
```

## Roadmap

Natural next steps, if higher fidelity is needed:

- replace approximate orbital propagation with JPL Horizons or SPICE state vectors
- add more bodies or optional satellite sets
- add alternate slices or volumetric views
- integrate worldline accumulation instead of only instantaneous rate comparison
- add uncertainty notes directly into the UI
