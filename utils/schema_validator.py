import json
import os
from jsonschema import validate, ValidationError

class SchemaValidator:
    def __init__(self):
        self.schema_cache = {}
        self.schema_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schemas')
        
    def load_schema(self, schema_name):
        """Load schema from file if not already cached."""
        if schema_name not in self.schema_cache:
            schema_path = os.path.join(self.schema_dir, f"{schema_name}.json")
            with open(schema_path, 'r') as f:
                self.schema_cache[schema_name] = json.load(f)
        return self.schema_cache[schema_name]
        
    def validate_response(self, response_data, schema_name):
        """Validate response data against schema."""
        schema = self.load_schema(schema_name)
        try:
            validate(instance=response_data, schema=schema)
            return True, None
        except ValidationError as e:
            return False, str(e)

    def get_schema_path(self, schema_name):
        """Get full path to schema file."""
        return os.path.join(self.schema_dir, f"{schema_name}.json") 