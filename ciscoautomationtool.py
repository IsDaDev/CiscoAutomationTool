filePath = "input.txt"

#imports
from pyautogui import typewrite as tw
from pyautogui import press
from pywinauto import Desktop
import time
import sys

# Empty arrays and counter integer variable
interfaces = []
ip = []

# function to read from the input-file
def read(path):
    # File that contains the router configuration
    f = open(path)
    if not f:
        sys.exit("Error finding file\nCheck the path on line 1")
    # Reads all lines into content buffer
    content = f.readlines()

    return content


# enter function
def enter():
    press("enter")

# exit function
def leave():
    tw("exit")
    enter()

# function to get into the global config mode
def getToGlobalConf():
    time.sleep(0.2)
    tw("no")
    enter()
    enter()
    tw("enable")
    enter()
    tw("conf t")
    enter()
    print("GetToGlobalConf")

# function to configure an interface
# params: Interface to config, Prefix for the IP, the IP and the Subnetmask
def configureInt(interface, ipPrefix, ip, sn):
    fullIP = ipPrefix + ip
    tw(f"int {interface}")
    enter()
    tw(f"ip address {fullIP} {sn}")
    enter()
    tw("no shutdown")
    enter()
    leave()
    enter()

# colors to make it fancy lol
class Color:
    GREEN = '\033[92m'
    ORANGE = '\033[38;2;255;165;0m'
    DEFAULT = '\033[0m'

# just a lil message of the day
def modt():
    print(Color.GREEN + "*********************************************************************")
    print("Tool to automate router and switch configuration in CiscoPacketTracer")
    print("Tool by" + Color.ORANGE + " IsDaDev")
    print(Color.GREEN + "*********************************************************************" + Color.DEFAULT)

# main function
def main():
    modt()
    # Default values
    # Change if needed
    defaultSubnetmaskR2R = "255.255.255.252"
    defaultSubnetmaskR2E = "255.255.255.0"
    defaultIPPrefix = "192.168."
    # routerName is not defined yet
    routerName = ""
    #counter variable
    counter = 0

    content = read(filePath)

    
    for element in content:
        counter += 1

        # error if file has empty lines
        if len(element.strip()) == 0:
            sys.exit("Empty data found in the file")

        if element.find("RT") != -1:
            routerName = element.strip("\n")
            print("The router you want to configure: ",routerName)
            continue
        if counter % 2 == 0:
            # Odd index
            # If the index is odd, its added to the interfaces array
            interfaces.append(element.strip("\n"))
        else:
            # Even index
            # If the index is even, its added to the ip array
            ip.append(element.strip("\n"))
    
    for i in range(len(interfaces)):
        print(f"Configuring {interfaces[i]} with IP {ip[i]}")
    
    # Error handling for the file length
    if counter % 2 != 1:
        sys.exit("Too few arguments in file")

    # Query if the values are default
    isDefault = input("Default Values?\nYes or No\n").lower()

    # if the values are not default asks the user to input the ip prefix, 
    # default subnetmask for R2E networks and default subnetmask for R2R networks
    if isDefault != "yes":
        defaultIPPrefix = input("What is the default IP Prefix\nFormat: xxx.xxx.\n")
        if len(defaultIPPrefix) < 5:
            sys.exit("Input for IP Prefix is invalid")
        # input for the subnetmask R2E
        defaultSubnetmaskR2E = input("""What is the subnetmask for Router 2 Ethernet networks
                                        \nFormat: xxxx.xxxx.xxxx.xxxx\n""")
        # error handling for the default subnetmask for R2E
        if len(defaultSubnetmaskR2E) <= 8 and len(defaultSubnetmaskR2E) >= 15:
            sys.exit("Input for Router2Ethernet subnetmask is invalid")
        # input for the subnetmask R2R
        defaultSubnetmaskR2R = input("""What is the subnetmask for Router 2 Router networks?
                                        \nFormat: xxxx.xxxx.xxxx.xxxx\n""")
        # error handling for the default subnetmask for R2R
        if len(defaultSubnetmaskR2R) <= 8 and len(defaultSubnetmaskR2R) >= 15:
            sys.exit("Input for Router2Router subnetmask is invalid")

    # function to check if the interface is non-serial
    def intS(index):
        prefixes = ["Ge", "G", "Fe", "F"]
        # loops through each prefix in the prefix-array
        for prefix in prefixes:
            # returns true if the interface is found
            if prefix.lower() in interfaces[index].lower():
                return True
                print(True)
        return False

    # selects the window that matches the first entry in the input file
    routerWindow = Desktop(backend="win32").window(title=routerName)
    # sets the window into focus
    routerWindow.set_focus()

    # siwtch to global configuration mode
    getToGlobalConf()

    # loops through every single interface
    for i in range(int(counter / 2)):
        # if its an Serial Interface it configures is with the default subnetmask for R2R
        if interfaces[i].find("S") != -1:
            configureInt(interfaces[i], defaultIPPrefix, ip[i], defaultSubnetmaskR2R)
        # if its Gigabit- or FastEthernet, configures it with default subnetmask for R2E
        elif intS(i):
            configureInt(interfaces[i], defaultIPPrefix, ip[i], defaultSubnetmaskR2E)
        # exit if the interface is either unrecognized or invalid
        else: 
            sys.exit("Invalid interface type")
    
    print("Program finished successfully")

# call for the main function
if __name__ == "__main__":
    main()