import re

BASIC_EMAIL_REGEX = r"(^.+@.+\..+$)"
BASIC_EMAIL_REGEX_COMPILED = re.compile(BASIC_EMAIL_REGEX)


def check_email_format(email_addr: str):
    return BASIC_EMAIL_REGEX_COMPILED.match(email_addr)
