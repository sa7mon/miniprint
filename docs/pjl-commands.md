## Kernel Commands 

### ENTER
### COMMENT

## Job separation
### JOB
### EOJ

## Environment

### DEFAULT
### INITIALIZE
### RESET
### SET

## Status Readback
### INQUIRE
### DINQUIRE
### ECHO
### INFO
### USTATUS
### TIMED
### USTATUSOFF

## Device Attendance
### RDYMSG
Request:

`.%-12345X@PJL RDYMSG DISPLAY="My message!"\r\n.%-12345X`

Response:

`(Empty ACK)`

### OPMSG
### STMSG

## File System
### FSAPPEND
### FSDIRLIST
Request to list directory:

`.%-12345X@PJL FSDIRLIST NAME="0:/nonexistent" ENTRY=1 COUNT=65535.%-12345X`

1. Response if directory doesn't exist

	`@PJL FSDIRLIST NAME="0:/nonexistent"\r\nFILEERROR=3\r\n`
2. Response if it does


### FSDELETE
### FSDOWNLOAD
### FSINIT
### FSMKDIR
### FSQUERY
### FSUPLOAD

