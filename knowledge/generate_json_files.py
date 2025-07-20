import json
import os
import re
import zipfile
from typing import List, Dict, Any


def generate_json_files(conditions: List[Dict[str, Any]], output_dir: str = "medical_conditions",
                        create_zip: bool = True) -> str:
    """
    Generate JSON files from a list of medical condition dictionaries.

    Args:
        conditions: List of dictionaries containing "title", "content", and "category"
        output_dir: Directory to save the generated files
        create_zip: Whether to create a zip file containing all JSON files

    Returns:
        Path to the generated zip file or directory
    """
    os.makedirs(output_dir, exist_ok=True)

    file_paths = []

    for i, condition in enumerate(conditions, 1):
        title = condition["title"]
        shortened_title = re.sub(r'[^\w\s]', '', title).lower().replace(' ', '_')[:30]
        filename = f"medical_condition_{i+15}_{shortened_title}.json"
        file_path = os.path.join(output_dir, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(condition, f, indent=2, ensure_ascii=False)

        file_paths.append(file_path)
        print(f"Created: {filename}")

    if create_zip and file_paths:
        zip_path = f"{output_dir}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in file_paths:
                zipf.write(file_path, os.path.basename(file_path))
        print(f"Created zip file: {zip_path}")
        return zip_path

    return output_dir


if __name__ == "__main__":
    conditions = [ ]

    zip_or_dir_path = generate_json_files(conditions)
    print(f"Files generated at: {zip_or_dir_path}")
