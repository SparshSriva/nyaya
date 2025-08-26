from flask import Flask, request, jsonify
from services.dewey_service import DeweyService

app = Flask(__name__)

def get_dewey_service():
    # This function can be patched during testing
    return DeweyService()

@app.route('/api/dewey', methods=['GET'])
def get_dewey_subject():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Dewey code must be provided"}), 400

    dewey_service = get_dewey_service()
    subject = dewey_service.find_subject(code)

    if subject:
        return jsonify(subject)
    else:
        return jsonify({"error": "Dewey code not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
