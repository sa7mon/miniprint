from pyfakefs import fake_filesystem
import re

class Printer:
    def __init__(self, logger, id="hp LaserJet 4200", code=10001, ready_msg="Ready", online=True):
        self.id = id
        self.code = code
        self.ready_msg = ready_msg
        self.online = online
        self.logger = logger
        self.rexp = re.compile(r'\s+(\S+)\s+=\s+(?:"([^=]+)"|(\S+))')  # Compile once to decrease match time over multiple uses
        self.fs = fake_filesystem.FakeFilesystem()
        self.fos = fake_filesystem.FakeOsModule(self.fs)

        # Filesystem from HP LaserJet 4200n
        self.fs.create_dir("/PJL")
        self.fs.create_dir("/PostScript")
        self.fs.create_dir("/saveDevice/SavedJobs/InProgress")
        self.fs.create_dir("/saveDevice/SavedJobs/KeepJob")
        self.fs.create_dir("/webServer/default")
        self.fs.create_dir("/webServer/home")
        self.fs.create_dir("/webServer/lib")
        self.fs.create_dir("/webServer/objects")
        self.fs.create_dir("/webServer/permanent")
        self.fs.add_real_file(source_path="fake-files/csconfig", read_only=True, target_path="/webServer/default/csconfig")
        self.fs.add_real_file(source_path="fake-files/device.html", read_only=True, target_path="/webServer/home/device.html")
        self.fs.add_real_file(source_path="fake-files/hostmanifest", read_only=True, target_path="/webServer/home/hostmanifest")
        self.fs.create_file("/webServer/lib/keys")
        self.fs.create_file("/webServer/lib/security")
    

    def get_parameters(self, command):
        '''
            Gets key=value pairs seperated by either '=' or ' = '
            Notes:
                - Whitespace can be either a space charater or a \t
                - Whitespace is only required before a key
                    - Example: Immediately after the D in "@PJL COMMAND a=1"
                - Whitespace surrounding the equal sign is optional and may be 0 or many characters
                - String values must be surrounded by double quotes (")

            Valid inputs:
                @PJL COMMAND a = "b" b=2
                @PJL COMMAND a = "asf" b = "asdf"
                @PJL COMMAND a=2 b = "asd"
                @PJL COMMAND DISPLAY = "rdymsg"
                @PJL COMMAND DISPLAY = "rdymsg" OTHER = "asdf"
                @PJL COMMAND A = 1 B = 2
                @PJL COMMAND    A = 1     B = 2
                @PJL COMMAND A = 1 B    =   2

            Invalid inputs:
                @PJL COMMANDA=1
        '''
        request_parameters = {}

        # Get a=b value pairs
        for x in command.split(" "):
            if "=" in x and len(x) > 1:
                key = x.split("=")[0]
                value = x.split("=")[1]
                request_parameters[key] = value

        # Get a = "b" value pairs
        results = self.rexp.finditer(command)
        if results is not None:
            for r in results:
                key = r.group(1)
                value = r.group(2) if r.group(2) is not None else r.group(3)
                if key not in request_parameters:
                    request_parameters[key] = value
    
        return request_parameters
    
    
    def does_path_exist(self, path):
        return self.fos.path.exists(path)
        
    
    def command_echo(self, request):
        self.logger.info("echo - request - Received request for delimiter")
        response = "@PJL " + request
        response += '\x1b'
        self.logger.info("echo - response - Responding with: " + str(response.encode('UTF-8')))
        return response
    
    
    def command_fsdirlist(self, request):
        request_parameters = self.get_parameters(request)
        requested_dir = request_parameters["NAME"].replace('"', '').split(":")[1]
    
        self.logger.debug("fsdirlist - request - Requested dir: '" + requested_dir + "'")
        return_entries = ""
    
        if self.fos.path.exists(requested_dir):
            return_entries = ' ENTRY=1\r\n. TYPE=DIR\r\n.. TYPE=DIR'
            for entry in self.fos.scandir(requested_dir):
                if entry.is_file():
                    return_entries += "\r\n" + entry.name + " TYPE=FILE SIZE=0" #TODO check size
                elif entry.is_dir():
                    return_entries += "\r\n" + entry.name + " TYPE=DIR"
        else:
            return_entries = "FILEERROR = 3" # "file not found"
    
        response = '@PJL FSDIRLIST NAME=' + request_parameters['NAME'] + return_entries
        self.logger.info("fsdirlist - response - " + str(response.encode('UTF-8')))
        return response
        

    def command_fsmkdir(self, request):
        request_parameters = self.get_parameters(request)
        requested_dir = request_parameters["NAME"].replace('"', '').split(":")[1]
        self.logger.info("fsmkdir - request - " + requested_dir)
    
        """
        Check if dir exists
            If it does, do nothing and return empty ACK
            If it doesn't, create dir and return empty ACK
        """
        if self.fos.path.exists(requested_dir):
            pass
        else:
            self.fs.create_dir(requested_dir)
    
        self.logger.info("fsquery - response - Sending empty response")
        return ''
    
    
    def command_fsquery(self, request):
        request_parameters = self.get_parameters(request)
        self.logger.info("fsquery - request - " + request_parameters["NAME"])
    
        requested_item = request_parameters["NAME"].replace('"', '').split(":")[1]
        self.logger.debug("fsquery - request - requested_item: " + requested_item)
        return_data = ''
    
        if (self.fos.path.exists(requested_item)):
            a = self.fs.get_object(requested_item)
            if type(a) == fake_filesystem.FakeFile:
                return_data = "NAME=" + request_parameters["NAME"] + " TYPE=FILE SIZE=0" # TODO Get actual file size
            elif type(a) == fake_filesystem.FakeFileFromRealFile:
                size = self.fos.stat(requested_item).st_size
                return_data = "NAME=" + request_parameters["NAME"] + " TYPE=FILE SIZE=" + str(size)
            elif type(a) == fake_filesystem.FakeDirectory:
                return_data = "NAME=" + request_parameters["NAME"] + " TYPE=DIR"
        else:
            return_data = "NAME=" + request_parameters["NAME"] + " FILEERROR=3\r\n" # File not found
    
        response='@PJL FSQUERY ' + return_data
        self.logger.info("fsquery - response - " + str(return_data.encode('UTF-8')))
        return response
    

    def command_fsupload(self, request):
        request_parameters = self.get_parameters(request)
        self.logger.info("fsupload - request - " + request_parameters["NAME"])
    
        upload_file = request_parameters["NAME"].replace('"', '').split(":")[1]
        self.logger.debug("fsupload - request - requested file: " + upload_file)

        response=''
        self.logger.info("fsupload - response - " + str(response.encode('UTF-8')))
        return response

    
    def command_info_id(self, request):
        self.logger.info("info_id - request - ID requested")
        response = '@PJL INFO ID\r\n' + self.id + '\r\n\x1b'
        self.logger.info("info_id - response - " + str(response.encode('UTF-8')))
        return response
        
        
    def command_info_status(self, request):
        self.logger.info("info_status - request - Client requests status")
        response = '@PJL INFO STATUS\r\nCODE=' + str(self.code) + '\r\nDISPLAY="' + self.ready_msg + '"\r\nONLINE=' + str(self.online)
        self.logger.info("info_status - response - " + str(response.encode('UTF-8')))
        return response 
        
    
    def command_rdymsg(self, request):
        request_parameters = self.get_parameters(request)
        rdymsg = request_parameters["DISPLAY"]
        self.logger.info("rdymsg - request - Ready message: " + rdymsg)
    
        self.ready_msg = rdymsg.replace('"', '')
        self.logger.info("rdymsg - response - Sending back empty ACK")
        return ''
    
    
    def command_ustatusoff(self, request):
        self.logger.info("ustatusoff - request - Request received")
        self.logger.info("ustatusoff - response - Sending empty reply")
        return ''
            
