# gravitymap

`gravitymap` generates a first post-Newtonian proper-time heatmap for the local solar system. The scalar field is

```text
H(x) = [1 + Phi(x)/c^2 - v(x)^2/(2c^2)] / [1 + Phi_earth/c^2 - v_earth^2/(2c^2)]
```

where the reference clock is a human at mean sea level on Earth's equator at local noon, using barycentric coordinate time and weak-field GR.

## What is implemented

- A 1PN proper-time rate calculator using the Newtonian potential of the Sun, Earth, and optionally Jupiter
- A circular-orbit solar-system approximation shifted into the barycentric frame
- An Earth-surface reference clock that includes Earth's orbital and rotational motion
- A CLI that samples a 2D ecliptic slice and renders a heatmap image
- Optional export of the raw field data as a compressed NumPy archive

## Assumptions

- Weak-field, slow-motion regime only
- Circular orbits for Earth and Jupiter, not JPL ephemerides
- Bodies modeled as uniform spheres to avoid singular potentials inside their radii
- Grid clocks use either barycentric rest (`stationary`) or a Sun-centered circular-orbit approximation (`circular-solar-orbit`)
- Earth's obliquity, the Moon, and higher-order PN corrections are omitted

## Usage

Install dependencies and run the default render:

```bash
uv sync
uv run python -m gravitymap
```

Or use the console script:

```bash
uv run gravitymap --output outputs/solar-system.png --data-output outputs/solar-system.npz
```

Useful options:

- `--velocity-model stationary`
- `--velocity-model circular-solar-orbit`
- `--width-au 12 --height-au 12`
- `--resolution 600`
- `--no-jupiter`
- `--earth-phase-deg 0 --jupiter-phase-deg 60`

## Output

The PNG heatmap colors `(H - 1) * 1e9`, so the colorbar is in parts per billion relative to the Earth-surface reference clock. The optional `.npz` file stores:

- `x_au`
- `y_au`
- `ratio`

## Tests

```bash
uv run python -m unittest discover -s tests -v
```
