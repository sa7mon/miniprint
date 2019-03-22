from pyfakefs import fake_filesystem

# Create a fake directory from an existing directory

fs = fake_filesystem.FakeFilesystem()
fos = fake_filesystem.FakeOsModule(fs)

fs.create_dir("/PJL")
fs.create_dir("/PostScript")
fs.create_dir("/saveDevice/SavedJobs/InProgress")
fs.create_dir("/saveDevice/SavedJobs/KeepJob")
fs.create_dir("/webServer/default")
fs.create_dir("/webServer/home")
fs.create_dir("/webServer/lib")
fs.create_dir("/webServer/objects")
fs.create_dir("/webServer/permanent")
fs.create_file("/webServer/default/csconfig")
# fs.create_file("/webServer/home/device.html")
fs.add_real_file(source_path="../fake-files/device.html", read_only=True, target_path="/webServer/home/device.html")
fs.create_file("/webServer/home/hostmanifest")
fs.create_file("/webServer/lib/keys")
fs.create_file("/webServer/lib/security")


a = fs.get_object("/webServer/default/csconfig")
print(fos.stat("/webServer/default/csconfig").st_size)


# print(fs)

# print(fos.path.exists("/webServer/lib/security"))

# paths = ["/webServer", "/webServer/lib", "/asf"]

# for path in paths:
#     print("path: ", path)
#     if not fos.path.exists(path):
#         print("Path doesn't exist.")
#         break

#     for entry in fos.scandir(path):
#         if entry.is_file():
#             print(entry.name, "FILE")
#         elif entry.is_dir():
#             print(entry.name, "DIR")

# print("---------------------")

# paths = ["/webServer/lib", "/webServer/lib/keys"]
# for path in paths:
#     if fos.path.exists(path):
#         a = fs.get_object(path)
#         if type(a) == fake_filesystem.FakeFile:
#             print(path, " - exists - FILE")
#         elif type(a) == fake_filesystem.FakeDirectory:
#             print(path, "- exists - DIR")


    # try:
    #     print(fos.listdir(path))
    #     # for item in fos.listdir(path):
    #     #     # print(item, type(fs.get_object(path+'/'+item)))
    #     #     if type(fs.get_entry(path+'/'+item)) == FakeDirectory:
    #     #         print(item, 'DIR')
    #     #     else:
    #     #         print(item, 'FILE')
    # except OSError as e:
    #     assert e.errno == errno.ENOTDIR, 'unexpected errno: %d' % e.errno
    #     assert e.strerror == 'Not a directory in the fake filesystem'
# print(fos.path.exists("/"))
# print(fos.path.exists("/.."))




