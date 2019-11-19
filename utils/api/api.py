class APIError(Exception):
    def __init__(self, msg, err=None):
        self.err = err
        self.msg = msg
        super(err, msg)
