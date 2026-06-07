import logging
from typing import List, Dict, Any, Optional
from src.database.db_client import db
from datetime import datetime

logger = logging.getLogger(__name__)

class ExpenseTracker:
    async def get_monthly_expense(self, year: int, month: int) -> Dict[str, Any]:
        """
        Get total expenses for a given month, broken down by bill type.
        """
        # Query all paid bills for the month
        query = f"""
            SELECT bill_type, SUM(paid_amount) as total, COUNT(*) as count
            FROM bills 
            WHERE strftime('%Y-%m', paid_date) = '{year:04d}-{month:02d}'
            AND status = 'paid'
            GROUP BY bill_type
        """
        rows = await db.fetch_all(query)
        
        total = 0
        by_category = {}
        for row in rows:
            bill_type = row[0]
            amount = row[1] if row[1] is not None else 0
            count = row[2]
            by_category[bill_type] = {"total": amount, "count": count}
            total += amount
        
        # Get year-over-year change
        last_year_total = await self.get_month_total(year - 1, month)
        yoy_change = None
        if last_year_total is not None and last_year_total != 0:
            yoy_change = ((total - last_year_total) / last_year_total) * 100
        
        return {
            "month": f"{month:02d}/{year}",
            "total": total,
            "by_category": by_category,
            "bill_count": sum(v["count"] for v in by_category.values()),
            "yoy_change_pct": yoy_change,
            "unpaid_count": await self.get_unpaid_count(year, month)
        }
    
    async def get_month_total(self, year: int, month: int) -> Optional[int]:
        """Get total paid amount for a given month."""
        query = f"""
            SELECT SUM(paid_amount) 
            FROM bills 
            WHERE strftime('%Y-%m', paid_date) = '{year:04d}-{month:02d}'
            AND status = 'paid'
        """
        row = await db.fetch_one(query)
        if row and row[0] is not None:
            return int(row[0])
        return 0
    
    async def get_unpaid_count(self, year: int, month: int) -> int:
        """Get count of unpaid bills for a given month (based on due date)."""
        query = f"""
            SELECT COUNT(*) 
            FROM bills 
            WHERE strftime('%Y-%m', due_date) = '{year:04d}-{month:02d}'
            AND status != 'paid'
        """
        row = await db.fetch_one(query)
        return row[0] if row and row[0] is not None else 0
    
    async def get_upcoming_bills(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Get bills due in the given month that are not yet paid."""
        query = f"""
            SELECT id, bill_type, issuer, amount_due, due_date
            FROM bills 
            WHERE strftime('%Y-%m', due_date) = '{year:04d}-{month:02d}'
            AND status != 'paid'
            ORDER BY due_date
        """
        rows = await db.fetch_all(query)
        bills = []
        for row in rows:
            bills.append({
                "id": row[0],
                "bill_type": row[1],
                "issuer": row[2],
                "amount_due": row[3],
                "due_date": row[4]
            })
        return bills
