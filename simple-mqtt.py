################################################################################
#
# Bare Conductive Pi Cap
# ----------------------
#
# simple-mqtt.py - sends capacitive touch / release data from MPR121 to a
# specified MQTT broker.
#
# Written for Raspberry Pi.
#
# Original example by Sven Haiges.
#
# Bare Conductive code written by Szymon Kaliski.
#
# This work is licensed under a Creative Commons Attribution-ShareAlike 3.0
# Unported License (CC BY-SA 3.0) http://creativecommons.org/licenses/by-sa/3.0/
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#################################################################################

from time import sleep
from mosquitto import Mosquitto
import signal, sys, getopt, MPR121

try:
  sensor = MPR121.begin()
except Exception as e:
  print e
  sys.exit(1)

# handle ctrl+c gracefully
def signal_handler(signal, frame):
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# print help
def print_help():
  print "Sends Pi Cap touch readings through MQTT - MUST be run as root.\n"
  print "Usage: python simple-mqtt.py [OPTIONS]\n"
  print "Options:"
  print "  -b, --broker    MQTT broker [REQUIRED]"
  print "  -u, --username  MQTT broker username [OPTIONAL]"
  print "  -p, --password  MQTT broker password [OPTIONAL]"
  print "      --help      displays this message"
  sys.exit(0)

broker   = ""
username = None
password = None

# arguments parsing
def parse_args(argv):
  # we need to tell python that those variables are global
  # we don't want to create new local copies, but change global state
  global broker, username, password

  try:
    opts, args = getopt.getopt(argv, "b:u:p:", [ "broker=", "username=", "password=", "help" ])
  except getopt.GetoptError:
    print_help()

  for opt, arg in opts:
    if opt in ("-b", "--broker"):
      broker = arg
    elif opt in ("-u", "--username"):
      username = arg
    elif opt in ("-p", "--password"):
      password = arg
    elif opt in ("--help"):
      print_help()

# parse arguments on start
parse_args(sys.argv[1:])

# stop if no broker is provided
if not broker:
  print_help()

# setup MQTT
client = Mosquitto()

# set username/password if needed
if username:
  client.username_pw_set(username, password)

# connect to broker
# Python version doesn't need 'mqtt://'
client.connect(broker)

while True:
  if sensor.touch_status_changed():
    sensor.update_touch_data()

    for i in range(12):
      if sensor.is_new_touch(i):
        if username:
          client.publish(username + "/feeds/picap-touched", i)
        else:
          client.publish("/feeds/picap-touched", i)

      elif sensor.is_new_release(i):
        if username:
          client.publish(username + "/feeds/picap-released", i)
        else:
          client.publish("/feeds/picap-released", i)

  sleep(0.01)
