# RotateScreen

## Usage

Rotate your screen, touchscreen and pen clockwise:

```shell
rotate-screen
```

Example output on a Microsoft Surface Go 2:

```
Rotating eDP-1 ...
  Mapping ELAN9038:00 04F3:2A1C to eDP-1
  Mapping ELAN9038:00 04F3:2A1C Stylus Pen (0) to eDP-1
  Mapping ELAN9038:00 04F3:2A1C Stylus Eraser (0) to eDP-1
  Mapping ELAN9038:00 04F3:2A1C Stylus to eDP-1
Mapping of ELAN9038:00 04F3:2A1C Stylus to eDP-1 failed
```

## Further ideas

```python
def get_sensor_orientation():
    """
    Get rotation from `monitor-sensor`.
    Example:
    - stdout: === Has accelerometer (orientation: left-up)
    - stdout:     Accelerometer orientation changed: left-up
    """
```
