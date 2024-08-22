import json
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage
)

def load_members():
    with open('members.json', 'r') as file:
        return json.load(file)

def save_members(members):
    with open('members.json', 'w') as file:
        json.dump(members, file, indent=2)

def get_member_status(messaging_api, event, logger):
    user_id = event.source.user_id
    token = event.reply_token
    message = event.message.text
    members = load_members()
    if user_id in members:
        # logger.info(f"{members[user_id]} logged in")
        return True
    elif message.startswith("TungHoSteel:"):
        new_name = message.split(":")[1]
        members[user_id] = new_name
        save_members(members)
        logger.info(f"New member added: {user_id} -> {new_name}")
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=token,
                messages=[TextMessage(text=f"Welcome {new_name}!")]
            )
        )
    else:
        logger.info(f"{user_id} is not a member")
        return False