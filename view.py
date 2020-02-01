## Install instructions
# sudo apt-get install omxplayer screen
#     os.system("screen -dmS pic sh -c 'python pic.py'")
import os, urlparse, time, sys, urllib2, subprocess, datetime, json

running = {}

config_modified = 0.0

basepath = os.path.dirname(os.path.realpath(__file__)) + "/"

config = {}
config_modified = os.stat(basepath + "config.json").st_mtime

player_env = os.environ.copy()

def logmsg(msg):
    print(msg)
    now = datetime.datetime.now()
    with open("/var/log/unifi_view.log", "a") as myfile:
        myfile.write(now.strftime("%Y-%m-%d %H:%M:%S") + " " + msg + "\n")
        myfile.close()

def json_load(jsonfile):
    f = open(jsonfile, 'r')
    content = f.read()
    f.close()
    try:
        return json.loads(content)
    except ValueError, e:
        logmsg(">>> JSON error in {file}".format(file=jsonfile))
        return {}
        
def config_read():
    global config, config_modified
    config = json_load(basepath + "config.json")
    config_modified = os.stat(basepath + "config.json").st_mtime
    config["blanking"] = " --blank=0xFF000000 "
    for source in config["content"]:
        if config['content'][source]['type'] != 'stream' and source in config['layout']:
            config["blanking"] = "" # blanking screen isnt needed when an image is in the list
    

def measure_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    return (temp.replace("temp=",""))

def start_player(x1, y1, x2, y2, rtsp, id):
    if config["content"][id].has_key('args'):
        os.system("screen -dmS {id} sh -c 'omxplayer --avdict rtsp_transport:tcp --win \"{x1} {y1} {x2} {y2}\" {rtsp} {args} {blank} --dbus_name org.mpris.MediaPlayer2.omxplayer.{id}'".format(x1=x1, y1=y1, x2=x2, y2=y2, rtsp=rtsp, id=id, args=streams[id]['args']))
    else:
        os.system("screen -dmS {id} sh -c 'omxplayer --avdict rtsp_transport:tcp --win \"{x1} {y1} {x2} {y2}\" {rtsp} {blank} --live -n -1 --timeout 30 --dbus_name org.mpris.MediaPlayer2.omxplayer.{id}'".format(x1=x1, y1=y1, x2=x2, y2=y2, rtsp=rtsp, id=id, blank=config["blanking"]))
    if len(config["blanking"]) > 0:
        config["blanking"] = ""

def set_player_env():
    try:
        global player_env
        playerbus = open("/tmp/omxplayerdbus.root", 'r')
        player_env["DBUS_SESSION_BUS_ADDRESS"] = playerbus.read().strip()
        playerbus.close()
    
        playerpid = open("/tmp/omxplayerdbus.root.pid", 'r')
        player_env["DBUS_SESSION_BUS_PID"] = playerpid.read().strip()
        playerpid.close()
    except:
        print("Could not set player env")
        
