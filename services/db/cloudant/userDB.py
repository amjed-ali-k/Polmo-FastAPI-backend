from typing import Optional
import json
from ibm_cloud_sdk_core import ApiException
from ibmcloudant.cloudant_v1 import CloudantV1, Document, IndexField, IndexDefinition
from config import settings
from models.user import User, UserInDB

client = CloudantV1.new_instance()
user_db_name = "users"


async def get_user_from_id(key: str) -> Optional[UserInDB]:
    try:
        document = client.get_document(db=user_db_name, doc_id=key).get_result()
        return UserInDB(**document)
    except Exception as e:
        print(e)
        return None


async def get_user_from_username_db(username: str) -> Optional[UserInDB]:
    s = {"username": {"$eq": username}}
    try:
        document = client.post_find(db=user_db_name, selector=s, limit=1).get_result()
        if len(document["docs"]) > 0:
            return UserInDB(**document["docs"][0])
        else:
            return None
    except Exception as e:
        print(e)
        return None


async def create_new_user_to_db(user: UserInDB) -> UserInDB:
    await create_db_if_not_exists(user_db_name)
    new_user: Document = Document(id=user.key, **user.dict())
    # Save the document in the database
    response = client.post_document(
        db=user_db_name,
        document=new_user
    ).get_result()
    return UserInDB(**user.dict())


async def update_user_to_db(user: User, userindb: UserInDB) -> Optional[UserInDB]:
    try:
        document = client.get_document(db=user_db_name, doc_id=userindb.key).get_result()
        document.update(**{k: v for k, v in user.dict().items() if v is not None})
        client.post_document(db=user_db_name, document=document).get_result()
        res = client.get_document(db=user_db_name, doc_id=userindb.key).get_result()
        if res:
            print(res)
            return UserInDB(**res)
        else:
            return None
    except Exception as e:
        print(e)
        return None


async def update_password_to_db(hashed_password, userindb: User) -> UserInDB:
    document = client.get_document(db=user_db_name, doc_id=userindb.key).get_result()
    document['hashed_password'] = hashed_password
    return client.post_document(db=user_db_name, document=document).get_result()


async def create_db_if_not_exists(db_name):
    # Try to create database if it doesn't exist
    try:
        put_database_result = client.put_database(
            db=db_name
        ).get_result()
        if put_database_result["ok"]:
            print(f'"{db_name}" database created.')
            # Create Index for username
            index_field = IndexField(username="asc")
            index = IndexDefinition(fields=[index_field])
            r = client.post_index(
                db=db_name,
                ddoc='json-index',
                name='getUserByUsername',
                index=index,
                type='json'
            ).get_result()
            print("Index created")
            print(r)
    except ApiException as ae:
        if ae.code == 412:
            pass
