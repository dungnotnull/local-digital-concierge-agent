'
import asyncio
import logging
from src.database.db_client import db
from src.database.migration import init_db
from src.tools.llm_client import llm_client
from src.agents.bill_processor.bill_processor import BillProcessor
from src.agents.scheduler.scheduler import ReminderEngine
from src.agents.expense_tracker.expense_tracker import ExpenseTracker
from src.agents.service_finder.service_finder import ServiceFinder
from src.agents.message_drafter.message_drafter import MessageDrafter
from src.agents.maintenance_tracker.maintenance_tracker import MaintenanceTracker
from src.agents.knowledge_updater.knowledge_updater import KnowledgeUpdater

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.bill_processor = BillProcessor()
        self.reminder_engine = ReminderEngine()
        self.expense_tracker = ExpenseTracker()
        self.service_finder = ServiceFinder()
        self.message_drafter = MessageDrafter()
        self.maintenance_tracker = MaintenanceTracker()
        self.knowledge_updater = KnowledgeUpdater()
    
    async def start(self):
        """Start all agent components."""
        logger.info("Starting Local Digital Concierge Agent...")
        
        # Initialize database
        await db.connect()
        await init_db()
        
        # Start reminder engine
        await self.reminder_engine.start()
        
        # Start knowledge updater in the background
        asyncio.create_task(self.knowledge_updater.start_update_job())
        
        logger.info("All components started. Agent is running.")
        
        # Keep the orchestrator running
        try:
            while True:
                await asyncio.sleep(3600)  # Sleep for an hour
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown all components."""
        logger.info("Shutting down components...")
        await self.reminder_engine.shutdown()
        await db.close()
        logger.info("Shutdown complete.")

# For running directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = Orchestrator()
    asyncio.run(agent.start())
'
