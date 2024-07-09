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

def replace_p_tag_content(p_tag, replacement_text):
    # Reemplaza el contenido de una etiqueta <p> con un nuevo texto
    for content in p_tag.contents:
        if isinstance(content, Tag):
            content.decompose()
        else:
            p_tag.string = replacement_text

def extract_and_replace_p_tags_from_file(file_path, replacement_text):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        p_tags = soup.find_all('p')

        for p_tag in p_tags:
            replace_p_tag_content(p_tag, replacement_text)

        return str(soup)

def extract_and_replace_p_tags_from_directory(directory_path, replacement_text):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                if file in EXCLUDED_COMPONENTS:
                    continue
                file_path = os.path.join(root, file)
                new_content = extract_and_replace_p_tags_from_file(file_path, replacement_text)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)

def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    components_directory = os.path.join(project_root, 'src', 'components')
    replacement_text = "CONSTANTE_REEMPLAZO"  # Cambia esto por la constante que quieres insertar

    if not os.path.isdir(components_directory):
        print(f"Directory '{components_directory}' does not exist.")
        return

    extract_and_replace_p_tags_from_directory(components_directory, replacement_text)

    print("Replacement of <p> tag contents completed.")

if __name__ == "__main__":
    main()
