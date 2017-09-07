from dougbot.core.db.admindao import AdminDAO

ALIASES = ['admin']

admindao = AdminDAO()


async def run(alias, message, args, client):
    if not is_user_admin(message.author, client) and not is_user_owner(message.author, client):
        return

    if len(args) < 2:
        await client.confusion(message)
        print('BAD INPUT TO ADMIN')
        return

    user_id = get_id_from_username(client, args[1])
    print(args[1])

    if user_id is None:
        print('BAD USERNAME')
        await client.confusion(message)
        return

    if args[0] == 'add':
        admindao.add_admin(user_id)
        print('ADDED %s' % user_id)
    elif args[0] == 'remove':
        if user_id == client.config.owner:
            return
        admindao.remove_admin(user_id)
        print('REMOVED %s' % user_id)
    else:
        await client.confusion(message)


def get_id_from_username(client, username):
    members = client.get_all_members()

    # Is a mention of a user, so the id is within the name
    if '<@' in username and len(username) > 2:
        user_id = username[2:len(username) - 1]
        return user_id

    user_id = None
    for member in members:
        if member.name == username:
            user_id = member.id
            break

    return user_id


def is_user_owner(user, client):
    return user.id == client.config.owner


def is_user_admin(user, client):
    if is_user_owner(user, client):
        return True
    return admindao.is_admin(user.id)