def check_player(player_id, player_rtsp):
    try:
        test = subprocess.Popen(['dbus-send', '--print-reply=literal', '--session', '--reply-timeout=1000', '--dest=org.mpris.MediaPlayer2.omxplayer.' + str(player_id), '/org/mpris/MediaPlayer2', 'org.freedesktop.DBus.Properties.Position'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=player_env)
        stdout,stderr = test.communicate()
        position = stdout.strip()
        
        position = position.split(" ")
           
        if position[0] == "int64" and int(position[1]) > 0:
            return True # player is fine
        else:
            logmsg("{id}: {stdout} - Error: {stderr}".format(id=player_id, stdout=stdout.strip(), stderr=str(stderr)))
            player_pid = get_player_pid(player_rtsp)
            screen_pid = get_screen_pid(player_rtsp)
            if player_pid != -1:
                logmsg("Trying to fix " + player_id)
                os.system("kill -9 " + str(player_pid))
                os.system("kill -9 " + str(screen_pid))
            else:
                logmsg("Could not determine PID for " + player_id)
                stopstrim()
                time.sleep(2)
                startstrim()
                time.sleep(20)
    except:
        print("Could not check player {id}".format(id=player_id))
    return False # something is wrong with the player
    
def get_player_pid(stream):
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            out = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read().split('\0')
            if 'omxplayer' in out[0]:
                if out[5].strip() == stream.strip():
                    return int(pid)
        except IOError: # proc has already terminated
            return -1
            
def get_screen_pid(stream):
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            out = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read().split('\0')
            if 'SCREEN' in out[0]:
                if stream in out[5]:
                    return int(pid)
        except IOError: # proc has already terminated
            return -1

def startstrim():
    global running
    config_read()
    
    running = {}
    os.system("killall omxplayer screen") # Make sure there is no leftover streams running
    time.sleep(1)
    
    logmsg("Starting streams")
    for pos in config["layout"]:
        try:
            if pos in config["content"]: # Check if the layout position has been found in the list of streams
                if config['content'][pos]['type'] == 'stream':
                    running[pos] = config['content'][pos]['source']
                    logmsg("Starting {rtsp} on {pos}".format(rtsp=running[pos], pos=pos))
                    start_player(config["layout"][pos]['x1'], config["layout"][pos]['y1'], config["layout"][pos]['x2'], config["layout"][pos]['y2'], config["content"][pos]['source'], pos)
                elif config['content'][pos]['type'] == 'image':
                    logmsg("Starting {rtsp} on {pos}".format(rtsp=config['content'][pos]['source'], pos=pos))
                    #os.system("screen -dmS {id} sh -c 'python {basepath}pic.py {x1} {y1} {x2} {y2} {source} {id}'".format(x1=config['layout'][pos]['x1'], y1=config['layout'][pos]['y1'], x2=config['layout'][pos]['x2'], y2=config['layout'][pos]['y2'], source=config['content'][pos]['source'], id=pos, basepath=basepath))
                    os.system("python {basepath}pic.py {x1} {y1} {x2} {y2} {source} {id} &".format(x1=config['layout'][pos]['x1'], y1=config['layout'][pos]['y1'], x2=config['layout'][pos]['x2'], y2=config['layout'][pos]['y2'], source=config['content'][pos]['source'], id=pos, basepath=basepath))
                elif config['content'][pos]['type'] == 'video':
                    logmsg("Starting {rtsp} on {pos}".format(rtsp=config['content'][pos]['source'], pos=pos))
                    #os.system("screen -dmS {id} sh -c 'python {basepath}pic.py {x1} {y1} {x2} {y2} {source} {id}'".format(x1=config['layout'][pos]['x1'], y1=config['layout'][pos]['y1'], x2=config['layout'][pos]['x2'], y2=config['layout'][pos]['y2'], source=config['content'][pos]['source'], id=pos, basepath=basepath))
                    os.system("python {basepath}usb_cam.py {x1} {y1} {x2} {y2} {source} {id} &".format(x1=config['layout'][pos]['x1'], y1=config['layout'][pos]['y1'], x2=config['layout'][pos]['x2'], y2=config['layout'][pos]['y2'], source=config['content'][pos]['source'], id=pos, basepath=basepath))

                else:
                    logmsg("Unknown type '{type}' has been used for {pos}".format(type=config['content'][pos]['type'], pos=pos))
        except Exception as e:
            print(e)
            logmsg("Could not start {pos}".format(pos=pos))

def stopstrim():
    logmsg("Removing sources")
    os.system("killall omxplayer screen")
    #os.system("pkill -f pic.py")
    for pos in config["layout"]:
        #os.system("ps aux  |  grep -i pic.py |  awk '{print $2}'  |  xargs sudo kill -10")
        os.system("pkill -10 -f '.*{id}'".format(id=pos))
    os.system("screen -wipe")
    
def main():
    logmsg(">> Starting")
    
    with open('/boot/config.txt', 'r') as f:
        found = False
        for line in f:
            cmd = line.strip().split('=')
            if cmd[0] == "gpu_mem":
                found = True
                if int(cmd[1]) < 256:
                    found = False
        if found == False:
            print("Consider using at least 256MB for gpu memory by adding 'gpu_mem=256' to /boot/config.txt")
            time.sleep(15) # Allow some time for the message to be seen
        
    startstrim()
    
    logmsg("Watchdoge started")
    
    while True:
        time.sleep(30)
        
        if os.stat(basepath + "config.json").st_mtime != config_modified:
            logmsg("Configuration has changed, reloading")
            stopstrim()
            time.sleep(1)
            startstrim()
        else:
            #os.system('clear')
            set_player_env() # Set player environment
                
            for pos in running:
                try:
                    if check_player(pos, running[pos][1]) is False:
                        logmsg("{pos} is not playing {rtsp}".format(rtsp=running[pos], pos=pos))
                        start_player(config["layout"][pos]['x1'], config["layout"][pos]['y1'], config["layout"][pos]['x2'], config["layout"][pos]['y2'], streams[pos]['rtsp'], pos)
                except:
                    pass

    logmsg("Loop stopped???")
            
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            print("Killing everything")
            stopstrim()
            os.system("killall omxplayer screen")
            sys.exit(0)
        except SystemExit:
            os._exit(0)
