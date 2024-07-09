import os
import re
import json

# Lista de componentes a excluir (modificar según sea necesario)
EXCLUDED_COMPONENTS = [
    'C8.jsx',
    # Añade más componentes a excluir aquí
]

def extract_p_tags_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Regex to find all <p>...</p> tags
        p_tags = re.findall(r'<p.*?>(.*?)<\/p>', content, re.DOTALL)
        return p_tags

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
