#!/usr/bin/python3.4
#################################################################################################################################################################
#
# Author : Randeep P R
# website : https://www.linuxhelp.in
#
#################################################################################################################################################################
import sys,getopt,requests,os,tempfile,urllib3,subprocess,pysftp
from ftplib import FTP_TLS

STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
STATUS_UNKNOWN = 3
urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings()

# Usage
def usage():
  print("\n")
  print("Checks the upload/downloaded operations of a file agains the host with https/ftps/sftp")
  print("\t-h : Prints this help")
  print("\t-H : Hostname")
  print("\t-u : Username")
  print("\t-p : password")
  print("\t-V : Enables verbose")
  print("Usage : {0} -H Hostname -u test10 -s 'abcdefghi'".format(sys.argv[0]))
  print("\n")
  sys.exit(STATUS_UNKNOWN)

def delete_temp_file(path,verbose):
  if verbose:
    print("Came to detele the file {0}".format(path))
  subprocess.check_call("rm -rf {0}".format(path), shell=True)

def check_https(hostname,file_name,username,password,verbose):
  if verbose:
    print("-"*60)
  https_services_failed = []
 
  # HTTPS: Upload the file.
  if verbose:
    print("HTTPS: Uploading the file")
    #print(file_name,username,password,hostname)
  url = 'https://{0}'.format(hostname)

  fh = open(file_name, 'rb')
  files = {'file': ('http.txt', fh, 'multipart/form-data', {'Expires': '0'})}
  try:
    p = requests.post(url, files=files,auth=('{0}'.format(username),'{0}'.format(password)),verify=False)
  except:
    if verbose:
      print("HTTPS: Failed to upload the file via http.")
      print(p.status_code)
    https_services_failed.append('https_upload')
  else:
    fh.close()
    if p.status_code == 200:
      if verbose:
        print("HTTPS: File uploaded successfully.")
    else:
      if verbose:
        print(p.status_code)
        print("HTTPS: Failed to upload the file via http.")
      https_services_failed.append('https_upload') 

  # HTTPS: Download the file. 
  if verbose:
    print("-"*60)
    print("HTTPS: Downloading the uploaded file.\n")
  url='https://{0}/{1}'.format(hostname,'http.txt')
  try:
    g = requests.get(url,auth=('{0}'.format(username),'{0}'.format(password)),verify=False)
  except:
    if verbose:
      print("HTTPS: Failed to download the file via http")
    https_services_failed.append('https_download')
  else:
    if g.status_code == 200:
      if verbose:
        print("HTTPS: Downloaded the file successfully.")
    else:
      if verbose:
        print(g.status_code)
        print("HTTPS: Failed to download the file via http")
      https_services_failed.append('https_download')

  # HTTPS: Remove the uploaded file.
  url='https://{0}/{1}'.format(hostname,'http.txt')
  headers = {'content-type': 'multipart/form-data'}
  try:
    d =  requests.delete(url,auth=('{0}'.format(username),'{0}'.format(password)),verify=False) 
  except:
    if verbose:
      print("HTTPS: Failed to delete the uploaded file via http")
      print(d.text)
    https_services_failed.append('https_delete')
  else:
    if d.status_code == 200:
      if verbose:
        print("HTTPS: Deleted the file successfully.")
    else:
      if verbose:
        print(d.status_code)
        print(d.text)
        print("HTTPS: Failed to delete the uploaded file via http")
      https_services_failed.append('https_delete')
 
  return  https_services_failed

def check_sftp(hostname,file_name,username,password,verbose):
  sftp_services_failed = []
  if verbose:
    print("-"*60)
    print("Filename passed to upload is {0}".format(file_name))
  sftip_file = file_name
  cnopts = pysftp.CnOpts()
  cnopts.hostkeys = None

  # Uploadi the file.
  if verbose:
    print("Uploading the file {0}".format(file_name))
  try:
    with pysftp.Connection(host=hostname, username=username, password=password,cnopts=cnopts) as sftp:
      sftp.put(sftip_file,'sftp.txt')
      #data = sftp.listdir()
  except:
    if verbose:
      print("sftp upload failed.")
    sftp_services_failed.append('sftp_upload')  
  else:
    if verbose:
      print("SFTP: File uploaded sucessfully.")
    pass
  	
  # Download the uploaded file.
  if verbose:
    print("-"*60)
  if verbose: 
    print("Downloading the file {0}".format('sftp.txt'))
  try:
    with pysftp.Connection(host=hostname, username=username, password=password,cnopts=cnopts) as sftp:
      sftp.get('sftp.txt','/tmp/sftp.txt')
  except:
    if verbose:
      print("sftp download failed.")
    sftp_services_failed.append('sftp_download')
  else:
    if verbose:
      print("SFTP: File downloaded successfully.")
    pass

  # Remove the uploaded file.
  if verbose: 
    print("Removing the uploaded file")
  try:
    with pysftp.Connection(host=hostname, username=username, password=password,cnopts=cnopts) as sftp:
      sftp.remove('sftp.txt')
  except:
    if verbose:
      print("sftp: Deleting uploaded file failed.")
    sftp_services_failed.append('sftp_delete')
  else:
    if verbose:
      print("SFTP: Deleted uploaded file successfully.")
    pass

  delete_temp_file('/tmp/sftp.txt',verbose)
  return sftp_services_failed

