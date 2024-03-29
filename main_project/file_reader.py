class File_Reader:
    
    def __init__(self, file_path):
        self.file_path = file_path

    def get_contents(self):
        contents = None
        with open(self.file_path) as file:
            contents = file.read()
        if not contents:
            # throws exception
            raise Exception("File Error: Invalid file") 
        return contents