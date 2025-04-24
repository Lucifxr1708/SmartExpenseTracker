from models import User, Expense
from datetime import datetime, timedelta
import random
import pickle
import os
import logging

def generate_dummy_data():
    # Create a demo user
    demo_user = User("demo", "demo@example.com")
    demo_user.set_password("password")
    demo_user.monthly_salary = 6000.00  # Set monthly salary to $6000
    demo_user.current_savings = 14000.00  # Initial savings
    demo_user.last_savings_update = datetime.now()
    demo_user.save()

    print(f"Created demo user: email=demo@example.com, password=password")

    # Categories with realistic descriptions and target monthly spending
    expense_categories = {
        "Food": {
            "items": [
                "Grocery shopping", "Restaurant dinner", "Coffee shop", "Lunch at work",
                "Food delivery"
            ],
            "monthly_target": 800
        },
        "Transportation": {
            "items": [
                "Gas refill", "Bus ticket", "Train pass", "Car maintenance",
                "Parking fees"
            ],
            "monthly_target": 400
        },
        "Entertainment": {
            "items": [
                "Movie tickets", "Netflix subscription", "Concert tickets",
                "Video games", "Streaming services"
            ],
            "monthly_target": 300
        },
        "Shopping": {
            "items": [
                "Clothes shopping", "Electronics", "Home decor", "Books",
                "Personal care items"
            ],
            "monthly_target": 500
        },
        "Bills": {
            "items": [
                "Electricity bill", "Water bill", "Internet service", "Phone bill",
                "Insurance payment"
            ],
            "monthly_target": 1200
        },
        "Other": {
            "items": [
                "Healthcare", "Gift for friend", "Home repairs", "Pet supplies",
                "Office supplies"
            ],
            "monthly_target": 800
        }
    }

    # Generate 4 months of expenses
    current_date = datetime.now()
    start_date = current_date - timedelta(days=120)  # 4 months ago

    # Track monthly totals to ensure realistic spending
    monthly_totals = {}

    while start_date <= current_date:
        month_key = (start_date.year, start_date.month)
        if month_key not in monthly_totals:
            monthly_totals[month_key] = {cat: 0 for cat in expense_categories.keys()}

        # Generate different number of expenses for each day
        daily_expenses = random.randint(1, 4)  # At least 1 expense per day

        for _ in range(daily_expenses):
            # Select random category, prioritizing those under monthly target
            available_categories = [
                cat for cat, info in expense_categories.items()
                if monthly_totals[month_key][cat] < info["monthly_target"]
            ]

            if not available_categories:
                continue  # Skip if all categories are at target

            category = random.choice(available_categories)
            description = random.choice(expense_categories[category]["items"])

            # Calculate remaining budget for this category
            remaining_budget = (expense_categories[category]["monthly_target"] -
                             monthly_totals[month_key][category])

            # Generate amount based on remaining budget
            min_amount = min(10, remaining_budget)
            max_amount = min(remaining_budget * 0.5, 200)  # No more than 50% of remaining budget
            amount = round(random.uniform(min_amount, max_amount), 2)

            # Create and save expense
            expense = Expense(demo_user.id, amount, category, description, start_date)
            expense.save()

            # Update monthly total
            monthly_totals[month_key][category] += amount

        start_date += timedelta(days=1)

    # Print summary
    total_expenses = 0
    for (year, month), categories in monthly_totals.items():
        month_total = sum(categories.values())
        total_expenses += month_total
        print(f"\nMonth {month}/{year}:")
        print(f"Total expenses: ${month_total:.2f}")
        for category, amount in categories.items():
            print(f"  {category}: ${amount:.2f}")

    print(f"\nCreated expenses over the last 4 months")
    print(f"Monthly salary: ${demo_user.monthly_salary:.2f}")
    print(f"Initial savings: ${demo_user.current_savings:.2f}")
    print("You can now login with email=demo@example.com and password=password")


if __name__ == "__main__":
    generate_dummy_data()