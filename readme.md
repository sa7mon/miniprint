# miniprint

[![Build Status](https://travis-ci.com/sa7mon/miniprint.svg?token=KqpCvMUSb1yeyAUKGDAx&branch=master)](https://travis-ci.com/sa7mon/miniprint)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/6d424ff40c7d494e88b9bfe11c117e1f)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=sa7mon/miniprint&amp;utm_campaign=Badge_Grade)
[![License](https://img.shields.io/github/license/sa7mon/miniprint.svg)](https://github.com/sa7mon/miniprint/blob/master/LICENSE.md)


<img align="right" width="212" height="288" src="https://user-images.githubusercontent.com/3712226/54886937-78f7b180-4e5b-11e9-8ccc-18716f2b5a3b.png">

A medium interaction printer honeypot

## About 

miniprint acts like a standard networked printer that has been accidentally exposed to the public internet. 

It speaks the Printer Job Language (PJL) over the raw network "protocol"

## Logs
Logs are in format: `time - loglevel - method - operation - message`

## Requirements
* Python >= 3.5

## Printer Language Support
| **Language** | **Support** |
|:------------:|:-----------:|
|      PJL     |      No     |
|      PCL     |      No     |
|  PostScript  |      No     |

## Printer Protocol Support
| Protocol | Port | Support |
|:--------:|:----:|:-------:|
|    Raw   | 9100 |   Yes   |
|    Web   |  80  |    No   |
|    IPP   |  631 |    No   |
|    LPD   |  515 |    No   |

## PJL Support

|      Category     | PJL Command/Sub-command | Support |
|:-----------------:|:-----------------------:|:-------:|
| Kernel            |          ENTER          |         |
| Kernel            |         COMMENT         |         |
| Job Separation    |           JOB           |         |
| Job Separation    |           EOJ           |         |
| Environment       |         DEFAULT         |         |
| Environment       |        INITIALIZE       |         |
| Environment       |          RESET          |         |
| Environment       |           SET           |         |
| Status Readback   |         INQUIRE         |         |
| Status Readback   |         DINQUIRE        |         |
| Status Readback   |           ECHO          |         |
| Status Readback   |         INFO ID         |   Yes   |
| Status Readback   |       INFO CONFIG       |         |
| Status Readback   |       INFO FILESYS      |         |
| Status Readback   |       INFO MEMORY       |         |
| Status Readback   |      INFO PAGECOUNT     |         |
| Status Readback   |       INFO STATUS       |   Yes   |
| Status Readback   |      INFO VARIABLES     |         |
| Status Readback   |       INFO USTATUS      |         |
| Status Readback   |         USTATUS         |         |
| Status Readback   |          TIMED          |         |
| Status Readback   |        USTATUSOFF       |   Yes   |
| Device Attendance |          RDYMSG         |         |
| Device Attendance |          OPMSG          |         |
| Device Attendance |          STMSG          |         |
| File System       |         FSAPPEND        |         |
| File System       |        FSDIRLIST        |   Yes   |
| File System       |         FSDELETE        |         |
| File System       |        FSDOWNLOAD       |   Yes   |
| File System       |          FSINIT         |         |
| File System       |         FSMKDIR         |   Yes   |
| File System       |         FSQUERY         |   Yes   |
| File System       |         FSUPLOAD        |   Yes   |

## Thanks
* to frbexiga at BinaryEdge
