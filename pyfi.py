


# get all files ending with a given extension in a drive or folder
 
import os
import hashlib
import datetime
import traceback
import time

#TODO:  add code for excluding directories
  # http://stackoverflow.com/questions/19859840/excluding-directories-in-os-walk

#Set properties
  
#for multiple file types
filetypes = ['.mp3','.wav']
min_file_size = 100000

#
def modification_date(filename):
    time_of_mod = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(time_of_mod)


# for getting the hex version of md5 
def get_md5(fileObjectToHash, block_size=2024):
    md5 = hashlib.md5()
    while True:
        data = fileObjectToHash.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest() # hex digest is better than digest, for standart use.

outfile = "out.txt"
testfile = "test.mp3"


if os.name == 'nt':
  folder = "C:\\"

elif os.name == 'posix':
      print 'OS is Mac/Linux'
      folder = "/"
else: #quit if not NT
  exit()

  print "All files ending with .txt in folder %s:" % folder
file_list = []
for file_type in filetypes:
  for (paths, dirs, files) in os.walk(folder):
      for file in files:
          if file.endswith(file_type):
              #print file
              filename = os.path.join(paths, file)
              #print filename
              file_list.append(os.path.join(paths, file))
              try:
                  file_to_hash = open(filename,'rb')
                  
              except IOError, e:
                  print 'No such file or directory: %s' %e
                  break
              #print "File to hash " + str(file_to_hash)
              hash = get_md5(file_to_hash)
              file_stat = os.stat(filename)
              out_put_file = open(outfile,'a')
              if file_stat.st_size > min_file_size: 
                out_put_file.write(os.path.join(paths, file) + "," + hash+"," + str(file_stat.st_size)+"," + str(modification_date(filename)) + '\n')
              out_put_file.close()
              # debug
              #print out_put_file
              file_to_hash.close()
#debug
#print out_put_file




