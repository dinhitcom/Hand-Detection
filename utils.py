import os
import shutil
import stat

def clean_if_exists(path):
    if os.path.exists(path):
        os.chmod(path, stat.S_IWRITE)
        shutil.rmtree(path)
        return 0
    return -1


def mkdir_if_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)
        return 0
    return -1
