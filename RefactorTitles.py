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

def extract_tags_from_file(file_path, tags):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        
        extracted_data = []
        for tag in tags:
            elements = soup.find_all(tag)
            for element in elements:
                inner_content = ''.join(str(e) for e in element.contents if isinstance(e, (str, Tag)))
                cleaned_content = clean_text(inner_content)
                extracted_data.append(cleaned_content)
        
        return extracted_data

def extract_tags_from_directory(directory_path, tags):
    tags_dict = {}
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                if file in EXCLUDED_COMPONENTS:
                    continue
                file_path = os.path.join(root, file)
                tags_content = extract_tags_from_file(file_path, tags)
                if tags_content:
                    relative_path = os.path.relpath(file_path, directory_path)
                    tags_dict[relative_path] = tags_content
    return tags_dict

def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    components_directory = os.path.join(project_root, 'src', 'components')
    output_file = os.path.join(project_root, 'tags_content.json')

    if not os.path.isdir(components_directory):
        print(f"Directory '{components_directory}' does not exist.")
        return

    tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    tags_dict = extract_tags_from_directory(components_directory, tags)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tags_dict, f, ensure_ascii=False, indent=4)

    print(f"Extracted tags have been saved to '{output_file}'.")

if __name__ == "__main__":
    main()
