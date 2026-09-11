"""Generate fake text files for concurrent search experiments."""

from __future__ import annotations

import argparse
import uuid
from pathlib import Path

from faker import Faker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def generate_files(count: int, output_dir: Path = DATA_DIR) -> list[Path]:
    """Create ``count`` text files named with UUIDs and filled by Faker.

    Args:
        count: Number of files to create.
        output_dir: Directory to write files into.

    Returns:
        Paths of the created files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    faker = Faker()
    created: list[Path] = []

    for _ in range(count):
        path = output_dir / f"{uuid.uuid4()}.txt"
        paragraphs = faker.paragraphs(nb=faker.random_int(min=3, max=8))
        path.write_text("\n\n".join(paragraphs) + "\n", encoding="utf-8")
        created.append(path)

    return created


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Generate N text files with Faker content under data/."
    )
    parser.add_argument(
        "count",
        type=int,
        help="Number of files to generate",
    )
    return parser.parse_args()


def main() -> None:
    """Generate files from the command line."""
    args = parse_args()
    if args.count < 1:
        raise SystemExit("count must be a positive integer")

    files = generate_files(args.count)
    print(f"Generated {len(files)} file(s) in {DATA_DIR}")


if __name__ == "__main__":
    main()
