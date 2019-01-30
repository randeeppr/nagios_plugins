#!/usr/bin/python
import sys,getopt,subprocess

STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
STATUS_UNKNOWN = 3

# Usage
def usage():
  print("\n")
  print("Checks vrrp juniper")
  print("\t-h : Prints this help")
  print("\t-H : Hostname.")
  print("\t-c : SNMP Community.")
  print("\t-v : SNMP Version")
  print("\t-m : Mode (2-backup,3-Master)")
  print("\t-V : Enables verbose")
  print("Usage :./check_vrrp_juniper.py -H FQDN  -c public -v 2c ")
  print("\n")
  sys.exit(STATUS_UNKNOWN)

def get_snmp(hostname,snmp_community,snmp_version,verbose):
  if verbose: 
    print(hostname,snmp_community,snmp_version)
  response = subprocess.check_output("snmpwalk -c {0} -v {1} {2} 1.3.6.1.2.1.68.1.3.1.3 | awk '{{print $NF}}'".format(snmp_community,snmp_version,hostname), shell=True)
  return response

# Main function starts here
def main(argv):
  verbose = False
  # Getting commandline arguments
  if len(sys.argv) < 2:
    usage()
  try:
        opts, args = getopt.getopt(argv,"hH:c:v:m:V")
  except getopt.GetoptError:
        usage()
  for opt, arg in opts:
        if opt == '-h':
                usage()
        elif opt in ("-H", "--hostname"):
                hostname = arg
        elif opt in ("-c", "--community"):
                snmp_community = arg
        elif opt in ("-m", "--mode"):
                mode = arg
        elif opt in ("-v", "--version"):
                snmp_version = arg
        elif opt in ("-V", "--verbose"):
                verbose = True

  if verbose:
    print(hostname)
    print(snmp_community)
    print(snmp_version)
    print(mode)

  response = get_snmp(hostname,snmp_community,snmp_version,verbose)
  response = response.split()
  response = map(int, response)

  if verbose:
    print(response)

  if mode == "master":
     code = 3
  elif mode == "backup":
     code = 2
  else:
     print("Unknown mode 2-backup, 3-master")
     sys.exit(3)

  if verbose:
    print(repr(code))
  
  # Icinga output
  if any(x != code for x in response):
    print("Critical! The host {0} is not acting as {1}.".format(hostname,mode))
    sys.exit(2)
  else:
    print("OK! The host {0} is acting as {1}.".format(hostname,mode))
    sys.exit(0)

if __name__ == "__main__":
   main(sys.argv[1:])
