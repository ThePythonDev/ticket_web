import os
import json
import base64
import pandas as pd
import google.generativeai as genai
from flask import Flask, request, render_template, send_file

app = Flask(__name__)

def sort_ticket_data(extracted_list):
    sorted_rows = []
    for item in extracted_list:
        row = {
            "Date": item.get("Date"),
            "Ticket": item.get("Ticket_Number"),
            "Truck ID": item.get("Truck_ID"),
            "Driver Name": item.get("Driver_Name"),
            "1= HANGER": "", "1.1-23.99": "", "24-35.99": "", "36-47.99": "", "48+": ""
        }
        try:
            val = float(item.get("Measure", 0))
            h_type = str(item.get("Hazard_Type", "")).upper()
            if "HANGER" in h_type:
                row["1= HANGER"] = 1
            elif "LEANER" in h_type:
                if 1.1 <= val <= 23.99: row["1.1-23.99"] = val
                elif 24.0 <= val <= 35.99: row["24-35.99"] = val
                elif 36.0 <= val <= 47.99: row["36-47.99"] = val
                elif val >= 48.0: row["48+"] = val
        except: pass
        sorted_rows.append(row)
    return sorted_rows

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    api_key = request.form.get('api_key')
    pdf_file = request.files.get('file')
    if not api_key or not pdf_file: return "Missing data", 400

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    pdf_data = base64.b64encode(pdf_file.read()).decode('utf-8')

    prompt = "Extract all tickets from the PDF. Return a JSON array of objects with keys: Ticket_Number, Date, Truck_ID, Driver_Name, Hazard_Type, Measure. No markdown."
    
    response = model.generate_content([{'mime_type': 'application/pdf', 'data': pdf_data}, prompt])

    try:
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(raw_text)
        final_data = sort_ticket_data(data)
        df = pd.DataFrame(final_data)
        csv_path = "/tmp/extracted_tickets.csv" # Use /tmp for web hosts
        df.to_csv(csv_path, index=False)
        return send_file(csv_path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
