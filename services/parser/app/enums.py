from enum import Enum

class DLQReason(str, Enum):
    JSON_PARSE_ERROR = "json_decode_failed"
    SCHEMA_VALIDATION = "schema_validation_failed"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    UNKNOWN = "unknown_error"
    PARSER_NO_MATCH = "parser_no_match"