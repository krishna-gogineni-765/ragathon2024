from astrapy.db import AstraDB

class AstraDBVectorStore():
    def __init__(self, url, auth_token, vs_collection):
        self.db = AstraDB(token=auth_token.get_secret_value(), api_endpoint=url)
        self.image_vector_collection = self.db.collection(vs_collection)

    def add_document(self, document):
        self.image_vector_collection.insert_one(document)

    def get_top_k_similar(self, vector, k):
        return self.image_vector_collection.vector_find(vector, limit=k, fields=["filename", "_id", "description"])





