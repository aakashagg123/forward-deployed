"""Minimal JSON-Schema argument validator for tool calls. Run: python3 validate.py"""

TYPES = {"string": str, "number": (int, float), "integer": int,
         "boolean": bool, "object": dict, "array": list}


def validate(args, schema):
    if schema.get("type") == "object":
        for key in schema.get("required", []):
            if key not in args:
                return f"missing required field {key!r}"
        for key, spec in schema.get("properties", {}).items():
            if key in args:
                err = _check(args[key], spec, key)
                if err:
                    return err
    return None


def _check(value, spec, path):
    t = spec.get("type")
    if t and not isinstance(value, TYPES[t]):
        return f"{path}: expected {t}, got {type(value).__name__}"
    if "enum" in spec and value not in spec["enum"]:
        return f"{path}: {value!r} not in {spec['enum']}"
    return None


if __name__ == "__main__":
    schema = {"type": "object",
              "properties": {"unit": {"type": "string", "enum": ["c", "f"]},
                             "temp": {"type": "number"}},
              "required": ["temp"]}
    print(validate({"temp": 20, "unit": "c"}, schema))   # None
    print(validate({"unit": "k"}, schema))               # missing required 'temp'
    print(validate({"temp": "hot"}, schema))             # type error
