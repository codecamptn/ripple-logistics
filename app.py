from flask import Flask, jsonify, render_template

app = Flask(__name__, static_folder="static", static_url_path="/static")


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "RIPPLE backend is running"
    })


if __name__ == "__main__":
    app.run(debug=True)