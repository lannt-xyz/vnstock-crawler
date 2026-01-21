from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from app.scheduler.jobs import sync_market_data, sync_macro_data
from vnstock import Vnstock
from app.logger import logger

def get_symbols():
    # Get list of symbols from market listing
    market = Vnstock().market()
    listings = market.listing()
    return [item.get('symbol') for item in listings if item.get('symbol')]

def schedule_jobs():
    logger.info("Starting scheduler...")
    scheduler = BlockingScheduler()

    # Sync market data daily at 9 AM
    scheduler.add_job(sync_market_data, CronTrigger(hour=9, minute=0))

    # Sync macro data daily at 8 AM
    scheduler.add_job(sync_macro_data, CronTrigger(hour=8, minute=0))

    # Get symbols and schedule company-specific jobs
    symbols = get_symbols()
    for symbol in symbols[:10]:  # Limit to first 10 for demo, remove limit in production
        # Sync company data weekly on Monday at 10 AM
        scheduler.add_job(lambda sym=symbol: sync_company_data(sym), CronTrigger(day_of_week='mon', hour=10, minute=0))
        # Sync financial data weekly on Tuesday at 10 AM
        scheduler.add_job(lambda sym=symbol: sync_financial_data(sym), CronTrigger(day_of_week='tue', hour=10, minute=0))
        # Sync trading data daily at 11 AM
        scheduler.add_job(lambda sym=symbol: sync_trading_data(sym), CronTrigger(hour=11, minute=0))
        # Sync news and events daily at 12 PM
        scheduler.add_job(lambda sym=symbol: sync_news_data(sym), CronTrigger(hour=12, minute=0))
        scheduler.add_job(lambda sym=symbol: sync_event_data(sym), CronTrigger(hour=12, minute=30))

    logger.info("Scheduler started. Waiting for jobs...")
    scheduler.start()

if __name__ == "__main__":
    schedule_jobs()