from enum import Enum


# Enums
class SaleType(Enum):
    DIRECT = 'direct'
    INDIRECT = 'indirect'


class DeliveryType(Enum):
    FREE = 'free'
    PAID = 'paid'
    EXPRESS = 'express'


class DeliveryStatus(Enum):
    PENDING = 'pending'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELED = 'canceled'


class ChargeType(Enum):
    PER_ITEM_SOLD = 'per_item_sold'
    PER_ITEM_PER_TIME = 'per_item_per_time'


class PaymentMethod(Enum):
    TELEBIRR = 'telebirr'
    MPESA = 'm-pesa'
    BANK_TRANSFER = 'bank_transfer'


class PaymentStatus(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
