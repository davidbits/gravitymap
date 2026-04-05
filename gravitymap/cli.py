from __future__ import annotations

import argparse
from datetime import datetime, time, timezone
from pathlib import Path

from gravitymap.physics import evaluate_heatmap
from gravitymap.render import save_field_data, save_heatmap
from gravitymap.solar_system import (
    build_solar_system,
    default_render_moment,
    earth_surface_reference_clock,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a sourced first post-Newtonian proper-time heatmap for the solar system."
    )
    default_moment = default_render_moment()
    parser.add_argument(
        "--date",
        default=default_moment.date().isoformat(),
        help="UTC date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--utc-hour",
        type=float,
        default=float(default_moment.hour),
        help="UTC hour for body positions.",
    )
    parser.add_argument("--output", type=Path, default=Path("outputs/gravitymap.png"))
    parser.add_argument("--data-output", type=Path, default=None)
    parser.add_argument("--width-au", type=float, default=90.0)
    parser.add_argument("--height-au", type=float, default=90.0)
    parser.add_argument("--z-au", type=float, default=0.0)
    parser.add_argument("--resolution", type=int, default=700)
    parser.add_argument(
        "--velocity-model",
        choices=("stationary-barycentric", "circular-solar-orbit"),
        default="stationary-barycentric",
        help="Velocity assigned to sampled grid points.",
    )
    parser.add_argument("--latitude-deg", type=float, default=0.0)
    parser.add_argument("--solar-time-hours", type=float, default=12.0)
    parser.add_argument("--altitude-m", type=float, default=0.0)
    parser.add_argument("--no-moon", action="store_true")
    parser.add_argument("--no-pluto", action="store_true")
    return parser


def _parse_moment(date_text: str, utc_hour: float) -> datetime:
    parsed_date = datetime.strptime(date_text, "%Y-%m-%d").date()
    hour = int(utc_hour)
    minute = int(round((utc_hour - hour) * 60.0))
    if minute == 60:
        hour += 1
        minute = 0
    return datetime.combine(parsed_date, time(hour % 24, minute), tzinfo=timezone.utc)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    moment = _parse_moment(args.date, args.utc_hour)
    bodies = build_solar_system(
        moment=moment,
        include_moon=not args.no_moon,
        include_pluto=not args.no_pluto,
    )
    reference_clock = earth_surface_reference_clock(
        bodies,
        latitude_deg=args.latitude_deg,
        local_solar_time_hours=args.solar_time_hours,
        altitude_m=args.altitude_m,
    )
    result = evaluate_heatmap(
        bodies=bodies,
        reference_clock=reference_clock,
        width_au=args.width_au,
        height_au=args.height_au,
        resolution=args.resolution,
        z_au=args.z_au,
        velocity_model_name=args.velocity_model,
    )

    image_path = save_heatmap(args.output, result, bodies)
    print(f"Saved heatmap to {image_path}")
    print(f"UTC epoch: {moment.isoformat()}")
    print(f"Bodies included: {', '.join(body.name for body in bodies)}")
    print(f"Minimum H: {result.ratio.min():.15f}")
    print(f"Maximum H: {result.ratio.max():.15f}")

    if args.data_output is not None:
        data_path = save_field_data(args.data_output, result)
        print(f"Saved field data to {data_path}")

    return 0
