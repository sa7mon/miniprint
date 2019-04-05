'''
miniprint - a medium interaction printer honeypot
Copyright (C) 2019 Dan Salmon - salmon@protonmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''


from printer import Printer
import logging
from glob import glob
import os

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
    

def test_fsdownload():
    p = Printer(logger)
    c = b'FSDOWNLOAD FORMAT:BINARY SIZE=52 NAME="0:/test2.txt"\r\nthis is a file with only one line and no line breaks\r\n'
    r = p.command_fsdownload(c.decode('UTF-8'))
    assert r == ''

    r = p.command_fsquery('@PJL FSQUERY NAME="0:/test2.txt"')
    assert r == '@PJL FSQUERY NAME="0:/test2.txt" TYPE=FILE SIZE=52'

    c = b'FSDOWNLOAD FORMAT:BINARY SIZE=77 NAME="0:/test2.txt"\r\nthis is a file with 2 lines\nhere is the second line with no ending line break\r\n'
    r = p.command_fsdownload(c.decode('UTF-8'))
    assert r == ''

    r = p.command_fsquery('@PJL FSQUERY NAME="0:/test2.txt"')
    assert r == '@PJL FSQUERY NAME="0:/test2.txt" TYPE=FILE SIZE=77'


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

    params = p.get_parameters('@PJL COMMAND A=45 B="0:/test.txt"\r\nheres a bunch of other data')
    assert params['A'] == "45"
    assert params['B'] == '"0:/test.txt"'


def test_info_id_default():
    p = Printer(logger)
    r = p.command_info_id("")
    assert r == '@PJL INFO ID\r\nhp LaserJet 4200\r\n\x1b'


def test_info_id_custom():
    printer_id = "my custom printer"
    p2 = Printer(logger, printer_id=printer_id)
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
    

def test_raw_print_job():
    p = Printer(logger)
    t = "TEST - this is the first line of my raw print job"
    p.append_raw_print_job(t)
    assert p.current_raw_print_job == t
    assert p.printing_raw_job == True
    p.save_raw_print_job()
    assert p.printing_raw_job == False
    assert p.current_raw_print_job == ''

    files_list = glob(os.path.join("uploads", '*.txt'))
    a = sorted(files_list, reverse=True)[0]
    assert os.path.isfile(a) == True

    contents = ''
    with open(a, 'r') as f:
        contents = f.read()
    assert contents == t


def test_rdymsg():
    p = Printer(logger)
    r = p.command_rdymsg('@PJL RDYMSG DISPLAY="hello"')
    assert p.ready_msg == 'hello'
    assert r == ''


def test_ustatusoff():
    p = Printer(logger)
    r = p.command_ustatusoff("")
    assert r == ''