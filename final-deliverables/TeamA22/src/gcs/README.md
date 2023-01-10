# Autonomous Bomber - GCS End

This code is run on the GCS computer and connects directly to the application running on the Raspberry Pi. This code receives telemetry data from pi.py and returns the calculated coordinates of the target.

## Dependencies

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all the dependencies for GCS operation. You don't need to pip install the libraries that come with the standard library. This is an exhaustive list all library requirements on the GCS end.
 - socket (version 1.0.0)
 - keyboard (version 0.13.5)
 - matplotlib (version 3.5.1)
 - jsonlib (version 1.6.1)
 - numpy (version 1.22.3)
 - pickle-mixin (version 1.0.2)
 - sys (standard library)

Example
```bash
pip install matplotlib=3.5.1
```

## Usage
Run the GCS-with-GSD.py file from the command line.
```bash
python GCS-with-GSD.py
```
Make sure to run the file from the directory it's in.

## Files
#### GCS-with-GSD.py
Main script for the ground control station. Reads in telemetry from the copter and calculates the target coordinates.
#### MAP.png
Image of the testing location. Taken from google maps.

## Authors
Ayush Luthra

Alex Wheelis

Kishan Joshi

Harrison Tseng
