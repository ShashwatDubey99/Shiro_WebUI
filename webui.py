from flask import Flask, render_template
import ssl

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

@app.route("/easyrun")
def img2img():
    return render_template("easyrun.html")

if __name__ == "__main__":
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile="./cert.pem", keyfile="./key.pem")
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=ssl_context)
