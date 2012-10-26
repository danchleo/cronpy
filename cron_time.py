# format
# day hour minute second cmd
#
# time format
#   * or */2 or 2
#   * - run direct
#   */2 - run at every 2 (days, hours, minutes, seconds) 
#   2 - run at 2 (day, hour, minute, second)
#
# sample: * * * */5 gedit, means run gedit every 5 seconds
#         * * * 5 gedit, means run gedit at 5 second in every minutes, such as run at 10:23:05 and 10:24:05, and so on

import os,sys,time,threading,signal,datetime,subprocess

base_path = os.path.dirname(__file__)
task_file = os.path.join(base_path, 'cron.txt')

tasks = []

f = open(task_file, 'rb')

while 1:
    c = f.readline()
    if c == '':
        break;
    else:
        c = c.replace("\n", '')
        if c != '':
            print 'tasks: %s' % c
            tasks.append(c)

f.close()

if len(tasks) == 0:
    print 'empty tasks'
    sys.exit(0)

# tasks = ['* * * */5 Z:\\test.bat']
run_tasks = {}

def signal_handler(signal, frame):
    print 'shutdown'
    for key in run_tasks:
        run_tasks[key].stop()
        run_tasks[key].join()

    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class Task(threading.Thread):
    def __init__(self, cron_str):
        self.compile(cron_str)
        self.is_stop = False
        self.last_run = None
        super(Task, self).__init__(name=self.thread_name)

    def compile(self, cron_str):
        configs = cron_str.split(' ')
        if len(configs) != 5 or configs[4] == '':
            raise CronException('config error: %s' % cron_str)

        self.day = configs[0]
        self.hour = configs[1]
        self.minute = configs[2]
        self.second = configs[3]
        self.cmd = configs[4]
        self.thread_name = self.cmd


    def run(self):
        while not self.is_stop:
            self.run_task()
            time.sleep(1)

    def run_task(self):
        current_date = datetime.datetime.now()
        current_day = int(datetime.datetime.now().strftime('%d'))
        current_hour = int(datetime.datetime.now().strftime('%H'))
        current_minute = int(datetime.datetime.now().strftime('%M'))
        current_second = int(datetime.datetime.now().strftime('%S'))

        if self.day != '*':
            day = self.day.split('/')
            if len(day) == 1:
                day = int(day[0])
                if day != current_day:
                    return False

            elif len(day) == 2:
                if day[0] == '*':
                    if self.last_run is not None and (current_date - self.last_run).days < int(day[1]):
                        return False

                else:
                    return False

        if self.hour != '*':
            hour = self.hour.split('/')
            if len(hour) == 1:
                hour = int(hour[0])
                if hour != current_hour:
                    return False

            elif len(hour) == 2:
                if hour[0] == '*':
                    if self.last_run is not None:
                        deldate = current_date - self.last_run
                        if (deldate.days*24*3600 + deldate.seconds) < int(hour[1])*3600:
                            return False

                else:
                    return False

        if self.minute != '*':
            minute = self.minute.split('/')
            if len(minute) == 1:
                minute = int(minute[0])
                if minute != current_minute:
                    return False

            elif len(minute) == 2:
                if minute[0] == '*':
                    if self.last_run is not None:
                        deldate = current_date - self.last_run
                        if (deldate.days*24*3600 + deldate.seconds) < int(minute[1])*60:
                            return False

                else:
                    return False

        if self.second != '*':
            second = self.second.split('/')
            if len(second) == 1:
                second = int(second[0])
                if second != current_second:
                    return False

            elif len(second) == 2:
                if second[0] == '*':
                    if self.last_run is not None:
                        deldate = current_date - self.last_run
                        if (deldate.days*24*3600 + deldate.seconds) < int(second[1]):
                            return False

                else:
                    return False

        print 'start: %s at %s' % (self.cmd, current_date.strftime('%Y-%m-%d %H:%M:%S'))
        p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
        output, outerror = p.communicate()
        p.wait()
        self.last_run = datetime.datetime.now()

    def stop(self):
        self.is_stop = True

class CronException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.msg = message

    def __str__(self):
        return repr(self.msg)


for task in tasks:
    run_tasks[task] = Task(task)
    run_tasks[task].setDaemon(True)
    run_tasks[task].start()

while 1:
    time.sleep(1)

