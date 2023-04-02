from pathlib import Path
import sys
from typing import Optional

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

from links_to_html_ import main as html_to_links
from links_to_html_ import catch_file_exceptions


KNOWN_IMAGES = ('.png', '.svg', '.jpg', '.jpeg', '.gif', '.webp')

env = Environment(loader=FileSystemLoader('.'))

template = env.get_template('templates/index.html')


@catch_file_exceptions
def read_file(urlfile: Path) -> str:
    """Read file and return url if it exist, or empty string."""
    with open(urlfile, 'r', encoding='utf-8') as fh:
        raw_expenses = fh.read()

    return raw_expenses if raw_expenses else ''


def get_url_from_file(file: Path) -> Optional[str]:
    """Get the url-link from html-file."""
    soup = BeautifulSoup(read_file(file), 'lxml')
    return soup.find('a')['href'] if soup.find('a') else None  # soup.find('a')['href']


def gather_info(folder: Path) -> tuple:
    """Gather urls and image-links to dictionaries from files in folder."""
    urls = {}
    img_links = {}
    for file_system_object in folder.iterdir():
        if file_system_object.is_file():
            if file_system_object.suffix.lower() == '.html':
                urls[file_system_object.stem[:2]] = get_url_from_file(file_system_object) or 'The link is missing!'
            elif file_system_object.suffix.lower() in KNOWN_IMAGES:
                img_links[file_system_object.stem[:2]] = f'{folder.parts[-1]}/{file_system_object.name}'
    
    strict_urls = {}
    strict_img_links = {}

    for number in range(14):
        key = str(number) if number > 9 else f'0{number}'
        strict_urls[key] = urls[key] if urls.get(key, None) else ''
        strict_img_links[key] = img_links[key] if img_links.get(key, None) else ''
        if not strict_img_links[key]:
            strict_img_links[key] = 'templates/default.png'

    return strict_urls, strict_img_links


def subfolders_process(folder: Path) -> tuple:
    """Run through subfolders in main folder, and create bookmark html-links file 
    (main-ile) from all html-links file."""
    input_data = []
    main_file: Path = folder.joinpath('index.html')
    for file_system_object in folder.iterdir():
        if file_system_object.is_dir():
            if not file_system_object.name[:2].isdigit():
                continue
            input_data.append(gather_info(file_system_object))
            
        elif file_system_object.suffix.lower() == '.txt':
            # save name for main file
            main_file: Path = folder.joinpath(f'{file_system_object.stem}.html')

    rezult_data = []
    for urls, imgs in input_data:
        data = []
        for url in urls:
            data.append((urls.get(url, ''), imgs.get(url, '')))
        rezult_data.append(data)
        
    return main_file, rezult_data


@catch_file_exceptions
def create_main_file(file: Path, input_data: list) -> None:
    """Create main html-links file."""
    output = template.render(link_lines=input_data)

    with open(file, 'w', encoding='utf-8') as fh:
        fh.write(output)


def main() -> None:
    descr = 'Create html links-file.'

    print(f'{descr}\nStart at path: ', folder_for_processing := Path(sys.argv[0]).parent.absolute())

    if input('Press Enter to continue or type something first - to exit:'):
        exit()

    try:
        file, data = subfolders_process(folder_for_processing)
        create_main_file(file, data)  # Enter the main folder

    except Exception as err:
        print(f'\tError while get access to file or sub-folder in main folder(\n\t{folder_for_processing}):\n{err}')
        
    input('\nAll done, press Enter to exit:\n')


if __name__ == '__main__':
    html_to_links()
    main()
