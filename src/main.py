"""Main application entry point."""

import asyncio
import signal
from loguru import logger

from src.config import setup_logging, settings
from src.database import init_database
from src.core import Scheduler


class Application:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.scheduler = None
        self.shutdown_event = asyncio.Event()
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_event.set()
    
    async def run(self):
        """Run the application."""
        # Setup logging
        setup_logging()
        
        logger.info("=" * 60)
        logger.info("Telegram Autoposting Bot - Professional Edition")
        logger.info("=" * 60)
        logger.info(f"Channel: {settings.channel_username}")
        logger.info(f"Check interval: {settings.check_interval_minutes} minutes")
        logger.info(f"Translation: {'Enabled' if settings.enable_translation else 'Disabled'}")
        logger.info(f"Image fetching: {'Enabled' if settings.enable_image_fetching else 'Disabled'}")
        logger.info(f"RSS Feeds: {len(settings.rss_feed_list)}")
        logger.info("=" * 60)
        
        try:
            # Initialize database
            logger.info("Initializing database...")
            await init_database()
            
            # Create and initialize scheduler
            logger.info("Creating scheduler...")
            self.scheduler = Scheduler()
            await self.scheduler.initialize()
            
            # Start scheduler
            logger.success("Application started successfully!")
            logger.info("Press Ctrl+C to stop")
            
            # Run scheduler
            scheduler_task = asyncio.create_task(self.scheduler.start())
            shutdown_task = asyncio.create_task(self.shutdown_event.wait())
            
            # Wait for either scheduler to finish or shutdown signal
            done, pending = await asyncio.wait(
                [scheduler_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
            
            # Stop scheduler
            if self.scheduler:
                await self.scheduler.stop()
            
            logger.success("Application stopped gracefully")
            
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            if self.scheduler:
                await self.scheduler.stop()
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise
        finally:
            logger.info("Cleanup complete")


async def main():
    """Main entry point."""
    app = Application()
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, app.handle_shutdown)
    signal.signal(signal.SIGTERM, app.handle_shutdown)
    
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
