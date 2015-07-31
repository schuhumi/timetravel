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
snapFolder = "timetravel"
snapPath = subvol0Path+"/"+snapFolder

mountSettingFileName = "mountsetting.timetravel"
defaultSettingFileName = "defaultsetting.timetravel"

def errr(msg):
    print("ERROR: "+msg)

def cleanup():
    umountSubvol0()

# geht the /dev/sdXY where the btrfs filesystem is located on
def getRootDev():
    p = subprocess.Popen(['mount'], stdout=subprocess.PIPE)
    output, err = p.communicate()
    output = output.decode("utf-8")
    
    rootDev = ""
    rootIndicator = " on / type btrfs"
    for line in output.split("\n"):
        if rootIndicator in line:
            rootDev = line[0:line.index(rootIndicator)]
    return rootDev

def mountSubvol0 ():
    if subvol0IsMounted():
        return
    
    if not os.path.isdir(subvol0Path):
        subprocess.check_call(["mkdir", "-p", subvol0Path])
    
    subprocess.check_call(["mount", "-o", "subvolid=0", getRootDev(), subvol0Path])

def umountSubvol0 ():
    if not subvol0IsMounted():
        return
    subprocess.check_call(["umount", subvol0Path])
    
def subvol0IsMounted ():
    p = subprocess.Popen(['mount'], stdout=subprocess.PIPE)
    output, err = p.communicate()
    output = output.decode("utf-8")

    mounted = False
    mountedIndicator = getRootDev()+" on "+subvol0Path+" type btrfs"
    for line in output.split("\n"):
        if mountedIndicator in line:
            mounted = True
            
    return mounted 

def listSnaps ():
    global subvol0Path, snapPath, snapFolder
    if not subvol0IsMounted():
        mountSubvol0()
        
    p = subprocess.Popen(['btrfs', 'subvolume', 'list', subvol0Path], stdout=subprocess.PIPE)
    output, err = p.communicate()
    output = output.decode("utf-8")
    btrfsList = output.split("\n")
    
    snaplist = {}
    listOfVolumes = os.listdir(snapPath)
    for volume in listOfVolumes:
        snaplist[volume] = []
        listOfSnaps = os.listdir(snapPath+"/"+volume)
        for snap in listOfSnaps:
            for btrfsEntry in btrfsList:
                #print("path "+snapFolder+"/"+volume+"/"+snap," in ",btrfsEntry)
                if "ID " in btrfsEntry and "gen " in btrfsEntry and "top level " in btrfsEntry and "path " in btrfsEntry:
                    if snapFolder+"/"+volume+"/"+snap == btrfsEntry.split("path ")[1]:
                        index_ID = btrfsEntry.index("ID")
                        index_gen = btrfsEntry.index("gen")
                        index_top_level = btrfsEntry.index("top level")
                        index_path = btrfsEntry.index("path")
                        ID = btrfsEntry[index_ID+2:index_gen].strip()
                        gen = btrfsEntry[index_gen+3:index_top_level].strip()
                        top_level = btrfsEntry[index_top_level+9:index_path].strip()
                        path = btrfsEntry[index_path+4:].strip()
                        snaplist[volume].append({"ID":ID, "gen":gen, "top level":top_level, "path":path})    

    return snaplist

def snapFolderExists ():
    global snapPath
    if not subvol0IsMounted():
        mountSubvol0()
    return os.path.isdir(snapPath)
    
def createSnapFolder ():
    global snapPath
    if not subvol0IsMounted():
        mountSubvol0()
    subprocess.check_call(["mkdir", "-p", snapPath])

def volumeExists(volume=""):
    global snapPath
    if not subvol0IsMounted():
        mountSubvol0()
    if len(volume)<1:
        errr("No volume given, therefore can't test whether it exists!")
        return
    #print("isdir: "+snapPath+"/"+volume, os.path.isdir(snapPath+"/"+volume))
    return os.path.isdir(snapPath+"/"+volume)
    
def volumeSetMountSetting(volume="", mount=""):
    global snapPath
    if not subvol0IsMounted():
        mountSubvol0()
    with open(snapPath+"/"+volume+"/"+mountSettingFileName, 'w') as f:
        f.write(mount)
        
def volumeGetMountSetting(volume=""):
    global snapPath
    if not subvol0IsMounted():
        mountSubvol0()
    mount = None
    with open(snapPath+"/"+volume+"/"+mountSettingFileName, 'r') as f:
        mount = f.read()
    return mount
    
