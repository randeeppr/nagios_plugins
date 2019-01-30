#!/usr/bin/python
import sys,getopt,re,socket
from telnetlib import Telnet

STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
STATUS_UNKNOWN = 3

# Usage
def usage():
  print("\n")
  print("Checks the login of Asterisk AMI call manager")
  print("\t-h : Prints this help")
  print("\t-H : Hostname")
  print("\t-p : Asterisk port")
  print("\t-u : Username")
  print("\t-s : Secret/password")
  print("\t-V : Enables verbose")
  print("Usage :./check_Asterisk_login.py -H FQDN -p 5038 -u icinga_ami -s 'abcdefghijk'")
  print("\n")
  sys.exit(STATUS_UNKNOWN)

# Main function starts here
def main(argv):
  verbose = False
  # Getting commandline arguments
  if len(sys.argv) < 2:
    usage()
  try:
        opts, args = getopt.getopt(argv,"hH:u:s:p:V")
  except getopt.GetoptError:
        usage()
  for opt, arg in opts:
        if opt == '-h':
                usage()
        elif opt in ("-H", "--hostname"):
                hostname = arg
        elif opt in ("-p", "--port"):
                port = int(arg)
        elif opt in ("-u", "--username"):
                username = arg
        elif opt in ("-s", "--secret"):
                secret = arg
        elif opt in ("-V", "--verbose"):
                verbose = True

  if verbose:
    print(hostname)
    print(username)
    print(secret)
    print(port)
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  result = sock.connect_ex((hostname,port))
  if result != 0:
    print("Critical! Asterisk port is not open.")
    sys.exit(2)

  tn = Telnet(hostname,port)

  if verbose:
    tn.set_debuglevel(100)
  tn.write("Action: Login\n")
  tn.write("Username: %s\n" %username)
  tn.write("Secret: %s\n" %secret)
  tn.write("\n")
  telnet_response = tn.read_until("\r\n\r\n")
  tn.close()
  if verbose:
    print(telnet_response)
    print(repr(telnet_response))
  response_pattern = re.search('^Response: (.*)\r\n',telnet_response,re.M)
  response = response_pattern.groups(1)
  if verbose:
    print(response)
  message_pattern = re.search('^Message: (.*)\r\n\r\n',telnet_response,re.M)
  message = message_pattern.groups(1)
  response = (str(response[0])).strip()
  message = (str(message[0])).strip()

  # icinga message
  if verbose:
    print(repr(response))
  if response == "Success":
    print("OK! {0}.".format(message))
    sys.exit(0)
  else:
    print("Critical! {0}.".format(message))
    sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])
