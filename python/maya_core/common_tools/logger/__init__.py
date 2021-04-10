class Logger(object):
    def __init__(self):
        self.status = True

    def info(self, message):
        if self.status:
            print "# Info:  " + ("-" * 15) + "  " + message

    def warning(self, message):
        if self.status:
            print "# Warning:  " + ("-" * 15) + "  " + message

    def error(self, message):
        if self.status:
            print "# Error:  " + ("-" * 15) + "  " + message

    def result(self, message):
        prev_status = self.status
        self.status = True
        print "# Result:  " + ("-" * 15) + "  " + message
        self.status = prev_status
