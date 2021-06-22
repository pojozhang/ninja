from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger


class Strategy:

    def __init__(self, context):
        self.context = context
        self.cron = context.cron
        self.args = context.args
        self.nextState = None
        self.scheduler = BlockingScheduler(job_defaults={'coalesce': True})

    def trigger(self, *args, **kwargs):
        self.nextState(*args, **kwargs)

    def goto(self, state):
        self.nextState = state

    def start(self):
        if self.cron == 'forever':
            while self.context.active:
                self.run()
            return
        self.scheduler.add_job(self.run, self.cron_trigger())
        self.scheduler.start()

    def cron_trigger(self):
        values = self.cron.split(' ', -1)
        return CronTrigger(second=values[0], minute=values[1], hour=values[2], day=values[3], month=values[4],
                           day_of_week=values[5])

    def run(self):
        pass

    def test(self):
        pass
