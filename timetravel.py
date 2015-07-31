#!/usr/bin/env python3

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  


import timetravel_backend as tt
import sys
import os

def printUsage ():
    print("""Usage:
    
    listing volumes and their snapshots:
    
            list [<volume>]
    
    volume handling:
    
            volume create <name> <path>
            
            volume delete <name>
    
    snapshot handling inside volumes:
    
            snapshot create <volume> <name>
            
            snapshot delete <volume> <name>
            
            snapshot rename <volume> <name> <newname>
            
            snapshot copy   <volume> <name> <name of copy>
    
    rolling back volumes to a certain snapshot:
    
            rollback <volume>  <new name for current> <snapshot to roll back to>
            """)
    quit()

if len(sys.argv)<=1:
    printUsage()

euid = os.geteuid()
if euid != 0:
    args = ['sudo', sys.executable] + sys.argv + [os.environ]
    os.execlpe('sudo', *args)

if sys.argv[1] == "list":
    snaplist = tt.listSnaps()
    if len(sys.argv) > 2:
        if sys.argv[2] in snaplist:
            for snap in snaplist[sys.argv[2]]:
                print("ID: "+snap["ID"]+" \ttop level: "+snap["top level"]+"\tgen: "+snap["gen"]+"\tpath: "+snap["path"])
        else:
            print("volume "+sys.argv[2]+" not found")
    else:
        for volume in snaplist:
            print(volume+":")
            for snap in snaplist[volume]:
                print("\tID: "+snap["ID"]+" \ttop level: "+snap["top level"]+"\tgen: "+snap["gen"]+"\tpath: "+snap["path"])
    tt.cleanup()
    quit()
elif sys.argv[1] == "volume":
    if len(sys.argv)<=2:
        printUsage()
    elif sys.argv[2] == "create":
        if len(sys.argv)!=5:
            printUsage()
        else:
            tt.createVolume(sys.argv[3], sys.argv[4])
            tt.cleanup()
            quit()
    elif sys.argv[2] == "delete":
        if len(sys.argv)!=4:
            printUsage()
        else:
            tt.deleteVolume(sys.argv[3])
            tt.cleanup()
            quit()
elif sys.argv[1] == "snapshot":
    if len(sys.argv)<=2:
        printUsage()
    elif sys.argv[2] == "create":
        if len(sys.argv)!=5:
            printUsage()
        else:
            tt.createSnapshot(sys.argv[3], sys.argv[4])
            tt.cleanup()
            quit()
    elif sys.argv[2] == "delete":
        if len(sys.argv)!=5:
            printUsage()
        else:
            tt.deleteSnapshot(sys.argv[3], sys.argv[4])
            tt.cleanup()
            quit()
    elif sys.argv[2] == "rename":
        if len(sys.argv)!=6:
            printUsage()
        else:
            tt.renameSnapshot(sys.argv[3], sys.argv[4], sys.argv[5])
            tt.cleanup()
            quit()
    elif sys.argv[2] == "copy":
        if len(sys.argv)!=6:
            printUsage()
        else:
            tt.copySnapshot(sys.argv[3], sys.argv[4], sys.argv[5])
            tt.cleanup()
            quit()
elif sys.argv[1] == "rollback":
    if len(sys.argv) != 5:
        printUsage()
    else:
        tt.rollback(sys.argv[2], sys.argv[3], sys.argv[4])
        tt.cleanup()
        quit()
else:
    printUsage()
