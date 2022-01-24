from azure.cosmos import CosmosClient
from config import DefaultConfig
from data_models import UserProfile

CONFIG=DefaultConfig()

uri = CONFIG.COSMOS_uri
key = CONFIG.COSMOS_key
database_name = CONFIG.COSMOS_database_name
container_name = CONFIG.COSMOS_container_name

class UserDAO:
    #Inserisco un utente non registrato
    @staticmethod
    def insertUser(user: UserProfile):
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        container.upsert_item({
            'id': user.id,
            'name': user.name,
            'wishlist': user.wishlist
        })
    #Cerco l'utente nel database
    @staticmethod
    def searchUserById(id_user: str):
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        for item in container.query_items(query=f'SELECT * FROM {container_name} u WHERE u.id LIKE "{id_user}"',
                                          enable_cross_partition_query=True):
            user = UserProfile(item['id'],item['name'], item['wishlist'])

            return user
    #Aggiungo/Rimuovo un nuovo elemento alla wishlist dell'utente
    @staticmethod
    def updateUserById(user: UserProfile):
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        for item in container.query_items(query=f'SELECT * FROM {container_name} u WHERE u.id LIKE "{user.id}"',
                                          enable_cross_partition_query=True):
            container.replace_item(item, {
                'id': user.id,
                'name': user.name,
                'wishlist': user.wishlist
            }, populate_query_metrics=None, pre_trigger_include=None, post_trigger_include=None)
            return