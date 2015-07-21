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


import subprocess
import os

version = "0.01"

subvol0Path = "/subvol0"
snapFolder = "snap"
snapPath = subvol0Path+"/"+snapFolder
rootDev = ""

def errr(msg):
    print("ERROR: "+msg)

def cleanup():
    umountSubvol0()

def mountSubvol0 ():
    global rootDev
    if subvol0IsMounted():
        return
    
    if not os.path.isdir(subvol0Path):
        subprocess.check_call(["mkdir", subvol0Path])

    p = subprocess.Popen(['mount'], stdout=subprocess.PIPE)
    output, err = p.communicate()
    output = output.decode("utf-8")

    rootDev = ""
    rootIndicator = " on / type btrfs"
    for line in output.split("\n"):
        if rootIndicator in line:
            rootDev = line[0:line.index(rootIndicator)]
    
    subprocess.check_call(["mount", "-o", "subvolid=0", rootDev, subvol0Path])

def umountSubvol0 ():
    if not subvol0IsMounted():
        return
    subprocess.check_call(["umount", subvol0Path])
    
def subvol0IsMounted ():
    p = subprocess.Popen(['mount'], stdout=subprocess.PIPE)
    output, err = p.communicate()
    output = output.decode("utf-8")

    mounted = False
    mountedIndicator = rootDev+" on "+subvol0Path+" type btrfs"
    for line in output.split("\n"):
        if mountedIndicator in line:
            mounted = True
            
    return mounted 

def listSnaps ():
    if not subvol0IsMounted():
        mountSubvol0()
    
    p = subprocess.Popen(['btrfs', 'subvolume', 'list',  '-a', subvol0Path], stdout=subprocess.PIPE)
    output, err = p.communicate()
    output = output.decode("utf-8")
    
    snaplist = []
    for line in output.split("\n"):
        if not ("ID" in line and "gen" in line and "top level" in line and "path" in line):
            continue
        index_ID = line.index("ID")
        index_gen = line.index("gen")
        index_top_level = line.index("top level")
        index_path = line.index("path")
        ID = line[index_ID+2:index_gen].strip()
        gen = line[index_gen+3:index_top_level].strip()
        top_level = line[index_top_level+9:index_path].strip()
        path = line[index_path+4:].strip()
        snaplist.append({"ID":ID, "gen":gen, "top level":top_level, "path":path})
        #print(ID,gen,top_level,path)

    return snaplist

def snapExists (name = ""):
    global snapFolder
    if len(name)<1:
        errr("No name of snapshot given, therefore can't test whether it exists!")
        return
    exists = False
    snaplist = listSnaps()
    for snap in snaplist:
        if snap["path"] == snapFolder+"/"+name:
            exists = True
    return exists

def createSnapshot (name = ""):
    if len(name)<1:
        errr("No name of snapshot given, therefore can't create it!")
        return
    if not subvol0IsMounted:
        mountSubvol0()
    if snapExists(name):
        errr("Snapshot named '"+name+"' already exists, therefore can't create it!")
        return
    subprocess.check_call(['btrfs', 'subvolume', 'snapshot',  '/', snapPath+"/"+name])
    
def deleteSnapshot (name = ""):
    if len(name)<1:
        errr("No name of snapshot given, therefore can't delete it!")
        return
    if not subvol0IsMounted:
        mountSubvol0()
    
    if getDefault()["path"] == snapFolder+"/"+name:
        errr("Snapshot '"+name+"' cannot be deleted since it's set as default for /!")
        return
    if not snapExists(name):
        errr("Snapshot '"+name+"' does not exist, therefore can't delete it!")
        return
        
    p = subprocess.check_call(['btrfs', 'subvolume', 'delete',  snapPath+"/"+name])

def renameSnapshot (origin="", destination=""):
    if len(origin)<1:
        errr("Name of snapshot not given, therefore can't rename it!")
        return
    if len(destination)<1:
        errr("Can't rename snapshot since no name to rename it to is given!")
        return
    if not subvol0IsMounted():
        mountSubvol0()
    if not snapExists(origin):
        errr("Origin snapshot '"+origin+"' does not exist, therefore can't rename it!")
        return
    if snapExists(destination):
        errr("Destination snapshot '"+destination+"' already exists, therefore can't rename '"+origin+"' to '"+destination+"'!")
        return
    os.rename(snapPath+"/"+origin, snapPath+"/"+destination)
    
def copySnapshot (origin="", destination=""):
    if len(origin)<1:
        errr("Name of snapshot not given, therefore can't copy it!")
        return
    if len(destination)<1:
        errr("Can't copy snapshot since no destination is given!")
        return
    if not subvol0IsMounted():
        mountSubvol0()
    if not snapExists(origin):
        errr("Origin snapshot '"+origin+"' does not exist, therefore can't copy it!")
        return
    if snapExists(destination):
        errr("Destination snapshot '"+destination+"' already exists, therefore can't copy '"+origin+"' to '"+destination+"'!")
        return
    subprocess.check_call(['btrfs', 'subvolume', 'snapshot',  snapPath+'/'+origin, snapPath+"/"+destination])
    
def getIdOfSnapshot (name = ""):
    Id = None
    snaplist = listSnaps()
    for snap in snaplist:
        if snapFolder+"/"+name == snap["path"]:
            Id = snap["ID"]
    return Id
    
def getDefault ():
    p = subprocess.Popen(['btrfs', 'subvolume', 'get-default',  '/'], stdout=subprocess.PIPE)
    output, err = p.communicate()
    line = output.decode("utf-8")
    
    index_ID = line.index("ID")
    index_gen = line.index("gen")
    index_top_level = line.index("top level")
    index_path = line.index("path")
    ID = line[index_ID+2:index_gen].strip()
    gen = line[index_gen+3:index_top_level].strip()
    top_level = line[index_top_level+9:index_path].strip()
    path = line[index_path+4:].strip()
    return {"ID":ID, "gen":gen, "top level":top_level, "path":path}
    
def setDefault (name=None):
    if not name:
        errr("No name given, therefore can't set default snapshot!")
        return
    snaplist = listSnaps()
    exists = False
    Id = None
    for snap in snaplist:
        if snap["path"] == snapFolder+"/"+name:
            Id = snap["ID"]
    if not Id:
        errr("Snapshot with name "+name+" doesn't exist, therefore can't set default!")
        return
    subprocess.check_call(['btrfs', 'subvolume', 'set-default',  Id, subvol0Path])

def rollback (currentRename = "", backupToLoad="", newCurrName="current", disableConfirm=False):
    if not disableConfirm:
        check = input("WARNING! You're about to do a roll-back. This will cause the machine to reboot! Are you sure you wan't to reboot now? [yes|NO] ")
        if check.strip().lower() != "yes":
            return
    if len(currentRename)<1:
        errr("Can't roll back since no name to rename current default is given!")
        return
    if len(backupToLoad)<1:
        errr("Can't roll back since the name of the backup to roll back to is not given!")
        return
    if snapExists(newCurrName) and (getDefault()["path"] != snapFolder+"/"+newCurrName):
        errr("Can't roll back since a snapshot with the name for new current ('"+newCurrName+"') already exists!")
        return
    renameSnapshot( getDefault()["path"][len(snapFolder+"/"):], currentRename)
    copySnapshot( backupToLoad, newCurrName )
    setDefault(newCurrName)
    subprocess.check_call(['sync'])
    subprocess.check_call(["shutdown", "-r", "now"])
    
    
    
