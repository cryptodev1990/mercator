# from sqlalchemy import create_engine
# from app.crud.db_credentials import db_conn_with_secrets
#
#
# # TODO to write, pass this a connection ID and a bunch of shapes
# # TODO to read, pass this a connection ID
# def governor_factory():
#     creds = db_conn_with_secrets()
#     engine = create_engine(f'{creds.driver}://{creds.db_user}:{creds.db_password}@{creds.db_host}:{creds.db_port}/{creds.db_database}')
#
#
#     class DbGovernor():
#
#         def get_current_db_contents():
#             pass
#
#
#         def create_publications_table():
#             pass
#
#
#         def read_from_publications_table():
#             pass
#
#
#         def upsert_publications_table()
#             pass
#
#
#     return DbGovernor()
#
#
