from flask import Flask, render_template, request

from scraper import scraper
from server import server

app = Flask(__name__)


@app.route('/')
def run_command():
    return render_template('frontend.html', context={'urls': scraper.pages})


@app.route('/open/', methods=['POST'])
def open_site():
    if request.args.get('url'):
        server.spawn_window(request.args.get('url'))

    return 'Ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

