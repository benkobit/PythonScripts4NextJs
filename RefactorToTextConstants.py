import re
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileProcessingError(Exception):
    pass

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

def clean_text(text):
    """
    Remove unnecessary spaces and <br /> elements from the text.
    """
    text = text.replace('{" "}', '').replace('<br />', '').strip()
    return ' '.join(text.split())

def replace_text_with_constants(content, tag_pattern, const_prefix, is_alt=False):
    """
    Replace matched text or alt attributes with constants.
    """
    # Exclude SVG content from the matches temporarily
    svg_pattern = r'(<svg.*?>.*?</svg>)'
    svg_matches = re.findall(svg_pattern, content, re.DOTALL)
    for i, match in enumerate(svg_matches):
        placeholder = f'__SVG_PLACEHOLDER_{i}__'
        content = content.replace(match, placeholder)

    matches = re.findall(tag_pattern, content, re.DOTALL)
    constants = {}
    counter = 1

    for match in matches:
        if is_alt:
            prefix, text, suffix = match
            text = clean_text(text)
            const_name = f'{const_prefix}_{counter}'
            constants[const_name] = text
            content = content.replace(f'{prefix}{text}{suffix}', f'alt={{{const_name}}}')
        else:
            start_tag, text, end_tag = match[0], match[1], match[2]
            if not text:  # In case of <h2> tag
                start_tag, text, end_tag = match[3], match[4], match[5]

            text = clean_text(text)
            const_name = f'{const_prefix}_{counter}'
            constants[const_name] = text
            content = content.replace(f'{start_tag}{text}{end_tag}', f'{start_tag}{{{const_name}}}{end_tag}')
        counter += 1

    # Restore SVG content
    for i, match in enumerate(svg_matches):
        placeholder = f'__SVG_PLACEHOLDER_{i}__'
        content = content.replace(placeholder, match)

    return content, constants

def generate_constants_definitions(constants):
    """
    Generate constant definitions from a dictionary of constants.
    """
    return '\n'.join([f'const {name} = "{value}";' for name, value in constants.items()])

def insert_constants(content, constants_definitions):
    """
    Insert constant definitions after the last import statement.
    """
    import_statements = re.findall(r'^(import .+?;)', content, re.MULTILINE)
    if import_statements:
        last_import = import_statements[-1]
        content = content.replace(last_import, f'{last_import}\n\n{constants_definitions}')
    else:
        content = f'{constants_definitions}\n\n{content}'
    return content

def replace_texts_and_alts_with_constants(file_path):
    """
    Process a file to replace text and alt attributes with constants.
    """
    content = read_file(file_path)
    if content is None:
        return

    p_h2_pattern = r'(<p.*?>)(.*?)(</p>)|(<h2.*?>)(.*?)(</h2>)'
    content, text_constants = replace_text_with_constants(content, p_h2_pattern, 'TEXT')

    alt_pattern = r'(alt=")([^"]+)(")'
    content, alt_constants = replace_text_with_constants(content, alt_pattern, 'ALT', is_alt=True)

    all_constants = {**text_constants, **alt_constants}
    constants_definitions = generate_constants_definitions(all_constants)

    content = insert_constants(content, constants_definitions)

    write_file(file_path, content)

def process_all_components(directory, exclude_files=[]):
    """
    Process all components in the specified directory, excluding specified files.
    """
    for filename in os.listdir(directory):
        if filename.startswith("C") and (filename.endswith(".js") or filename.endswith(".jsx")) and filename not in exclude_files:
            file_path = os.path.join(directory, filename)
            replace_texts_and_alts_with_constants(file_path)

if __name__ == "__main__":
    directory = 'src/components/agua'
    exclude_files = ['C23.jsx']
    process_all_components(directory, exclude_files)
