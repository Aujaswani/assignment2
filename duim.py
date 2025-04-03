#!/usr/bin/env python3

import subprocess, sys, os, argparse

"""
OPS445 Assignment 2 - Winter 2025
Program: duim.py 
Author: Your Name Here

This script runs 'du -d 1' on a specified directory, parses the output, and displays
a bar graph for each subdirectory showing disk usage as a percentage of the total.
Supports human-readable sizes (-H) and custom bar lengths (-l).

Date: 2025-04-03
"""

def parse_command_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="DU Improved -- See Disk Usage Report with bar charts",
        epilog="Copyright 2025"
    )
    parser.add_argument("-l", "--length", type=int, default=20,
                        help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action="store_true",
                        help="print sizes in human readable format (e.g. 1K 23M 2G)")
    parser.add_argument("target", nargs="?", default=".",
                        help="The directory to scan.")
    return parser.parse_args()

def percent_to_graph(percent, total_chars):
    """Returns a bar graph string representing a percentage."""
    if percent < 0 or percent > 100:
        raise ValueError("Percentage must be between 0 and 100")
    filled = int(round((percent / 100.0) * total_chars))
    return '=' * filled + ' ' * (total_chars - filled)

def call_du_sub(location):
    """Runs `du -d 1` and returns the output as a list of lines."""
    if not os.path.isdir(location):
        print(f"Error: {location} is not a valid directory.")
        return []
    try:
        proc = subprocess.Popen(['du', '-d', '1', location],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode != 0:
            print("Error executing du:", err.decode().strip())
            return []
        return [line.strip() for line in out.decode().strip().split('\n') if line.strip()]
    except Exception as e:
        print("Exception occurred:", e)
        return []

def create_dir_dict(alist):
    """Parses du output into a dictionary {path: size_in_bytes}."""
    dir_dict = {}
    for line in alist:
        parts = line.split()
        if len(parts) >= 2:
            try:
                dir_dict[parts[1]] = int(parts[0])
            except ValueError:
                continue
    return dir_dict

def human_readable(size):
    """Converts byte size to a human-readable string."""
    for unit in ['B','K','M','G','T']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} P"

if __name__ == "__main__":
    args = parse_command_args()
    target = args.target

    if not os.path.isdir(target):
        print(f"Error: {target} is not a valid directory.")
        sys.exit(1)

    du_lines = call_du_sub(target)
    dir_dict = create_dir_dict(du_lines)
    target_abs = os.path.abspath(target).rstrip('/')

    total_size = None
    for path, size in dir_dict.items():
        if os.path.abspath(path).rstrip('/') == target_abs:
            total_size = size
            break

    if total_size is None:
        print("Error: Could not determine total size for the target directory.")
        sys.exit(1)

    items = [(p, s) for p, s in dir_dict.items() if os.path.abspath(p).rstrip('/') != target_abs]
    items.sort(key=lambda x: x[1], reverse=True)

    for path, size in items:
        percent = (size / total_size) * 100
        bar = percent_to_graph(percent, args.length)
        size_str = human_readable(size) if args.human_readable else f"{size} B"
        print(f"{percent:4.0f}% [{bar}] {size_str:>10}  {path}")

    total_str = human_readable(total_size) if args.human_readable else f"{total_size} B"
    print(f"Total: {total_str}  {target}")
