# superDarnJson

To run ensure davitpy is installed on your machine as well as twisted and json python packages.

First:
Launch the specific pydmap_read_*.py file this file can be adjusted for any radar just change the HOST variable if necessary. Along with the orginal station's port for the PORT variable and a free port for PORT_JSON_SERVE.

Second:
To run launch with this command (properties should be adjusted for the other radar stations, port should match port given for PORT_JSON_SERVE):
python basic_gui.py hosts=localhost ports=6025 maxbeam=16 nrangs=75 names="McMurdo B" beams=8 rad=mcm filepath="/var/www/html/java/mcmb/"


Args definition
hosts - Name of host to connect to
ports - port number to connect to
maxbeams - number of beams for the radar you are pointing to
nrangs - number of gates for the radar that is begin pointed to
names - Name of the radar
beams - Beam that you want the time plot to focus on
rad - Radars 3 letter abriviation
channel - Radars channel (optional)
filepath - path to where you would like the saved images to be stored

A way to run these two tasks to handle loss of connection as a cronjob is following the set up of the startbasic_*.sh bash files.


Files that need to be copied to the davitpy library located in the python section of your machine
--plotUtils.py --davitpy/pydarn/plotting/
--radDataTypes --davitpy/pydarn/sdio/
--mapOverlay   --davitpy/utils/

The file radarPos.py needs to be copied into davitpy in the same folder as plotUtils.py
