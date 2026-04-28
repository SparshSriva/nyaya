import json
import os

class DeweyService:
    def __init__(self, data_path=None):
        if data_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(script_dir, '..', 'Datasets', 'dewey_decimal_data.json')
        self.dewey_data = self._load_dewey_data(data_path)

    def _load_dewey_data(self, filepath):
        with open(filepath, 'r') as f:
            return json.load(f)

    def find_subject(self, code):
        if not code:
            return None

        class_code = code[:1] + "00"

        if len(code) == 1:
            division_code = class_code
        else:
            division_code = code[:2] + "0"

        section_code = code[:3]

        if class_code in self.dewey_data:
            class_match = self.dewey_data[class_code]
            if division_code in class_match["divisions"]:
                division_match = class_match["divisions"][division_code]
                if section_code in division_match["sections"]:
                    return division_match["sections"][section_code]
                return {"name": division_match.get("name")}
            return {"name": class_match.get("name")}

        return None
