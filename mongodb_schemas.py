"""
MongoDB Schema Definitions for Super Receptionist
TODO: Review and adjust these schemas based on your specific requirements
"""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field

# ============================================================================
# MENU SCHEMA
# ============================================================================
# TODO: Review menu schema - adjust fields based on your shop's needs
# TODO: Consider adding: images, dietary info (vegan, gluten-free), availability status
# TODO: Consider adding: preparation time, ingredients list
class MenuItemSchema(BaseModel):
    """Schema for menu items stored in MongoDB"""
    name: str = Field(..., description="Item name (e.g., 'Panna Cotta')")
    description: Optional[str] = Field(None, description="Item description")
    price: Optional[float] = Field(None, description="Price in dollars")
    category: Optional[str] = Field(None, description="Category (e.g., 'Desserts', 'Cakes')")
    # TODO: Add more fields as needed:
    # image_url: Optional[str] = None
    # available: bool = True
    # preparation_time: Optional[int] = None  # minutes
    # ingredients: List[str] = []
    # dietary_info: List[str] = []  # ['vegan', 'gluten-free', etc.]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# MongoDB Collection: menu_items
# Indexes to consider:
# TODO: Create index on 'category' for faster filtering
# TODO: Create index on 'name' for search functionality
# TODO: Create index on 'available' if you add availability status

# ============================================================================
# ORDERS SCHEMA
# ============================================================================
# TODO: Review orders schema - this matches the workflow diagram requirements
# TODO: Consider adding: customer contact info, payment status, delivery method
# TODO: Consider adding: order status (pending, confirmed, completed, cancelled)
class OrderSchema(BaseModel):
    """Schema for orders - matches workflow diagram"""
    order_id: str = Field(..., description="Unique order ID")
    customer: str = Field(..., description="Customer name")
    total: float = Field(..., description="Total amount in dollars")
    date_time: datetime = Field(..., description="Order date and time")
    note: Optional[str] = Field(None, description="Order notes/special instructions")
    # TODO: Add more fields as needed:
    # customer_email: Optional[str] = None
    # customer_phone: Optional[str] = None
    # address: Optional[str] = None
    # payment_status: str = "pending"  # pending, paid, refunded
    # order_status: str = "pending"  # pending, confirmed, in_progress, completed, cancelled
    # payment_method: Optional[str] = None  # cash, venmo, zelle, etc.
    # pickup_time: Optional[datetime] = None
    # created_at: datetime = Field(default_factory=datetime.utcnow)
    # updated_at: datetime = Field(default_factory=datetime.utcnow)

# MongoDB Collection: orders
# Indexes to consider:
# TODO: Create unique index on 'order_id'
# TODO: Create index on 'customer' for customer lookup
# TODO: Create index on 'date_time' for date range queries
# TODO: Create index on 'order_status' if you add status field

# ============================================================================
# ORDER DETAILS SCHEMA
# ============================================================================
# TODO: Review order details schema - matches workflow diagram
# TODO: Each order detail links to an order via order_id
# TODO: Consider adding: unit price, subtotal, customization options
class OrderDetailSchema(BaseModel):
    """Schema for order details - individual items in an order"""
    order_detail_id: str = Field(..., description="Unique order detail ID")
    order_id: str = Field(..., description="Links to order.order_id")
    product_name: str = Field(..., description="Product/item name")
    quantity: int = Field(..., description="Quantity ordered")
    unit_price: Optional[float] = Field(None, description="Price per unit")
    subtotal: Optional[float] = Field(None, description="Quantity * unit_price")
    # TODO: Add more fields as needed:
    # product_id: Optional[str] = None  # Link to menu item if applicable
    # customization: Optional[str] = None  # Special requests
    # cake_design_id: Optional[str] = None  # If it's a cake with specific design
    # created_at: datetime = Field(default_factory=datetime.utcnow)

# MongoDB Collection: order_details
# Indexes to consider:
# TODO: Create index on 'order_id' for fast order detail lookup
# TODO: Create index on 'product_name' for product analysis
# TODO: Create compound index on ['order_id', 'order_detail_id']

# ============================================================================
# ORDER SUMMARY SCHEMA (for daily/weekly summaries)
# ============================================================================
# TODO: Review summary schema - matches workflow diagram requirement
# TODO: "Create summary (total products each type by date)"
class OrderSummarySchema(BaseModel):
    """Schema for order summaries - total products by type and date"""
    summary_date: datetime = Field(..., description="Date of summary")
    product_type: str = Field(..., description="Product type/name")
    total_quantity: int = Field(..., description="Total quantity sold")
    total_revenue: Optional[float] = Field(None, description="Total revenue for this product")
    # TODO: Add more fields as needed:
    # order_count: int = 0  # Number of orders containing this product
    # average_order_value: Optional[float] = None
    # created_at: datetime = Field(default_factory=datetime.utcnow)

# MongoDB Collection: order_summaries
# Indexes to consider:
# TODO: Create compound index on ['summary_date', 'product_type']
# TODO: Create index on 'summary_date' for date range queries

# ============================================================================
# EXAMPLE USAGE IN DATABASE OPERATIONS
# ============================================================================
"""
Example of how these schemas would be used:

# Create an order
order = {
    "order_id": "ORD-2024-001",
    "customer": "John Doe",
    "total": 38.0,
    "date_time": datetime.utcnow(),
    "note": "Happy Birthday my love"
}

# Create order details
order_details = [
    {
        "order_detail_id": "DET-001",
        "order_id": "ORD-2024-001",
        "product_name": "Panna Cotta",
        "quantity": 9,
        "unit_price": 4.22,
        "subtotal": 38.0
    }
]

# Create summary
summary = {
    "summary_date": datetime(2024, 11, 13),
    "product_type": "Panna Cotta",
    "total_quantity": 9,
    "total_revenue": 38.0
}
"""

