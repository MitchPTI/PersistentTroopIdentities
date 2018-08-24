import re

def file_print_lines_with_op(filename, *ops):
    with open(filename, "r+") as fh:
        lines = fh.readlines()
    
    for line_no, line in enumerate(lines):
        if re.match("^\s*\(({})".format("|".join(ops)), line):
            print "{} line {}: {}".format(filename, line_no, line.strip())

module_types_with_code = (
    "dialogs"
    , "game_menus"
    , "mission_templates"
    , "presentations"
    , "scripts"
    , "simple_triggers"
    , "triggers"
)

operations_to_replace = (
    "party_add_members"
    , "party_force_add_members"
    #, "party_add_template" # This is very unlikely to be used on either player party or player-owned garrison
    , "remove_troops_from_companions"
    , "party_remove_members"
    , "party_clear"
)

print "Lines containing operations that may potentially need to be replaced:\n"
for module_type in module_types_with_code:
    filename = "module_{}.py".format(module_type)
    file_print_lines_with_op(filename, *operations_to_replace)
