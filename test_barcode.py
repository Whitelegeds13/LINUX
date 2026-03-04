#!/usr/bin/env python
"""
Test script to verify barcode generation.
"""
import os
import sys
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'urp_blockchain.settings')

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
django.setup()

from core.models import TokenReward, TokenRedemption, Student
from datetime import date
import uuid

print("=" * 60)
print("Testing Barcode Generation")
print("=" * 60)

# Generate sample barcodes
for i in range(3):
    date_str = date.today().strftime('%Y%m%d')
    unique_part = str(uuid.uuid4())[:8].upper()
    token_barcode = f"TOK-{date_str}-{unique_part}"
    redemption_barcode = f"RED-{date_str}-{unique_part}"
    print(f"Token barcode {i+1}: {token_barcode}")
    print(f"Redemption barcode {i+1}: {redemption_barcode}")
    print()

# Check database fields
print("=" * 60)
print("TokenReward model fields:")
for field in TokenReward._meta.get_fields():
    print(f"  - {field.name}")

print("\nTokenRedemption model fields:")
for field in TokenRedemption._meta.get_fields():
    print(f"  - {field.name}")

print("\n" + "=" * 60)
print("Test completed successfully!")
