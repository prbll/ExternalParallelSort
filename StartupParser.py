import argparse
import uuid
import multiprocessing


class StartupParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False, description='Startup parser')

    def get_arguments(self):
        self.parser.add_argument('-m', '--memory_usage', action='store',
                                 help='Лимит памяти для программы в байтах. По умолчанию 1 Гб.')
        self.parser.add_argument('-f', '--file',
                                 action='store',
                                 help='Имя файла для сортировки. '
                                      'По умолчанию создает неотсортированный файл на 1Гб и сортирует его. '
                                      'Значения от 0 до 255.')
        self.parser.add_argument('-p', '--processes', action='store',
                                 help='Максимальное количество создаваемых процессов')
        self.parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Помощь.', )

        args = self.parser.parse_args()

        file_name = args.file if args.file else str(uuid.uuid4())

        memory = int(args.memory_usage) if args.memory_usage else 1024 * 1024 * 256

        processes = int(args.processes) if args.processes else multiprocessing.cpu_count()

        return file_name, memory, processes
