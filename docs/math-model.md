# Mathematical Model

This document describes the approximation implemented in `gravitymap`.

## 1. Weak-field proper-time rate

For a slowly moving clock in weak gravity, the leading-order proper-time rate is

```text
dτ/dt ≈ 1 + Φ/c² - v²/(2c²)
```

where:

- `t` is a common coordinate time
- `τ` is proper time along the clock's worldline
- `Φ` is the Newtonian gravitational potential
- `v` is the speed of the clock in the chosen coordinate frame
- `c` is the speed of light

This is the first post-Newtonian, or `1PN`, approximation used throughout the project.

## 2. Potential model

At a point `x`, the code computes the total potential as a sum over included bodies:

```text
Φ(x) = - Σ_i G M_i / |x - x_i|
```

for points outside each body.

Inside a body, the implementation switches to a uniform-density sphere potential:

```text
Φ_inside(r) = - G M (3R² - r²) / (2R³)
```

This avoids singular behavior at `r = 0` and keeps the field finite in rendered slices that intersect a planet or the Sun.

## 3. Heatmap normalization

The displayed scalar field is

```text
H(x) =
[1 + Φ(x)/c² - v(x)²/(2c²)]
/
[1 + Φ_ref/c² - v_ref²/(2c²)]
```

where the denominator is computed once from the reference observer on Earth.

Interpretation:

- `H < 1`: local clock slower than reference
- `H = 1`: same rate as reference
- `H > 1`: local clock faster than reference

## 4. Coordinate choices

The app compares all clocks at one common barycentric coordinate time. Body positions are converted into a barycentric frame before the heatmap is evaluated.

That matters because the velocity term depends on the chosen frame. The app currently supports two sampling models:

### `stationary-barycentric`

Each sampled point is assigned zero velocity in the barycentric frame.

This isolates gravitational differences plus the fact that the Earth reference clock itself is moving.

### `circular-solar-orbit`

Each sampled point is assigned the tangential speed of a circular orbit around the Sun at that radius, then shifted by the Sun's barycentric velocity.

This is not a true ephemeris-driven orbit for every point. It is a comparison model intended to show how adding orbital motion changes the field.

## 5. Earth reference observer

The reference clock is constructed from:

- Earth's barycentric orbital state
- Earth rotation
- chosen latitude
- chosen local solar time
- chosen altitude

The local surface point is oriented using:

- Earth's spin axis, approximated by the mean obliquity
- the direction from Earth toward the Sun
- an hour-angle rotation for local solar time

The reference velocity is:

```text
v_ref = v_earth_orbit + (ω_earth × r_surface)
```

where `ω_earth` is the angular velocity vector of Earth rotation.

## 6. Scope and limitations

The current implementation is intentionally not a full relativistic ephemeris package.

It does not include:

- higher-order post-Newtonian terms
- frame-dragging or Kerr corrections
- multipole gravity fields
- light-time corrections
- full worldline integration
- high-precision lunar or planetary ephemerides such as JPL Horizons state vectors

So the correct interpretation is:

- physically motivated and equation-based
- appropriate for weak-field solar-system visualization
- not a precision timing product for navigation or mission design
