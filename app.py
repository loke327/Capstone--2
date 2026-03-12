from flask import Flask, request, jsonify,render_template
import sqlite3
from liveness import liveness_check
from crypto_utils import *
from flask import session, redirect, url_for, render_template
import threading
from datetime import datetime 
import os
import cv2
import time
from flask import send_from_directory
from blockchain.sidechain import Sidechain
from blockchain.main_chain import MainChain
from blockchain.utils import sha256_hash
import threading
from biometric_recording import start_biometric_recording



recording = False
video_thread = None
video_path = None
document_chain = Sidechain("DOCUMENT")
media_chain = Sidechain("MEDIA")
biometric_chain = Sidechain("BIOMETRIC")
court_chain = Sidechain("COURT")

main_chain = MainChain()


app = Flask(__name__)
app.secret_key = "doctor_secret_key"
DB = "database.db"

def db_connect():
    return sqlite3.connect(DB)

# Create table
with sqlite3.connect("database.db") as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS court_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT,
        investigation_id TEXT,
        hash TEXT,
        received_at TEXT
    )
    """)


doctor_private, doctor_public = generate_keys()
assistant_private, assistant_public = generate_keys()

def record_video():
    global recording, video_path

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    video_path = f"recordings/final_evidence{int(time.time())}.mp4"
    out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))

    while recording:
        ret, frame = cap.read()
        if not ret:
            continue
        out.write(frame)

    cap.release()
    out.release()
@app.route("/add_forensic_data", methods=['POST'])
def add_forensic_data():

    data = request.get_json(silent=True)

    if not data:
        return {"error": "JSON body required"}, 400

    forensic_data = data.get("content")
    data_type = data.get("type")

    data_hash = sha256_hash(forensic_data)

    if data_type == "document":
        block = document_chain.add_block(data_hash)
        anchor = main_chain.anchor_sidechain("DOCUMENT", document_chain.latest_hash())

    elif data_type == "media":
        block = media_chain.add_block(data_hash)
        anchor = main_chain.anchor_sidechain("MEDIA", media_chain.latest_hash())

    elif data_type == "biometric":
        block = biometric_chain.add_block(data_hash)
        anchor = main_chain.anchor_sidechain("BIOMETRIC", biometric_chain.latest_hash())

    elif data_type == "court":
        block = court_chain.add_block(data_hash)
        anchor = main_chain.anchor_sidechain("COURT", court_chain.latest_hash())

    else:
        return {"error": "Invalid forensic type"}, 400

    return {
        "message": "Forensic data added successfully",
        "data_hash": data_hash,
        "sidechain_block": block,
        "mainchain_anchor": anchor
    }

@app.route("/verify_forensic_data", methods=['GET','POST'])
def verify_forensic_data():
    
    data = request.get_json(silent=True)

    if not data:
        return {"error": "JSON body required"}, 400
    original_data = data.get("content")
    claimed_hash = data.get("hash")

    recalculated_hash = sha256_hash(original_data)

    if recalculated_hash == claimed_hash:
        return {
            "status": "VALID",
            "message": "Evidence integrity verified"
        }
    else:
        return {
            "status": "TAMPERED",
            "message": "Evidence integrity compromised"
        }

@app.route("/debug_sidechain")
def debug_sidechain():
    return {
        "court_sidechain": court_chain.chain,
        "document_sidechain":document_chain.chain,
        "media_sidechain": media_chain.chain,
        "main_chain": main_chain.chain
    }


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/court")
def court():
    return render_template("court.html")

@app.route("/recordings/<path:filename>")
def recordings(filename):
    return send_from_directory("recordings", filename)

@app.route("/login", methods=["GET", "POST"])
def login():
    global recording, video_thread

    if request.method == "GET":
        return render_template("login.html")
    
    data = request.get_json()

    # SIMPLE demo credentials
    if data["username"] == "doctor" and data["password"] == "1234":
        session["doctor_logged_in"] = True
        video_thread = threading.Thread(
            target=start_biometric_recording
            )
        video_thread.start()
        return jsonify({"success": True})

    return jsonify({"success": False}), 401


@app.route("/dashboard")
def dashboard():
    if not session.get("doctor_logged_in"):
        return redirect("/login")

    # Run liveness ONLY ONCE
    if not session.get("liveness_verified"):
        if not liveness_check():
            return "Liveness failed", 403
        session["liveness_verified"] = True

    return render_template("dashboard.html")

@app.route("/save_temp", methods=["POST"])
def save_temp():
    if not session.get("doctor_logged_in"):
        return jsonify({"error": "Unauthorized"}), 403

    session["case_data"] = request.get_json()
    return jsonify({"success": True})

@app.route("/get_temp")
def get_temp():
    return jsonify(session.get("case_data"))

@app.route("/review")
def review():
    if not session.get("doctor_logged_in"):
        return redirect("/login")

    if not session.get("case_data"):
        return redirect("/dashboard")

    return render_template("review.html")

@app.route("/write_report", methods=["POST"])
def write_report():
    
    global recording

    if not session.get("doctor_logged_in"):
        return jsonify({"error": "Unauthorized"}), 403

    recording = False

    case = session.get("case_data")
    signed_name = request.get_json().get("signed_name")
    
    # Path of merged evidence file
    video_path = "recordings/final_evidence.mp4"
    
    # Generate hash of evidence file FIRST
    with open(video_path, "rb") as f:
        media_hash = sha256_hash(f.read()
                                 )
        
    # Now create the report text    
    full_text = f"""
    Case ID: {case['case_id']}
    Case Name: {case['case_name']}
    Investigation ID: {case['investigation_id']}
    Doctor ID: {case['doctor_id']}
    Doctor Name: {case['doctor_name']}
    Working At: {case['doctor_org']}
    Summary: {case['summary']}
    Signed By: {signed_name}
    Video Evidence: {video_path}
    Evidence hash: {media_hash}
    """

    hash_val = sha256_hash(full_text.encode())
     # 2️⃣ Generate SHA-256 hash
    # -------------------------------
    # 🔗 SIDECHAIN INTEGRATION (ADD HERE)
    # -------------------------------
    if video_path:
        with open(video_path, "rb") as f:
            media_hash = sha256_hash(f.read())
    else:
        media_hash = sha256_hash("no_video".encode())
        
    doc_hash = sha256_hash(case["summary"].encode())

    # 3️⃣ Add block to COURT sidechain
    court_block = court_chain.add_block(hash_val)

    document_block = document_chain.add_block(doc_hash)
    
    media_block = media_chain.add_block(media_hash)
    # 4️⃣ Anchor sidechain hash to MAIN chain
    main_block = main_chain.anchor_sidechain(
        "COURT",
        court_chain.latest_hash()
    )

    main_chain.anchor_sidechain(
        "DOCUMENT",
        document_chain.latest_hash()
    )

    main_chain.anchor_sidechain(
        "MEDIA",
        media_chain.latest_hash()
    )
    signature = sign_hash(doctor_private, hash_val)

    with sqlite3.connect("database.db") as conn:
     cur = conn.cursor()
     cur.execute(
        "INSERT INTO reports (summary, hash, doctor_sig) VALUES (?, ?, ?)",
        (
            full_text,   # ✅ ALL case + doctor + summary + signed by + video
            hash_val,    # ✅ hash
            signature    # ✅ digital signature (RSA)
        )
     )
     cur.execute(
                """
                INSERT INTO court_records (case_id, investigation_id, hash, received_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    case["case_id"],
                    case["investigation_id"],
                    hash_val,
                    datetime.now().isoformat()
                )
            )

    return jsonify({
        "message":"Digitally signed & sent to court",
        "case_id":case["case_id"],
        "hash": hash_val,
        "court_sidechain_block": court_block,
        "mainchain_block": main_block,
        "signed_by": signed_name,
        "video": video_path
    })

