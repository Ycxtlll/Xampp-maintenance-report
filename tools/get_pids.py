import psutil
import pprint


class WatchProcess:
    def __init__(self, name, port, pid):
        self._name = name
        self._port = port
        self._pid = pid

    def get_pid(self):
        return self._pid

    def set_pid(self, pid):
        self._pid = pid


def get_pids():
    _processes = {
        "tomcat8080": WatchProcess(["java", "tomcat"], 8080, 0),
        "tomcat8081": WatchProcess(["java", "tomcat"], 8081, 0),
        "tomcat8082": WatchProcess(["java", "tomcat"], 8082, 0),
        "mysql": WatchProcess(["mysql"], 3306, 0),
        "apache": WatchProcess(["httpd"], 80, 0),
        "memcached": WatchProcess(["memcached"], 11211, 0),
        "zookeeper": WatchProcess(["prunsrv"], 0, 0),
        "java": WatchProcess(["java"], 2181, 0),
    }
    for process in _processes:
        _processes.get(process).set_pid(
            get_process_pid(_processes.get(process)))
    return _processes


def get_process_pid(watchProcess):
    for pid in psutil.pids():
        process = psutil.Process(pid)
        for name in watchProcess._name:
            if name in process.name():
                if name is not "prunsrv":
                    for conn in psutil.Process(pid).connections():
                        if watchProcess._port == conn.laddr.port:
                            return pid
                else:
                    return pid


def _test():
    processes = get_pids()
    for process in processes:
        print(process, processes.get(process).get_pid())


if __name__ == "__main__":
    _test()
