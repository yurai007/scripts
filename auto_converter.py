#!/usr/bin/python3

import os
from string import Template
from collections import deque
import pyparsing as pp
import sys

"""
ref: https://en.cppreference.com/w/cpp/language/declarations

Assume that source file is well-formed C/C++. Brief grammar description:

1. initialized simple declaration = decl-specifier-seq init-declarator-list;
2. decl-specifier-seq = [inline, constexpr, constinit, static, thread_local, extern] type-specifier-seq
3. type-specifier-seq = cv qualifiers [class, struct, enum, union] type_name
4. init-declarator-list =  {declarator initializer,}^N (list)
5. declarator = [*name, &name, &&name, name[N]]
6. initializer is in form:

    = expression 	        (2)

Parsing C++ is hard. Therefore to not mess things up we use (very) conservative approach with
some extra steps like:
    * bailing out when expression is nullptr and declarator is pointer
    * bailing out when declarator is array
    * not supporting aggregate initialization/designated initializers expressions
    * tracking comments and (simple) scopes: https://en.cppreference.com/w/cpp/language/auto

You can take a look on test.cc to get idea.

TODO: warn when auto deduces undesired type e.g
      when type_name is arithmetic and expression is simple literal without suffix
"""
debug = False
report_transformed = True

def fprintln(f, *args):
    for arg in args:
        f.write(arg)
    f.write('\n')

def log_error(function, cpp_line, pe):
    if debug:
       print(f"  {function}: {cpp_line}  Error: {pe}")
    return False

def parse_simple_list_item(cpp_line):
    identifier = pp.Word(pp.alphanums)
    forbidden_nulls = pp.oneOf("nullptr")
    expression = ~forbidden_nulls + pp.OneOrMore(pp.Word(pp.printables, excludeChars="{}"))
    init_decl_list = identifier + "=" + expression("expression")
    try:
        presult = init_decl_list.parseString(cpp_line)
    except pp.ParseException as pe:
        return log_error("parse_simple_list_item", cpp_line, pe)
    return True

def parse_one_init_declarator_brackets(cpp_line):
    identifier = pp.Word(pp.alphanums)
    expression = pp.OneOrMore(pp.Word(pp.printables, excludeChars=";{}"))
    init_decl_list = identifier + "=" + pp.Word(pp.alphas, pp.printables, excludeChars=";()") \
        + "(" + expression  + ";"
    try:
        presult = init_decl_list.parseString(cpp_line)
    except pp.ParseException as pe:
        return log_error("parse_one_init_declarator_brackets", cpp_line, pe)
    return True

def parse_init_declarator_list(cpp_line):
    proper_list = True
    splitted = cpp_line.split(', ')
    if not splitted[-1].endswith(';'):
        proper_list = False
    else:
        for str in splitted:
            if not parse_simple_list_item(str):
                proper_list = False
    return proper_list or parse_one_init_declarator_brackets(cpp_line)

def parse_declaration(cpp_line):
    identifier = pp.Word(pp.alphanums)
    number = pp.pyparsing_common.signed_integer
    forbidden_type_names = pp.oneOf("using")
    type_name = ~forbidden_type_names + pp.Word(pp.alphas, pp.printables, excludeChars="*&")("type_name")
    cv = "const volatile "
    type = "class struct enum union "
    rest = "inline constexpr constinit static thread_local extern"
    cvtype = pp.oneOf(cv + type + rest)
    type_specifier_seq = (pp.OneOrMore(cvtype) + type_name) | type_name
    decl_prefix = pp.oneOf("* & &&")
    init_declarator_list = pp.OneOrMore(pp.Word(pp.printables))
    declaration = type_specifier_seq + pp.Optional(decl_prefix("decl_prefix")) + \
       init_declarator_list().addCondition(lambda toks: parse_init_declarator_list(' '.join(toks)))
    declaration.ignore(pp.cStyleComment)
    declaration.ignore(pp.cppStyleComment)
    try:
        presult = declaration.parseString(cpp_line)
        type_name = presult["type_name"]
        return (True, type_name)
    except pp.ParseException as pe:
        return log_error("parse_declaration", cpp_line, pe)

def parse_for_init():
    init_statement = pp.OneOrMore(pp.Word(pp.printables, excludeChars=";")).setParseAction(' '.join) \
      + pp.FollowedBy(';') + pp.Suppress(';')
    return init_statement("declaration")

class_open = 0
class_maybe_open = False
function_or_namespace_open = False

# just simple tracking with no sophisticated parsing
def track_scopes(cpp_line):
    # handle class
    global class_open, class_maybe_open, function_or_namespace_open
    class_or_struct = False
    if cpp_line.lstrip().startswith("class") or cpp_line.lstrip().startswith("struct"):
        class_or_struct = True
        if "{" in cpp_line and not "}" in cpp_line:
            class_open += 1
        elif not "{" in cpp_line and not ";" in cpp_line:
             class_maybe_open = True
    if "}" in cpp_line and ";" in cpp_line and class_open > 0:
         class_open -= 1
    # handle function
    if "{" in cpp_line and not "}" in cpp_line:
        if not class_or_struct and not class_maybe_open:
            function_or_namespace_open = True
        if class_maybe_open:
            class_maybe_open = False
            class_open += 1
    if cpp_line.lstrip().startswith("}") and not ";" in cpp_line:
        function_or_namespace_open = False

    return True if class_open == 0 else function_or_namespace_open

def parse(cpp_line):
   if not track_scopes(cpp_line):
       return False
   if cpp_line.lstrip().startswith("for"):
       try:
           for_loop = pp.oneOf("for") + "(" + parse_for_init()
           presult = for_loop.parseString(cpp_line)["declaration"]
           return parse_declaration(presult[0] + ';')
       except pp.ParseException as pe:
           return False
   return parse_declaration(cpp_line)

def track_comments(raw_line):
    if raw_line.startswith("/*"):
        track_comments.multiline_comment = True
    if raw_line.startswith("*/") or raw_line.endswith("*/"):
        track_comments.multiline_comment = False
    return not raw_line.startswith("//") and not track_comments.multiline_comment

track_comments.multiline_comment = False

def main():
    if len(sys.argv) != 2:
        return
    filename = sys.argv[1]
    cin = open(filename, 'r')
    lines = deque([line.rstrip('\n') for line in cin])
    cin.close()
    cout = open(filename + ".out", 'w')
    while lines:
        transformed = False
        raw_line = lines.popleft()
        if track_comments(raw_line):
            transformed = parse(raw_line)
            if transformed:
                raw_line = raw_line.replace(transformed[1], 'auto', 1)
            if report_transformed and transformed:
                print(f"{transformed}       {raw_line}")
        fprintln(cout, raw_line)
    cout.close()

if __name__ == "__main__":
    main()
