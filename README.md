# pnpstitch 0.1

PNPStitch is a set of tools to stitch a group of PNG files that have the same
dimension into sheets of pages together with cut lines.

The motivation of the project is to supplement [Squib](
https://github.com/andymeneely/squib) that doesn't have the ability to generate
cut lines on the margin or generate duplex output (yet).

This project consist of two tools:

- `pnpstitch.py`: Stitch a group of PNG files that have the same dimension into
  sheets of pages together with cut lines along the margins.
- `pnpduplex.py`: Combine two PDF files into a single duplex PDF file for use
  in duplex printers.

## Installation

This project depends on the use of Cairo via CFFI. On an Ubuntu system, you'd
need to install libffi-dev through apt:

`sudo apt install libffi-dev libcairo2-dev`.

Would highly recommend that you install this package in a virtualenv and
install the requirements via pip.

## Usage

The documentation of both tools are documented in the usage help.

`pnpstitch.py` has an option to override the page and cut line configuration
to tailor to your printer settings. See `sample_config.ini` for all the
options.
