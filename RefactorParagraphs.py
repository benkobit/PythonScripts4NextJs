import os
import json
import re
from bs4 import BeautifulSoup, Tag

# Lista de componentes a excluir (modificar según sea necesario)
EXCLUDED_COMPONENTS = [
    'C8.jsx',
    'C13.jsx',
    'Footer.jsx',
    'C4.jsx',
    'Flyout.jsx',
    'C25.jsx',
    'C23.jsx',
    # Añade más componentes a excluir aquí
]

def clean_text(text):
    # Elimina saltos de línea y múltiples espacios
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_constant_name(component_name, index):
    return f"{component_name}_paragraph_{index + 1}"

def process_p_tag(p_tag, component_name, index):
    inner_content = ''.join(str(e) for e in p_tag.contents if isinstance(e, (str, Tag)))
    cleaned_content = clean_text(inner_content)
    constant_name = generate_constant_name(component_name, index)
    
    if any(tag in cleaned_content for tag in ['<br', '<span', '<a', '<strong', '<em']):
        new_tag = f'<p dangerouslySetInnerHTML={{ __html: {constant_name} }} />'
    else:
        new_tag = f'<p>{{ {constant_name} }}</p>'
    
    return cleaned_content, constant_name, new_tag

def extract_p_tags_from_file(file_path, component_constants):
    component_name = os.path.splitext(os.path.basename(file_path))[0]
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        p_tags = soup.find_all('p')

        modified = False
        constants = {}
        new_content = content

        for index, p_tag in enumerate(p_tags):
            cleaned_content, constant_name, new_tag = process_p_tag(p_tag, component_name, index)
            constants[constant_name] = cleaned_content
            
            original_tag_str = str(p_tag)
            if original_tag_str in new_content:
                new_content = new_content.replace(original_tag_str, new_tag)
                modified = True

        if modified:
            constants_declaration = '\n'.join([f'const {name} = `{content}`;' for name, content in constants.items()])
            
            # Encuentra la última declaración de import y añade las constantes después de ella
            import_statements = re.findall(r'^import .+?;$', new_content, re.MULTILINE)
            if import_statements:
                last_import_statement = import_statements[-1]
                insertion_point = new_content.find(last_import_statement) + len(last_import_statement)
                new_content = new_content[:insertion_point] + '\n' + constants_declaration + new_content[insertion_point:]
            else:
                new_content = constants_declaration + '\n\n' + new_content
            
            component_constants[file_path] = constants
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)

        return modified

def extract_p_tags_from_directory(directory_path):
    p_tags_dict = {}
    component_constants = {}
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                if file in EXCLUDED_COMPONENTS:
                    continue
                file_path = os.path.join(root, file)
                modified = extract_p_tags_from_file(file_path, component_constants)
                relative_path = os.path.relpath(file_path, directory_path)
                p_tags_dict[relative_path] = 'modified' if modified else 'not modified'

    return p_tags_dict, component_constants

def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    components_directory = os.path.join(project_root, 'src', 'components')
    output_file = os.path.join(project_root, 'p_tags_status.json')
    constants_file = os.path.join(project_root, 'paragraph_constants.json')

    if not os.path.isdir(components_directory):
        print(f"Directory '{components_directory}' does not exist.")
        return

    p_tags_dict, component_constants = extract_p_tags_from_directory(components_directory)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(p_tags_dict, f, ensure_ascii=False, indent=4)

    with open(constants_file, 'w', encoding='utf-8') as f:
        json.dump(component_constants, f, ensure_ascii=False, indent=4)

    print(f"Status of <p> tag modifications have been saved to '{output_file}'.")
    print(f"Paragraph constants have been saved to '{constants_file}'.")

if __name__ == "__main__":
    main()
