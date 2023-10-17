from os import listdir
from os.path import isfile, join


class WordListService:
    def __init__(self):
        self.dictionaries = {}
        self.load_dictionaries()

    def load_dictionaries(self):
        path = './dicitionaries/'
        for file in listdir(path):
            if isfile(join(path, file)) and file.endswith('.dict'):
                self.load_dictionary(path, file)

    def has_dictionaries(self, dictionaries):
        dictionary_list = map(lambda d: d.strip(), dictionaries.split(","))
        for dictionary in dictionary_list:
            if not self.dictionaries.__contains__(dictionary):
                return False
        return True

    def load_dictionary(self, path, filename):
        dictionary_name = filename[0:-5]
        dictionary = []
        print("Loading dictionary: " + filename)
        with open(join(path, filename)) as file:
            words = map(lambda w: w.strip(), file.read().replace('\n', ',').split(','))
            for word in words:
                if len(word) > 0 and not dictionary.__contains__(word):
                    dictionary.push(word)

        self.dictionaries[dictionary_name] = dictionary

    def get_dictionaries(self, dictionary_list):
        all_words = []
        dicts = map(lambda d: d.strip(), dictionary_list.split(","))
        for dictionary in dicts:
            all_words.extend(dictionary)

        return self.deduplicate_words(all_words)

    def deduplicate_words(self, input):
        output = []
        for word in input:
            if not output.__contains__(word):
                output.append(word)
        return output
