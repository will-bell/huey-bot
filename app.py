import time

from flask import Flask, request

from common import send_message_to_test_group

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    app.logger.debug('Got a message!')

    # Comfortable amount of time to not cause a graphical glitch in GroupMe
    time.sleep(1)

    data = request.get_json()

    send_message_to_test_group("got a message")

    return "ok", 200


if __name__ == '__main__':
    app.run(debug=True, reload=False)
