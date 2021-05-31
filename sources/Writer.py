class Writer:
    def write(self, text):
        pass


class ConsoleWriter(Writer):

    def write(self, text):
        print(text)


class FileWriter(Writer):

    def __init__(self, path) -> None:
        super().__init__()
        self.file = open(path, 'w+')

    def write(self, text):
        print(text, file = self.file)
