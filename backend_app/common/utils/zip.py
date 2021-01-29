import os
import zipfile
# from io import StringIO
#
#
# class InMemoryZip(object):
#     def __init__(self):
#         # Create the in-memory file-like object
#         self.in_memory_zip = StringIO.StringIO()
#
#     def append(self, filename_in_zip, file_contents):
#         '''Append a file with name filename_in_zip and contents of
#         file_contents to the in-memory zip.'''
#         # Get a handle to the in-memory zip in append mode
#         zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)
#
#         # Write the file to the in-memory zip
#         zf.writestr(filename_in_zip, file_contents)
#
#         # Mark the files as having been created on Windows so that
#         # Unix permissions are not inferred as 0000
#         for zfile in zf.filelist:
#             zfile.create_system = 0
#
#         return self
#
#     def read(self):
#         '''Return a string with the contents of the in-memory zip.'''
#         self.in_memory_zip.seek(0)
#         return self.in_memory_zip.read()
#
#     def writetofile(self, filename):
#         '''Writes the in-memory zip to a file.'''
#         f = file(filename, "w")
#         f.write(self.read())
#         f.close()


def zipdir(path, ziph):
    # ziph is zipfile handle
    abs_src = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        # print(root, dirs, files )
        for file in files:
            absname = os.path.abspath(os.path.join(root, file))
            arcname = absname[len(abs_src) + 1:]
            # print ('zipping %s as %s' % (os.path.join(root, file), arcname))
            # ziph.write(os.path.join(root, file))
            ziph.write(absname, arcname)
