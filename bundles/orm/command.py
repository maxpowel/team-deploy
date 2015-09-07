import inject
from bundles.orm.entity_manager import EntityManager
from bundles.command.app import app


@app.command('schema:create', description='Creates database schema')
@inject.param('entity_manager', EntityManager)
def schema_create(i, o, entity_manager):
    o.writeln("Creating schema...")
    entity_manager.generate_schema()
    o.writeln("Done")
