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
import subprocess
import time

euid = os.geteuid()
if euid != 0:
    args = ['sudo', sys.executable] + sys.argv + [os.environ]
    os.execlpe('sudo', *args)

veto_leftOverFiles = False

while True:
    print("\nChecking setup...")

    p = subprocess.Popen(['btrfs', 'subvolume', 'get-default',  '/'], stdout=subprocess.PIPE)
    output, err = p.communicate()
    
    #line = output.decode("utf-8")
    #index_ID = line.index("ID")
    #index_gen = line.index("gen")
    #index_top_level = line.index("top level")
    #index_path = line.index("path")
    #ID = line[index_ID+2:index_gen].strip()
    #gen = line[index_gen+3:index_top_level].strip()
    #top_level = line[index_top_level+9:index_path].strip()
    #path = line[index_path+4:].strip()

    breadcrumbs = output.decode("utf-8").split()
    ID = breadcrumbs[breadcrumbs.index("ID")+1]
    
    if ID != "0": # check for / being a subvolume
        if tt.snapFolderExists(): # check for timetravel having it's folder
            # check whether there's a volume configured for /
            volumeConfiguredForRoot = None
            snapslist = tt.listSnaps()
            for volume in snapslist:
                if tt.volumeGetMountSetting(volume) == "/":
                    volumeConfiguredForRoot = volume
            if volumeConfiguredForRoot:
                # check whether there are leftover files in subvolume 0
                listOfSubvol0 = os.listdir(tt.subvol0Path)
                if listOfSubvol0 == [tt.snapFolder] or veto_leftOverFiles:
                    print("Everything should be fine. Have fun :)")
                    quit()
                else:
                    print("There are leftover files in subvolume 0 (everything apart from '"+tt.snapFolder+"'). If they are from the migration of your rootfs to a subvolume it should be safe to delete them. This is a list of the leftover files:")
                    listOfSubvol0.remove(tt.snapFolder)
                    for i in range(len(listOfSubvol0)):
                        if os.path.isdir(tt.subvol0Path+"/"+listOfSubvol0[i]):
                            ftype = "Folder  "
                        elif os.path.isfile(tt.subvol0Path+"/"+listOfSubvol0[i]):
                            ftype = "File    "
                        else:
                            ftype = "Unknown "
                        print(str(i)+":\t "+ftype+"\t "+listOfSubvol0[i])
                    selected = False
                    while not selected:
                        selected = input("Do you want to:\n a) leave the files as they are\n b) delete a selection of files with your filemanager\n c) delete all files automatically\n? ")
                        if not selected in ["a", "b", "c"]:
                            selected = False
                    
                    if selected == "a": # leave the files as they are
                        pass
                    elif selected == "b": # delete a selection with the filemanager
                        print("You can now open a filemanager of your choice, point it to '"+tt.subvol0Path+"' and delete the leftover files (!!! DO NOT DELETE '"+tt.snapFolder+"'!!!) as long as this utility is waiting here. Close the filemanager and press any key when you're done.")
                        input()
                    elif selected == "c": # delete all leftover files automatically
                        print("deleting all files...")
                        time.sleep(1)
                        print("done")
                    veto_leftOverFiles = True
            else:
                print("Your rootfs (/) is on a subvolume but timetravel is not set to manage it. This utility will help you set it up properly")
                time.sleep(1) # do things
        else:
            print("The folder where timetravel stores the snapshots does not exist yet. This utility will create it now")
            tt.createSnapFolder()
    else:
        print("Your rootfs is currently placed in the outermost btrfs-subvolume (0). This utility will help you to move it into a subvolume to make use of timetravel.")
        time.sleep(1) # do things
        os.makedirs("/"+snapfolder+"/root")
        subprocess.check_call(['btrfs', 'subvolume', 'snapshot',  "/", "/"+snapFolder+"/root/current"])
        
        os.makedirs(subvol0Path)
        tt.mountSubvol0()
        tt.setDefault("/", "current")
        
        subprocess.check_call(['sync'])
        subprocess.check_call(["shutdown", "-r", "now"])
    
