"""Test namespace routes."""

# Create organization
# Create users


def setup_data(conn: Connection):
    org = create_organization("Example.com")
    users = [
        {"name": "Alice", "email": "alice@example.com"}
        {"name": "Bob", "email": "bob@example.com"}
    ]
    for user in users:
        create_user(user)
        add_user_to_org()
# Setup database
# - Organization 1 - example.com
#   - Alice
#   - Bob
# - Organization 2 - example.net
#   - Carol

def test_namespace():
    """Create a new namespace."""
    pass
