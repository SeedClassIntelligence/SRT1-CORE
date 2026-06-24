import re
import os
from typing import List, Dict, Any, Optional

# Symbol types that represent structural anchors, not executable code
ANCHOR_TYPES = {"html_id", "html_class", "script", "style", "css_selector", "css_variable",
                "config_key", "h1_header", "h2_header", "h3_header"}

def _create_symbol(name: str, sym_type: str, line: int, end_line: int = None, deps: List[str] = None, params: List[str] = None, docstring: str = "", category: str = None) -> Dict[str, Any]:
    # Auto-classify: if caller doesn't specify, infer from type
    if category is None:
        category = "anchor" if sym_type in ANCHOR_TYPES else "code"
    return {
        "name": name,
        "type": sym_type,
        "line": line,
        "end_line": end_line or line,
        "dependencies": deps or [],
        "parameters": params or [],
        "docstring_first_line": docstring,
        "category": category,
    }

def _extract_jsdoc(lines: List[str], current_idx: int) -> str:
    """Look upwards from current line to find JSDoc/Block comments."""
    doc_lines = []
    i = current_idx - 1
    while i >= 0:
        line = lines[i].strip()
        if not line:
            i -= 1
            continue
        if line == '*/':
            i -= 1
            while i >= 0:
                l = lines[i].strip()
                if l.startswith('/*'):
                    return " ".join(reversed(doc_lines)).replace('*', '').strip()
                doc_lines.append(l)
                i -= 1
            break
        elif line.startswith('//'):
            doc_lines.append(line.lstrip('/ ').strip())
            i -= 1
            while i >= 0 and lines[i].strip().startswith('//'):
                doc_lines.append(lines[i].strip().lstrip('/ ').strip())
                i -= 1
            return " ".join(reversed(doc_lines))
        else:
            break
    return ""

def parse_javascript_typescript(source: str, is_ts: bool = False) -> List[Dict[str, Any]]:
    symbols = []
    lines = source.split('\n')
    
    class_pattern = re.compile(r'^\s*(?:export\s+(?:default\s+)?)?class\s+([A-Za-z0-9_]+)')
    func_pattern = re.compile(r'^\s*(?:export\s+(?:default\s+)?)?(?:async\s+)?function\s+([A-Za-z0-9_]+)\s*\((.*?)\)')
    arrow_pattern = re.compile(r'^\s*(?:export\s+(?:default\s+)?)?(?:const|let|var)\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?(?:\((.*?)\)|[A-Za-z0-9_]+)\s*=>')
    ts_interface_pattern = re.compile(r'^\s*(?:export\s+)?interface\s+([A-Za-z0-9_]+)')
    ts_type_pattern = re.compile(r'^\s*(?:export\s+)?type\s+([A-Za-z0-9_]+)\s*=')
    ts_enum_pattern = re.compile(r'^\s*(?:export\s+)?enum\s+([A-Za-z0-9_]+)')
    
    # Very basic dependency extraction (function calls)
    call_pattern = re.compile(r'([A-Za-z0-9_]+)\s*\(')

    for i, line in enumerate(lines):
        # Classes
        m = class_pattern.search(line)
        if m:
            doc = _extract_jsdoc(lines, i)
            symbols.append(_create_symbol(m.group(1), "class", i+1, docstring=doc))
            continue
            
        # Functions
        m = func_pattern.search(line)
        if m:
            doc = _extract_jsdoc(lines, i)
            params = [p.strip() for p in m.group(2).split(',') if p.strip()]
            symbols.append(_create_symbol(m.group(1), "function", i+1, params=params, docstring=doc))
            continue
            
        # Arrow Functions
        m = arrow_pattern.search(line)
        if m:
            doc = _extract_jsdoc(lines, i)
            params = [p.strip() for p in (m.group(2) or "").split(',') if p.strip()]
            symbols.append(_create_symbol(m.group(1), "function", i+1, params=params, docstring=doc))
            continue
            
        if is_ts:
            m = ts_interface_pattern.search(line)
            if m:
                symbols.append(_create_symbol(m.group(1), "interface", i+1, docstring=_extract_jsdoc(lines, i)))
                continue
            m = ts_type_pattern.search(line)
            if m:
                symbols.append(_create_symbol(m.group(1), "type", i+1, docstring=_extract_jsdoc(lines, i)))
                continue
            m = ts_enum_pattern.search(line)
            if m:
                symbols.append(_create_symbol(m.group(1), "enum", i+1, docstring=_extract_jsdoc(lines, i)))
                continue
                
    # Dependency pass - naive (assign calls to last seen symbol)
    current_symbol = None
    for i, line in enumerate(lines):
        # Check if line matches an existing symbol start
        sym_match = next((s for s in symbols if s["line"] == i+1), None)
        if sym_match:
            current_symbol = sym_match
            
        if current_symbol:
            calls = call_pattern.findall(line)
            for call in calls:
                if call not in ('if', 'for', 'while', 'switch', 'catch', 'function', 'return', current_symbol['name']):
                    if call not in current_symbol['dependencies']:
                        current_symbol['dependencies'].append(call)
                        
    return symbols

