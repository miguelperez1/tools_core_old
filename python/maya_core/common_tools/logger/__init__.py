class Logger(object):
    def __init__(self):
        self.status = True

    def info(self, message):
        out_message = None
        if self.status:
            out_message = "# Info:  " + ("-" * 15) + "  " + message
            print(out_message)

        return out_message

    def warning(self, message):
        out_message = None

        if self.status:
            out_message = "# Warning:  " + ("-" * 15) + "  " + message
            print out_message

        return out_message

    def error(self, message):
        out_message = "# Error:  " + ("-" * 15) + "  " + message
        print(out_message)
        return out_message

    def result(self, message):
        prev_status = self.status
        self.status = True
        out_message = "# Result:  " + ("-" * 15) + "  " + message
        print(out_message)
        self.status = prev_status
        return out_message
