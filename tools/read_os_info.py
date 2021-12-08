import re
import psutil
import time


class OsInfo:
    _times = 30
    _sleep = 1

    def __init__(self, pid=None):
        print("OsInfo is running...")
        print("runtimes:", self._times, "sleep:", self._sleep)
        self._pid = pid
        if pid is None:
            print("Read osInfo of SYSTEM")
            self._process = psutil
        else:
            print("Read osInfo of PROCESS", pid)
            self._process = psutil.Process(pid)

    def changeTimes(self, runtime=None, sleep=None):
        if runtime is not None:
            self._times = runtime
        else:
            self._times = 30
        if sleep is not None:
            self._sleep = sleep
        else:
            self._sleep = 1

    def get_threads(self):
        if self._pid is None:
            return '-'
        else:
            sum = 0
            for i in range(0, self._times):
                time.sleep(self._sleep)
                ts = self._process.num_threads()
                sum += ts
            return "{:.0f}".format(sum / self._times)

    def get_cpu_usage(self):
        self._process.cpu_percent()
        sum = 0
        for i in range(0, self._times):
            time.sleep(self._sleep)
            cp = self._process.cpu_percent()
            sum += cp
        return "{:.2f}%".format(sum / self._times)

    def get_memory_usage(self):
        sum = 0
        if self._pid is None:
            for i in range(0, self._times):
                time.sleep(self._sleep)
                used = self._process.virtual_memory().used
                sum += used
        else:
            for i in range(0, self._times):
                time.sleep(self._sleep)
                used = self._process.memory_info().rss
                sum += used
        return "{:.0f}".format(sum / self._times / 1024 / 1024)

    def get_disk_io_read(self):
        sum = 0
        for i in range(0, self._times):
            pre = self._get_disk_io_helper(0)
            now = self._get_disk_io_helper(0)
            sub_io = now - pre
            sum += sub_io
        return sum / self._times / 1024

    def get_disk_io_write(self):
        sum = 0
        for i in range(0, self._times):
            pre = self._get_disk_io_helper(1)
            now = self._get_disk_io_helper(1)
            sub_io = now - pre
            sum += sub_io
        return sum / self._times / 1024

    def _check_pid_disk(self):
        if self._pid is None:
            return self._process.disk_io_counters()
        else:
            return self._process.io_counters()

    def _get_disk_io_helper(self, type):
        time.sleep(self._sleep / 2)
        disk_io = self._check_pid_disk()
        read = disk_io.read_bytes
        write = disk_io.write_bytes
        if type == 0:
            return read
        if type == 1:
            return write

    # only for system, unsupport process
    def get_net_io(self):
        if self._pid is None:
            sum = 0
            for i in range(0, self._times):
                pre = self._get_net_io_helper()
                now = self._get_net_io_helper()
                sum += (now - pre)
            return "{:.0f}".format(sum / self._times / 1024)
        else:
            print("Isn't support process.")

    def _get_net_io_helper(self):
        time.sleep(self._sleep / 2)
        net = self._process.net_io_counters()
        recv = net.bytes_recv
        sent = net.bytes_sent
        return recv + sent


def _test():
    osInfo = OsInfo()
    print("runtime", osInfo._times, "sleep", osInfo._sleep)
    print("threads", osInfo.get_threads())
    print("cpu_usage", osInfo.get_cpu_usage())
    print("memory_usage", osInfo.get_memory_usage())
    print("disk_io", "{:.0f}KB/s".format(osInfo.get_disk_io_read() +
          osInfo.get_disk_io_write()))


if __name__ == '__main__':
    _test()
