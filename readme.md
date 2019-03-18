A medium interaction printer honeypot

miniprint acts like a standard networked printer that has been "accidentally" exposed to the public internet

It speaks the Printer Job Language (PJL) over the RAW "protocol".

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
| File System       |        FSDOWNLOAD       |         |
| File System       |          FSINIT         |         |
| File System       |         FSMKDIR         |   Yes   |
| File System       |         FSQUERY         |   Yes   |
| File System       |         FSUPLOAD        |         |

## Thanks
* to frbexiga at BinaryEdge
