from sys import stderr

def debug(msg, opts):
    """
    Debug message
    """
    if opts.verbose:
        print("DEBUG: {}.".format(msg), file=stderr)

def info(msg, opts):
    """
    Info message
    """
    if opts.verbose:
        print(msg, file=stderr)