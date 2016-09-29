# superDarnJson

This real-time data setup creates images that are saved with the current display of the radar. This is done by using 2 main groups of python functions. The first pydmap\_read\_\*.py which translates the current binary information transmitted from the radar to a python JSON package. The second group starts with basic\_gui.py which is the setup program for the real-time data display it calls the connection.py which connects to the port created by pydmap\_read\_\*.py. Connection.py also calls the graphing functions that create the saved image to be accessed by index.html. This setup removes the users need to run a program on their computer that creates the real-time data display and instead moves it to a host computer.

To run ensure davitpy is installed on your machine as well as twisted and at least python 2.7

**Location of the needed packages:**

[davitpy] (https://github.com/vtsuperdarn/davitpy)

[twisted] (http://twistedmatrix.com/trac/)


**Davitpy Files that need to be modified**

These files need to be copied to the davitpy library located in the python section of your machine

-plotUtils.py --davitpy/pydarn/utils/

-radDataTypes.py --davitpy/pydarn/sdio/

-mapOverlay.py   --davitpy/utils/

The file radarPos.py needs to be copied into davitpy in davitpy/pydarn/plotting/


**First:**

Edit or create a specific pydmap\_read\_\*.py file where \* is the abrivation of the radar. In editing this file to point to a new radar change the HOST variable to desired port number. Also, modify PORT\_JSON\_SERVE to a new port number make sure this number is not being used by any other functionality on your machine.

**Second:**

Edit or create a startbasic\_\*.sh file where again \* is the same radar name as used in the First step. 

To edit this file:

First, update the RADAR variable to the previously mentioned radar name along with its channel. For instance for the Mcmurdo Radar channel A the RADAR variable is mcma where mcm is the radar name and a is the channel.

Second, update the file path in line 6, and 9 to match your filepath your errlog files

Next, update the name of the file for every call of pydamp\_read\_\*.py to match the file name that you edited or created in the first step (lines 19 and 21).

Fourth, update file path to the location of basic_gui.py the rest of the contained files. If the startbasic\_\*.sh file you are updating is in the same location remove this line. (line 20) 

Fifth, update the arguments within the call to basic\_gui.py as shown below.
 
python2 basic_gui.py hosts=localhost ports=6025 maxbeam=16 nrangs=75 names="McMurdo B" beams=8 rad=mcm filepath="/var/www/html/java/mcmb/"


**Argument Definition For basic\_gui.py**

```
hosts - Name of host to connect to

ports - port number to connect to

maxbeams - number of beams for the radar you are pointing to

nrangs - number of gates for the radar that is begin pointed to

names - Name of the radar

beams - Beam that you want the time plot to focus on

rad - Radars 3 letter abriviation

channel - Radars channel (optional)

filepath - path to where you would like the saved images to be stored
```

The at minimum the passed in arguments that should be updated are ports, names, rad, channel(optional), and filepath. 

- ports - change to the port number written in pydamp\_read\_\*.py for PORT\_JSON\_SERVE variable.
- names - change to the full radar name. ie. For Mcmurdo the radar names could be Mcmurdo A or Mcmurdo B
- rad - change to the radar's abrivation. ie. For Mcumurdo the radar name is mcm
- channel(optional) - this variable only needs to be included if the radar has channels. For instance Adak East or West files do not have channel so do not have channel variables. But, Kodiak and Mcmurdo do have channels and the basic\_gui.py call includes the channel variable.
- filepath - update to the desired file path.

**To Run**

Run startbasic\_\*.sh as a bash file or set it up as a cronjob that runs once a minute.

**Once Updated**

To view online ensure the file index.html is in the correct file path for your webserver. For lines 86 - 92 it is a drop box of all of the avaiable radars. So, if you have less radars active reduce this list, if you have more increase it. Make sure that the option value matches the folder names that the images are located (should be your filepath).

**Other Information** 

- If it doesn't already exist create an errlog file folder in the same location this file folder will contain daily log information. With file names containing date the file was created as well as radar name.
- Create a file folder with the name data. This file will contain files that are used to plot the time plot graphs if connection is lost.
- Create a file with named after the radar's abriviation that will store the images for that radar.


