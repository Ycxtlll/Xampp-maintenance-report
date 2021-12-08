import xlwt
import datetime
import time
import tools.get_pids as GetPids
from tools.read_os_info import OsInfo
import tools.backups as Backups


class ProcessInfo:
    _thread_number = 0
    _cpu_usage = 0
    _memory_usage = 0
    _disk_io_read = 0
    _disk_io_write = 0

    def get_thread_number(self):
        return self._thread_number

    def get_cpu_usage(self):
        return self._cpu_usage

    def get_memory_usage(self):
        return self._memory_usage

    def get_disk_io_read(self):
        return self._disk_io_read

    def get_disk_io_write(self):
        return self._disk_io_write

    def to_string(self):
        print("threads", self._thread_number, end=", ")
        print("cpu usage", self._cpu_usage, end=", ")
        print("memory usage", self._memory_usage, end=", ")
        print("disk usage read", self._disk_io_read, end=", ")
        print("disk usage write", self._disk_io_write)


def get_sysinfo():
    sysinfo = []
    osInfo = OsInfo()
    sysinfo.append(osInfo.get_threads())
    sysinfo.append(osInfo.get_cpu_usage())
    sysinfo.append(osInfo.get_memory_usage())
    sysinfo.append("{:.0f}".format(
        osInfo.get_disk_io_read() + osInfo.get_disk_io_write()))
    sysinfo.append(osInfo.get_net_io())
    return sysinfo


def get_process_info(pid):
    process_info = ProcessInfo()
    osInfo = OsInfo(pid)
    process_info._thread_number = osInfo.get_threads()
    process_info._cpu_usage = osInfo.get_cpu_usage()
    process_info._memory_usage = osInfo.get_memory_usage()
    process_info._disk_io_read = "{:.0f}".format(osInfo.get_disk_io_read())
    process_info._disk_io_write = "{:.0f}".format(osInfo.get_disk_io_write())
    return process_info


def get_watch_processes():
    watch_processes = {
        "tomcat8080": ProcessInfo(),
        "tomcat8081": ProcessInfo(),
        "tomcat8082": ProcessInfo(),
        "mysql": ProcessInfo(),
        "apache": ProcessInfo(),
        "memcached": ProcessInfo(),
        "zookeeper": ProcessInfo(),
        "java": ProcessInfo(),
    }
    processes = GetPids.get_pids()
    for process in processes:
        pid = processes.get(process).get_pid()
        if pid is not None:
            watch_processes[process] = get_process_info(pid)
    return watch_processes