def parse_go(source: str) -> List[Dict[str, Any]]:
    symbols = []
    lines = source.split('\n')
    
    # func name(params) OR func (receiver) name(params)
    func_pattern = re.compile(r'^\s*func\s+(?:\([^)]+\)\s+)?([A-Za-z0-9_]+)\s*\((.*?)\)')
    type_struct_pattern = re.compile(r'^\s*type\s+([A-Za-z0-9_]+)\s+struct')
    type_interface_pattern = re.compile(r'^\s*type\s+([A-Za-z0-9_]+)\s+interface')
    
    for i, line in enumerate(lines):
        m = func_pattern.search(line)
        if m:
            doc = _extract_jsdoc(lines, i) # Reusing simple upwards comment search
            params = [p.strip() for p in m.group(2).split(',') if p.strip()]
            symbols.append(_create_symbol(m.group(1), "function", i+1, params=params, docstring=doc))
            continue
            
        m = type_struct_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "struct", i+1, docstring=_extract_jsdoc(lines, i)))
            continue
            
        m = type_interface_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "interface", i+1, docstring=_extract_jsdoc(lines, i)))
            continue
            
    return symbols

def parse_rust(source: str) -> List[Dict[str, Any]]:
    symbols = []
    lines = source.split('\n')
    
    func_pattern = re.compile(r'^\s*(?:pub\s+)?(?:async\s+)?fn\s+([A-Za-z0-9_]+)\s*\((.*?)\)')
    struct_pattern = re.compile(r'^\s*(?:pub\s+)?struct\s+([A-Za-z0-9_]+)')
    enum_pattern = re.compile(r'^\s*(?:pub\s+)?enum\s+([A-Za-z0-9_]+)')
    trait_pattern = re.compile(r'^\s*(?:pub\s+)?trait\s+([A-Za-z0-9_]+)')
    impl_pattern = re.compile(r'^\s*impl(?:<.*?>)?\s+([A-Za-z0-9_]+)')
    
    for i, line in enumerate(lines):
        m = func_pattern.search(line)
        if m:
            doc = _extract_jsdoc(lines, i)
            params = [p.strip() for p in m.group(2).split(',') if p.strip()]
            symbols.append(_create_symbol(m.group(1), "function", i+1, params=params, docstring=doc))
            continue
            
        m = struct_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "struct", i+1, docstring=_extract_jsdoc(lines, i)))
            continue
            
        m = enum_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "enum", i+1, docstring=_extract_jsdoc(lines, i)))
            continue
            
        m = trait_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "trait", i+1, docstring=_extract_jsdoc(lines, i)))
            continue
            
        m = impl_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "impl", i+1, docstring=_extract_jsdoc(lines, i)))
            continue
            
    return symbols

