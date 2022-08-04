from app.db.session import SessionLocal
from app.crud.user import (
    delete_user,
    get_user_by_email,
)
from app import schemas

from app.crud.organization import create_organization, hard_delete_organization
from utils import make_user


def test_reading_connection_outside_org():
    # Create a user without an org
    test_emails = [
        "alice.testuser@mercator.tech",
        "bob.testuser@mercator.tech",
        "carol.testuser@mercator.tech",
        "dave.testuser@mercator.tech"
    ]
    orgs = []
    def setup():
        db = SessionLocal()
        for test_email in test_emails:
            make_user(db, test_email)

        # Bob and Alice are in the same org
        bob_user = get_user_by_email(db, test_emails[0])
        alice_user = get_user_by_email(db, test_emails[1])
        orgs.append(create_organization(db, schemas.OrganizationCreate(name="Mercator Test Org"), user=bob_user))
        update_organization_for_user(db, alice_user, orgs[0])
        update_organization_for_user(db, bob_user, orgs[0])

        # Carol is in a different org
        carol_user = get_user_by_email(db, test_emails[2])
        orgs.append(create_organization(db, schemas.OrganizationCreate(name="Quincy's Test Org"), user=carol_user))
        carol_user = get_user_by_email(db, test_emails[1])
        update_organization_for_user(db, carol_user, orgs[1])

        # Dave is not in an any org


    def test_org_isolation():
        pass

        # Bob can read credentials for org
        # Alice can read credentials for org
        # Alice can't read credentials for other orgs
        # Alice can't edit credentials for the org

        # Carol can't read credentials from other orgs
        # Dave can read only his own credentials


    def test_no_user():
        pass
        # TODO pick up here
        # Dave is not in an any org
        # dave_user = get_user_by_email(db, test_emails[3])

        # Bob creates data

        # Alice can read the data
        # Alice can edit the data

        # Carol can't read the data
        # Dave can't read the data
 
    
    def cleanup():
        db = SessionLocal()
        hard_delete_organization(db, user.organization_id)
        for test_email in test_emails:
            user = get_user_by_email(db, test_email)
            delete_user(db, user.id)
    
    def run_test():
        try:
            setup()
            test_org_isolation()
            test_no_user()
        finally:
            cleanup()
    
    pass
    # run_test()