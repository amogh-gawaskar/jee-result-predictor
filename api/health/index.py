from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def health(path):
    return jsonify({'status': 'ok'})

def handler(request):
    return app(request)
