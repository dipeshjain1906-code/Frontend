import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from db_connection import get_db
from db_procedures import *

app = Flask(__name__)
CORS(app)

db = get_db()

# ---------------- PATIENT ----------------
@app.route('/api/patients', methods=['GET'])
def get_patients():
    try:
        return jsonify(list(db.patients.find({}, {"_id": 0})))
    except:
        return jsonify({"error": "Failed"}), 500


@app.route('/api/patients', methods=['POST'])
def add_patient():
    data = request.json
    if not data.get("Name"):
        return jsonify({"error": "Name required"}), 400

    try:
        insert_patient(db, data)
        return jsonify({"message": "Added", "PatientID": data.get("PatientID")})
    except Exception as e:
        return jsonify({"error": f"Database insertion failed: {str(e)}"}), 500


# ---------------- VACCINE ----------------
@app.route('/api/vaccines', methods=['GET'])
def get_vaccines():
    return jsonify(list(db.vaccines.find({}, {"_id": 0})))


@app.route('/api/vaccines', methods=['POST'])
def add_vaccine():
    try:
        insert_vaccine(db, request.json)
        return jsonify({"message": "Added", "VaccineID": request.json.get("VaccineID")})
    except Exception as e:
        return jsonify({"error": f"Database insertion failed: {str(e)}"}), 500


# ---------------- ALLERGY ----------------
@app.route('/api/allergies', methods=['POST'])
def add_allergy():
    try:
        insert_allergy(db, request.json)
        return jsonify({"message": "Added"})
    except Exception as e:
        return jsonify({"error": f"Database insertion failed: {str(e)}"}), 500


# ---------------- CONTRA ----------------
@app.route('/api/contraindications', methods=['POST'])
def add_contra():
    try:
        insert_contraindication(db, request.json)
        return jsonify({"message": "Added", "ContraindicationID": request.json.get("ContraindicationID")})
    except Exception as e:
        return jsonify({"error": f"Database insertion failed: {str(e)}"}), 500


# ⭐ CHECK
@app.route('/api/check_contraindication', methods=['POST'])
def check_contra():
    data = request.json
    result = check_contraindication(db, data["PatientID"], data["VaccineID"])
    return jsonify(result)


# ---------------- IMMUNIZATION ----------------
@app.route('/api/immunizations', methods=['POST'])
def add_immunization():
    data = request.json

    try:
        result = check_contraindication(db, data["PatientID"], data["VaccineID"])

        if result["blocked"]:
            return jsonify({"error": "Blocked", "details": result}), 400

        insert_immunization(db, data)
        return jsonify({"message": "Added"})
    except Exception as e:
        return jsonify({"error": f"Database insertion failed: {str(e)}"}), 500


# ---------------- ADVERSE REACTIONS ----------------
@app.route('/api/adverse_reactions', methods=['POST'])
def record_reaction():
    try:
        data = request.json
        insert_adverse_reaction(db, data)
        return jsonify({"message": "Reaction recorded"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ---------------- DASHBOARD ----------------
@app.route('/api/dashboard/<patient_id>', methods=['GET'])
def get_dashboard(patient_id):
    try:
        data = get_patient_dashboard_data(db, patient_id)
        if not data:
            return jsonify({"error": "Patient not found"}), 404
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', '8000'))
    app.run(host='0.0.0.0', port=port, debug=False)
