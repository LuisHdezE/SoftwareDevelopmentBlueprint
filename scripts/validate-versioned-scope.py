#!/usr/bin/env python3
"""Dispatch scoped checks without changing release identity."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def commands(scope, stable, development):
    if scope not in ("skills", "mobile-licensing"):
        raise ValueError("unsupported scope")
    if (stable, development) == ("0.5.4", "0.5.5-dev"):
        # The development validator checks inherited stable contracts, counts,
        # licensing boundary, and frozen release-candidate closure.
        return [("validate-development.py",)]
    if (stable, development) == ("0.5.4", None):
        return [("validate-release-v054.py", "--scope", scope)]
    if stable == "0.5.3" and development in (None, "0.5.4-dev"):
        if scope == "skills":
            return [("validate-skills.py",)]
        result = [("validate-mobile-licensing.py",)]
        if development == "0.5.4-dev":
            result.append(("validate-mobile-licensing-boundary.py",))
        return result
    raise ValueError(f"unsupported version pair: {stable!r}, {development!r}")

def self_test():
    for scope in ("skills", "mobile-licensing"):
        assert commands(scope, "0.5.4", "0.5.5-dev") == [("validate-development.py",)]
        assert commands(scope, "0.5.4", None) == [("validate-release-v054.py", "--scope", scope)]
        for stable, dev in [("0.5.4", ""), ("0.5.4", "0.5.6-dev"), ("0.5.3", "0.5.5-dev"), ("9.9.9", None)]:
            try:
                commands(scope, stable, dev)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid version pair accepted")
    assert commands("skills", "0.5.3", None) == [("validate-skills.py",)]
    assert commands("skills", "0.5.3", "0.5.4-dev") == [("validate-skills.py",)]
    assert commands("mobile-licensing", "0.5.3", None) == [("validate-mobile-licensing.py",)]
    assert commands("mobile-licensing", "0.5.3", "0.5.4-dev") == [
        ("validate-mobile-licensing.py",), ("validate-mobile-licensing-boundary.py",)]
    print("PASS version dispatch matrix: supported pairs and fail-closed unknown pairs")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=["skills", "mobile-licensing"])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.scope is None:
        parser.error("--scope required")
    try:
        stable = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        marker = ROOT / "DEVELOPMENT_VERSION"
        development = marker.read_text(encoding="utf-8").strip() if marker.exists() else None
        plan = commands(args.scope, stable, development)
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    for command in plan:
        print("Dispatch:", *command, flush=True)
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / command[0]), *command[1:]], cwd=ROOT)
        if result.returncode:
            return result.returncode
    return 0

if __name__ == "__main__":
    sys.exit(main())