def check_ftps(hostname,temp_name,username,password,verbose):
  ftps_services_failed = []
  if verbose:
    print("-"*60)
  if verbose:
    print(temp_name)
  ftps = FTP_TLS(hostname)
  ftps.login(username, password)
  ftps.prot_p()          
  #ftps.retrlines('LIST')
  if verbose:
    ftps.set_debuglevel(2)
  
  # Upload the file
  if verbose:
    print("FTPS: Uploading the file.")
  try:
    ftps.storbinary('STOR {0}'.format('ftps.txt'), open(temp_name,'rb'))
  except:
    if verbose:
      print("FTPS: Uploading the file failed.")
    ftps_services_failed.append('ftps_upload')
  else:
    if verbose:
      print("FTPS: Uploaded file successfully.")
    pass

  # Download the file
  if verbose:
    print("FTPS: Downloading the file.")
  try:
    myfile = open('/tmp/ftps.txt', 'wb')
    ftps.retrbinary('RETR {0}'.format('ftps.txt'), myfile.write)
  except:
    if verbose:
      print("FTPS: Downloading the uploaded file failed.")
    ftps_services_failed.append('ftps_download')
  else:
    if verbose:
      print("FTPS: Downloaded the uploaded file successfully.")

  # Delete the file from remote system
  try:
    ftps.delete('ftps.txt')
  except:
    if verbose:
      print("FTPS: Deleting uploaded file failed.")
    ftps_services_failed.append('ftps_delete')
  else:
    if verbose:
      print("FTPS: Deleted the uploaded file successfully.")
    pass

  # Close the ftps connection.
  ftps.close()

  # Detel the file which is downloaded
  delete_temp_file('/tmp/ftps.txt',verbose)

  return ftps_services_failed

# Main function starts here
def main(argv):
  verbose = False
  # Getting commandline arguments
  if len(sys.argv) < 2:
    usage()
  try:
        opts, args = getopt.getopt(argv,"hH:u:p:V")
  except getopt.GetoptError:
        usage()
  for opt, arg in opts:
        if opt == '-h':
                usage()
        elif opt in ("-H", "--hostname"):
                hostname = arg
        elif opt in ("-u", "--username"):
                username = arg
        elif opt in ("-p", "--password"):
                password = arg
        elif opt in ("-V", "--verbose"):
                verbose = True

  #if verbose:
  #  print(hostname)
  #  print(username)
  #  print(password)

  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

  # Creating temporary file.
  tempfile.tempdir = '/tmp/icinga'
  temp, temp_name = tempfile.mkstemp()
  if verbose:
    print(temp_name)
  os.write(temp,'Temporary file created by check_file_operations.py script for testing upload & download.\n'.encode())
  os.close(temp)
 
  https_services_failed = check_https(hostname,temp_name,username,password,verbose)
  if verbose:
    print("https_services_failed is {0}".format(https_services_failed))

  sftp_services_failed = check_sftp(hostname,temp_name,username,password,verbose)
  if verbose:
    print("sftp_services_failed is {0}".format(sftp_services_failed))

  ftps_services_failed = check_ftps(hostname,temp_name,username,password,verbose)
  if verbose:
    print("ftps_services_failed is {0}".format(ftps_services_failed))
  
  delete_temp_file(temp_name,verbose)
 
  failed = []
  failed = https_services_failed + sftp_services_failed + ftps_services_failed

  if verbose:
    print("Failed are".format(failed))

  if https_services_failed or sftp_services_failed  or ftps_services_failed:
    print("Critical! The following operations failed: {0}".format(','.join(failed)))
    sys.exit(2)
  else:
    print("OK! HTTPS/SFTP/FTPS upload/download operations are working file.")
    sys.exit(0)

if __name__ == "__main__":
   main(sys.argv[1:])
