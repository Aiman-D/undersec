import re
import numpy as np
import sqlparse
from sqlparse.sql import TokenList
from sqlparse.tokens import Keyword, Comment, DML, DDL

def extract_features(query_text: str, user: str, time_of_day: int = 12, rows_affected: int = 1) -> dict:
    """Extracts 11 ML features from an SQL query using AST parsing for better security analysis."""
    
    # AST Parsing
    statements = [stmt for stmt in sqlparse.parse(query_text) if stmt.tokens]
    
    if not statements:
        return {
            "qt_score": 0, "schema_change": 0, "has_multi_statement": 0,
            "has_comment": 0, "has_union": 0, "rows_affected_log": np.log1p(rows_affected),
            "time_of_day": float(time_of_day), "user_frequency": 1.0, "q_len": len(query_text),
            "complexity": 0, "table_len": 0
        }
    
    qt_score = 0
    schema_change = 0
    has_comment = 0
    has_union = 0
    complexity = 0
    
    # 3. Multi-statement (Classic SQLi / Piggybacking)
    has_multi_statement = 3 if len(statements) > 1 else 0
    
    for stmt in statements:
        # Query Type classification
        stmt_type = stmt.get_type()
        if stmt_type == 'DROP':
            qt_score = max(qt_score, 10)
        elif stmt_type == 'ALTER':
            qt_score = max(qt_score, 8)
        elif stmt_type in ['DELETE', 'TRUNCATE']:
            qt_score = max(qt_score, 5)
        elif stmt_type == 'UPDATE':
            qt_score = max(qt_score, 2)
        elif stmt_type == 'INSERT':
            qt_score = max(qt_score, 1)
            
        # 2. Schema Change
        if stmt_type in ['DROP', 'ALTER', 'CREATE']:
            schema_change = 5
            
        # Deep Token Inspection for Comments, Union, Joins
        def walk_tokens(token_list):
            nonlocal has_comment, has_union, complexity
            for token in token_list.tokens:
                if token.ttype in Comment:
                    has_comment = 3
                if token.ttype is Keyword:
                    val = token.value.upper()
                    if val == 'UNION':
                        has_union = 3
                    elif val in ['JOIN', 'AND', 'OR']:
                        complexity += 1
                if isinstance(token, TokenList):
                    walk_tokens(token)
                    
        walk_tokens(stmt)

    # 6. Rows Affected (Log scaled)
    rows_affected_log = np.log1p(rows_affected)
    
    # 7. Time of day
    time_of_day_val = float(time_of_day)
    
    # 8. User frequency
    user_frequency = 1.0 
    
    # 9. Query Length
    q_len = len(query_text)
    
    # 11. Table Name Length (Heuristic for obfuscated automated queries)
    # Fast regex fallback for table name length instead of complex AST token walking for identifiers
    q_upper = query_text.upper()
    table_match = re.search(r'(?:FROM|UPDATE|JOIN|INTO)\s+([a-zA-Z0-9_]+)', q_upper)
    table_len = len(table_match.group(1)) if table_match else 0

    return {
        "qt_score": qt_score,
        "schema_change": schema_change,
        "has_multi_statement": has_multi_statement,
        "has_comment": has_comment,
        "has_union": has_union,
        "rows_affected_log": rows_affected_log,
        "time_of_day": time_of_day_val,
        "user_frequency": user_frequency,
        "q_len": q_len,
        "complexity": complexity,
        "table_len": table_len
    }

def features_to_vector(features: dict) -> list:
    """Converts the feature dictionary into an ordered 11-D array for the model."""
    return [
        features["qt_score"],
        features["schema_change"],
        features["has_multi_statement"],
        features["has_comment"],
        features["has_union"],
        features["rows_affected_log"],
        features["time_of_day"],
        features["user_frequency"],
        features["q_len"],
        features["complexity"],
        features["table_len"]
    ]