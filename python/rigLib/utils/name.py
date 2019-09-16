"""
name utils @utils

utilities to work with names and strings
"""

def remove_suffix(name):
    """
    remove suffix from given name string
    
    @param name: str, given name string to process
    @return: str, name without suffix
    """
    
    edits = name.split('_')
    if len(edits) < 2:
        return name
    
    suffix = '_' + edits[-1]
    name_no_suffix = name[:-len(suffix)]
    
    return name_no_suffix

