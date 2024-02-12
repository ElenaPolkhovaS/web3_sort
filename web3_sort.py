import shutil
import sys
import os
import re
import zipfile
from pathlib import Path
from threading import Thread

def sorting_files(path):
    folders = ['images', 'documents', 'audio', 'video', 'archives', 'unknown_extensions']

    for folder in folders:
        (path / folder).mkdir(exist_ok=True)
    print("Директорії створено")

    document_rules = {'extensions': ['.doc', '.docs', '.txt', '.pdf', '.xlsx', '.pptx'],
                      'folder_name': 'documents',
                      'type_files': 'документи'}
    image_rules = {'extensions': ['.jpeg', '.png', '.jpg', '.svg'],
                   'folder_name': 'images',
                   'type_files': 'зображення'}
    audio_rules = {'extensions': ['.mp3', '.ogg', '.wav', '.amr'],
                   'folder_name': 'audio',
                   'type_files': 'музику'}
    video_rules = {'extensions': ['.avi', '.mp4', '.mov', '.mkv'],
                   'folder_name': 'video',
                   'type_files': 'відео'}

    rules_list = [document_rules, image_rules, audio_rules, video_rules]

    unk_lists = set()
    threads = []

    for rules in rules_list:
        thread = Thread(target=process_files, args=(path, rules))
        threads.append(thread)
        thread.start()

    archives_extensions = ['.zip', '.gz', '.tar', '.ZIP', '.GZ', '.TAR']
    for ext in archives_extensions:
        for arh in path.glob(f'**/*{ext}'):
            if arh.is_file():
                process_archives(arh, path)
    print(f"Архіви оброблено")

    for doc in path.glob('*/'):
        folder_name = doc.name
        if folder_name not in folders:
            new_folder_name = Path(str(path), folder_name)
            for doc_unk in new_folder_name.glob('**/*'):
                if doc_unk.is_file():
                    f_ext = doc_unk.suffix
                    unk_lists.add(f_ext)
                    process_unknown(doc_unk, path)
    print(f'Невідомі розширення: {unk_lists}')

    for thread in threads:
        thread.join()   

    for dir_empt in path.glob('**/*'):
        if dir_empt.is_dir() and not dir_empt.stem in folders and not any(dir_empt.glob('*')):
            try:
                dir_empt.rmdir()
            except FileExistsError:
                pass

def normalize(f_name):
    symbols = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯЄІЇҐ"
    translit = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g", "A", "B", "V", "G", "D", "E", "E", "J", "Z", "I", "J", "K", "L", "M", "N", "O", "P", "R", "S", "T", "U",
               "F", "H", "TS", "CH", "SH", "SCH", "", "Y", "", "E", "YU", "YA", "JE", "I", "JI", "G")
    trans = {}
    for s, t in zip(symbols, translit):
        trans[ord(s)] = t
    file_name, file_extension = os.path.splitext(f_name)
    normalized_name = file_name.translate(trans)
    normalized_file_name = re.sub(r'\W', '_', normalized_name)
    normalized_file = f"{normalized_file_name}{file_extension}"
    return normalized_file

def process_files(path, rules):
    extensions_list = rules['extensions']
    folder_name = rules['folder_name']
    type_files = rules['type_files']

    for ext in extensions_list:
        for doc in path.glob(f'**/*{ext}'):
            if doc.is_file():
                f_name = doc.name
                normalized_file = normalize(f_name)
                new_path = path.joinpath(folder_name, normalized_file)
                shutil.move(str(doc), str(new_path))
    print(f"Відсортовано {type_files}")

def process_archives(arh, path):
    if arh.is_file():
        try:
            with zipfile.ZipFile(arh, 'r') as zip_ref:
                arh_full_name = arh.name
                arh_name, arh_extension = os.path.splitext(arh_full_name)
                new_arh = path.joinpath('archives', arh_name)
                shutil.unpack_archive(arh, new_arh)
                os.remove(arh)
        except zipfile.BadZipFile:
            print(f"Помилка: {arh.name} — архів пошкоджений")
            os.remove(arh)
        except zipfile.LargeZipFile:
            print(f"Помилка: {arh.name} — архів занадто великий")
            os.remove(arh)
        except Exception as e:
            print(f"Помилка при роботі з {arh.name}: {e}")
            os.remove(arh)

def process_unknown(doc_unk, path):
    if doc_unk.is_file():
        f_name = doc_unk.name
        normalized_file = normalize(f_name)
        new_path = path.joinpath('unknown_extensions', normalized_file)
        shutil.move(str(doc_unk), str(new_path))

def main():
    args = sys.argv
    args_string = ' '.join(args)
    print(args_string)
    if len(sys.argv) != 2:
        print('Incorrect data')
        sys.exit(1)
    else:
        user_input = sys.argv[1]
        path = Path(user_input)
        if path.exists():
            if path.is_dir():
                sorting_files(path)
        else:
            print(f'{path.absolute} is not exists')

if __name__ == '__main__':
    main()
