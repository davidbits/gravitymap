# Physics Overview

`gravitymap` is not trying to show an absolute "speed of time." It shows a relative clock-rate field inside the solar system after choosing a specific reference observer:

- a human on Earth's surface
- at a chosen latitude
- at a chosen local solar time
- at a chosen altitude

Every pixel in the heatmap answers the same question:

```text
If a clock were placed here right now, how fast would it tick compared with the chosen Earth clock?
```

The result is a dimensionless ratio:

```text
H(x) = dτ(x) / dτ_ref
```

where:

- `dτ(x)` is the local proper-time rate at the sampled point
- `dτ_ref` is the proper-time rate of the Earth-based reference observer

## What makes clocks differ

The implementation follows the usual weak-field relativistic picture used in solar-system timing problems:

- deeper gravitational wells make clocks run slower
- faster motion makes clocks run slower

That means the displayed value depends on two things at each point:

- the summed gravitational potential from the included solar-system bodies
- the velocity assigned to the sample point in the chosen comparison frame

## What the colors mean

The UI and exported plots display:

```text
(H - 1) × 10^9
```

So the colors are shown in parts per billion relative to the Earth reference clock.

Interpretation:

- negative values: slower than the Earth reference
- zero: same rate as the Earth reference
- positive values: faster than the Earth reference

## What is actually being compared

This is an instantaneous comparison at one barycentric coordinate time. It is not integrating full worldlines over months or years.

So the map should be read as:

- "clock-rate field at this chosen instant"

not:

- "total elapsed age difference after a journey"

## Why this is still physically meaningful

This kind of comparison is standard in relativistic navigation and time-transfer problems. The key point is that the map becomes meaningful once the reference observer and common coordinate time are fixed.

The project currently uses:

- barycentric solar-system positions and velocities for the included bodies
- a configurable Earth-surface reference observer
- a first post-Newtonian approximation appropriate for weak gravity and non-relativistic motion

## What the app is attempting to show

The app is trying to make three effects visible at once:

1. The Sun dominates the large-scale gravitational structure of the field.
2. Planets and the Moon create small local perturbations on top of that background.
3. Changing the assumed velocity model for the sampled grid changes the clock-rate field, because time dilation depends on motion as well as gravity.

That is why the same spatial slice can change when the velocity model changes, even if the bodies stay in the same positions.
