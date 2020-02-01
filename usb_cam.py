import time, pygame, sys, signal, os, datetime
import pygame.camera

config = {}
config["offset_width"] = int(sys.argv[1])
config["offset_height"] = int(sys.argv[2])
config["pic_width"] = int(sys.argv[3])-config["offset_width"]
config["pic_height"] = int(sys.argv[4])-config["offset_height"]
config["source"] = sys.argv[5]

def logmsg(msg):
    msg = "pic.py > " + msg
    print(msg)
    now = datetime.datetime.now()
    with open("/var/log/unifi_view.log", "a") as myfile:
        myfile.write(now.strftime("%Y-%m-%d %H:%M:%S") + " " + msg + "\n")
        myfile.close()


def receiveSignal(signalNumber, frame):
    logmsg('Received: {number} on {id}'.format(number=signalNumber, id=sys.argv[6]))
    pygame.quit()
    time.sleep(0.5)
    exit()
    return

try:
    logmsg('Showing {file} on {id}'.format(file=sys.argv[5], id=sys.argv[6]))
    
    signals = {
        signal.SIGABRT: 'signal.SIGABRT',
        signal.SIGALRM: 'signal.SIGALRM',
        signal.SIGBUS: 'signal.SIGBUS',
        signal.SIGCHLD: 'signal.SIGCHLD',
        signal.SIGCONT: 'signal.SIGCONT',
        signal.SIGFPE: 'signal.SIGFPE',
        signal.SIGHUP: 'signal.SIGHUP',
        signal.SIGILL: 'signal.SIGILL',
        signal.SIGINT: 'signal.SIGINT',
        signal.SIGPIPE: 'signal.SIGPIPE',
        signal.SIGPOLL: 'signal.SIGPOLL',
        signal.SIGPROF: 'signal.SIGPROF',
        signal.SIGQUIT: 'signal.SIGQUIT',
        signal.SIGSEGV: 'signal.SIGSEGV',
        signal.SIGSYS: 'signal.SIGSYS',
        signal.SIGTERM: 'signal.SIGTERM',
        signal.SIGTRAP: 'signal.SIGTRAP',
        signal.SIGTSTP: 'signal.SIGTSTP',
        signal.SIGTTIN: 'signal.SIGTTIN',
        signal.SIGTTOU: 'signal.SIGTTOU',
        signal.SIGURG: 'signal.SIGURG',
        signal.SIGUSR1: 'signal.SIGUSR1',
        signal.SIGUSR2: 'signal.SIGUSR2',
        signal.SIGVTALRM: 'signal.SIGVTALRM',
        signal.SIGXCPU: 'signal.SIGXCPU',
        signal.SIGXFSZ: 'signal.SIGXFSZ',
        }

    for num in signals:
        signal.signal(num, receiveSignal)
 
    # Initializing PyGame and the camera.
    pygame.init()
    pygame.camera.init()
 
    # Specifying the camera to be used for capturing images. If there is a single camera, then it have the index 0.
    cam = pygame.camera.Camera(config["source"], (config["pic_width"], config["pic_height"]))
 
    # Preparing a resizable window of the specified size for displaying the captured images.
    window = pygame.display.set_mode((0, 0), pygame.NOFRAME)
    pygame.mouse.set_visible(False) #hide the mouse cursor
 
    # Starting the camera for capturing images.
    cam.start()
 
    while True:
        pygame.time.wait(1000/30)
        image = cam.get_image()
        
        image = pygame.transform.scale(image, (config["pic_width"], config["pic_height"])) # Image size width/height
        window.blit(image, (config["offset_width"], config["offset_height"]))
        
        pygame.display.update()
finally:
    cam.stop()
    pygame.quit()
    time.sleep(0.5)