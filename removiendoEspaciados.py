import re
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None

def write_file(file_path, content):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        logging.info(f'Processed file saved to {file_path}')
    except IOError as e:
        logging.error(f"Error writing file {file_path}: {e}")

def remove_placeholder_spaces(content):
    """
    Remove all occurrences of {" "} from the content.
    """
    pattern = re.compile(r'\{\s*"\s*"\s*\}')
    modified_content = pattern.sub(' ', content)

    return modified_content

def process_component(file_path):
    """
    Process the specified component file to remove placeholder spaces.
    """
    content = read_file(file_path)
    if content is None:
        return

    modified_content = remove_placeholder_spaces(content)
    write_file(file_path, modified_content)

def process_all_components(directory):
    """
    Recursively process all .js and .jsx files in the specified directory.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.js') or file.endswith('.jsx'):
                file_path = os.path.join(root, file)
                process_component(file_path)

if __name__ == "__main__":
    components_directory = 'src/components'
    process_all_components(components_directory)
