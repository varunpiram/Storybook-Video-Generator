from flask import Flask, request, jsonify, render_template
import os
from handler import generate

app = Flask(__name__)

# Sets route for the app and allows GET and POST methods
@app.route('/', methods=['GET', 'POST'])

# Will return index html file - if POST method used then will grab email and topic
# responses, and will return json to give notification
def index():
    if request.method == 'POST':

        data = request.get_json()
        email = data.get('email')
        prompt = data.get('topic')
        generate(prompt, email)
        return jsonify({'message': 'Your video is being processed, an email will be sent once it is ready.'}), 202

    return render_template('index.html')

# Runs app locally
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)