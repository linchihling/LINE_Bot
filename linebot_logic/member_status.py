def get_member_status(members, logger, user_id):
    if user_id in members:
        # logger.info(f"{members[user_id]} logged in")
        return True
    else:
        logger.info(f"{user_id} is not a member")
        return False