from flask import request

from bot_api.register import users_db


@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    user_id = data["user_id"]  # From Telegram or app
    code = data["code"]
    if users_db.get(user_id, {}).get("code") == code:
        users_db[user_id]["verified"] = True
        return {"message": "Verified"}, 200
    return {"error": "Invalid code"}, 400

