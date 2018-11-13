import os
import sys
import time
import keyboard
import subprocess

if(sys.platform == "win32"):

    import win32file
    import winreg
    def locate_usb():
        drive_list = []
        drivebits=win32file.GetLogicalDrives()
        for d in range(1,26):
            mask=1 << d
            if drivebits & mask:
                # here if the drive is at least there
                drname='%c:\\' % chr(ord('A')+d)
                t=win32file.GetDriveType(drname)
                if t == win32file.DRIVE_REMOVABLE:
                    drive_list.append(drname)
        return drive_list

    drives = locate_usb()
    alt = None
    ctrl = None
    altgr = None
    shift = None
    win = None
    imgPathFile = open('imgPath.txt', 'r')
    imgPath = imgPathFile.readline()
    imgPathFile.close()
    while True:
        new_drives = locate_usb()
        #Fonction Axel
        if(len(new_drives) > len(drives)):
            print("New connection at %s" %[value for value in new_drives if value not in drives]) 
            keyboard.unhook(alt)
            keyboard.unhook(ctrl)
            keyboard.unhook(altgr)
            keyboard.unhook(shift)
            keyboard.unhook(win)
            keyboard.unhook(esc)
            oKey = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System',0,winreg.KEY_SET_VALUE)
            winreg.SetValueEx(oKey,'DisableTaskMgr',0,winreg.REG_DWORD,0)
            keyboard.send("esc")
        elif(len(new_drives) < len(drives)):
            print("Disconnection at %s" %[value for value in drives if value not in new_drives])
            alt = keyboard.block_key('alt')
            ctrl = keyboard.block_key('ctrl')
            altgr = keyboard.block_key('alt gr')
            shift = keyboard.block_key('shift')
            win = keyboard.block_key('windows gauche')
            esc = keyboard.block_key('esc')
            oKey = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System',0,winreg.KEY_SET_VALUE)
            winreg.SetValueEx(oKey,'DisableTaskMgr',0,winreg.REG_DWORD,1)
            subprocess.Popen(["python","image.py",imgPath])
        drives = new_drives
        print("---------------")
        time.sleep(0.5)
    
    

elif(sys.platform == "linux"):

    import pyudev

    imgPathFile = open('imgPath.txt', 'r')
    imgPath = imgPathFile.readline()
    imgPathFile.close()
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('block')
    #Fonction Axel
    for device in iter(monitor.poll, None):
        if device.action == 'add':
            print('{} connected'.format(device))
            print(device.sys_name)
            os.system('xinput --set-prop "AT Translated Set 2 keyboard" "Device Enabled" 1')
            subprocess.Popen(["xte","key Escape"])
        if device.action == 'remove':
            print('{} disconnected'.format(device))
            os.system('xinput --set-prop "AT Translated Set 2 keyboard" "Device Enabled" 0')
            subprocess.Popen(["python3","image.py",imgPath])
