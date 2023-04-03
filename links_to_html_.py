# Be careful ! Analyze the code first!
from pathlib import Path
import sys
from threading import Thread


# from jinja2 import Template  # ...
HTML_TEMPLATE = '''<!DOCTYPE HTML>
<html>
  <head>
    <title>Google automatic redirect</title>
    <meta http-equiv="refresh" content="0; url=$$$$" />
  </head>
  <body>
    <h1>For older browsers, click Redirect</h1>
    <p><a href="$$$$">Redirect</a></p>
  </body>
</html>
'''


def catch_file_exceptions(function):
    def wrapper(*args, **kwargs):
        try:
            reresult = function(*args, **kwargs)

        except Exception as err:
            print(f'\tError while processing arguments(\n\t{args},\n{kwargs}):\n\t{err}')
            return ''

        return reresult
    
    return wrapper


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
        # delete file(url):
        # # create thread remove_link_file with args - for this file
        thread_rm = Thread(target=remove_link_file, args=(file,))
        thread_rm.start()
 

def normalize_name(file: Path) -> str:
    """Replace unsupported characters for NTFS in the name."""
    bad_symbols = '"*/?><:|\\'
    new_name: str = ''.join(['_' if symbol in bad_symbols else symbol for symbol in file.stem])
    
    return new_name if len(new_name) < 220 else f'{new_name[:214]}..._'  # name without extension


@catch_file_exceptions
def read_url_from_file(urlfile: Path) -> str:
    """Read file and return url if exist, or empty string."""
    url = ''
    with open(urlfile, 'r', encoding='utf-8') as fh:
        raw_expenses = fh.readlines()
        for line in raw_expenses:
            url = line[4:].strip() if line.startswith('URL=') else ''
            if url:
                break

    return url if url else ''


@catch_file_exceptions
def remove_link_file(file_to_remove: Path) -> str:
    """Remove file (silent)."""
    file_to_remove.unlink(missing_ok=True)  # missing exceptions will be ignored
    return 'True'
    

@catch_file_exceptions
def save_html_link_file(file_to_save: Path, content: str) -> str:
    """Save new file with content."""
    file_candidate: Path = file_to_save
    number = 0
    while file_candidate.exists():
        number += 1
        file_candidate = file_to_save.parent.joinpath(f'{file_to_save.stem}{str(number)}.html')

    with open(file_candidate, 'w', encoding='utf-8') as fh:
        fh.write(f'{content}\n')

    return 'True'


def run_through_path(folder: Path) -> None:
    """Run through all folders and subfolders, and create html-link file for each lnk-file."""
    for file_system_object in folder.iterdir():
        if file_system_object.is_dir():
            if '.git' in file_system_object.name:
                continue
            # create thread run_through_path with args - for each sub-folder
            thread = Thread(target=run_through_path, args=(file_system_object,))
            thread.start()
            
        elif file_system_object.suffix.lower() in ('.desktop', '.url'):
            # create thread - for each link-file
            thread_moving_file = Thread(target=convert_link_to_html, args=(file_system_object,))
            thread_moving_file.start()


def main() -> None:
    descr = 'Convert all .url & .desktop files to html links-files with normal name, & remove original files.'
    # print(f'{descr}\nStart at path: ', folder_for_processing := Path(os.path.abspath(os.path.dirname(sys.argv[0]))))
    print(f'{descr}\nStart at path: ', folder_for_processing := Path(sys.argv[0]).parent.absolute())

    if input('Press Enter to continue or type something first - to exit:'):
        exit()

    try:
        run_through_path(folder_for_processing)  # Enter the main folder

    except Exception as err:
        print(f'\tError while get access to file or sub-folder in main folder(\n\t{folder_for_processing}):\n{err}')
        
    input('\nAll done, press Enter\n')


if __name__ == '__main__':
    main()
