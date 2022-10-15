"""Test namespace routes."""
from app.crud.organization import set_active_organization
from app.db.metadata import users as user_tbl
from app.db.metadata import organizations as org_tbl
from app.db.metadata import organization_members as org_mbr_tbl


from sqlalchemy import insert, select
from sqlalchemy.engine import Connection
from pydantic import UUID4

# Create organization
# Create users

# Setup database
# - Organization 1 - example.com
#   - Alice
#   - Bob
# - Organization 2 - example.net
#   - Carol

from typing import cast, Dict, Any


def test_namespace():
    """Create a new namespace."""


# read namespaces

# create new namespace

# update a namespace

# drop namespace
