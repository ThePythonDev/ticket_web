import os
import json
import base64
import pandas as pd
import google.generativeai as genai
from flask import Flask, request, render_template, send_file

app = Flask(__name__)

# --- GET API KEY FROM SYSTEM VARIABLE ---
SYSTEM_API_KEY = os.environ.get('api_key')

def sort_ticket_data(extracted_list):
    sorted_rows = []
    for item in extracted_list:
        # Default empty columns for the spreadsheet
        row = {
            "Date": item.get("Date"),
            "Ticket": item.get("Ticket_Number"),
            "Truck ID": item.get("Truck_ID"),
            "Driver Name": item.get("Driver_Name"),
            "1= HANGER": "", 
            "1.1-23.99": "", 
            "24-35.99": "", 
            "36-47.99": "", 
            "48+": ""
        }
        
        try:
            # Clean up the measurement value (remove units if AI included them)
            measure_str = str(item.get("Measure", "0")).split(' ')[0]
            val = float(measure_str)
            h_type = str(item.get("Hazard_Type", "")).upper()

            if "HANGER" in h_type:
                row["1= HANGER"] = 1
            elif "LEANER" in h_type:
                if 1.1 <= val <= 23.99: 
                    row["1.1-23.99"] = val
                elif 24.0 <= val <= 35.99: 
                    row["24-35.99"] = val
                elif 36.0 <= val <= 47.99: 
                    row["36-47.99"] = val
                elif val >= 48.0: 
                    row["48+"] = val
        except:
            pass
            
        sorted_rows.append(row)
    return sorted_rows

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if not SYSTEM_API_KEY:
        return "Error: System variable 'api_key' not found on server.", 500
    
    pdf_file = request.files.get('file')
    if not pdf_file: 
        return "Error: No file uploaded.", 400

    # Configure AI
    genai.configure(api_key=SYSTEM_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Read and encode PDF
    pdf_data = base64.b64encode(pdf_file.read()).decode('utf-8')

    prompt = """
    Analyze these disaster recovery tickets. Extract all tickets found in the PDF.
    For each ticket, return a JSON object with:
    Ticket_Number, Date, Truck_ID (labeled as Crew), Driver_Name (labeled as Supervisor), Hazard_Type (HANGER or LEANER), Measure.
    Return the result as a simple JSON array of objects. Do not include markdown formatting or backticks.
    """

    try:
        response = model.generate_content([
            {'mime_type': 'application/pdf', 'data': pdf_data},
            prompt
        ])
        
        # Parse AI JSON response
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(raw_text)
        
        # Apply sorting logic
        final_data = sort_ticket_data(data)
        
        # Create CSV
        df = pd.DataFrame(final_data)
        csv_path = "/tmp/ticket_export.csv" 
        df.to_csv(csv_path, index=False)
        
        return send_file(csv_path, as_attachment=True, download_name="Ticket_Export.csv")
        
    except Exception as e:
        return f"Processing Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
