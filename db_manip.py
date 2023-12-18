from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd

class AnimalShelter(object):
    """ CRUD operations for Animal collection in MongoDB """

    def __init__(self, username, password):
        # Initializing the MongoClient. This helps to
        # access the MongoDB databases and collections.
        # This is hard-wired to use the aac database, the
        # animals collection, and the aac user.
        # Definitions of the connection string variables are unique to the individual Apporto environment

        # You must edit the connection variables below to reflect your own instance of MongoDB!

        # Connection Vars
        USER = 'aacuser'
        PASS = 'password'
        HOST = 'nv-desktop-services.apporto.com'
        PORT = 30416
        DB = 'AAC'
        COL = 'animals'

        # Init connection
        self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT))
        self.database = self.client['%s' % (DB)]
        self.collection = self.database['%s' % (COL)]

    #Complete this create method to implement the C in CRUD.
    def create(self, data):
        if data is not None:
            try:
                result = self.collection.insert_one(data)
                if result.inserted_id is not None:
                    return True
                else:
                    return False
            except Exception as e:
                print(f"Error during insertion: {e}")
        else:
            raise Exception("Nothing to save, because data parameter is empty")

    #Create method to implement the R in CRUD.
    def read(self, queryData):
        if queryData is not None:
            try:
                data = self.collection.find(queryData, {'_id':False})
                if data is not None:
                    print("Query Successful")
                    return pd.DataFrame(data)
                else:
                    data = self.collection.find({},{'_id':False})
                    print("Query Unsuccesful; returning null")
                    return pd.DataFrame() 
            except Exception as e:
                print(f'Error during query: {e}')
                return False
        else:
            data = self.collection.find({},{'_id':False})
            print('Query unsuccessful because query data is empty; returning null')

        return pd.DataFrame()

    #Method to implement the U in CRUD.
    def update(self, queryData, updateData):
        if queryData is not None and updateData is not None:
            try:
                result = self.collection.update_one(queryData, {'$set':updateData})
                if result.modified_count > 0:
                    print(f'Successfully modified {result.modified_count} document(s)')
                    return result.modified_count #if there are any documents that are modified, the update was successful
                else:
                    print(f'No modifications made; likely no documents were found during the query')
                    return result.modified_count #likely no documents were found during the query
            except Exception as e:
                print(f'Error during update: {e}') #catch potential errors
                return 0
        else:
            raise Exception("Either the data to query or the update conditions are empty; no changes made")

    #Method to implement the D in CRUD.
    def delete(self, queryData):
        if queryData is not None:
            try:
                result = self.collection.delete_many(queryData)
                if result.deleted_count > 0:
                    print(f'Successfully deleted {result.deleted_count} document(s)')
                    return result.deleted_count #Query found documents and deleted instances
                else:
                    print('Nothing to delete; likely no documents match the query')
                    return 0 #No documents match the query and therefore nothing is deleted
            except Exception as e:
                print(f'Error during deletion: {e}')
                return 0
        else:
            raise Exception('Nothing to delete because the queryData is empty')

