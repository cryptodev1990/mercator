"""App Database models."""

from app.db.engine import engine
from app.db.metadata.common import *
from app.db.metadata.namespaces import *
from app.db.metadata.organizations import *
from app.db.metadata.shapes import *
from app.db.metadata.users import *

# IMPORTANT: bind the metadata to the engine!
metadata.bind = engine
