


# get all files ending with a given extension in a drive or folder
 
import os
import hashlib
import datetime
import traceback
import time



#Set properties


filetypes = []
#for multiple file types
#filetypes.push = ['.iso','.mp3']

file_type_input = '.mp3'
while file_type_input <> ".0":
  filetypes.append(file_type_input)
  prompt_text = "Please input file types to search for, but don't add the period.\n  Enter '0' if satisfied with - " + ','.join(filetypes) +"\n: "
  file_type_input="."+raw_input(prompt_text)


min_file_size = 0
volume_name = raw_input("Name the volume you're searching (something distinct from other volumes): ")
outfile = "_filefish_out.txt" 

#testfile = "test.mp3"

# Testing a way to ignore directories
ignore = ['Volumes', '.Trash', '.MobileBackups', 'atest', 'Applications']

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


if os.name == 'nt':
  folder = raw_input("Enter the drive letter you'd like to search: ")

  if folder == '':
    folder = "C:\\"
  else:
    folder = folder + ":\\"  

elif os.name == 'posix':
  print 'OS is Mac/Linux'
  folder = raw_input("Enter the file path (Default is '/Users/': ")
  if folder == '':
    folder = "/Users/"
          
else: #quit if not NT
  exit()

  print "All files ending with .txt in folder %s:" % folder
file_list = []

# create output files if they don't exisit.
for file_type in filetypes:
      # Make the outfile append with the file type.
      #   THis keeps the output file specific to file type.
      #   Strip out the '.' from the file type
  file_type_no_period = file_type.translate(None,'.') 
  temp_outfile = file_type_no_period + outfile
  try: # check if the file exists already
      blank=open(temp_outfile,'r')
      blank.close()
      print "DEBUG: the file exisits and can be opened."   
  except IOError, e:
     # since the file doesn't exisit, create the file and add the header
      print "DEBUG:  the file doesn't exisit"
      startFile = open(temp_outfile,'a')
      startFile.write("Filename\tHash\tFileSize\tDate\tFileType\tVolumeName\n")
      startFile.close()

# start the walking process.
print "Start Time: " + str(datetime.datetime.now().time())
for (paths, dirs, files) in os.walk(folder, topdown=True):
      # Testing section
      for idir in ignore:
        if idir in dirs:
          dirs.remove(idir)

      dirs[:] = [d for d in dirs if d not in ignore]
      # Testing section end...
      for file in files:
        for file_type in filetypes:
          file_type_no_period = file_type.translate(None,'.') 
          temp_outfile = file_type_no_period + outfile    
          if file.endswith(file_type):
              out_put_file = open(temp_outfile,'a')
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
              if file_stat.st_size > min_file_size: 
                out_put_file.write(os.path.join(paths, file) + "\t" + hash+"\t" + str(file_stat.st_size)+"\t" + str(modification_date(filename)) + "\t" + file_type_no_period + "\t"+ volume_name + '\n')
              out_put_file.close()
              # debug
              #print out_put_file
              file_to_hash.close()
#debug
#print out_put_file
print "Thanks for using the filefinder.  We hope the hashes are helpful...."
print "End Time: " + str(datetime.datetime.now().time())




