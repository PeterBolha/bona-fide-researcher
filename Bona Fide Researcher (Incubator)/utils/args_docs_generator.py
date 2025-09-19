from argparse import ArgumentParser

from verify_eduperson import get_args_parser


def parser_to_markdown(parser: ArgumentParser) -> str:
    """
    Generates an ASCII table from the given parser containing the arguments,
    their required status and their descriptions. Can be embedded in a
    Markdown doc.
    :param parser: Parser to document
    :return: formatted ASCII table with the arguments documentation
    """
    rows = {"argument": [], "required": [], "desc": []}

    for action in parser._actions:
        if action.option_strings:  # skip positional
            arg = ", ".join(action.option_strings)

            required = "Yes" if action.required else "No"

            desc = action.help or ""

            rows["argument"].append(arg)
            rows["required"].append(required)
            rows["desc"].append(desc)

    ARG_HEADER = "Argument"
    arg_max_len = len(max(rows["argument"] + [ARG_HEADER], key=len))
    arg_padding = " " * (arg_max_len - len(ARG_HEADER))
    arg_delimiter = "-" * len(ARG_HEADER + arg_padding)

    REQUIRED_HEADER = "Required"
    required_max_len = len(max(rows["required"] + [REQUIRED_HEADER], key=len))
    required_padding = " " * (required_max_len - len(REQUIRED_HEADER))
    required_delimiter = "-" * len(REQUIRED_HEADER + required_padding)

    DESC_HEADER = "Description"
    desc_max_len = len(max(rows["desc"] + ["Description"], key=len))
    desc_padding = " " * (desc_max_len - len(DESC_HEADER))
    desc_delimiter = "-" * len(DESC_HEADER + desc_padding)

    delimiter_row = (f"|-{arg_delimiter}-|-{required_delimiter}-|"
                 f"-{desc_delimiter}-|")
    formatted_rows = [delimiter_row, f"| {ARG_HEADER + arg_padding} |"
                      f" {REQUIRED_HEADER + required_padding} | "
                      f"{DESC_HEADER + desc_padding} |", delimiter_row]


    for i in range(len(rows["argument"])):
        arg_row_padding = " " * (arg_max_len - len(rows['argument'][i]))
        required_row_padding = " " * (required_max_len - len(rows['required'][
                                                                i]))
        desc_row_padding = " " * (desc_max_len - len(rows['desc'][i]))

        formatted_rows.append(f"| {rows['argument'][i] + arg_row_padding} |"
                              f" {rows['required'][i] + required_row_padding} | "
                              f"{rows['desc'][i] + desc_row_padding} |")

    formatted_rows.append(delimiter_row)
    return "\n".join(formatted_rows)


def print_verify_eduperson_args_docs():
    parser = get_args_parser()
    print(parser_to_markdown(parser))


print_verify_eduperson_args_docs()
