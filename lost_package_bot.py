#!/usr/bin/env python3
"""
Lost Package Chatbot - CLI Prototype
Author: Dina Trac
Scenario: Helping a customer track a lost package

Features: 
- Conversation flow with state management
- Validation + error handling (unexpected customer input, invalid formatting)
- Mock backend with sample orders
- Human escalation when confidence is low
- Clear, user-friendly messaging
"""

import re
import sys
from datetime import datetime

SAMPLE_ORDERS = {
    # order_id: {email, zip code, order status, last_scan, carrier, eta, notes}
    "AB-123456": {
        "email": "dora@gmail.com",
        "zip": "94107",
        "status": "In Transit",
        "last_scan": "2025-09-06 14:15 PT - Arrived at San Francisco, CA facility",
        "carrier": "USPS",
        "eta": "2025-09-10",
        "notes": "Weather-related delay reported on 2025-09-05"
    },
    "AB-654321": {
        "email": "dino@yahoo.com",
        "zip": "93402",
        "status": "Out for Delivery",
        "last_scan": "2025-09-07 08:35 PT - Departed Sunnyvale, CA facility",
        "carrier": "UPS",
        "eta": "2025-09-07",
        "notes": ""
    },
    "AB-112233": {
        "email": "devin@gmail.com",
        "zip": "94704",
        "status": "Delivered",
        "last_scan": "2025-09-06 17:49 PT - Delivered, left at front door",
        "carrier": "FedEx",
        "eta": "2025-09-06",
        "notes": "Photo confirmation available"
    }
}

def is_valid_order(order_id: str) -> bool:
    return bool(re.fullmatch(r"AB-\d{6}", order_id.strip().upper()))

def is_valid_zip(zipcode: str) -> bool:
    return bool(re.fullmatch(r"\d{5}(-\d{4})?", zipcode.strip()))

def is_valid_email(email: str) -> bool:
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email.strip().lower()))

def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        print("\nGoodbye!")
        sys.exit(0)

def confirm_yes_no(text: str) -> bool:
    for _ in range(3):
        ans = ask(text + " (yes/no): ").lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Sorry, I didn’t catch that. Please answer yes or no.")
    print("Let's move on.")
    return False

def lookup_order(order_id: str, email: str, zip_code: str):
    rec = SAMPLE_ORDERS.get(order_id.upper())
    if not rec:
        return None, "Sorry, I could not find that order ID. Please check the format 'AB-123456'."
    if rec["email"].lower() != email.lower():
        return None, "The email does not match what we have on file."
    if rec["zip"] != zip_code:
        return None, "The ZIP code does not match what we have on file."
    return rec, None

def main():
    print("Hi! I’m eGain’s virtual assistant for lost packages. I can help locate your order and share the latest status update.")
    print("To get started, I’ll need your order ID (AB-123456), the email used for purchase, and your ZIP code.")

    # Order ID
    for _ in range(3):
        order_id = ask("Order ID: ")
        if is_valid_order(order_id):
            break
        print("That doesn't look right. Please try again. Example format: AB-123456.")
    else:
        print("We’re having trouble with the order format. I’ll connect you to a human agent.")
        return

    # Email
    for _ in range(3):
        email = ask("Email on the order: ")
        if is_valid_email(email):
            break
        print("That email doesn’t look valid. Please try again. Example: name@example.com.")
    else:
        print("We’re having trouble verifying the email. I’ll connect you to a human agent.")
        return

    # ZIP
    for _ in range(3):
        zip_code = ask("Shipping ZIP code: ")
        if is_valid_zip(zip_code):
            break
        print("Please enter a 5-digit ZIP (optional +4). Example: 94107 or 94107-1234.")
    else:
        print("We’re having trouble validating the ZIP. I’ll connect you with a human agent.")
        return

    print(f"\nThanks! Here’s what I have:\n  • Order ID: {order_id}\n  • Email: {email}\n  • ZIP: {zip_code}")
    if not confirm_yes_no("Is this information correct?"):
        print("No problem! For your security, I’ll transfer you to a human agent to continue.")
        return

    rec, err = lookup_order(order_id, email, zip_code)
    if err:
        print(err)
        if confirm_yes_no("Would you like me to connect you with a human agent now?"):
            print("Connecting you to a human agent… You’ll receive an email confirmation shortly.")
        else:
            print("Okay! You can come back anytime with updated order details.")
        return

    print("\n✅ Order found! Here’s the latest:")
    print(f" • Status: {rec['status']}")
    print(f" • Carrier: {rec['carrier']}")
    print(f" • Last Scan: {rec['last_scan']}")
    print(f" • ETA: {rec['eta']}")
    if rec['notes']:
        print(f" • Notes: {rec['notes']}")

    if rec["status"].lower() == "delivered":
        if confirm_yes_no("Was the package received?"):
            print("Great to hear! I’ll note that as confirmed.")
        else:
            print("I’m sorry about that. I can file a missing package report and notify the carrier and our support team.")
            if confirm_yes_no("Would you like me to file that now?"):
                ref = f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                print(f"Report filed. Reference: {ref}. You’ll receive updates via email within 24 hours.")
    else:
        if confirm_yes_no("Would you like SMS/email updates as the package moves?"):
            print("Updates enabled. You’ll be notified of new scans or status changes.")
        if confirm_yes_no("Need tips to avoid missed delivery (e.g., leave at door, schedule pickup)?"):
            print("I’ve sent delivery preference options to your email.")

    print("\nThank you for using eGain’s virtual assistant!")

if __name__ == "__main__":
    main()
