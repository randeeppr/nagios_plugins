#!/usr/bin/python
#################################################################################################################################################################
# Author : Randeep P R
# Email : randeep123@gmail.com
# Website : www.linuxhelp.in
#################################################################################################################################################################
import sys,getopt,requests,xmltodict,re

STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
STATUS_UNKNOWN = 3

# Usage
def usage():
  print("\n")
  print("Checks the status of the versa hub.")
  print("\t-h : Prints this help")
  print("\t-H : Hostname.")
  print("\t-i : HUB IDs.")
  print("\t-V : Enables verbose")
  print("Usage : ./check_versa_hub.py -i hub_id2,hub_id_2")
  print("\n")
  sys.exit(STATUS_UNKNOWN)

# Main function starts here
def main(argv):
  verbose = False
  # Getting commandline arguments
  try:
        opts, args = getopt.getopt(argv,"hi:H:u:p:V")
  except getopt.GetoptError:
        usage()
  for opt, arg in opts:
        if opt == '-h':
                usage()
        elif opt in ("-H", "--hostname"):
                hostname = arg
        elif opt in ("-i", "--hubids"):
                hubids = arg
        elif opt in ("-u", "--username"):
                username = arg
        elif opt in ("-p", "--password"):
                password = arg
        elif opt in ("-V", "--verbose"):
                verbose = True

  if verbose:
    print(hubids)
    print(type(hubids))
  hub_ids = hubids.split(",")
  if verbose:
    print(hub_ids)
    print(type(hub_ids))
    print(hostname)
    print(username)
    print(password)

  result = {} 
  ping_status = {}
  sync_status = {}
  services_status = {}
  hub_names ={}

  for hub in hub_ids:
    #print(hub)
    try:
        r = requests.get('https://{0}:9182/vnms/dashboard/applianceStatus/<organization-name>/{1}'.format(hostname,hub), auth=('{0}'.format(username), '{0}'.format(password)),verify=False)
        result[hub] = r.text
    except Exception as e:
        print "Error! Couldnt get response from api"
        if verbose == True:
          print e.message
        sys.exit(STATUS_UNKNOWN)

    xml = result[hub]
    if verbose == True:
     print(xml)

    # Get Hub names. <name>HUB-1</name>
    name_pattern = re.search('<name>(.*)</name>',xml)
    name = name_pattern.group(1)
    hub_names[hub] = name.encode('utf-8')

    # Checking ping status
    ping_check = re.search('<ping-status>(.*)</ping-status>',xml)
    p_status = ping_check.group(1)
    if p_status == 'REACHABLE':
      ping_status[hub] = True
    else:
      ping_status[hub] = False

    # Checking sync status
    sync_check = re.search('<sync-status>(.*)</sync-status>',xml)
    s_status = sync_check.group(1)
    if s_status == 'IN_SYNC':
      sync_status[hub] = True
    else:
      sync_status[hub] = False

    # Checking service status
    service_check = re.search('<services-status>(.*)</services-status>',xml)
    ser_status = service_check.group(1)
    if ser_status == 'GOOD':
      services_status[hub] = True
    else:
      services_status[hub] = False
  
  if verbose == True:
    print(ping_status)
    print(sync_status)
    print(services_status) 
    print(hub_names)

  ping_status_failed,sync_status_failed,services_status_failed = [],[],[]
  
  for hub in hub_ids:
    if not ping_status[hub]:
      ping_status_failed.append(hub_names[hub])

  for hub in hub_ids:
    if not sync_status[hub]:
      sync_status_failed.append(hub_names[hub])

  for hub in hub_ids:
    if not services_status[hub]:
      services_status_failed.append(hub_names[hub])

  if ping_status_failed:
   ping_message = "The following hubs are not reachable {0}.".format(ping_status_failed)
  else:
   ping_message = "All hubs are reachable."

  if sync_status_failed:
   sync_message = "The following hubs are not in sync {0}.".format(sync_status_failed)
  else:
   sync_message = "All hubs are in sync."

  if services_status_failed:
   services_message = "The following hub services are affected {0}.".format(services_status_failed)
  else:
   services_message = "All hub services are good."

  # Message to be shown on icinga
  if not ping_status_failed and not sync_status_failed and not services_status_failed:
   print("All hubs {0} are reachable, in sync and hub services are good.".format(hub_names.values()))
   sys.exit(0)
  else:
   print(ping_message+' '+sync_message+' '+services_message)
   sys.exit(2)   
 
if __name__ == "__main__":
   main(sys.argv[1:])
