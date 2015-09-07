import inject
from bundles.command.app import app
from bundles.orm.entity_manager import EntityManager
from bundles.user.entity import User
import uuid


@app.command('user:create', description='Creates an user')
@app.argument('name', description='The username', required=True)
@inject.param('entity_manager', EntityManager)
def user_create(i, o, entity_manager):
    name = i.get_argument('name')
    user = User()
    user.name = name
    user.token = uuid.uuid4().hex
    entity_manager.session.add(user)
    entity_manager.session.commit()
    o.writeln("User %s created with token %s" % (user.name, user.token))


@app.command('user:delete', description='Delete an user')
@app.argument('name', description='The username', required=True)
@inject.param('entity_manager', EntityManager)
def user_delete(i, o, entity_manager):
    name = i.get_argument('name')
    user = entity_manager.session.query(User).filter(User.name == name).first()
    if user:
        entity_manager.session.delete(user)
        entity_manager.session.commit()
        o.writeln("User %s deleted" % name)
    else:
        o.writeln("The user %s does not exists" % name)


@app.command('user:list', description='List all users')
@inject.param('entity_manager', EntityManager)
def user_list(i, o, entity_manager):

    for user in entity_manager.session.query(User).all():
        o.writeln("%s\t%s" % (user.name, user.token))

