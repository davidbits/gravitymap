from __future__ import annotations

import argparse
from pathlib import Path

from gravitymap.physics import evaluate_heatmap
from gravitymap.render import save_field_data, save_heatmap
from gravitymap.solar_system import build_local_solar_system, earth_surface_reference_clock


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a first post-Newtonian proper-time heatmap for the local solar system."
    )
    parser.add_argument("--output", type=Path, default=Path("outputs/gravitymap.png"))
    parser.add_argument("--data-output", type=Path, default=None)
    parser.add_argument("--width-au", type=float, default=12.0)
    parser.add_argument("--height-au", type=float, default=12.0)
    parser.add_argument("--z-au", type=float, default=0.0)
    parser.add_argument("--resolution", type=int, default=600)
    parser.add_argument(
        "--velocity-model",
        choices=("stationary", "circular-solar-orbit"),
        default="stationary",
        help="Velocity assigned to each sampled point.",
    )
    parser.add_argument("--earth-phase-deg", type=float, default=0.0)
    parser.add_argument("--jupiter-phase-deg", type=float, default=60.0)
    parser.add_argument("--no-jupiter", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    bodies = build_local_solar_system(
        earth_phase_deg=args.earth_phase_deg,
        jupiter_phase_deg=args.jupiter_phase_deg,
        include_jupiter=not args.no_jupiter,
    )
    reference_clock = earth_surface_reference_clock(bodies)
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
    print(f"Minimum H: {result.ratio.min():.15f}")
    print(f"Maximum H: {result.ratio.max():.15f}")

    if args.data_output is not None:
        data_path = save_field_data(args.data_output, result)
        print(f"Saved field data to {data_path}")

    return 0
