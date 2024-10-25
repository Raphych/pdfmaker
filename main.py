from flask import Flask, Response, request, jsonify, send_file
import io

from templates import invoice, proforma, order, creditnote

app = Flask(__name__)

def validate_request_data(data):
    if not data or 'filename' not in data:
        return False
    return True

@app.route('/pdf/invoice', methods=['POST'])
def generate_invoice():
    data = request.get_json()
    pdf_buffer = io.BytesIO()
    if not validate_request_data(data):
        return jsonify(error="Invalid or missing filename"), 400
    invoice.generate_invoice(buffer=pdf_buffer, data=data)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, download_name=data.get("filename", 'invoice.pdf'), as_attachment=True, mimetype='application/pdf' )

@app.route('/pdf/proforma', methods=['POST'])
def generate_proforma():
    data = request.get_json()
    pdf_buffer = io.BytesIO()
    if not validate_request_data(data):
        return jsonify(error="Invalid or missing filename"), 400
    proforma.generate_proforma(buffer=pdf_buffer, data=data)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, download_name=data.get("filename", 'proforma.pdf'), as_attachment=True, mimetype='application/pdf' )

@app.route('/pdf/order', methods=['POST'])
def generate_purchase_order():
    data = request.get_json()
    pdf_buffer = io.BytesIO()
    if not validate_request_data(data):
        return jsonify(error="Invalid or missing filename"), 400
    order.generate_order(buffer=pdf_buffer, data=data)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, download_name=data.get("filename", 'purchaseorder.pdf'), as_attachment=True, mimetype='application/pdf' )

# @app.route('/pdf/credit-note', methods=['POST'])
# def generate_credit_note():
#     data = request.get_json()
#     if not validate_request_data(data):
#         return jsonify(error="Invalid or missing filename"), 400
#     pdf_buffer = creditnote.generate_credit_note(data.get('filename'), data)
#     return Response(pdf_buffer, content_type='application/pdf')

# Error handler for missing or incorrect content
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error="Invalid or missing JSON content"), 400

if __name__ == '__main__':
    app.run(port=5002, debug=True)
