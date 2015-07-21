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

def printUsage ():
    print("""Usage:
    
    list
    
    snapshot:
            snapshot create <name>
            
            snapshot delete <name>
            
            snapshot rename <name> <newname>
            
            snapshot copy <name> <name of copy>
            
    rollback <new name for current> <snapshot to roll back to>""")
    quit()

if len(sys.argv)<=1:
    printUsage()

if sys.argv[1] == "list":
    snaplist = tt.listSnaps()
    for snap in snaplist:
        print("ID: "+snap["ID"]+" \ttop level: "+snap["top level"]+"\tgen: "+snap["gen"]+"\tpath: "+snap["path"])
    tt.cleanup()
    quit()
elif sys.argv[1] == "snapshot":
    if len(sys.argv)<=2:
        printUsage()
    elif sys.argv[2] == "create":
        if len(sys.argv)!=4:
            printUsage()
        else:
            tt.createSnapshot(sys.argv[3])
            tt.cleanup()
            quit()
    elif sys.argv[2] == "delete":
        if len(sys.argv)!=4:
            printUsage()
        else:
            tt.deleteSnapshot(sys.argv[3])
            tt.cleanup()
            quit()
    elif sys.argv[2] == "rename":
        if len(sys.argv)!=5:
            printUsage()
        else:
            tt.renameSnapshot(sys.argv[3], sys.argv[4])
            tt.cleanup()
            quit()
    elif sys.argv[2] == "copy":
        if len(sys.argv)!=5:
            printUsage()
        else:
            tt.copySnapshot(sys.argv[3], sys.argv[4])
            tt.cleanup()
            quit()
elif sys.argv[1] == "rollback":
    if len(sys.argv) != 4:
        printUsage()
    else:
        tt.rollback(sys.argv[2], sys.argv[3])
        tt.cleanup()
        quit()
else:
    printUsage()
