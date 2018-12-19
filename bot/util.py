import dateparser
import numparser

def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def parse_date(text):
    return dateparser.parse(text, languages=['ru', 'en'])

def parse_amount(text):
    num = numparser.numparser(text)
    if num is None:
        raise ValueError
    else:
        return num