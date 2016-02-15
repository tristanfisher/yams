from re import match, escape
# if localhost or localhost.localdomain or 127.0.0.1
localhost_domains = [
    "localhost",
    "localhost.localdomain",
    "127.0.0.1",
    "::1"
]

def regex_validate(input_data, match_pattern='^[\w_]+$'):
    """

    :param input_data: data to validate against a pattern
    :param match_pattern:  pattern to match data against
    :return: True if matches, else False
    """
    input_data = escape(input_data)
    if match(match_pattern, input_data):
        return True
    else:
        return False


user_valid_function_table = {
    're': regex_validate
    # could use a partial here and/or bind this to something like LDAP
}


# send_email should be "pluggable" from the config for flexibility and credentials.
# e.g. the config should point to this default stub and the NotImplementedError should be caught and wrapped in an HTTP
# 40x "email feature not configured...etc"
def send_email(address, subject, body, local_user=False):

    if local_user:
        # e.g. "root" has been passed in
        user_valid = user_valid_function_table['re'](address)
        if not user_valid:
            raise ValueError("User does not seem to be in the valid format for a local username: %s" % address)
    else:
        if not is_maybe_valid_email(address):
            raise ValueError("E-mail address does not seem to be correct.  Please check your input.  <%s>" % address)

    address = str(address).strip().split("@")

    # local machine is the domain portion?
    if localhost_domains in address[1]:
        print("# --- Local e-mail --- # \n"
              "Subject: %s \n"
              "Body: %s\n"
              "# --- #" % (subject, body))
    else:
        raise NotImplementedError

def is_maybe_valid_email(address):
    """Simply check that we have "something@domain"

    :param address: candidate address to test
    :return: True if it's possibly an e-mail address. return False otherwise.
    """

    address = str(address).strip().split("@")
    should_error = False

    # prevents missing @ or x@y@google.com
    if len(address) == 2:
        # check there's something on either end of @
        if not len(address[0]):
            should_error = True
        if not len(address[1]):
            should_error = True
    else:
        should_error = True

    return should_error
