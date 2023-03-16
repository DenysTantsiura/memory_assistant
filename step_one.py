# Be careful ! Analyze the code first!
import os
from pathlib import Path
import shutil
import sys
from threading import Thread
from time import time


# from jinja2 import Template  # ...
HTML_TEMPLATE = '''<!DOCTYPE HTML>
<html>
  <head>
    <title>Google automatic redirect</title>
    <meta http-equiv="refresh" content="0; url=$$$$"/>
  </head>
  <body>
    <h1>For older browsers, click Redirect</h1>
    <p><a href="$$$$">Redirect</a></p>
  </body>
</html>
'''

def convert_link_to_html(file: Path) -> None:
    """Create html with url-link from url-file."""
    # read url from link-file
    url: str = read_url_from_file(file)

    # get new name w/o extension
    new_name_for_file: str = normalize_name(file)  # without extension
    
    # create content for html-url file
    content: str = HTML_TEMPLATE[:].replace('$$$$', f'{url}')

    # find name w/o extension
    new_file: Path = file.parent.joinpath(f'{new_name_for_file}.html')

    # create and write html-file with name
    if save_html_link_file(new_file, content):
        # delete file(url)
        # # create thread remove_link_file with args - for this file
        thread_rm = Thread(target=remove_link_file, args=(file,))
        thread_rm.start()
 

def normalize_name(file: Path) -> str:
    """Replace unsupported characters for NTFS in the name."""
    bad_symbols = '"*/:?><\|'
    new_name: str = file.parent.joinpath(
        ''.join(['_' if symbol in bad_symbols else symbol for symbol in file.name])
        ).stem
    
    return new_name  # name without extension


# ! rewrite by with decorator
def read_url_from_file(urlfile: Path) -> str:
    """Read file and return url if exist, or empty string."""
    url = ''
    try:
        with open(urlfile, 'r', encoding="utf-8") as fh:
            raw_expenses = fh.readlines()
            for line in raw_expenses:
                # key, value = line.split("|")
                # expenses[key] = int(value)
                # url = line[4:] if 'URL=' in line else ''
                url = line[4:] if line.startswith('URL=') else ''
                if url:
                    break

    except Exception as err:
        print(f'\tError while read file (\n\t{urlfile}):\n{err}')
        return ''
    
    print(url)
    return url if url else ''


# ! rewrite by with decorator
def remove_link_file(file_to_remove: Path) -> bool:
    """Remove file (silent)."""
    try:
        file_to_remove.unlink(missing_ok=True)  # missing exceptions will be ignored

    except Exception as err:
        print(f'\tError while try remove file (\n\t{file_to_remove}):\n{err}')
        return False

    return True
    

# ! rewrite by with decorator
def save_html_link_file(file_to_save: Path, content: str) -> bool:
    """Save new file with content."""
    file_candidate: Path = Path(str(file_to_save))  # file_to_save.copy()
    # file_candidate: Path = file_to_save
    number = 0
    while file_candidate.exists():
        number += 1
        file_candidate = file_to_save.parent.joinpath(f'{file_to_save.stem}{str(number)}.html')

    try:
        with open(file_candidate, 'w', encoding="utf-8") as fh:
            fh.write(f'{content}\n')

    except Exception as err:
        print(f'\tError while try save file (\n\t{file_candidate}):\n{err}')
        return False

    return True


def run_through_path(folder: Path) -> None:
    """Run through all folders and subfolders, and create html-link file for each lnk-file."""
    for file_system_object in folder.iterdir():
        if file_system_object.is_dir():
            if '.git' in file_system_object.name:
                continue
            # create thread run_through_path with args - for each sub-folder
            thread = Thread(target=run_through_path, args=(file_system_object,))
            thread.start()

            # while thread.is_alive():  # wait during recursion thread
            #     pass

            # # create thread remove_empty_folder with args - for this folder
            # thread_rm = Thread(target=remove_empty_folder, args=(file_system_object,))
            # thread_rm.start()
            
        elif file_system_object.suffix in ('.desktop', '.url'):
            # create thread - for each file
            thread_moving_file = Thread(target=convert_link_to_html, args=(file_system_object,))
            thread_moving_file.start()
            

if __name__ == "__main__":
    
    print('full path =', folder_for_processing := Path(os.path.abspath(os.path.dirname(sys.argv[0]))))

    if input('Press Enter to continue or type something to exit.'):
        exit()

    run_through_path(folder_for_processing)

    # try:
    #     overrun_folder(folders, folders)  # Enter the main folder

    # except FileNotFoundError:
    #     raise FileNotFoundError(f'I can\'t find folder - {folders}')
        
    input('\nAll done, press Enter to exit:\n')

