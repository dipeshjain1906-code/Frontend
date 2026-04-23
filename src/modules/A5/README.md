# Clinic Management System 🏥

A database management system project developed for the Semester 4 DBMS coursework. This application provides a comprehensive UI and robust backend to securely manage patient clinical records, vaccination inventories, and patient logic.

## 👥 Team Members
- Dipesh Jain
- Bharadwaj Chikka
- Aditya Ekka

## 🛠️ Technology Stack
- **Frontend:** Streamlit 
- **Backend API:** Flask
- **Database:** MongoDB (PyMongo)
- **Data Visualizations:** Pandas

## 🚀 Features
- **Patient Management:** Track patient demographics, allergies, and contraindications.
- **Immunization Tracking:** Log and monitor vaccine doses safely.
- **Automated Logic Checks:** Prevent vaccines if a patient has a flagged contraindication. 
- **Analytics Dashboard:** Visual representation of key metrics and vaccination trends.

## 🔧 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-link>
   cd DBMS-Project/Chatgpt
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure you have Flask, Streamlit, PyMongo, requests, and pandas installed)*

3. **Start the database:**
   Ensure your local MongoDB instance is running on port `27017` and the `clinic_db` is initialized.

4. **Run the Backend (Flask):**
   Open a terminal and run the API:
   ```bash
   python flask_app.py
   ```
   The backend will run on `http://127.0.0.1:5005`.

5. **Run the Frontend (Streamlit):**
   Open a separate terminal and run the UI:
   ```bash
   streamlit run main.py
   ```

## 📝 Future Updates
- Advanced user authentication
- Exporting reports to PDF
- Complete testing suite integration

## ☁️ Streamlit Community Cloud Deployment

This project now supports **Streamlit-first deployment** (where only `main.py` is launched):

1. Set the Streamlit app entrypoint to: `src/modules/A5/main.py`
2. Add dependencies in `requirements.txt` (Streamlit, Flask, flask-cors, pymongo, python-dotenv, requests, pandas).
3. Configure secrets/environment variables in Streamlit Cloud:
   - `MONGO_URI` (required)
   - `FLASK_PORT=8000` (optional; default is 8000)
   - `API_BASE_URL=http://127.0.0.1:8000/api` (optional; auto-derived if omitted)
4. Deploy. The Streamlit app automatically starts the Flask backend internally if it is not already running.

For VM/Docker environments where custom start commands are allowed, you can still run:
```bash
python src/modules/A5/run_app.py
```