def createVolume(volume="", mount="", backupappend=".backup"):
    global snapPath
    
    if len(volume)<1:
        errr("No volume name given, therefore can't create volume")
        return
    if len(mount)<1:
        errr("No path to mount volume at given, therefore can't create volume")
        return
    if os.path.isdir(mount) or os.path.isfile(mount):
        errr("Path to mount volume already exist, therefore can't create volume")
        return
    if volumeExists(volume):
        errr("Volume already exists, therefore can't create it!")
        return
        
    # remove '/' at the end of the mount path if one happens to be there
    head, tail = os.path.split(mount)
    if tail == "":
        mount = head
    
    if not subvol0IsMounted():
        mountSubvol0()
    
    os.makedirs(snapPath+"/"+volume)
    volumeSetMountSetting(volume, mount)
    createSubvolume(snapPath+"/"+volume+"/current")
    setDefault(volume, "current")
    #createSnapshot(volume, "current")
    head, tail = os.path.split(mount)
    #os.rename(mount, mount+backupappend)
    os.makedirs(mount)
    mountVolume(volume)

def deleteVolume(volume=""):
    global snapPath
    if len(volume)<1:
        errr("No volume name given, therefore can't delete volume")
        return
    if not volumeExists(volume):
        errr("Volume does not exist, therefore can't delete it")
        return
    if volumeIsMounted(volume):
        umountVolume(volume)
    snaplist = listSnaps()[volume]
    for snap in snaplist:
        head, tail = os.path.split(snap["path"])
        deleteSnapshot(volume, tail)
    subprocess.check_call(['rm', '-r', snapPath+"/"+volume])

def volumeIsMounted(volume):
    p = subprocess.Popen(['mount'], stdout=subprocess.PIPE)
    output, err = p.communicate()
    output = output.decode("utf-8")

    mounted = False
    mountedIndicator = getRootDev()+" on "+volumeGetMountSetting(volume)+" type btrfs"
    for line in output.split("\n"):
        if mountedIndicator in line:
            mounted = True
            
    return mounted 
    
def umountVolume(volume=""):
    global subvol0Path
    if len(volume)<1:
        errr("No volume name given, therefore can't unmount volume")
        return
    subprocess.check_call(["umount", volumeGetMountSetting(volume)])
    
def mountVolume(volume=""):
    if len(volume)<1:
        errr("No volume name given, therefore can't mount volume")
        return
    subprocess.check_call(["mount", "-o", "subvolid="+getDefault(volume)["ID"], getRootDev(), volumeGetMountSetting(volume)])

def snapExists (volume="", name = ""):
    global snapFolder
    if not subvol0IsMounted():
        mountSubvol0()
    if len(name)<1:
        errr("No name of snapshot given, therefore can't test whether it exists!")
        return
    exists = False
    if volumeExists(volume):
        snaplist = listSnaps()
        #print("snaplist: ",snaplist)
        for snap in snaplist[volume]:
            #print(snap["path"]+"=="+snapFolder+"/"+volume+"/"+name+" ??")
            if snap["path"] == snapFolder+"/"+volume+"/"+name:
                exists = True
    return exists

def createSubvolume(path):
    if os.path.isdir(path) or os.path.isfile(path):
        errr("Path for subvolume to create already exists, therefore can't create subvolume!")
        return
    subprocess.check_call(['btrfs', 'subvolume', 'create',  path])

def createSnapshot (volume = "", name = ""):
    global snapPath
    if len(name)<1:
        errr("No name of snapshot given, therefore can't create it!")
        return
    if len(volume)<1:
        errr("No volume to snapshot given, therefore can't create snapshot!")
        return
    if not volumeExists(volume):
        errr("Desired volume doesn't exist, therefore can't create snapshot of it!")
        return
    if not subvol0IsMounted:
        mountSubvol0()
    if snapExists(volume, name):
        errr("Snapshot named '"+name+"' already exists, therefore can't create it!")
        return
    subprocess.check_call(['btrfs', 'subvolume', 'snapshot',  volumeGetMountSetting(volume), snapPath+"/"+volume+"/"+name])
    
def deleteSnapshot (volume = "", name = ""):
    global snapPath
    if len(name)<1:
        errr("No name of snapshot given, therefore can't delete it!")
        return
    if len(volume)<1:
        errr("No volume given, therefore can't delete snapshot of it!")
        return
    if not subvol0IsMounted:
        mountSubvol0()
    
    default = getDefault(volume)
    if "path" in default:
        if getDefault(volume)["path"] == snapFolder+"/"+name:
            errr("Snapshot '"+name+"' cannot be deleted since it's set as default for /!")
            return
    if not snapExists(volume, name):
        errr("Snapshot '"+name+"' does not exist, therefore can't delete it!")
        return
        
    p = subprocess.check_call(['btrfs', 'subvolume', 'delete',  snapPath+"/"+volume+"/"+name])