def parse_java(source: str) -> List[Dict[str, Any]]:
    symbols = []
    lines = source.split('\n')
    
    class_pattern = re.compile(r'^(?:\s*(?:public|private|protected|abstract|final)\s+)*class\s+([A-Za-z0-9_]+)')
    interface_pattern = re.compile(r'^(?:\s*(?:public|private|protected|abstract)\s+)*interface\s+([A-Za-z0-9_]+)')
    method_pattern = re.compile(r'^\s*(?:(?:public|private|protected|static|final|abstract|synchronized|native|strictfp)\s+)*[\w\<\>\[\]]+\s+([A-Za-z0-9_]+)\s*\((.*?)\)\s*(?:throws\s+[\w\s,]+)?\s*\{')
    
    for i, line in enumerate(lines):
        m = class_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "class", i+1, docstring=_extract_jsdoc(lines, i)))
            continue
            
        m = interface_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "interface", i+1, docstring=_extract_jsdoc(lines, i)))
            continue
            
        m = method_pattern.search(line)
        if m:
            params = [p.strip() for p in m.group(2).split(',') if p.strip()]
            symbols.append(_create_symbol(m.group(1), "function", i+1, params=params, docstring=_extract_jsdoc(lines, i)))
            continue
            
    return symbols

def parse_csharp(source: str) -> List[Dict[str, Any]]:
    symbols = []
    lines = source.split('\n')
    
    class_pattern = re.compile(r'^\s*(?:(?:public|private|protected|internal|static|sealed|abstract|partial)\s+)*class\s+([A-Za-z0-9_]+)')
    interface_pattern = re.compile(r'^\s*(?:(?:public|private|protected|internal|partial)\s+)*interface\s+([A-Za-z0-9_]+)')
    method_pattern = re.compile(r'^\s*(?:(?:public|private|protected|internal|static|virtual|override|abstract|sealed|async|partial)\s+)*[\w\<\>\[\]\?]+\s+([A-Za-z0-9_]+)\s*\((.*?)\)')
    
    for i, line in enumerate(lines):
        m = class_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "class", i+1, docstring=_extract_jsdoc(lines, i)))
            continue
            
        m = interface_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "interface", i+1, docstring=_extract_jsdoc(lines, i)))
            continue
            
        m = method_pattern.search(line)
        if m:
            # Skip common false positives
            if m.group(1) in ('if', 'for', 'while', 'switch', 'catch', 'return', 'using', 'lock', 'foreach'):
                continue
            params = [p.strip() for p in m.group(2).split(',') if p.strip()]
            symbols.append(_create_symbol(m.group(1), "function", i+1, params=params, docstring=_extract_jsdoc(lines, i)))
            continue
            
    return symbols

def parse_c_cpp(source: str) -> List[Dict[str, Any]]:
    symbols = []
    lines = source.split('\n')
    
    func_pattern = re.compile(r'^\s*(?:(?:inline|static|virtual|explicit|friend)\s+)*[\w\<\>\:\*\&]+\s+([A-Za-z0-9_:]+)\s*\((.*?)\)(?:\s*(?:const|override|final|noexcept))?\s*(?:\{|;)')
    struct_pattern = re.compile(r'^\s*(?:typedef\s+)?struct\s+([A-Za-z0-9_]+)')
    class_pattern = re.compile(r'^\s*class\s+([A-Za-z0-9_]+)')
    
    for i, line in enumerate(lines):
        m = struct_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "struct", i+1, docstring=_extract_jsdoc(lines, i)))
            continue
            
        m = class_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "class", i+1, docstring=_extract_jsdoc(lines, i)))
            continue
            
        m = func_pattern.search(line)
        if m:
            # Skip common false positives
            if m.group(1) in ('if', 'for', 'while', 'switch', 'catch', 'return'):
                continue
            params = [p.strip() for p in m.group(2).split(',') if p.strip()]
            symbols.append(_create_symbol(m.group(1), "function", i+1, params=params, docstring=_extract_jsdoc(lines, i)))
            continue
            
    return symbols

