try:
    import serial
    import json
except ImportError:
    print("Please check readme.md for installation and running instructions!")
    input("Press enter to continue...")
    import sys
    sys.exit()

DATA = None
def mainloop():
    with open('config.json', 'r') as data:
        DATA = json.load(data)
        
    print ("hello world")
    print(DATA)
    
if __name__ == '__main__':
    mainloop()
