#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/validate-platform-matrix.py"
DEVELOPMENT_VERSION_PATH = ROOT / "DEVELOPMENT_VERSION"

EXPECTED_DEVELOPMENT_VERSION = "0.5.5-dev"
PRESERVED_PLATFORM_CONTRACT = "0.5.4"


def fail(message: str) -> None:
    raise AssertionError(message)


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "blueprint_platform_matrix_validator", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        fail("cannot load platform matrix validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if not DEVELOPMENT_VERSION_PATH.is_file():
        fail("0.5.5 development platform-matrix wrapper requires DEVELOPMENT_VERSION")
    development_version = DEVELOPMENT_VERSION_PATH.read_text(encoding="utf-8").strip()
    if development_version != EXPECTED_DEVELOPMENT_VERSION:
        fail(
            f"expected DEVELOPMENT_VERSION={EXPECTED_DEVELOPMENT_VERSION}; "
            f"got {development_version}"
        )

    validator = load_validator()

    # Increment 0 opens the 0.5.5-dev governance lane only. The governed platform
    # matrix and all promoted schemas remain stable 0.5.4 until a later increment
    # explicitly evolves and re-proves that contract.
    validator.DEVELOPMENT_VERSION = PRESERVED_PLATFORM_CONTRACT

    result = validator.main()
    if result != 0:
        fail(f"platform matrix validator returned {result}")

    print(
        "PASS 0.5.5-dev compatibility: exhaustive platform matrix remains "
        f"governed by stable {PRESERVED_PLATFORM_CONTRACT}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
