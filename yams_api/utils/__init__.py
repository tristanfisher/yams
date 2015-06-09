import os

def _mkdir(_dir):
    if os.path.isdir(_dir): pass
    elif os.path.isfile(_dir):
        raise OSError("%s exists as a regular file." % _dir)
    else:
        parent, directory = os.path.split(_dir)
        if parent and not os.path.isdir(parent): _mkdir(parent)
        if directory: os.mkdir(_dir)