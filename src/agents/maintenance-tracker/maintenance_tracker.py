import logging
from typing import Optional, Tuple
from src.database.db_client import db
from src.models import MaintenanceItem
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MaintenanceTracker:
    @staticmethod
    def calculate_next_maintenance(item: MaintenanceItem) -> Tuple[Optional[str], Optional[int]]:
        """
        Calculate next service date and/or odometer based on last service and intervals.
        Returns (next_service_date, next_service_odometer)
        """
        next_date = None
        next_odo = None
        
        # If we have last service date and interval in days
        if item.last_service_date and item.interval_days:
            try:
                last_date = datetime.fromisoformat(item.last_service_date)
                next_date = (last_date + timedelta(days=item.interval_days)).isoformat()
            except ValueError as e:
                logger.warning(f"Could not parse last_service_date {item.last_service_date}: {e}")
        
        # If we have last service odometer and interval in km
        if item.last_service_odometer is not None and item.interval_km is not None:
            next_odo = item.last_service_odometer + item.interval_km
        
        # If both are calculated, we can choose the earlier one? But we'll return both and let the caller decide.
        # For simplicity, we return both.
        return next_date, next_odo
    
    async def schedule_maintenance_reminder(self, item: MaintenanceItem):
        """Schedule a reminder for a maintenance item."""
        # This would integrate with the reminder engine, but for now we just log.
        next_date, next_odo = self.calculate_next_maintenance(item)
        if next_date:
            logger.info(f"Maintenance reminder for {item.item_name} scheduled for {next_date}")
        if next_odo:
            logger.info(f"Maintenance reminder for {item.item_name} scheduled at odometer {next_odo} km")
    
    async def update_after_service(self, item_id: int, service_date: str, service_odometer: Optional[int] = None):
        """Update maintenance item after service has been performed."""
        # Update last service date and odometer
        update_fields = ["last_service_date = ?"]
        values = [service_date]
        if service_odometer is not None:
            update_fields.append("last_service_odometer = ?")
            values.append(service_odometer)
        
        # Recalculate next service
        # We would fetch the item, calculate next, and update those fields too.
        # For simplicity, we'll just update the last service fields and let the next calculation happen later.
        values.append(item_id)
        await db.execute(
            f"UPDATE maintenance_items SET {', '.join(update_fields)}, updated_at = datetime('now') WHERE id = ?",
            tuple(values)
        )
        logger.info(f"Updated maintenance item {item_id} with service date {service_date}")
