import os
import json
from bs4 import BeautifulSoup, Tag

# Lista de componentes a excluir (modificar según sea necesario)
EXCLUDED_COMPONENTS = [
    'C8.jsx',
    'C13.jsx',
    'Footer.jsx',
    'C4.jsx',
    'Flyout.jsx',
    # Añade más componentes a excluir aquí
]

def extract_p_tags_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        p_tags = soup.find_all('p')

        extracted_data = []
        for p_tag in p_tags:
            inner_content = ''.join(str(e) for e in p_tag.contents if isinstance(e, (str, Tag)))
            extracted_data.append(inner_content)
        
        return extracted_data

def extract_p_tags_from_directory(directory_path):
    p_tags_dict = {}
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                if file in EXCLUDED_COMPONENTS:
                    continue
                file_path = os.path.join(root, file)
                p_tags = extract_p_tags_from_file(file_path)
                if p_tags:
                    relative_path = os.path.relpath(file_path, directory_path)
                    p_tags_dict[relative_path] = p_tags
    return p_tags_dict

def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    components_directory = os.path.join(project_root, 'src', 'components')
    output_file = os.path.join(project_root, 'p_tags.json')

    if not os.path.isdir(components_directory):
        print(f"Directory '{components_directory}' does not exist.")
        return

    p_tags_dict = extract_p_tags_from_directory(components_directory)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(p_tags_dict, f, ensure_ascii=False, indent=4)

    print(f"Extracted <p> tags have been saved to '{output_file}'.")

if __name__ == "__main__":
    main()
