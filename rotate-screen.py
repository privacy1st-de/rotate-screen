#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import subprocess
import re
from pathlib import Path
from typing import NamedTuple

orientations = ['normal', 'right', 'inverted', 'left']


class Screen(NamedTuple):
    name: str
    devices: list[str]


def main():
    rotate_clockwise()


def rotate_clockwise():
    cfg = get_cfg()

    # screens from cfg that are connected
    screens = [Screen(name=name, devices=list(cfg[name].values()))
               for name in cfg
               if name != cfg.default_section
               and is_connected(name)]

    if len(screens) == 0:
        raise Exception('None of the configured screens are connected.')

    current_orientation = get_current_orientation(screens[0].name)
    next_orientation = orientations[(orientations.index(current_orientation) + 1) % len(orientations)]

    for screen in screens:
        rotate(screen, next_orientation)


def get_cfg() -> configparser.ConfigParser:
    config: configparser.ConfigParser = configparser.ConfigParser()
    config.read(get_cfg_path())
    return config


def get_cfg_path() -> Path:
    global_path = Path('/etc/rotate-screen.cfg')
    if global_path.exists():
        return global_path

    local_path = Path('example.cfg')
    if local_path.exists():
        return local_path

    raise Exception('No configuration file found.')


def rotate(screen: Screen, orientation):
    execute(['xrandr', '--output', screen.name, '--rotate', orientation])
    for device in screen.devices:
        execute(['xrandr', '--map-to-output', device, screen.name])


def get_current_orientation(screen: str):
    """
    @precond: is_connected(screen) = True

    Example:
    - stdout includes line: eDP connected primary 2880x1620+0+0 (0x55) normal (normal left inverted right x axis y axis) 344mm x 194mm
    - screen: eDP
    - returns: normal

    Example:
    - stdout includes line: eDP-1 connected 1920x1280+0+0 (0x46) normal (normal left inverted right x axis y axis) 222mm x 148mm
    - screen: eDP-1
    - returns: normal
    """
    stdout = execute(['xrandr', '--query', '--verbose'])
    # pattern = re.compile(rf'^{re.escape(screen)} .* \([^\)]+\) (\S+) \([^\)]+\) .*$', flags=re.MULTILINE)
    pattern = re.compile(rf'^{re.escape(screen)} connected [^\(]+ \([^\)]+\) (\S+) \([^\)]+\) [^\(]+$', flags=re.MULTILINE)
    match = pattern.search(stdout)
    if match is None: raise Exception(f'Did not find screen {screen} in stdout:\n{stdout}')
    return match.group(1)


def is_connected(screen: str):
    """
    Example:
    - stdout includes line: eDP connected primary 2880x1620+0+0 (normal left inverted right x axis y axis) 344mm x 194mm
    - returns: True
    """
    stdout = execute(['xrandr'])
    pattern = re.compile(rf'^({re.escape(screen)}\sconnected\s.*)$', flags=re.MULTILINE)
    match = pattern.search(stdout)
    return match is not None


def execute(command: list[str]) -> str:
    """
    :return: stdout of command execution
    """
    completed: subprocess.CompletedProcess = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise Exception(f'Exit Code: {completed.returncode}\n'
                        f'Stdout:\n{completed.stdout}\n'
                        f'Stderr:\n{completed.stderr}')
    return completed.stdout


if __name__ == '__main__':
    main()
