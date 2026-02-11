from flask import Flask, Response, request, jsonify, send_file
import io
import json
import logging
import os
import sys
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pdfmaker.log')
    ]
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info(f"Python version: {sys.version}")
try:
    import reportlab
    logger.info(f"reportlab version: {reportlab.Version}")
except Exception as e:
    logger.error(f"Failed to import reportlab: {e}")

try:
    import svglib
    logger.info(f"svglib loaded successfully")
except Exception as e:
    logger.error(f"Failed to import svglib: {e}")

try:
    from templates import invoice, proforma, order, creditnote
    logger.info("All templates loaded successfully")
except Exception as e:
    logger.error(f"Failed to import templates: {e}")
    logger.error(traceback.format_exc())
    raise

app = Flask(__name__)

# --- Swagger / OpenAPI docs ---

SWAGGER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swagger.json')

@app.route('/api-docs.json')
def swagger_json():
    with open(SWAGGER_PATH, 'r') as f:
        spec = json.load(f)
    return jsonify(spec)

@app.route('/api-docs')
def swagger_ui():
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>PDF Maker API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({ url: "/api-docs.json", dom_id: "#swagger-ui" });
  </script>
</body>
</html>'''
    return Response(html, mimetype='text/html')

# --- PDF generation endpoints ---

@app.route('/pdf/invoice', methods=['POST'])
def generate_invoice():
    logger.info("Received request for /pdf/invoice")
    data = request.get_json()
    pdf_buffer = io.BytesIO()

    try:
        invoice.generate_invoice(buffer=pdf_buffer, data=data)
        pdf_buffer.seek(0)
        filename = data.get("filename", 'invoice.pdf')
        logger.info(f"Successfully generated invoice: {filename}")
        return send_file(
            pdf_buffer,
            download_name=filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        logger.error(f"Failed to generate invoice: {e}")
        logger.error(traceback.format_exc())
        return jsonify(error=str(e)), 500


@app.route('/pdf/proforma', methods=['POST'])
def generate_proforma():
    logger.info("Received request for /pdf/proforma")
    data = request.get_json()
    pdf_buffer = io.BytesIO()

    try:
        proforma.generate_proforma(buffer=pdf_buffer, data=data)
        pdf_buffer.seek(0)
        filename = data.get("filename", 'proforma.pdf')
        logger.info(f"Successfully generated proforma: {filename}")
        return send_file(
            pdf_buffer,
            download_name=filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        logger.error(f"Failed to generate proforma: {e}")
        logger.error(traceback.format_exc())
        return jsonify(error=str(e)), 500


@app.route('/pdf/order', methods=['POST'])
def generate_purchase_order():
    logger.info("Received request for /pdf/order")
    data = request.get_json()
    pdf_buffer = io.BytesIO()

    try:
        order.generate_order(buffer=pdf_buffer, data=data)
        pdf_buffer.seek(0)
        filename = data.get("filename", 'purchaseorder.pdf')
        logger.info(f"Successfully generated order: {filename}")
        return send_file(
            pdf_buffer,
            download_name=filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        logger.error(f"Failed to generate order: {e}")
        logger.error(traceback.format_exc())
        return jsonify(error=str(e)), 500

@app.route('/pdf/credit-note', methods=['POST'])
def generate_credit_note():
    logger.info("Received request for /pdf/credit-note")
    data = request.get_json()
    pdf_buffer = io.BytesIO()

    try:
        creditnote.generate_credit_note(buffer=pdf_buffer, data=data)
        pdf_buffer.seek(0)
        filename = data.get("filename", 'creditnote.pdf')
        logger.info(f"Successfully generated credit note: {filename}")
        return send_file(
            pdf_buffer,
            download_name=filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        logger.error(f"Failed to generate credit note: {e}")
        logger.error(traceback.format_exc())
        return jsonify(error=str(e)), 500

# Error handler for missing or incorrect content
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error="Invalid or missing JSON content"), 400

if __name__ == '__main__':
    logger.info("Starting PDF Maker server on port 5002")
    app.run(port=5002, debug=True)
