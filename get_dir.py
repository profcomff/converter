import os
import platform


class GetCommand:

    command: str
    direct: str

    @staticmethod
    def find(name: str, paths: list):
        for i in paths:
            for root, dirs, files in os.walk(i):
                if name in files:
                    return os.path.join(root, name)

# Поиск по базовым катологам, куда мог быть установлен soffice.exe

    @classmethod
    def get_command(cls, OS: str, filename: str):

        ext_d = os.path.abspath(" ")

        if OS == "Windows":
            paths = ['\\Program Files', '\\Program Files (x86)', '\\ProgramData', '\\Users']
            slash = '\\'
            cd = f'{ext_d[:-2]}{slash}static{slash}'
            direct = cd + filename
            libre_path = cls.find('soffice.exe', paths)
            command = f'cd {cd} && "{libre_path}" --headless --convert-to pdf {direct}'

        else:
            slash = '/'
            cd = f'{ext_d[:-2]}{slash}static{slash}'
            direct = cd + filename
            command = f'cd {cd}; libreoffice --headless --convert-to pdf {direct}'

        return {'command': command, 'direct': direct}


    @classmethod
    def get_os(cls, filename):
        OS = platform.system()
        return cls.get_command(OS, filename)


    def __init__(self, filename):
        f = self.get_os(filename)
        self.command = f.get('command')
        self.direct = f.get('direct')


# Создает удобный инкапсулированный класс, который независимо от ОС выдает директорию файла
# И команду для libre, которую пихают в shell, использу функцию get_os, которая возвращает функцию