class ToExcel:
    GREEN = "green"
    GRAY = "gray"

    def __init__(self):
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.worksheet = self.workbook.add_sheet(
            str(datetime.date.today()), cell_overwrite_ok=True)

    def get_style(self, bg=None, title=False):
        borders = xlwt.Borders()
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        font = xlwt.Font()
        font.height = 20*11
        font.name = '等线'
        if title:
            font.bold = True
        style = xlwt.XFStyle()
        style.borders = borders
        style.font = font
        if bg is None:
            return style
        else:
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN
            if bg == self.GREEN:
                pattern.pattern_fore_colour = 42
            elif bg == self.GRAY:
                pattern.pattern_fore_colour = 22
            else:
                return style
            style.pattern = pattern
            return style

    def set_style_al(self, style):
        al = xlwt.Alignment()
        al.horz = 2
        al.vert = 1
        style.alignment = al
        return style

    def xl_write(self, row, col, contains, style=None):
        if style is not None:
            if col == 0 or row == 3:
                style = self.get_style(style, True)
            else:
                style = self.get_style(style)
        else:
            style = self.get_style()
        if col != 0:
            style = self.set_style_al(style)
        self.worksheet.write(row, col, contains, style)

    def pre_write(self):
        for i in range(0, 21):
            for j in range(0, 10):
                self.xl_write(i, j, "")
        for i in range(11, 14):
            for j in range(2, 10):
                self.xl_write(i, j, "-")
        self.worksheet.col(0).width = 256*20
        for i in range(1, 10):
            self.worksheet.col(i).width = 256*15
        self.worksheet.write_merge(
            20, 20, 0, 9, "较上次维护的变化与问题：", self.get_style())
        style = xlwt.easyxf('font:height 720')
        self.worksheet.row(20).set_style(style)
        self.xl_write(0, 0, "运维时间", self.GRAY)
        self.xl_write(0, 1, str(time.strftime("%H:%M")))
        self.xl_write(1, 0, "运维人", self.GRAY)
        self.xl_write(1, 1, "Will")
        self.xl_write(3, 0, "", self.GRAY)
        self.xl_write(4, 0, "线程数", self.GRAY)
        self.xl_write(5, 0, "CPU使用率(%)", self.GRAY)
        self.xl_write(6, 0, "内存占用(M)", self.GRAY)
        self.xl_write(7, 0, "磁盘读(K/s)", self.GRAY)
        self.xl_write(8, 0, "磁盘写(K/s)", self.GRAY)
        self.xl_write(9, 0, "网络发送(K/s)", self.GRAY)
        self.xl_write(10, 0, "网络接收(K/s)", self.GRAY)
        self.xl_write(11, 0, "磁盘剩余(G)", self.GRAY)
        self.xl_write(12, 0, "系统需要更新", self.GRAY)
        self.xl_write(12, 1, "否", self.GREEN)
        self.xl_write(13, 0, "备份数据库大小(M)", self.GRAY)
        self.xl_write(14, 0, "日志分析", self.GRAY)
        self.xl_write(14, 1, "正常", self.GREEN)

    def sys_write(self):
        watch_system = get_sysinfo()
        self.xl_write(3, 1, "系统", self.GRAY)
        self.xl_write(4, 1, watch_system[0], self.GREEN)
        self.xl_write(5, 1, watch_system[1], self.GREEN)
        self.xl_write(6, 1, watch_system[2], self.GREEN)
        style = self.set_style_al(self.get_style(self.GREEN))
        self.worksheet.write_merge(
            7, 8, 1, 1, watch_system[3], style)
        self.worksheet.write_merge(
            9, 10, 1, 1, watch_system[4], style)

    def process_write(self):
        watch_processes = get_watch_processes()
        col = 2
        for watch_process in watch_processes:
            self.xl_write(3, col, watch_process, self.GRAY)
            self.xl_write(4, col, watch_processes.get(
                watch_process).get_thread_number(), self.GREEN)
            self.xl_write(5, col, watch_processes.get(
                watch_process).get_cpu_usage(), self.GREEN)
            self.xl_write(6, col, watch_processes.get(
                watch_process).get_memory_usage(), self.GREEN)
            self.xl_write(7, col, watch_processes.get(
                watch_process).get_disk_io_read(), self.GREEN)
            self.xl_write(8, col, watch_processes.get(
                watch_process).get_disk_io_write(), self.GREEN)
            self.xl_write(9, col, 0, self.GREEN)
            self.xl_write(10, col, 0, self.GREEN)
            print(watch_process, end=": ")
            watch_processes.get(watch_process).to_string()
            col += 1

    def backup(self):
        size = Backups.backup()
        self.xl_write(13, 1, size, self.GREEN)
        freespace = "{:.0f} GB".format(Backups.get_free_space())
        print("Backup finish, free space:", freespace)
        self.xl_write(11, 1, freespace, self.GREEN)

    def print_to_excel(self):
        self.pre_write()
        self.sys_write()
        self.process_write()
        # self.backup()
        path = "C:/bitanswer/诚谦运维报告.xls"
        print("save to:", path)
        self.workbook.save(path)


if __name__ == '__main__':
    # ToExcel().print_to_excel()
    # input('Press <Enter>')
    print("hello world")
