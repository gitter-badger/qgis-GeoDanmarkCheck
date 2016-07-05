class ProgressReporter(object):
    def __init__(self):
        self.taskname = None
        self.tasksize = 0
        self.taskcompleted = 0
        self.taskcompletedpercentage = 0
        self.reportevery = 1
        self._nextreportat = 0

    def begintask(self, taskname, tasksize):
        self.taskname = taskname
        self.tasksize = tasksize
        self.reportevery = tasksize / 50.0
        self._nextreportat = 0
        self.completed(0)

    def completed(self, completed):
        self.taskcompleted = completed
        if completed >= self._nextreportat:
            self._report()
            self._nextreportat = min(self.tasksize, completed + self.reportevery)

    def completed_one(self):
        self.completed(self.taskcompleted + 1)

    def _report(self, force = False):
        # Better ways of reporting!
        print "{0} {1}% complete".format(self.taskname, 100.0 * self.taskcompleted / self.tasksize)
