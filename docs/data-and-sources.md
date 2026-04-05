# Data and Sources

This document explains which real solar-system data the current implementation uses, where it comes from, and what the main caveats are.

## Included bodies

The current app includes:

- Sun
- Mercury
- Venus
- Earth
- Moon
- Mars
- Jupiter
- Saturn
- Uranus
- Neptune
- Pluto

These are the bodies that contribute to the gravitational potential in the rendered field.

## Physical parameters used

For each body, the implementation needs at least:

- mass
- representative radius
- orbital elements or another way to estimate state vectors

Those values are mainly taken from NASA/JPL reference tables.

## Planetary orbital data

For Mercury through Neptune, the project uses JPL's "Approximate Positions of the Planets" element series:

- Source: <https://ssd.jpl.nasa.gov/planets/approx_pos.html>

This provides:

- semimajor axis and rate
- eccentricity and rate
- inclination and rate
- mean longitude and rate
- longitude of perihelion and rate
- longitude of ascending node and rate

The implementation converts those Keplerian elements into heliocentric state vectors, then shifts everything into a barycentric frame.

Important caveat:

- JPL states this approximation is intended for roughly `1800 AD` through `2050 AD`.

That date window is therefore the practical validity range of the current app.

## Planet masses and radii

The planetary masses and radii are taken from:

- JPL Planetary Physical Parameters
- Source: <https://ssd.jpl.nasa.gov/planets/phys_par.html>

This is the source used for:

- Mercury through Neptune
- Earth
- Pluto

The Sun is handled separately using:

- NASA Sun Fact Sheet
- Source: <https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html?level=1>

## Moon data

The Moon currently uses two JPL references:

- JPL Planetary Satellite Physical Parameters
  <https://ssd.jpl.nasa.gov/sats/phys_par/>
- JPL Planetary Satellite Mean Elements
  <https://ssd.jpl.nasa.gov/sats/elem/>

These are used for:

- lunar mass and mean radius
- a mean Earth-centered lunar orbit

Important caveat:

- JPL explicitly warns that the mean satellite elements are not intended for high-accuracy ephemeris computation.

So the Moon in this app should be read as:

- physically informed
- visually useful
- not a Horizons-grade lunar state

## Pluto data

Pluto is included because the user asked for the whole solar system, but the handling is less uniform than for the eight major planets.

The current implementation uses:

- JPL physical parameters for mass and radius
- NASA Pluto Fact Sheet for J2000 orbital elements and orbital period

Source:

- <https://nssdc.gsfc.nasa.gov/planetary/factsheet/plutofact.html?level=1>

The code infers Pluto's mean motion from the cited sidereal period and propagates from the J2000 elements.

That is acceptable for a broad visualization, but it is weaker than using a full modern ephemeris.

## Relativity references

The timing model is guided by these references:

- NIST: A Relativistic Framework to Establish Coordinate Time on the Moon and Beyond
  <https://www.nist.gov/publications/relativistic-framework-establish-coordinate-time-moon-and-beyond>
- Ashby and Nelson, Relativity in Fundamental Astronomy
  <https://tf.nist.gov/general/pdf/2444.pdf>

These support the weak-field picture that the local proper-time rate depends primarily on:

- gravitational potential
- velocity

## What the app is trying to show with this data

The app is not claiming to be a precision ephemeris viewer. It is trying to show a sourced and defensible approximation of:

- where the major solar-system masses are
- how those masses shape the gravitational potential
- how local motion assumptions affect the relative proper-time field

## Best interpretation of the current data quality

Reasonable:

- large-scale solar-system structure
- relative scale of the Sun versus planets
- broad timing differences across the inner and outer solar system

Less reliable:

- fine local structure around the Moon
- exact planetary positions far from the supported date range
- precision comparisons that would need JPL Horizons or SPICE kernels

If this project later needs higher fidelity, the next technical step is to replace the approximate element propagation with direct ephemeris states from JPL Horizons or SPICE kernels.
