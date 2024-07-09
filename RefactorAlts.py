import re
import os

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def generate_constants(content):
    alt_pattern = r'alt="([^"]+)"'
    image_alt_pattern = r'imageAlt:\s*"([^"]+)"'

    alt_matches = re.findall(alt_pattern, content)
    image_alt_matches = re.findall(image_alt_pattern, content)

    constants = {}
    counter = 1

    for match in alt_matches:
        const_name = f'ALT_{counter}'
        constants[match] = const_name
        counter += 1

    for match in image_alt_matches:
        const_name = f'IMAGE_ALT_{counter}'
        constants[match] = const_name
        counter += 1

    return constants

def insert_constants(content, constants):
    const_lines = [f'const {name} = "{value}";' for value, name in constants.items()]
    constants_code = '\n'.join(const_lines) + '\n\n'
    import_statements = re.findall(r'^(import .+?;)', content, re.MULTILINE)

    if import_statements:
        last_import = import_statements[-1]
        content = content.replace(last_import, f'{last_import}\n\n{constants_code}')
    else:
        content = f'{constants_code}\n\n{content}'

    return content

def replace_with_constants(content, constants):
    for value, const_name in constants.items():
        content = re.sub(rf'alt="{re.escape(value)}"', f'alt={{{const_name}}}', content)
        content = re.sub(rf'imageAlt:\s*"{re.escape(value)}"', f'imageAlt: {const_name}', content)

    return content

def process_file(file_path):
    content = read_file(file_path)
    constants = generate_constants(content)
    content_with_constants = insert_constants(content, constants)
    content_replaced = replace_with_constants(content_with_constants, constants)
    write_file(file_path, content_replaced)

def process_all_components(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".jsx") or file.endswith(".js"):
                file_path = os.path.join(root, file)
                process_file(file_path)

if __name__ == "__main__":
    directory = 'src/components'
    process_all_components(directory)
