class Strategy:

    def __init__(self, context):
        self.context = context
        self.args = context.args
        self.nextState = None

    def next(self, *args, **kwargs):
        self.nextState(*args, **kwargs)

    def goto(self, state):
        self.nextState = state

    def run(self):
        pass

    def test(self):
        pass

    def before_state_change(self, *args, **kwargs):
        self.context.before_state_change(state=self.state)

    def after_state_change(self, *args, **kwargs):
        self.context.after_state_change(state=self.state)