def parse_html(source: str) -> List[Dict[str, Any]]:
    symbols = []
    lines = source.split('\n')
    
    id_pattern = re.compile(r'id=["\']([A-Za-z0-9_-]+)["\']')
    class_pattern = re.compile(r'class=["\']([A-Za-z0-9_\-\s]+)["\']')
    script_pattern = re.compile(r'<\s*script(?:\s+[^>]*)?>')
    style_pattern = re.compile(r'<\s*style(?:\s+[^>]*)?>')
    
    for i, line in enumerate(lines):
        m = id_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "html_id", i+1))
            
        m = class_pattern.search(line)
        if m:
            # First class only to avoid bloat
            first_class = m.group(1).split()[0] if m.group(1) else ""
            if first_class:
                symbols.append(_create_symbol(first_class, "html_class", i+1))
                
        if script_pattern.search(line):
            symbols.append(_create_symbol("script_block", "script", i+1))
        
        if style_pattern.search(line):
            symbols.append(_create_symbol("style_block", "style", i+1))
            
    return symbols

def parse_css(source: str) -> List[Dict[str, Any]]:
    symbols = []
    lines = source.split('\n')
    
    selector_pattern = re.compile(r'^([\.#][A-Za-z0-9_\-\s\:,]+)\s*\{')
    var_pattern = re.compile(r'^\s*(--[A-Za-z0-9_\-]+)\s*:')
    
    for i, line in enumerate(lines):
        m = selector_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1).strip(), "css_selector", i+1))
            continue
            
        m = var_pattern.search(line)
        if m:
            symbols.append(_create_symbol(m.group(1), "css_variable", i+1))
            
    return symbols

def parse_config(source: str, ext: str) -> List[Dict[str, Any]]:
    symbols = []
    lines = source.split('\n')
    
    if ext == '.json':
        # Top level keys basic heuristic
        json_key_pattern = re.compile(r'^\s*"([A-Za-z0-9_\-]+)"\s*:')
        for i, line in enumerate(lines):
            m = json_key_pattern.search(line)
            if m:
                symbols.append(_create_symbol(m.group(1), "config_key", i+1))
                
    elif ext in ('.yaml', '.yml'):
        yaml_key_pattern = re.compile(r'^([A-Za-z0-9_\-]+)\s*:')
        for i, line in enumerate(lines):
            m = yaml_key_pattern.search(line)
            if m:
                symbols.append(_create_symbol(m.group(1), "config_key", i+1))
                
    return symbols

def parse_markdown(source: str) -> List[Dict[str, Any]]:
    symbols = []
    lines = source.split('\n')
    
    header_pattern = re.compile(r'^(#{1,3})\s+(.+)$')
    
    for i, line in enumerate(lines):
        m = header_pattern.search(line)
        if m:
            level = len(m.group(1))
            symbols.append(_create_symbol(m.group(2).strip(), f"h{level}_header", i+1))
            
    return symbols

def dispatch_parser(source: str, file_path: str, extension: str) -> List[Dict[str, Any]]:
    """Dispatch to the correct parser based on file extension."""
    ext = extension.lower()
    
    try:
        if ext in ('.js', '.jsx'):
            return parse_javascript_typescript(source, is_ts=False)
        elif ext in ('.ts', '.tsx'):
            return parse_javascript_typescript(source, is_ts=True)
        elif ext == '.go':
            return parse_go(source)
        elif ext == '.rs':
            return parse_rust(source)
        elif ext == '.java':
            return parse_java(source)
        elif ext == '.cs':
            return parse_csharp(source)
        elif ext in ('.c', '.cpp', '.h', '.hpp'):
            return parse_c_cpp(source)
        elif ext in ('.html', '.htm'):
            return parse_html(source)
        elif ext in ('.css', '.scss', '.less'):
            return parse_css(source)
        elif ext in ('.json', '.yaml', '.yml'):
            return parse_config(source, ext)
        elif ext == '.md':
            return parse_markdown(source)
    except Exception as e:
        print(f"    [WARN] Regex parse error in {file_path}: {e}")
        
    return []
