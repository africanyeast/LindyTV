import json
def SAVE_JSON_FILE(file_path, data):
    """Helper function to save JSON data."""
    try:
        with open(file_path, 'w') as outfile:
            json.dump(data, outfile, indent=4)
    except IOError as e:
        print(f"Failed to save JSON file {file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error saving file {file_path}: {e}")


def LOAD_JSON_FILE(file_path):
    """Helper function to load and return JSON data from a file."""
    try:
        with open(file_path, 'r') as infile:
            data = json.load(infile)
            return data
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error loading file {file_path}: {e}")
        return None


def GET_USER_FOLDER(username):
    return f'data/{username}'