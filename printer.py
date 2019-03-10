from pyfakefs import fake_filesystem

class Printer:
    def __init__(self, logger, id="hp LaserJet 4200", code=10001, ready_msg="Ready", online=True):
        self.id = id
        self.code = code
        self.ready_msg = ready_msg
        self.online = online
        self.logger = logger
        self.fs = fake_filesystem.FakeFilesystem()
        self.fos = fake_filesystem.FakeOsModule(self.fs)
        self.fs.create_dir("/PJL")
        self.fs.create_dir("/PostScript")
        self.fs.create_dir("/saveDevice/SavedJobs/InProgress")
        self.fs.create_dir("/saveDevice/SavedJobs/KeepJob")
        self.fs.create_dir("/webServer/default")
        self.fs.create_dir("/webServer/home")
        self.fs.create_dir("/webServer/lib")
        self.fs.create_dir("/webServer/objects")
        self.fs.create_dir("/webServer/permanent")
        self.fs.create_file("/webServer/default/csconfig")
        self.fs.create_file("/webServer/home/device.html")
        self.fs.create_file("/webServer/home/hostmanifest")
        self.fs.create_file("/webServer/lib/keys")
        self.fs.create_file("/webServer/lib/security")
    
    
    def get_parameters(self, command):
        request_parameters = {}
        for item in command.split(" "):
            if ("=" in item):
                request_parameters[item.split("=")[0]] = item.split("=")[1]
    
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
            elif type(a) == fake_filesystem.FakeDirectory:
                return_data = "NAME=" + request_parameters["NAME"] + " TYPE=DIR"
        else:
            return_data = "NAME=" + request_parameters["NAME"] + " FILEERROR=3\r\n" # File not found
    
        response='@PJL FSQUERY ' + return_data
        self.logger.info("fsquery - response - " + str(return_data.encode('UTF-8')))
        return response
    
    
    def command_info_id(self, request):
        self.logger.info("info_id - request - ID requested")
        response = '@PJL INFO ID\r\n' + self.id + '\r\n\x1b'
        self.logger.info("info_id - response - " + str(response))
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
            
