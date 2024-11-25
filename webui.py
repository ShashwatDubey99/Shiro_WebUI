from flask import Flask, render_template

app = Flask(__name__,static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gallery")
def gallery():
    return render_template("civitai_gallary_test.html")

@app.route("/tex2img")
def tex2img():
    return render_template("tex2img.html")

@app.route("/img2img")
def img2img():
    return render_template("img2img.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
