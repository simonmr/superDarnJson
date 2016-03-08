#!/bin/sh
SERVICE='basic_gui.py'
RADAR='mcma'
if ps ax | grep -v grep | grep $SERVICE | grep $RADAR > /dev/null
then
    cd /var/www/radar/html/java/images/gui/errlog/
    filenm=$(ls -t err*|grep "$RADAR" | head -1)
    echo "Latest $filenm"
    lline=$(tail -1 "/var/www/radar/html/java/images/gui/errlog/$filenm")
    echo "Last line of file: $lline"
    if [[ "$lline" == *"Time thread stopped"* ]]
    then
        ppid=$(ps -A -o pid,cmd|grep "$RADAR"|grep "$SERVICE" |head -n 1 | awk '{print $1}')
        echo "Killing $ppid"
        kill "$ppid"
    fi
else
    echo "$SERVICE is not running"
    pkill -9 -f pydmap_read_mca.py
    cd /var/www/radar/html/java/images/gui/
    python2 pydmap_read_mca.py &
    python2 basic_gui.py hosts=localhost ports=6041 maxbeam=16 nrangs=75 names="Mcmurdo A" beams=8 channels=a rad=mcm filepath="mcma/"
    
fi

