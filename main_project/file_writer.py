class File_Writer:

    def write(self, path, title, warnings, notes, content, mode = 'w', suffix = ""):
        path = path[0:-5] + f"_output_{suffix}.txt"
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