# gravitymap

`gravitymap` is an interactive solar-system proper-time viewer. It computes a first post-Newtonian scalar field

```text
H(x) = [1 + Phi(x)/c^2 - v(x)^2/(2c^2)] / [1 + Phi_ref/c^2 - v_ref^2/(2c^2)]
```

and compares each sampled point to a configurable reference observer on Earth's surface.

## What changed

- The project now uses sourced body data for the Sun, Moon, Mercury through Neptune, and Pluto.
- Planetary positions are date-dependent instead of fixed circular placeholders.
- There is an interactive UI built with Streamlit and Plotly.
- The export CLI still exists for writing PNG and `.npz` outputs.

## Sources used in the implementation

- JPL Approximate Positions of the Planets
  https://ssd.jpl.nasa.gov/planets/approx_pos.html
- JPL Planetary Physical Parameters
  https://ssd.jpl.nasa.gov/planets/phys_par.html
- NASA Sun Fact Sheet
  https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html?level=1
- JPL Planetary Satellite Physical Parameters
  https://ssd.jpl.nasa.gov/sats/phys_par/
- JPL Planetary Satellite Mean Elements
  https://ssd.jpl.nasa.gov/sats/elem/
- NASA Pluto Fact Sheet
  https://nssdc.gsfc.nasa.gov/planetary/factsheet/plutofact.html?level=1
- NIST: A Relativistic Framework to Establish Coordinate Time on the Moon and Beyond
  https://www.nist.gov/publications/relativistic-framework-establish-coordinate-time-moon-and-beyond
- Ashby and Nelson, Relativity in Fundamental Astronomy
  https://tf.nist.gov/general/pdf/2444.pdf

## Physics model

- Weak-field, slow-motion 1PN approximation only
- All clock rates are compared at a common barycentric coordinate time
- Potentials are summed from the included bodies
- Interior potentials are uniform-sphere approximations so the field stays finite inside each body
- Planetary positions use JPL's approximate element series, which are valid from 1800 through 2050
- The Moon uses JPL mean elements, which are descriptive rather than full ephemerides
- Pluto uses NASA fact-sheet J2000 elements with mean motion inferred from the cited sidereal period

## Install

```bash
uv sync
```

## Launch the UI

```bash
uv run gravitymap-ui
```

This starts a local Streamlit app. The sidebar lets you change:

- UTC date and hour
- view scale and slice height
- grid velocity model
- reference latitude, local solar time, and altitude
- Moon and Pluto inclusion

## Export a static heatmap

```bash
uv run python -m gravitymap --output outputs/gravitymap.png --data-output outputs/gravitymap.npz
```

Useful flags:

- `--date 2026-04-05`
- `--utc-hour 12`
- `--width-au 90 --height-au 90`
- `--resolution 700`
- `--velocity-model stationary-barycentric`
- `--velocity-model circular-solar-orbit`
- `--latitude-deg 0 --solar-time-hours 12`
- `--no-moon`
- `--no-pluto`

## Tests

```bash
uv run python -m unittest discover -s tests -v
```
