import multiprocessing
import time
import os
import math
import tempfile
import shutil
import re

import numpy as np

from StartupParser import StartupParser
from FileGenerator import FileGenerator


def check_uuid4(uuid):
    uuid_pattern = '^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    return False if re.match(uuid_pattern, uuid) is None else True


def sort(data):
    return np.sort(data)


def merge_files(files, memory_usage, temporary_directory):

    if len(files) <= 1:
        return False
    memory_usage = int(memory_usage / len(files))

    merged_file = tempfile.NamedTemporaryFile(mode="wb", dir=temporary_directory, delete=False)

    wrappers = {file: open(os.path.join(temporary_directory, file), "rb") for file in files}

    while True:
        data = np.array([], dtype=np.uint32)

        for file in files:
            data = np.append(data, np.fromfile(wrappers[file], count=memory_usage, dtype=np.uint32))

        if not len(data):
            break

        sort(data).tofile(merged_file)


if __name__ == '__main__':
    unsorted_file_name, memory, processes_amount = StartupParser().get_arguments()
    new_unsorted_file_name = ''
    sorted_file_name = 'Sorted_' + unsorted_file_name

    if check_uuid4(unsorted_file_name):
        print("File name was not passed as an argument. Let`s create one.")
        new_unsorted_file_name = 'Unsorted_' + unsorted_file_name
        FileGenerator().generate_file(file_name=new_unsorted_file_name, file_size='300MB')

    print("Sorting file...")
    start = time.time()

    working_directory = os.getcwd()
    support_directory = os.path.join(working_directory, 'Temp')
    if os.path.exists(support_directory):
        shutil.rmtree(support_directory)

    os.mkdir(support_directory)

    pool = multiprocessing.Pool(processes=processes_amount)

    amount_integers = memory // np.dtype(np.int32).itemsize

    f = open(new_unsorted_file_name, 'rb') if new_unsorted_file_name.find(unsorted_file_name) > 0 \
        else open(unsorted_file_name, 'rb')

    while True:
        numbers = np.fromfile(f, count=amount_integers//4, dtype=np.uint32)

        if not len(numbers):
            break

        size = int(math.ceil(float(len(numbers)) / processes_amount))
        numbers = [numbers[i * size:(i + 1) * size] for i in range(processes_amount)]
        numbers = np.asarray(numbers, dtype=np.uint32)
        sorted_arrays = pool.map(sort, numbers)

        for item in sorted_arrays:
            temporary_file = tempfile.NamedTemporaryFile(mode="wb", dir=support_directory, delete=False)
            np.asarray(item, dtype=np.uint32).tofile(temporary_file)
            temporary_file.close()

    pool.close()
    pool.join()

    print("Applying final merge of small files...")

    pool = multiprocessing.Pool(processes=processes_amount)
    while True:

        temporary_files = []
        for f in os.listdir(support_directory):
            if os.path.isfile(os.path.join(support_directory, f)):
                temporary_files.append(f)

        if len(temporary_files) <= 1:
            shutil.move(os.path.join(support_directory, temporary_files[0]), sorted_file_name)
            break

        files_division = int(math.ceil(float(len(temporary_files)) / processes_amount))

        if files_division < 2:
            files_division = 2

        handler = [temporary_files[i * files_division:(i + 1) * files_division] for i in range(processes_amount)]

        arg_list = [[handler[i], amount_integers//4, support_directory] for i in range(processes_amount)]
        ret = pool.starmap(merge_files, arg_list)

        for wrapper in temporary_files:
            os.unlink(os.path.join(support_directory, wrapper))

    pool.close()
    pool.join()

    if os.path.exists(support_directory):
        shutil.rmtree(support_directory)

    print("Sorting finished. Output file name is {}. Check project directory for it.\nSeconds elapsed: {}.".format(sorted_file_name, time.time() - start))