@app.route("/court_verify_case/<case_id>")
def court_verify_case(case_id):

    with sqlite3.connect("database.db") as conn:
        # 1️⃣ Get hash from court registry
        cur = conn.execute(
            "SELECT hash FROM court_records WHERE case_id=?",
            (case_id,)
        )
        row = cur.fetchone()

        if not row:
            return jsonify({"error": "Case ID not found in court records"}), 404

        hash_val = row[0]

        # 2️⃣ Get full report using hash
        cur = conn.execute(
            "SELECT summary FROM reports WHERE hash=?",
            (hash_val,)
        )
        report = cur.fetchone()

        if not report:
            return jsonify({"error": "Report not found"}), 404

    return jsonify({
        "case_id": case_id,
        "hash": hash_val,
        "full_details": report[0]
    })


@app.route("/court_verify/<hash_val>")
def court_verify(hash_val):
    with sqlite3.connect("database.db") as conn:
        cur = conn.execute(
            "SELECT case_id, investigation_id, received_at FROM court_records WHERE hash=?",
            (hash_val,)
        )
        row = cur.fetchone()

    if not row:
        return jsonify({"valid": False})

    return jsonify({
        "valid": True,
        "case_id": row[0],
        "investigation_id": row[1],
        "received_at": row[2]
    })

if __name__ == "__main__":
    app.run(debug=True)