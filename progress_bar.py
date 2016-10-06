def progress_bar(fraction):
    """Return a nice progress bar string, that you can print with

    print(progress_bar((i + 1) / n), end="\r")

    """
    return '\r[{0:50s}] {1:.1%}'.format('#' * int((fraction * 50)), fraction)
