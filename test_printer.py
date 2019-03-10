from printer import Printer
import logging

logger = logging.getLogger('miniprint')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)5s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def test_info_id_default():
    p = Printer(logger)
    r = p.command_info_id("")
    assert r == '@PJL INFO ID\r\nhp LaserJet 4200\r\n\x1b'


def test_info_id_custom():
    printer_id = "my custom printer"
    p2 = Printer(logger, id=printer_id)
    r2 = p2.command_info_id("")
    assert r2 == '@PJL INFO ID\r\n' + printer_id + '\r\n\x1b'
    
    
def test_info_status():
    p = Printer(logger)
    r = p.command_info_status("")
    assert r == '@PJL INFO STATUS\r\nCODE=10001\r\nDISPLAY="Ready"\r\nONLINE=True'
    
    
def test_ustatusoff():
    p = Printer(logger)
    r = p.command_ustatusoff("")
    assert r == ''