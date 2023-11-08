from flask import Flask, abort, jsonify, request
from fabric import Connection  # type: ignore
from dotenv import load_dotenv
import os


load_dotenv()
HOST = os.getenv("HOST")
LOGIN = os.getenv("LOGIN")
PASS = os.getenv("PASS")
KEY = os.getenv("KEY")


def send_reboot():
    try:
        c = Connection(HOST, user=LOGIN, connect_kwargs={"password": PASS})

        delay_seconds = 10  # 5 minutes
        reboot_command = f"sleep {delay_seconds} && reboot &"

        # Run the delayed reboot command on the remote router
        result = c.run(reboot_command, hide=True, pty=False)
        print(
            f"Scheduled a reboot on {HOST} in {delay_seconds} seconds. Result: {result.stdout.strip()}"
        )
        c.close()
        return False
    except Exception as e:
        return str(e.args)


app = Flask(__name__)


@app.route("/reboot", methods=["POST"])
def reboot():
    data = request.get_json()
    if data is not None:
        data = request.get_json()
        if data["key"] == KEY:
            status = send_reboot()
            if isinstance(status, bool):
                return jsonify({"status": "success"})
            else:
                return jsonify({"error": status})
        else:
            return jsonify({"error": "Invalid Key"}), 400
    else:
        return jsonify({"error": "Invalid JSON format"}), 400


@app.route("/<path:path>")
def default(path):
    abort(404)


if __name__ == "__main__":
    app.run()
