"""   Contains Information about the Collections.

    --------------------
    Classes :
        
        -----------------
        * Collection

        * Collections

        * Objects
        -----------------

    --------------------
"""

import time
from .database import Database
from hyperql.parser import Query

DEFAULT_QUERY = Query()


class Collection:
    """
        This class refers to the Collection itself.
        
        A Collection is a group of hyperlite objects ( similar to RDBMS table ).

        Every Collection is represented by an object of Collection class.
    """

    def __init__(self, col_name: str, parent: str):
        """
            Every collection contains a name, list of objects,
            indices and parent db object.
        """
        self.col_name = col_name
        self.objects = []
        self.indices = {}  # indices is a dict object
        # which stores object id as key
        # and object index as value

        self.parent = parent
        Collections.add_collection(self)  # Adds the collection to existing group of col.

    def __str__(self):
        """     String representation of collection.    """
        return self.col_name

    def insert(self, user_data: dict):
        """ 
            Instance method to insert new object into collection.

            Takes user data as parameter.
        """

        object_id = Objects.generate_id(self)  # unique id for every object

        self.objects.append(user_data)  # append new object to objects list

        # update indices dict for new object
        self.indices.update({
            object_id: self.objects.__len__() - 1
        })

        return object_id

    def update(self, new_data: dict, update_objects: dict):
        """     Instance method to update an object of the collection.    """

        for object in update_objects:
            for prop in new_data:
                if type(new_data[prop]) is dict:
                    operator = list(new_data[prop].keys())[0]
                    if operator == "&inc":
                        try:
                            object[prop] += new_data[prop][operator]
                        except KeyError:
                            object[prop] = 0
                            object[prop] += new_data[prop][operator]

                    if operator == "&dec":
                        try:
                            object[prop] -= new_data[prop][operator]
                        except KeyError:
                            object[prop] = 0
                            object[prop] -= new_data[prop][operator]

                    if operator == "&mul":
                        try:
                            object[prop] *= new_data[prop][operator]
                        except KeyError:
                            object[prop] = 0
                            object[prop] *= new_data[prop][operator]

                    if operator == "&div":
                        try:
                            object[prop] /= new_data[prop][operator]
                        except KeyError:
                            object[prop] = 0
                            object[prop] /= new_data[prop][operator]

                    if operator == "&pow":
                        try:
                            object[prop] **= new_data[prop][operator]
                        except KeyError:
                            object[prop] = 0
                            object[prop] **= new_data[prop][operator]

                    if operator == "&floor":
                        try:
                            object[prop] //= new_data[prop][operator]
                        except KeyError:
                            object[prop] = 0
                            object[prop] //= new_data[prop][operator]

                else:
                    object[prop] = new_data[prop]
            print()
            print()
            print(object)
            print()
            print()
        return True

    def read(self, objects: list, instruction: dict = {}, instructions: list = [], modifiers=None):
        """     Instance method to read the Objects data from the collection.    """

        output_objs = []
        if not instructions:
            for object in objects:
                if instruction['filter'](data=instruction['data'], field=object[instruction['field']]):
                    output_objs.append(object)
        else:
            for object in objects:
                output_obj = {}
                for instruction in instructions:
                    if object[instruction['field']]:
                        output_obj.update({
                            instruction['field']: object[instruction['field']]
                        })
                output_objs.append(output_obj)

        if modifiers != DEFAULT_QUERY.modifiers:
            if modifiers is not None:
                output_objs = output_objs[modifiers['skip']:modifiers['skip'] + modifiers['limit']]

        return output_objs

    def delete(self, object_id: str) -> bool:
        """
            Instance method to remove object.

            takes object_id as parameter.
        """
        if self._search(object_id) is not None:

            self.indices[self._search(object_id)] = None
            return True
        else:
            return False

    def _search(self, object_id: str):
        """
            Private Instance method to get object from object id.

            returns object associated with the given object_id.

        """
        try:
            return self.indices[object_id]

        except KeyError:
            # if object_id is not available
            return None

    @classmethod
    def meta_separator(cls, meta_data: dict) -> list:
        """
            @classmethod to fetch meta data from dict.

            if meta_data is of Read RequestType,
            then returns list containing db_name, col_name and Query

            if meta_data is of Insert RequestType,
            then returns list containing db_name and col_name.

            if meta_data is of Delete RequestType,
            then returns list containing db_name, col_name and object_id.

            if meta_data is of Update RequestType,
            then returns list containing db_name, col_name and object_id.

        """
        return [meta for meta in meta_data.values()]


class Collections:
    """   Maintains record of all Collections   """
    collection_list = {}
    meta_collection: Collection

    @classmethod
    def add_collection(cls, collection: Collection):
        if Collections.collection_list.get(collection.parent) is not None:
            Collections.collection_list.get(collection).add(collection)
        else:
            Collections.collection_list.update({
                collection.parent: {collection}
            })

    @classmethod
    def get_collection(cls, col_name: str, db_name):
        for database in Collections.collection_list:
            for collection in database:
                if col_name == collection.col_name:
                    return collection
                else:
                    # Fetching or create new Collection
                    new_collection = Collection(col_name, db_name)
                    Collections.add_collection(new_collection)
                    Collections.meta_collection.insert({
                        "db_name": db_name,
                        "col_name": col_name,
                        "time_stamp": time.time(), # its helps to find this collection on disk
                        "user": "Anonymous"
                    })
                    return new_collection


class Objects:
    """ Helps to Maintain record of all Objects """
    object_count = 0

    @classmethod
    def generate_id(cls, collection: Collection) -> str:
        obj_id = collection.parent.db_name + '.' + collection.col_name + '.' + str(Objects.object_count + 1)
        return obj_id
