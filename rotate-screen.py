#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import subprocess
import re
from pathlib import Path
from typing import NamedTuple

orientations = ['normal', 'right', 'inverted', 'left']


class Screen(NamedTuple):
    """
    The xrandr-name of a screen and a list of xinput-device-names that shall be mapped to the screen.
    """
    name: str
    devices: list[str]


def main():
    rotate_clockwise()


def rotate_clockwise():
    # Screens from configuration that are connected.
    screens = [screen for screen in Config().get_screens()
               if Xrandr.is_connected(screen.name)]

    if len(screens) == 0:
        raise Exception('None of the configured screens are connected.')

    current_orientation = Xrandr.get_orientation(screens[0].name)
    next_orientation = orientations[(orientations.index(current_orientation) + 1) % len(orientations)]

    for screen in screens:
        rotate(screen, next_orientation)


def rotate(screen: Screen, orientation):
    Xrandr.rotate(screen.name, orientation)
    for device in screen.devices:
        Xinput.map_to_output(device, screen.name)


class Config:
    """
    Json structure:

        {
          # List of screen names from xrandr:
          "screens": ["eDP", "HDMI-A-0", "eDP-1"]

          # List of devices from xinput that shall be mapped to a screen.
          "devices": [
            # A device can be identified by its exact name through `name` ...
            {"screen": "eDP-1", "name": "ELAN9038:00"},
            # ... or by `name_contains`.
            {"screen": "eDP-1", "name_contains": "ELAN9038"}
          ]
        }
    """

    def __init__(self):
        self.screens, self.devices = self.load_json()

    def get_screens(self) -> list[Screen]:
        return [Screen(name=screen, devices=self.get_devices_for(screen)) for screen in self.screens]

    def get_devices_for(self, screen: str) -> list[str]:
        device_names = []

        for device in self.devices:
            if device["screen"] != screen:
                continue
            if "name" in device:
                device_names.append(device["name"])
            if "name_contains" in device:
                for x_dev in Xinput.get_device_names():
                    if device["name_contains"] in x_dev:
                        device_names.append(x_dev)

        return device_names

    def load_json(self) -> tuple[list[str], list]:
        j = json.loads(self.get_cfg_path().read_text())
        if "screens" not in j:
            raise Exception("'screens' array missing in cfg.")
        screens = j["screens"]

        if "devices" not in j:
            raise Exception("'devices' array missing in cfg.")
        devices = j["devices"]
        for device in devices:
            if not "name" in device and not "name_contains" in device:
                raise Exception("Device must have 'name' or 'name_contains'.")

        return screens, devices

    @classmethod
    def get_cfg_path(cls) -> Path:
        global_path = Path('/etc/rotate-screen.json')
        if global_path.exists():
            return global_path

        local_path = Path('example.json')
        if local_path.exists():
            return local_path

        raise Exception('No configuration file found.')


class Xrandr:
    @classmethod
    def rotate(cls, screen: str, orientation: str):
        execute(['xrandr', '--output', screen, '--rotate', orientation])

    @classmethod
    def get_orientation(cls, screen: str):
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
        pattern = re.compile(rf'^{re.escape(screen)} connected [^\(]+ \([^\)]+\) (\S+) \([^\)]+\) [^\(]+$',
                             flags=re.MULTILINE)
        match = pattern.search(stdout)
        if match is None: raise Exception(f'Did not find screen {screen} in stdout:\n{stdout}')
        return match.group(1)

    @classmethod
    def is_connected(cls, screen: str):
        """
        Example:
        - stdout includes line: eDP connected primary 2880x1620+0+0 (normal left inverted right x axis y axis) 344mm x 194mm
        - returns: True
        """
        stdout = execute(['xrandr'])
        pattern = re.compile(rf'^({re.escape(screen)} connected .*)$', flags=re.MULTILINE)
        match = pattern.search(stdout)
        return match is not None


class Xinput:
    @classmethod
    def map_to_output(cls, device: str, screen: str):
        execute(['xinput', '--map-to-output', device, screen])

    @classmethod
    def get_device_tuples(cls) -> list[(int, str)]:
        ids = cls.get_device_ids()
        names = [execute(['xinput', 'list', '--name-only', id_]).strip() for id_ in ids]
        return [(id_, name) for id_, name in zip(ids, names)]

    @classmethod
    def get_device_names(cls) -> list[str]:
        return execute(['xinput', 'list', '--name-only']).strip().splitlines()

    @classmethod
    def get_device_ids(cls) -> list[int]:
        return [int(id_) for id_ in execute(['xinput', 'list', '--id-only']).strip().splitlines()]


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