def renameSnapshot (volume="", origin="", destination=""):
    global snapPath
    if len(volume)<1:
        errr("No volume given, therefore can't rename snapshot of the volume")
        return
    if len(origin)<1:
        errr("Name of snapshot not given, therefore can't rename it!")
        return
    if len(destination)<1:
        errr("Can't rename snapshot since no name to rename it to is given!")
        return
    if not subvol0IsMounted():
        mountSubvol0()
    if not snapExists(volume, origin):
        errr("Origin snapshot '"+origin+"' does not exist, therefore can't rename it!")
        return
    if snapExists(volume, destination):
        errr("Destination snapshot '"+destination+"' already exists, therefore can't rename '"+origin+"' to '"+destination+"'!")
        return
    os.rename(snapPath+"/"+volume+"/"+origin, snapPath+"/"+volume+"/"+destination)
    
def copySnapshot (volume="", origin="", destination=""):
    global snapPath
    if len(volume)<1:
        errr("No volume given, therefore can't copy snapshot of the volume")
        return
    if len(origin)<1:
        errr("Name of snapshot not given, therefore can't copy it!")
        return
    if len(destination)<1:
        errr("Can't copy snapshot since no destination is given!")
        return
    if not subvol0IsMounted():
        mountSubvol0()
    if not snapExists(volume, origin):
        errr("Origin snapshot '"+origin+"' does not exist, therefore can't copy it!")
        return
    if snapExists(volume, destination):
        errr("Destination snapshot '"+destination+"' already exists, therefore can't copy '"+origin+"' to '"+destination+"'!")
        return
    subprocess.check_call(['btrfs', 'subvolume', 'snapshot',  snapPath+'/'+volume+"/"+origin, snapPath+"/"+volume+"/"+destination])
    
def getIdOfSnapshot (volume="", name = ""):
    global snapFolder
    if not snapExists(volume, name):
        errr("Snapshot doesn't exist, therefore can't get it's ID")
        return None
    Id = None
    snaplist = listSnaps()
    for snap in snaplist[volume]:
        if snapFolder+"/"+volume+"/"+name == snap["path"]:
            Id = snap["ID"]
    return Id
    
def getDefault (volume=""):
    if len(volume)<1:
        errr("No volume given, therefore can't get it's default!")
        return
    if volumeGetMountSetting(volume) == "/":
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
    else:
        try:
            with open(snapPath+"/"+volume+"/"+defaultSettingFileName, 'r') as f:
                ID = f.read()
            snaplist = listSnaps()[volume]
            for snap in snaplist:
                if ID == snap["ID"]:
                    return snap
        except:
            errr("Reading default failed")
            return None
        return {"ID":ID}
    
def setDefault (volume="", name=""):
    global subvol0Path
    if len(name)<1:
        errr("No name given, therefore can't set default snapshot!")
        return
    if len(volume)<1:
        errr("No volume given, therefore can't a snapshot of it as default!")
        return
    Id = getIdOfSnapshot(volume, name)
    if not Id:
        errr("Snapshot with name "+name+" doesn't exist, therefore can't set default!")
        return
    if volumeGetMountSetting(volume) == "/":
        subprocess.check_call(['btrfs', 'subvolume', 'set-default',  Id, subvol0Path])
    else:
        with open(snapPath+"/"+volume+"/"+defaultSettingFileName, 'w') as f:
            f.write(str(Id))

def rollback (volume="", currentRename = "", backupToLoad="", newCurrName="current", disableConfirm=False):
    global snapFolder
    if volumeGetMountSetting(volume) == "/":
        if not disableConfirm:
            check = input("WARNING! You're about to do a roll-back. This will cause the machine to reboot! Are you sure you wan't to reboot now? [yes|NO] ")
            if check.strip().lower() != "yes":
                return
    else:
        if not disableConfirm:
            check = input("WARNING! You're about to do a roll-back. This will cause a remount of the folder to roll back! Are you sure you wan't to remount now? [yes|NO] ")
            if check.strip().lower() != "yes":
                return
    if not subvol0IsMounted():
        mountSubvol0()
    if len(volume)<1:
        errr("No volume to roll back given, therefore can't roll back!")
        return
    if len(currentRename)<1:
        errr("Can't roll back since no name to rename current default is given!")
        return
    if len(backupToLoad)<1:
        errr("Can't roll back since the name of the backup to roll back to is not given!")
        return
    if snapExists(volume, newCurrName) and (getDefault(volume)["path"] != snapFolder+"/"+volume+"/"+newCurrName):
        errr("Can't roll back since a snapshot with the name for new current ('"+newCurrName+"') already exists!")
        return
    if not snapExists(volume, backupToLoad):
        errr("Snapshot to roll back to doesn't exist, therefore can't roll back!")
        return
    head, tail = os.path.split(getDefault(volume)["path"])
    renameSnapshot(volume, tail, currentRename)
    copySnapshot(volume, backupToLoad, newCurrName )
    setDefault(volume, newCurrName)
    if volumeGetMountSetting(volume) == "/":
        subprocess.check_call(['sync'])
        subprocess.check_call(["shutdown", "-r", "now"])
    else:
        if volumeIsMounted(volume):
            umountVolume(volume)
        mountVolume(volume)
    
    
    
