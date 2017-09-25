from dougbot.core.db.admindao import AdminDAO

ALIASES = ['admin']

admindao = AdminDAO()

# TODO CLEANUP

async def run(alias, message, args, client):
    if not is_admin(message.author.name, client):
        return

    if len(args) < 2:
        await client.confusion(message)
        return

    user_id = id_from_username(client.get_all_members(), args[1])

    if user_id is None:
        await client.confusion(message)
        return

    if args[0] == 'add':
        username = username_from_id(client.get_all_members(), user_id)
        if is_admin(username, client):
            return
        admindao.add_admin(user_id, username)
        print('ADDED %s:%s' % (username, user_id))

    elif args[0] == 'remove':
        if user_id == client.config.owner:
            return
        admindao.remove_admin(user_id)
        print('REMOVED %s' % user_id)

    elif args[0] == 'list':
        admins = admindao.get_admins()
        msg = 'Admins:\n'
        for admin in admins:
            msg = msg + admin + '\n'
        await client.send_message(message.channel, msg)

    else:
        await client.confusion(message)


def is_mention(username):
    return username is not None and '<@' in username and len(username) > 2


def get_member_object(username: str, members):
    mem_obj = None

    for member in members:
        if member.name == username:
            mem_obj = member
            break

    return mem_obj


def username_from_id(members, id):
    if members is None or id is None:
        return

    for member in members:
        if member.id == id:
            return member.name

    return None


def id_from_username(members, username):
    if members is None or username is None:
        return None

    # Is a mention of a user, so the id is within the name
    if is_mention(username):
        return username[2:len(username) - 1]

    user_id = None
    for member in members:
        if member.name == username:
            user_id = member.id
            break

    return user_id


def is_user_owner(user, owner_id):
    return user.id == owner_id


def is_admin(username, client):
    user_mem_obj = get_member_object(username, client.get_all_members())
    if is_user_owner(user_mem_obj.name, client.config.owner):
        return True
    return admindao.is_admin(user_mem_obj.id)


def cleanup(client):
    admindao.close()
