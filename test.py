import os
import sys
import time
import keyboard
import subprocess

def lockAllWindows(*toHook):
    """
    Lock the keyboard and the shortcuts, remove task manager, then display an image fullscreen
    Take a list of keys to hook, and return a list of the hooks
    :return: list of hook
    """
    hooks = []
    for key in toHook:
        hooks.append(keyboard.block_key(key))
    oKey = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System',0,winreg.KEY_SET_VALUE)
    winreg.SetValueEx(oKey,'DisableTaskMgr',0,winreg.REG_DWORD,1)
    subprocess.Popen(["python","image.py",imgPath])
    return hooks


def unlockAllWindows(*hooks):
    """
    Unhook the keyboard, reactivate the task manager and remove the fullscreen image
    Take the list of hooks in argument
    :return:
    """
    for hook in hooks:
        keyboard.unhook(hook)
    oKey = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System',0,winreg.KEY_SET_VALUE)
    winreg.SetValueEx(oKey,'DisableTaskMgr',0,winreg.REG_DWORD,0)
    keyboard.send("esc")

def lockAllLinux():
    """
    Shut down all keyboard drivers, then display an image fullscreen
    :return:
    """
    os.system('xinput --set-prop "AT Translated Set 2 keyboard" "Device Enabled" 0')
    subprocess.Popen(["python3","image.py",imgPath])

def unlockAllLinux():
    """
    Put keyboard drives back on and remove the fullscreen image
    :return:
    """
    os.system('xinput --set-prop "AT Translated Set 2 keyboard" "Device Enabled" 1')
    subprocess.Popen(["xte","key Escape"])

def imageLoader():
    """
    Retrive image path
    :return: image path
    """
    imgPathFile = open('imgPath.txt', 'r')
    imgPath = imgPathFile.readline()
    imgPathFile.close()
    return imgPath


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
    """alt = None
    ctrl = None
    altgr = None
    shift = None
    win = None"""
    hooks = None
    imgPath = imageLoader()
    #Bloquer, checker tout les prts is clé, et delock si carte présente
    while True:
        new_drives = locate_usb()
        #Fonction Axel
        if(len(new_drives) > len(drives)):
            print("New connection at %s" %[value for value in new_drives if value not in drives])
            unlockAllWindows(hooks)
            """keyboard.unhook(alt)
            keyboard.unhook(ctrl)
            keyboard.unhook(altgr)
            keyboard.unhook(shift)
            keyboard.unhook(win)
            keyboard.unhook(esc)
            oKey = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System',0,winreg.KEY_SET_VALUE)
            winreg.SetValueEx(oKey,'DisableTaskMgr',0,winreg.REG_DWORD,0)"""
            keyboard.send("esc")
        elif(len(new_drives) < len(drives)):
            print("Disconnection at %s" %[value for value in drives if value not in new_drives])
            hooks = lockAllWindows(['alt','ctrl','alt gr','shift','esc','windows gauche'])
            """alt = keyboard.block_key('alt')
            ctrl = keyboard.block_key('ctrl')
            altgr = keyboard.block_key('alt gr')
            shift = keyboard.block_key('shift')
            win = keyboard.block_key('windows gauche')
            esc = keyboard.block_key('esc')
            oKey = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System',0,winreg.KEY_SET_VALUE)
            winreg.SetValueEx(oKey,'DisableTaskMgr',0,winreg.REG_DWORD,1)
            subprocess.Popen(["python","image.py",imgPath])"""
        drives = new_drives
        print("---------------")
        time.sleep(0.5)
    
    

elif(sys.platform == "linux"):

    import pyudev

    imgPath = imageLoader()
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('block')
    #Tout bloquer, et checker si carte la poru debloquer

    #Fonction Axel
    for device in iter(monitor.poll, None):
        if device.action == 'add':
            print('{} connected'.format(device))
            print(device.sys_name)
            unlockAllLinux()
        if device.action == 'remove':
            print('{} disconnected'.format(device))
            lockAllLinux()

