from debug_toolbar.panels.sqlalchemy import SQLAlchemyPanel as BasePanel

from mspy_vendi.db.engine import engine


class SQLAlchemyPanel(BasePanel):
    async def add_engines(self, *args, **kwargs):
        self.engines.add(engine.sync_engine)
