from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit
from drawpi.svgreader import slice, parse
from threading import Thread
import logging
from drawpi.runner import main

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TopSecretMagic'
socketio = SocketIO(app)

thread = None

class RunningThread(Thread):
    def __init__(self, commands, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = commands
    
    def run(self):
        try:
            main(self.commands)
            socketio.emit("StatusUpdate", {"error": False, "text":"Draw Completed Successfully"})
        except Exception as e:
            logging.error(str(e))
            socketio.emit("StatusUpdate", {"error": True, "text":"The application errored: "+ str(e)})
        socketio.emit("NewStatus", "ready")



class LogSenderHandler(logging.Handler):
    def emit(self, record):
        log = self.format(record)
        socketio.emit("CommandOutput", log)
        return True


@app.route("/")
def index():
    return send_file("site/index.html")

@socketio.on("SVGLoad")
def load_svg(text):
    emit("SVGProcessed", slice(parse(text)))

@socketio.on("RunCommands")
def run_commands(commands):
    global thread

    if thread is None or not thread.is_alive():
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
            datefmt="%Y-%m-%d %H:%M:%S", 
            level=logging.DEBUG, 
            handlers=[LogSenderHandler()]
        )
        thread = RunningThread(commands)
        thread.start()
        socketio.emit("NewStatus", "running")
        emit("StatusUpdate", {"error": False, "text":"Draw has begun"})
    else:
        emit("StatusUpdate", {"error": True, "text":"Cannot Start while Running"})
        
    

def run():
    socketio.run(app)

if __name__ == "__main__":
    run()