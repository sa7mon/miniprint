# miniprint

[![Build Status](https://travis-ci.com/sa7mon/miniprint.svg?token=KqpCvMUSb1yeyAUKGDAx&branch=master)](https://travis-ci.com/sa7mon/miniprint)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/6d424ff40c7d494e88b9bfe11c117e1f)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=sa7mon/miniprint&amp;utm_campaign=Badge_Grade)
[![License](https://img.shields.io/github/license/sa7mon/miniprint.svg)](https://github.com/sa7mon/miniprint/blob/master/LICENSE.md)

<img align="right" width="212" height="288" src="https://user-images.githubusercontent.com/3712226/54886937-78f7b180-4e5b-11e9-8ccc-18716f2b5a3b.png">

A medium interaction printer honeypot

## About 

miniprint acts like a standard networked printer that has been accidentally exposed to the public internet. 

It speaks the Printer Job Language (PJL) over the raw network "protocol"

## Features
* A fully-featured virtual filesystem in which attackers can read and write files and directories - nothing gets written to the host
* Any PostScript or plaintext print jobs sent to the printer will be saved to the `uploads/` directory
* Extensive (probably too much) logging
* Shodan Honeycore: 0

## Installation
1. `virtualenv venv && source ./venv/bin/activate` (optional)
1. `pip install -r requirements.txt`
1. `python3 ./miniprint.py`

## Usage
```
usage: miniprint [-b,--bind HOST] [-l,--log-file FILE] [-t,--time-out TIME] [-h]

miniprint - a medium interaction printer honeypot
       by Dan Salmon: @BLTjetpack, github.com/sa7mon 

optional arguments:
  -b, --bind <host>       Bind the server to <host> (default: localhost)
  -l, --log-file <file>   Save all logs to <file> (default: ./miniprint.log)
  -t, --timeout <time>    Wait up to <time> seconds for commands before disconnecting client (default: 120)

  -h, --help  show this help message and exit
```
To interactively attack `miniprint` on localhost, you can use [PRET](https://github.com/RUB-NDS/PRET) with the following command: `python ./pret.py localhost pjl`

Logs are generated in format: `time - loglevel - method - operation - message` and are saved to `miniprint.log` by default.

## Requirements
  * Python >= 3.5

## Printer Protocol Support
| Protocol | Port | Support |
|:--------:|:----:|:-------:|
|    Raw   | 9100 |   Yes   |
|    Web   |  80  |    No   |
|    IPP   |  631 |    No   |
|    LPD   |  515 |    No   |

## Printer Control Language Support
| **Language** | **Support** |
|:------------:|:-----------:|
|      PJL     |      [Yes](https://github.com/sa7mon/miniprint/wiki/PJL-Command-Support)    |
|      PML     |      No     |

## Page Description Language Support
| **Language** | **Support** |
|:------------:|:-----------:|
|      PDF     |      Yes    |
|      XPS     |      No     |
|  PostScript  |      No     |
|   Plaintext  |      Yes    |
|      PCL     |      No     |

## Known Issues
  * PostScript files printed that don't contain `%%EOF` at the end will cause the printer to wait indefinitely for the end of the job.

## Thanks
  * frbexiga at BinaryEdge
  * Jens Müller for the [hacking-printers.net](https://hacking-printers.net/wiki/) wiki
