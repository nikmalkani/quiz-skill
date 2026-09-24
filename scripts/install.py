#!/usr/bin/env python3
"""Install shared quiz and OpenCode /quiz links, or check their status."""

import argparse
import os
from pathlib import Path
import sys


def links():
    source = Path(__file__).resolve().parents[1]
    config = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    opencode = Path(os.environ.get("OPENCODE_CONFIG_DIR", str(config / "opencode")))
    return [(Path.home() / ".agents/skills/quiz", source),
            (opencode / "commands/quiz.md", source / "integrations/opencode/quiz.md")]


def matches(destination, source):
    return destination.is_symlink() and destination.resolve() == source.resolve() and source.exists()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check local links without changing files")
    args = parser.parse_args()
    targets = links()
    if args.check:
        for destination, source in targets:
            print(("Installed: " if matches(destination, source) else "Missing or different: ") + str(destination))
        return 0 if all(matches(d, s) for d, s in targets) else 1
    # Preflight all destinations before making any links; never replace another installation.
    for destination, source in targets:
        if not source.exists():
            print("Missing source: " + str(source), file=sys.stderr)
            return 1
        if os.path.lexists(destination) and not matches(destination, source):
            print("Existing installation left untouched: " + str(destination), file=sys.stderr)
            return 1
    for destination, source in targets:
        if not matches(destination, source):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.symlink_to(source, target_is_directory=source.is_dir())
        print("Installed: " + str(destination))
    print("Start a new Codex/OpenCode session in the repository you want to study.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
