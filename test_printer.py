from printer import Printer
import logging

logger = logging.getLogger('miniprint')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)5s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def test_echo():
    p = Printer(logger)
    r = p.command_echo('ECHO DELIMITER20687')
    assert r == '@PJL ECHO DELIMITER20687\x1b'
    

def test_fsquery():
    p = Printer(logger)
    r = p.command_fsquery('@PJL FSQUERY NAME="0:/webServer"')
    assert r == '@PJL FSQUERY NAME="0:/webServer" TYPE=DIR'


def test_fsmkdir():
    p = Printer(logger)
    r = p.command_fsmkdir('@PJL FSMKDIR NAME="0:/testdir"')
    assert r == ''
    assert p.does_path_exist("/testdir") == True


def test_fsupload_bad():
    p = Printer(logger)
    r = p.command_fsupload('@PJL FSUPLOAD NAME="0:/none"')
    assert r == '@PJL FSUPLOAD NAME="0:/none"\r\nFILEERROR=3\r\n'


def test_fsupload_good():
    p = Printer(logger)
    r = p.command_fsupload('@PJL FSUPLOAD NAME="0:/webServer/home/device.html"')
    assert r.encode('UTF-8') == b'@PJL FSUPLOAD FORMAT:BINARY NAME="0:/webServer/home/device.html" OFFSET=0 SIZE=165\r\n<html><head>\n<meta http-equiv="Refresh" content="0; URL=this.LCDispatcher?dispatch=html&cat=1&pos=0">\n<title>Printer Content</title></head>\n<body>\n</body></html>'


def test_get_parameters():
    p = Printer(logger)
    params = p.get_parameters('@PJL RDYMSG DISPLAY = "rdymsg"')
    assert params['DISPLAY'] == "rdymsg"

    params = p.get_parameters('@PJL COMMAND A=1 B=2')
    assert params['A'] == "1"
    assert params['B'] == "2"

    params = p.get_parameters('@PJL COMMAND A="value" B=2')
    assert params['A'] == '"value"'
    assert params['B'] == "2"

    params = p.get_parameters('@PJL COMMAND A = 1 B = 2')
    assert params['A'] == "1"
    assert params['B'] == "2"

    params = p.get_parameters('@PJL COMMAND A = 1     B = 2')
    assert params['A'] == "1"
    assert params['B'] == "2"


def test_info_id_default():
    p = Printer(logger)
    r = p.command_info_id("")
    assert r == '@PJL INFO ID\r\nhp LaserJet 4200\r\n\x1b'


def test_info_id_custom():
    printer_id = "my custom printer"
    p2 = Printer(logger, id=printer_id)
    r2 = p2.command_info_id("")
    assert r2 == '@PJL INFO ID\r\n' + printer_id + '\r\n\x1b'
    
    
def test_info_status_default():
    p = Printer(logger)
    r = p.command_info_status("")
    assert r == '@PJL INFO STATUS\r\nCODE=10001\r\nDISPLAY="Ready"\r\nONLINE=True'
    
    
def test_info_status_custom():
    p = Printer(logger, code=140, ready_msg="testing")
    r = p.command_info_status("")
    assert r == '@PJL INFO STATUS\r\nCODE=140\r\nDISPLAY="testing"\r\nONLINE=True'
    

def test_rdymsg():
    p = Printer(logger)
    r = p.command_rdymsg('@PJL RDYMSG DISPLAY="hello"')
    assert p.ready_msg == 'hello'
    assert r == ''
    

def test_ustatusoff():
    p = Printer(logger)
    r = p.command_ustatusoff("")
    assert r == ''