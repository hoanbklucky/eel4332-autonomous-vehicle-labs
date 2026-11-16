#!/usr/bin/env python3
"""Confirm server-side model state before the course launch opens its GUI."""
import argparse
import re
import subprocess
import time


def matches(output, world, name):
    return (f'world [{world}]' in output
            and re.search(r'^\s*-\s*Name:\s*' + re.escape(name) + r'\s*$', output, re.M)
            and 'Pose [' in output)


def wait(world, name, timeout):
    deadline = time.monotonic() + timeout
    last = ''
    while time.monotonic() < deadline:
        try:
            result = subprocess.run(['gz', 'model', '-m', name, '--pose'],
                                    capture_output=True, text=True,
                                    timeout=min(10.0, max(0.1, deadline-time.monotonic())))
            last = result.stdout + '\n' + result.stderr
            if result.returncode == 0 and matches(last, world, name):
                print(result.stdout, flush=True)
                return True
        except subprocess.TimeoutExpired:
            last = 'Timed out waiting for gz model state.'
        time.sleep(0.5)
    print(f'Could not verify {name!r} in world {world!r}. Last query:\n{last}', flush=True)
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--world', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--timeout', type=float, default=90.0)
    args = parser.parse_args()
    raise SystemExit(0 if wait(args.world, args.name, args.timeout) else 1)
