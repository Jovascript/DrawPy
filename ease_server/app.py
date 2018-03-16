from flask import Flask, request, flash, redirect, render_template
import parse_hpgl
import drawpi
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def run_file():
    f = request.files["commands"]
    commands = f.read()
    commands = parse_hpgl.convert_to_jcode(commands)
    drawpi.runner.main(commands)
    flash("It has been executed")
    return redirect("/")

if __name__ == "__main__":
    app.run()