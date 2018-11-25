#!/bin/bash

# AUthor Randeep P R - randeep123@gmail.com
# Date 25-11-2018

set -o nounset
set -o errexit
version="1.0.0"

STATUS_OK=0
STATUS_WARNING=1
STATUS_CRITICAL=2
STATUS_UNKNOWN=3
verbose="False"
OS=`uname -s`

usage () {
    echo "Usage: ./check_storage_path.sh -t type"
    echo "    -h displays help"
    echo "    -t Type"
    echo "    -V Enable debug mode"
    echo ""
    exit ${STATUS_UNKNOWN}
}

# Get command line options
[ $# -eq 0 ] && usage
while getopts  "ht:V" OPTION; do
    case ${OPTION} in
        h) usage ;;
        t) if [[ ! -z ${OPTARG} ]]; then
               type=${OPTARG}
           else
               usage
           fi
        ;;
        V) verbose="True"
        ;;
        *) usage ;;
    esac
done

# if type = multipath
if [ "$type" == "multipath" ]
  then
      MULITPATH="$(rpm -qa | grep -i multipath |wc -l)"
      if [ $MULITPATH -ge 1 ]
      then
  	    MULT="$(multipath -ll)"
	    MULT_FAILED="$(echo -n $MULT | grep -i failed)"
	    if [ "$verbose" == "True" ]
	    then
	      echo "$MULT"
              echo "$MULT_FAILED"
	    fi
	    if [ "$MULT" == "" ]
            then
              echo "UNKNOWN! No mulitpath devices found"
              exit "$STATUS_UNKNOWN"
	    elif [ "$MULT_FAILED" == "" ]
  	    then
              echo "SAN OK. All paths are fine."
              exit "$STATUS_OK"
	    else
              echo "SAN issue detected. One or more SAN paths is in degraded mode."
              exit "$STATUS_CRITICAL"
	    fi
      else
        echo "UNKNOWN! multipath rpms are not installed"
        exit "$STATUS_UNKNOWN"
      fi


# if type = powerpath
elif [ "$type" == "powerpath" ]
then
# Routine to check is PowerPath is installed and being used.  If not, exit 0
case "$OS" in
    'Linux' )
        POWERPATH_CHECK=`rpm -qa | grep EMC | wc -l`
            if [ $POWERPATH_CHECK -eq 1 -o $POWERPATH_CHECK -gt 1 ]; then
                CHECK_DEGRADED=`/usr/bin/sudo /sbin/powermt display | egrep "degraded|failed" | wc -l`
                    if [ $CHECK_DEGRADED -eq 1 -o $CHECK_DEGRADED -gt 1 ]; then
                        echo "SAN issue detected. One or more SAN paths is in degraded mode."
                        exit 2
                    else
                        echo "SAN OK. All paths are fine."
                        exit 0
                    fi
            else
                echo "EMC PowerPath not installed.  No valid check."
                exit 0
            fi
    ;;
    'HP-UX' )
        POWERPATH_CHECK=`/usr/sbin/swlist | grep EMC | wc -l`
            if [ $POWERPATH_CHECK -eq 1 -o $POWERPATH_CHECK -gt 1 ]; then
                CHECK_DEGRADED=`/usr/local/bin/sudo /sbin/powermt display | grep degraded | wc -l`
                    if [ $CHECK_DEGRADED -eq 1 -o $CHECK_DEGRADED -gt 1 ]; then
                        echo "SAN issue detected.  One or more SAN paths is in degraded mode."
                        exit 2
                    else
                        echo "SAN OK. All paths are fine."
                        exit 0
                    fi
            else
                echo "EMC PowerPath not installed.  No valid check."
                exit 0
            fi
    ;;
    'SunOS' )
        POWERPATH_CHECK=`pkginfo | grep EMC | wc -l`
            if [ $POWERPATH_CHECK -eq 1 -o $POWERPATH_CHECK -gt 1 ]; then
                CHECK_DEGRADED=`/usr/local/bin/sudo /etc/powermt display | grep degraded | wc -l`
                    if [ $CHECK_DEGRADED -eq 1 -o $CHECK_DEGRADED -gt 1 ]; then
                        echo "SAN issue detected.  One or more SAN paths is in degraded mode."
                        exit 2
                    else
                        echo "SAN OK. All paths are fine."
                        exit 0
                    fi
            else
                echo "EMC PowerPath not installed.  No valid check."
                exit 0
            fi
    ;;
esac
fi

