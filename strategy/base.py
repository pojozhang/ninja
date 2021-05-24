from transitions import Machine


def run(strategy):
    strategy.run()
    while strategy.context.active and len(strategy.nextTrigger) > 0:
        strategy.run_next()


class Strategy:

    def __init__(self, context, initial_state='init', states=[], transitions=[]):
        self.context = context
        self.args = context.args
        self.stateMachine = Machine(model=self, states=states, transitions=transitions,
                                    initial=initial_state, before_state_change=self.before_state_change,
                                    after_state_change=self.after_state_change)
        self.nextTrigger = []

    def next(self, trigger, *args, **kwargs):
        if len(self.nextTrigger) > 0:
            raise RuntimeError('can not set next state')
        self.nextTrigger = [(trigger, args, kwargs)]

    def run_next(self):
        trigger, args, kwargs = self.nextTrigger[0]
        self.nextTrigger = []
        self.trigger(trigger, *args, **kwargs)

    def run(self):
        pass

    def before_state_change(self, *args, **kwargs):
        self.context.before_state_change(state=self.state)

    def after_state_change(self, *args, **kwargs):
        self.context.after_state_change(state=self.state)
