from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['POST', 'OPTIONS'])
def colleges(path):
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # For now, return a message that college feature requires full backend
        return jsonify({
            'success': False,
            'error': 'College recommendations feature requires pandas and large CSV file. Please use the prediction feature only, or deploy backend separately on Render/Railway.'
        }), 501
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def handler(request):
    return app(request)
