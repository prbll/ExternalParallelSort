import time
import numpy as np


class FileGenerator:
    def __init__(self):
        self.file_name = 'UnsortedFile'
        self.file_size = '1024MB'

        self.min_value = 0
        self.max_value = 256

    def generate_file(self, **params):
        self.file_name = self.__get_argument(params, 'file_name', self.file_name)
        self.file_size = self.__get_argument(params, 'file_size', self.file_size)

        self.min_value = self.__get_argument(params, 'min_value', self.min_value)
        self.max_value = self.__get_argument(params, 'max_value', self.max_value)

        start_time = time.clock()
        print("Creating file...")
        file = open(self.file_name, mode='wb')

        target_size = self.__get_amount_of_integers(self.file_size) // 1000

        steps = [x/10 for x in range(1, 11)]
        counter = 0

        for size in range(target_size):
            progress = size / target_size

            if progress >= steps[counter]:
                print("[{}%] created. Seconds elapsed: {}.".format(steps[counter]*100, time.clock()-start_time))
                counter += 1

            numbers = np.random.randint(self.min_value, self.max_value, size=1000, dtype=np.uint32)
            file.write(numbers)

        file.close()

        print("File creating finished: {} seconds elapsed.".format(time.clock() - start_time))

    @staticmethod
    def __get_amount_of_integers(file_size: str):
        if 'GB' in file_size:
            file_size = int(file_size.replace('GB', ''))
            file_size = str(file_size * 1024) + 'MB'

        if 'MB' in file_size:
            file_size = int(file_size.replace('MB', ''))
            file_size = str(file_size * 1000) + 'KB'

        if 'KB' in file_size:
            file_size = int(file_size.replace('KB', ''))
            file_size = file_size * 1000

        amount_integers = file_size // 4

        return amount_integers

    @staticmethod
    def __get_argument(params: dict, key, default_value):
        return params[key] \
            if key in params.keys()\
            else default_value
