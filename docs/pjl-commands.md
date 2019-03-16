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

#### INFO MEMORY
* **Request**: 
	`.%-12345X@PJL INFO MEMORY @PJL ECHO DELIMITER49751 .%-12345X`
	
* **Reponse:**:
	
	```
	@PJL INFO MEMORY
	TOTAL=27435520
	LARGEST=15505376
	.@PJL ECHO DELIMITER49751
	.
	```

#### INFO PAGECOUNT
* **Reqest**:
	`.%-12345X@PJL INFO PAGECOUNT@PJL ECHO DELIMITER60705.%-12345X`

* **Response**:
	```
	@PJL INFO PAGECOUNT
	711797
	.@PJL ECHO DELIMITER60705
	.
	```
	
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
* **Request**:
	
	Directory: `.%-12345X@PJL FSDELETE NAME="0:/newdir".%-12345X`
	
* **Response**:

	`(Empty ACK)`
### FSDOWNLOAD
* **Request**:
	```
	.%-12345X@PJL FSDOWNLOAD FORMAT:BINARY SIZE=47 NAME="0:/put_test.txt"
	this is a file I'm uploading from my Mac

	.%-12345X.%-12345X@PJL FSQUERY NAME="0:/put_test.txt"
	@PJL ECHO DELIMITER30896

	.%-12345X
	```

* **Response**:
	
	`(Empty ACK)`

### FSINIT
### FSMKDIR
* **Request**:

	`.%-12345X@PJL FSMKDIR NAME="0:/newdir".%-12345X`

* **Response**:

	`(Empty ACK)`

### FSQUERY
### FSUPLOAD
* **Request**:
	
	`.%-12345X@PJL FSUPLOAD NAME="0:/webServer/home/device.html" OFFSET=0 SIZE=171@PJL ECHO DELIMITER45288.%-12345X`
	
* **Response**:

	```
	@PJL FSUPLOAD FORMAT:BINARY NAME="0:/webServer/home/device.html" OFFSET=0 SIZE=171
	<html><head>
	<meta http-equiv="Refresh" content="0; URL=this.LCDispatcher?dispatch=html&cat=1&pos=0">
	<title>Printer Content</title></head>
	<body>
	</body></html>.@PJL ECHO DELIMITER45288.
	```
