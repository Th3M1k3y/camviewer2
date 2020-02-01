import time, pygame, sys, signal, os, datetime

# sudo python pic.py 0 540 958 539 /home/pi/img.jpg

offset_width = int(sys.argv[1]) #0 how far off to left corner to display photos
offset_height = int(sys.argv[2]) #540 how far off to left corner to display photos

pic_width = int(sys.argv[3])-offset_width #958 #how wide to scale the jpg when replaying
pic_height = int(sys.argv[4])-offset_height #539 how high to scale the jpg when replaying

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
    
    #signal.signal(signal.SIGUSR1, receiveSignal)
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
    pygame.mouse.set_visible(False) #hide the mouse cursor	
    filename = sys.argv[5]
    img=pygame.image.load(filename)
    img = pygame.transform.scale(img, (pic_width, pic_height)) # Image size width/height
    screen.blit(img, (offset_width,offset_height))
    pictureFrame = pygame.Rect(offset_width, offset_height, pic_width, pic_height)
    pygame.display.update(pictureFrame)
    while True:
        pygame.time.wait(1000)
        pygame.display.update(pictureFrame)
finally:
    pygame.quit()
    time.sleep(0.5)