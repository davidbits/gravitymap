from __future__ import annotations

from datetime import date, datetime, time, timezone

import pandas as pd
import streamlit as st

from gravitymap.catalog import BODY_DEFINITIONS, SOURCES
from gravitymap.constants import AU
from gravitymap.physics import evaluate_heatmap
from gravitymap.render import build_plotly_figure
from gravitymap.solar_system import (
    build_solar_system,
    earth_surface_reference_clock,
    valid_approximation_window,
)


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
          --gm-bg: linear-gradient(145deg, #f8f1dd 0%, #fffaf2 45%, #dce7f2 100%);
          --gm-card: rgba(255, 252, 246, 0.86);
          --gm-ink: #1c2a39;
          --gm-accent: #8b4f2a;
        }
        .stApp {
          background: var(--gm-bg);
          color: var(--gm-ink);
        }
        .gm-hero {
          background: var(--gm-card);
          border: 1px solid rgba(28, 42, 57, 0.08);
          border-radius: 20px;
          padding: 1.2rem 1.4rem;
          box-shadow: 0 10px 35px rgba(28, 42, 57, 0.08);
        }
        .gm-small {
          color: #4f6475;
          font-size: 0.96rem;
        }
        h1, h2, h3 {
          font-family: "Georgia", "Times New Roman", serif;
          letter-spacing: 0.01em;
        }
        [data-testid="stMetricValue"] {
          color: var(--gm-accent);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _compose_moment(observation_date: date, utc_hour: float) -> datetime:
    hour = int(utc_hour)
    minute = int(round((utc_hour - hour) * 60.0))
    if minute == 60:
        hour += 1
        minute = 0
    return datetime.combine(
        observation_date, time(hour % 24, minute), tzinfo=timezone.utc
    )


@st.cache_data(show_spinner=False)
def _compute_scene(
    observation_date_iso: str,
    utc_hour: float,
    include_moon: bool,
    include_pluto: bool,
    latitude_deg: float,
    local_solar_time_hours: float,
    altitude_m: float,
    width_au: float,
    height_au: float,
    z_au: float,
    resolution: int,
    velocity_model: str,
):
    observation_date = date.fromisoformat(observation_date_iso)
    moment = _compose_moment(observation_date, utc_hour)
    bodies = build_solar_system(
        moment=moment,
        include_moon=include_moon,
        include_pluto=include_pluto,
    )
    reference_clock = earth_surface_reference_clock(
        bodies,
        latitude_deg=latitude_deg,
        local_solar_time_hours=local_solar_time_hours,
        altitude_m=altitude_m,
    )
    result = evaluate_heatmap(
        bodies=bodies,
        reference_clock=reference_clock,
        width_au=width_au,
        height_au=height_au,
        resolution=resolution,
        z_au=z_au,
        velocity_model_name=velocity_model,
    )
    return moment, bodies, reference_clock, result


def run() -> None:
    st.set_page_config(page_title="gravitymap", layout="wide")
    _apply_styles()

    min_date, max_date = valid_approximation_window()

    st.markdown(
        """
        <div class="gm-hero">
          <h1>gravitymap</h1>
          <div class="gm-small">
            Interactive first post-Newtonian proper-time heatmap of the sourced solar system,
            normalized to a reference observer on Earth's surface.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Scene")
        observation_date = st.date_input(
            "UTC date", value=date(2026, 4, 5), min_value=min_date, max_value=max_date
        )
        utc_hour = st.slider(
            "UTC hour", min_value=0.0, max_value=23.75, value=12.0, step=0.25
        )
        view_preset = st.selectbox(
            "View preset",
            ("Full solar system", "Outer planets", "Inner system", "Custom"),
        )

        if view_preset == "Full solar system":
            width_au = height_au = 90.0
        elif view_preset == "Outer planets":
            width_au = height_au = 40.0
        elif view_preset == "Inner system":
            width_au = height_au = 4.0
        else:
            width_au = st.slider(
                "Width [AU]", min_value=0.5, max_value=120.0, value=20.0, step=0.5
            )
            height_au = st.slider(
                "Height [AU]", min_value=0.5, max_value=120.0, value=20.0, step=0.5
            )

        z_au = st.slider(
            "Slice z [AU]", min_value=-5.0, max_value=5.0, value=0.0, step=0.1
        )
        resolution = st.slider(
            "Resolution", min_value=200, max_value=900, value=500, step=50
        )
        velocity_model = st.selectbox(
            "Grid velocity model",
            ("stationary-barycentric", "circular-solar-orbit"),
        )

        st.header("Reference Clock")
        latitude_deg = st.slider(
            "Latitude [deg]", min_value=-90.0, max_value=90.0, value=0.0, step=1.0
        )
        local_solar_time_hours = st.slider(
            "Local solar time [hours]",
            min_value=0.0,
            max_value=23.5,
            value=12.0,
            step=0.5,
        )
        altitude_m = st.slider(
            "Altitude [m]", min_value=0, max_value=10000, value=0, step=100
        )

        st.header("Bodies")
        include_moon = st.checkbox("Include Moon", value=True)
        include_pluto = st.checkbox("Include Pluto", value=True)

    moment, bodies, reference_clock, result = _compute_scene(
        observation_date.isoformat(),
        utc_hour,
        include_moon,
        include_pluto,
        latitude_deg,
        local_solar_time_hours,
        float(altitude_m),
        width_au,
        height_au,
        z_au,
        resolution,
        velocity_model,
    )

    delta_ppb = (result.ratio - 1.0) * 1e9
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Bodies", len(bodies))
    metric_col2.metric("Min Δ", f"{delta_ppb.min():.3f} ppb")
    metric_col3.metric("Max Δ", f"{delta_ppb.max():.3f} ppb")
    metric_col4.metric("Reference factor", f"{reference_clock.factor:.12f}")

    left, right = st.columns((3.2, 1.2))
    with left:
        st.plotly_chart(build_plotly_figure(result, bodies), use_container_width=True)
    with right:
        st.subheader("Epoch")
        st.write(moment.isoformat())
        st.subheader("Reference observer")
        st.write(
            f"Latitude {reference_clock.latitude_deg:.1f}°, local solar time "
            f"{reference_clock.local_solar_time_hours:.1f} h, altitude {reference_clock.altitude_m:.0f} m."
        )
        st.subheader("Included bodies")
        st.write(", ".join(body.name for body in bodies))

    st.subheader("Current body states")
    body_rows = [
        {
            "Body": body.name,
            "Mass (kg)": body.mass_kg,
            "Radius (km)": body.radius_m / 1_000.0,
            "x (AU)": body.position_m[0] / AU,
            "y (AU)": body.position_m[1] / AU,
            "z (AU)": body.position_m[2] / AU,
            "Sources": ", ".join(BODY_DEFINITIONS[body.name].source_ids),
        }
        for body in bodies
    ]
    st.dataframe(pd.DataFrame(body_rows), use_container_width=True, hide_index=True)

    with st.expander("Model and source notes"):
        st.markdown(
            """
            The heatmap uses the weak-field 1PN approximation

            `dτ/dt ≈ 1 + Φ/c² - v²/(2c²)`

            and normalizes every sampled point to the Earth-surface reference clock chosen in the sidebar.

            Notes:
            - Planetary positions use JPL's approximate Keplerian elements and rates, valid from 1800-01-01 to 2050-12-31.
            - The Moon uses JPL's mean lunar elements, which JPL explicitly describes as descriptive rather than high-precision ephemerides.
            - Pluto propagation uses the NASA fact-sheet J2000 elements with mean motion inferred from the cited sidereal period.
            - Interior potentials are modeled as uniform spheres to keep the field finite inside bodies.
            """
        )
        for source in SOURCES:
            st.markdown(f"- [{source.title}]({source.url}): {source.note}")


if __name__ == "__main__":
    run()
