import shutil
import os
import time
import platform
import ctypes

Path = r"C:\xampp\mysql\data"
backPath = os.path.join(r"C:\back", str(
    time.strftime("%Y-%m-%d") + r"\bit_e3"))


def backup():
    shutil.copytree(Path, backPath)
    return "{:.0f} MB".format(__get_size(backPath)/1024/1024)


def __get_size(file_path):
    size = 0
    for root, dirs, files in os.walk(file_path):
        size += sum([os.path.getsize(os.path.join(root, name))
                    for name in files])
    return size


def get_free_space(folder=r"C:/"):
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value / 2**30


def _test():
    print("backup test", backup())


if __name__ == '__main__':
    print(get_free_space())
