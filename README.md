# timetravel

Linux utility to simplify btrfs snapshots and make jumping in time a breeze

##<bold>UNDER HEAVY DEVELOPMENT, DO ONLY USE ON TESTING MACHINES!</bold>

#### Usage:

timetravel.py:
    
      list
      
      snapshot:
              snapshot create <name>
              
              snapshot delete <name>
              
              snapshot rename <name> <newname>
              
              snapshot copy <name> <name of copy>
              
      rollback <new name for current> <snapshot to roll back to>

timetravel-gui.py is useless right now.

#### Preparation:

To make timetravel work you need to:
* have your rootfs in a subvolume
* have the dafault subvolume be your rootfs
* place this subvolume at <code>\<subvolume0>/snaps/current</code> ("current" is the snapshots name)

To give you an idea how to go about this:
* <code>mkdir /snaps</code>
* <code>btrfs subvolume snapshot / /snaps/current</code>
* <code>btrfs subvolume list -a / # check for id</code>
* <code>btrfs subvolume set-default \<id of current> /</code>
* <code>reboot</code>

You can then remove everything except the snapshots in the outermost subvolume (0):
* <code>mount -o subvolid=0 /dev/sdX /mnt</code>
* <code># rm -r every folder except for snaps</code>
* <code>umount /mnt</code>
