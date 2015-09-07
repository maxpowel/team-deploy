from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bundles.config import Config
from bundles.orm.entity import Base

import inject


class EntityManager(object):
    @inject.param('config', Config)
    def __init__(self, config):
        conf = config['entity_manager']
        self.engine = create_engine("%s/%s" % (conf['driver'], conf['database']))
        session = sessionmaker(bind=self.engine)
        self.session = session()

    def generate_schema(self):

        Base.metadata.create_all(bind=self.engine)

    def make_session(self):
        session = sessionmaker(bind=self.engine)
        return session()
