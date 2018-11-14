import subprocess
import sys
import os

def require(*packages):
    """
    function to check the import of a package, and install it if not already here
    :param packages:
    :return:
    """
    for package in packages:
        try:
            __import__(package[0])
            print("Import gone well for : "+package[0])
        except ImportError:
            if(sys.platform == "win32"):
                subprocess.Popen(['pip','install',package[1]])
            elif(sys.platform == "linux"):
                subprocess.Popen(['pip3','install',package[1]])

def setup():
    """
    Setup all dependencies for the service
    :return:
    """
    require(('keyboard','keyboard'),('PIL','Pillow'),('begin','begins'))
    if(sys.platform == "win32"):
        require(('pywin32','pywin32'),('tkinter','python-tk'))
    elif(sys.platform == "linux"):
        require(('pyudev','pyudev'))
        subprocess.Popen('sudo apt-get install -y python3-tk', shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=subprocess.STDOUT, executable="/bin/bash")
        subprocess.Popen('sudo apt-get install -y xautomation', shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=subprocess.STDOUT, executable="/bin/bash")
