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
    

class File_Writer:

    def write(self, path, title, warnings, notes, content, mode = 'w'):
        path = path[0:-5] + "_output.txt"
        try:
            with open(path, mode) as file:
                if warnings is not None:
                    file.writelines(warnings)

                file.writelines(f'\n\n-----{title}-----\n\n')
                file.writelines(content)
                if notes is not None:
                    file.writelines(notes)

        except BaseException:
            pass