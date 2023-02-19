class Use_Chain:
    
    def __init__(self):
        self.__chain = {}

    def used(self, variable_name, instruction, used_first_operand):
        if variable_name not in self.__chain:
            self.__chain[variable_name] = []
        self.__chain[variable_name].append((instruction, used_first_operand))

    def get_all_uses(self, variable_name):
        if variable_name in self.__chain:
            return self.__chain[variable_name]
        return None

    def print(self):
        for id in self.__chain:
            for use in self.__chain[id]:
                print(id, use[0], use[1])

    def replace(self, old_instruction, new_instruction, variable_id, used_as_first_operand):
        if variable_id in self.__chain:
            for use in self.__chain[variable_id]:
                if use[0] == old_instruction:
                    self.__chain[variable_id].remove(use)
                    self.__chain[variable_id].append((new_instruction, use[1]))
        else:
            #TODO:add new use here
            pass