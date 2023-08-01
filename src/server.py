from flask import Flask, request, send_file


app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_csv():
    if "file" not in request.files:
        return "No file part in the request", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    file.save("chrome_history_received.csv")  # Save the uploaded file with a new name
    return "File uploaded successfully"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
