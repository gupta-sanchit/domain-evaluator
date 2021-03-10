from crontab import CronTab

cron = CronTab(user=True)
job = cron.new(command='python -m DomainFetcher.script')
job.minute.every(1)

cron.write()
