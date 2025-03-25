from flask import Flask, render_template, request, send_file
import qrcode
import qrcode.image.svg
import cv2
import numpy as np
import os
import uuid
import time  

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join("static", "qr_codes")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist

# QR Code Generator function (Route)

@app.route("/", methods=["GET", "POST"])
def index():
    qr_code_url = None  # URL to display the QR code
    filename = None

    if request.method == "POST":
        data = request.form.get("qr_data")
        if data:
            timestamp = int(time.time())  # Generate unique filename
            filename = f"qrcode_{timestamp}.png"
            qr_code_path = os.path.join(UPLOAD_FOLDER, filename)

            # Generate and save the QR code
            qr = qrcode.make(data)
            qr.save(qr_code_path)

            qr_code_url = f"/{qr_code_path}"  # Flask URL path for the QR code

            print(f"Generated QR Code: {qr_code_url}")  # Debugging output

    return render_template("index.html", qr_code=qr_code_url, filename=filename)

# Route (function) to download the QR code as an SVG file
@app.route("/download/<filename>")
def download_qr(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

# QR Code Scanner Route
@app.route("/scan", methods=["POST"])
def scan_qr():
    file = request.files["file"]
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Read the image using OpenCV
        img = cv2.imread(file_path)
        if img is None:
            return "Error: Unable to read the image. Please upload a valid QR code image.", 400

        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)

        if not data:
            return "Error: No QR code detected in the uploaded image.", 400

        return render_template("index.html", scanned_data=data)

    return "No QR Code found", 400


if __name__ == "__main__":
    app.run(debug=True)
