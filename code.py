import wifi
from adafruit_wsgi.wsgi_app import WSGIApp
import wsgiserver
import time
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import usb_hid
from collections import OrderedDict

time.sleep(3)

keys = OrderedDict([
    ('A', Keycode.A), ('B', Keycode.B), ('C', Keycode.C), ('D', Keycode.D),
    ('E', Keycode.E), ('F', Keycode.F), ('G', Keycode.G), ('H', Keycode.H),
    ('I', Keycode.I), ('J', Keycode.J), ('K', Keycode.K), ('L', Keycode.L),
    ('M', Keycode.M), ('N', Keycode.N), ('O', Keycode.O), ('P', Keycode.P),
    ('Q', Keycode.Q), ('R', Keycode.R), ('S', Keycode.S), ('T', Keycode.T),
    ('U', Keycode.U), ('V', Keycode.V), ('W', Keycode.W), ('X', Keycode.X),
    ('Y', Keycode.Y), ('Z', Keycode.Z), ("DOT", Keycode.PERIOD),
    ('WINDOWS', Keycode.WINDOWS), ('BACKSPACE', Keycode.BACKSPACE),
    ('SPACE', Keycode.SPACE), ('ENTER', Keycode.ENTER),
    ('CAPSLOCK', Keycode.CAPS_LOCK), ('DOWNARROW', Keycode.DOWN_ARROW),
    ('UPARROW', Keycode.UP_ARROW), ('LEFTARROW', Keycode.LEFT_ARROW),
    ('RIGHTARROW', Keycode.RIGHT_ARROW),
])

def start_wifi():
    if not wifi.radio.ipv4_address_ap:
        wifi.radio.start_ap("STEPINET", "stepi123")
    return wifi.radio.ipv4_address_ap

web_app = WSGIApp()
kbd = Keyboard(usb_hid.devices)

port = 80
server = None
running = True

def start_server():
    global server, port
    while True:
        try:
            server = wsgiserver.WSGIServer(port, application=web_app)
            server.start()
            break
        except OSError as e:
            if e.errno == 112:
                port += 1
            else:
                raise

@web_app.route("/shutdown")
def shutdown(request):
    global running
    running = False
    return "200 OK", [('Content-Type', 'text/html')], ["KILLED"]

@web_app.route("/write/<keyname>")
def _write(request, keyname):
    if keyname in keys:
        try:
            kbd.send(keys[keyname])
            time.sleep(0.1)
        except Exception as e:
            return "500 Internal Server Error", [('Content-Type', 'text/html')], [f"Error: {str(e)}"]
        return "302 Found", [('Location', '/')], []
    return "404 Not Found", [('Content-Type', 'text/html')], ["Key not found"]

@web_app.route("/")
def index(request):
    response = """
    <head>
        <meta charset='UTF-8'>
        <title>PIkiboard</title>

        <style>
            .kb {
                display: inline-block;
            }

            .btn {
                  align-items: center;
                  appearance: none;
                  background-color: #FCFCFD;
                  border-radius: 4px;
                  border-width: 0;
                  box-shadow: rgba(45, 35, 66, 0.4) 0 2px 4px,rgba(45, 35, 66, 0.3) 0 7px 13px -3px,#D6D6E7 0 -3px 0 inset;
                  box-sizing: border-box;
                  color: #36395A;
                  cursor: pointer;
                  display: inline-flex;
                  font-family: "JetBrains Mono",monospace;
                  height: 48px;
                  justify-content: center;
                  line-height: 1;
                  list-style: none;
                  overflow: hidden;
                  padding-left: 16px;
                  padding-right: 16px;
                  position: relative;
                  text-align: left;diq
                  text-decoration: none;
                  transition: box-shadow .15s,transform .15s;
                  user-select: none;
                  -webkit-user-select: none;
                  touch-action: manipulation;
                  white-space: nowrap;
                  will-change: box-shadow,transform;
                  font-size: 18px;
                }
                
                .btn:focus {
                  box-shadow: #D6D6E7 0 0 0 1.5px inset, rgba(45, 35, 66, 0.4) 0 2px 4px, rgba(45, 35, 66, 0.3) 0 7px 13px -3px, #D6D6E7 0 -3px 0 inset;
                }
                
                .btn:hover {
                  box-shadow: rgba(45, 35, 66, 0.4) 0 4px 8px, rgba(45, 35, 66, 0.3) 0 7px 13px -3px, #D6D6E7 0 -3px 0 inset;
                  transform: translateY(-2px);
                }
                
                .btn:active {
                  box-shadow: #D6D6E7 0 3px 7px inset;
                  transform: translateY(2px);
                }
        </style>
    </head>"""
    for key in keys:
        if key == "WINDOWS":
            response += f'''
                <br>
                <br>
                <a class="btn" href="/write/{key}">{key}</a>
            '''
        else:
            response += f'''
                <a class="btn" href="/write/{key}">{key}</a>
            '''
    return "200 OK", [('Content-Type', 'text/html')], [response]

if __name__ == "__main__":
    start_wifi()
    start_server()
    while True:
        try:
            server.update_poll()
            time.sleep(0.01)
            if not wifi.radio.ipv4_address_ap:
                print("WiFi AP dropped, restarting AP.")
                start_wifi()
        except OSError as e:
            print("Server error:", e)
            time.sleep(1)
            start_wifi()
            start_server()
