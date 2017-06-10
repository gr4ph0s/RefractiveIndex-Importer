import os
import json


class JsonFunction():
    """
    class for handling json I/O

    TODO: better file hanlding
    """

    def __init__(self):
        self.fileContent = str()
        self.file = os.path.join(os.path.dirname(os.path.dirname(os.path.split(__file__)[0])),"index.json") #The full path of the json file


    def load_json_file(self):
        """
        Load the self.file into json file content
        """
        with open(self.file) as json_data:
            self.fileContent = json.load(json_data)

    def save_json_file(self):
        """
        Save the self.fileContent to self.file
        """
        with open(self.file, 'w') as outfile:
            json.dump(self.fileContent, outfile, sort_keys = True, indent = 4)

    def delete_data(self,name):
        """
        Delete an entry in self.fileContent(only in memory you need to call self.saveJsonFile for make change in file)
        :param name: str => the name of the key to remove
        """
        self.fileContent.pop(name)

    def add_data(self,name,value):
        """
        Add an entry in self.fileContent(only in memory you need to call self.saveJsonFile for make change in file)
        :param name: str => the key name
        :param value: any => the key value
        """
        self.fileContent[name] = value

    def metal_exist(self,name):
        """
        Check if a key already exist in the list
        :param name: str => The name of the key to check
        :return: True if exist, false otherwise
        """
        if self.fileContent.has_key(name):
            return True
        else:
            return False

    def get_all_name(self):
        """
        Get all existant key in the list
        :return: list of key name
        """
        buffer = []
        for key, _ in self.fileContent.items():
            buffer.append(key)

        return buffer

    def get_RGB_data(self,activeName):
        """
        Get the content of a key
        :param activeName: Str => Key name
        :return: Value stored to the key, None if nothing
        """
        return self.fileContent.get(activeName)