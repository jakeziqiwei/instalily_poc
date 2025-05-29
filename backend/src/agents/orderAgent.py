import uuid
from datetime import datetime


class OrderAgent:
    def __init__(self, orderdb):
        self.orderdb = orderdb

    async def run(self, function_name: str, data: dict):
        """Handle all order-related operations"""

        handlers = {
            "place_order": self._place_order,
            "check_order_status": self._check_status,
            "cancel_order": self._cancel_order
        }

        handler = handlers.get(function_name)
        if not handler:
            return {"message": "Unknown order function"}

        return handler(data)

    def _place_order(self, data):
        """Create a new order"""
        try:
            order = self.orderdb.create_order(
                user_id=data["user_id"],
                items=data["items"],
                total_amount=data["total_amount"],
                status="confirmed"
            )

            return {
                "message": f"Order {order.order_id} created successfully!",
                "order_id": order.order_id,
                "total": order.total_amount,
                "status": order.status
            }
        except Exception as e:
            return {"message": f"Order failed: {str(e)}"}

    def _check_status(self, data):
        """Check order status"""
        try:
            order = self.orderdb.get_order_by_id(data["order_id"])
            if not order:
                return {"message": "Order not found"}

            return {
                "order_id": order.order_id,
                "status": order.status,
                "total": order.total_amount,
                "items": order.items,
                "created": order.order_date.isoformat() if order.order_date else None
            }
        except Exception as e:
            return {"message": f"Status check failed: {str(e)}"}

    def _cancel_order(self, data):
        """Cancel an order"""
        try:
            order = self.orderdb.get_order_by_id(data["order_id"])
            if not order:
                return {"message": "Order not found"}

            if order.status == "shipped":
                return {"message": "Cannot cancel shipped orders"}

            self.orderdb.update_order_status(data["order_id"], "cancelled")
            return {"message": f"Order {data['order_id']} cancelled successfully"}
        except Exception as e:
            return {"message": f"Cancellation failed: {str(e)}"}

    async def get_order_status(self, order_id):
        return self.orderdb.get_order_status(order_id)

    async def get_order_details(self, order_id):
        return self.orderdb.get_order_details(order_id)

    async def cancel_order(self, order_id):
        return self.orderdb.cancel_order(order_id)

    async def create_order(self, data):
        return self.orderdb.create_order(
            user_id=data["user_id"],
            items=data["items"],
            total_amount=data["total_amount"]
        )
