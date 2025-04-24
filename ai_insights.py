from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
import calendar

def get_ai_insights(expenses,
                   generate: bool = False,
                   selected_month: Optional[int] = None,
                   selected_year: Optional[int] = None,
                   monthly_salary: float = 0,
                   current_savings: float = 0) -> str:
    """
    Generate AI insights based on user expenses.

    Args:
        expenses: List of user expenses
        generate: Boolean flag to determine if insights should be generated
        selected_month: The month for which insights are being generated
        selected_year: The year for which insights are being generated
        monthly_salary: User's monthly salary
        current_savings: User's current savings

    Returns:
        A string containing AI-generated insights
    """
    if not expenses:
        return "Start tracking your expenses to receive AI-powered insights!"

    if not generate:
        return ""

    insights = []
    month_name = calendar.month_name[selected_month] if selected_month else "current month"

    # Calculate total spending
    total_spending = sum(expense.amount for expense in expenses)

    # Calculate category-wise spending
    category_spending = {}
    for expense in expenses:
        category_spending[expense.category] = category_spending.get(
            expense.category, 0) + expense.amount

    # Monthly budget analysis
    if monthly_salary > 0:
        spending_ratio = (total_spending / monthly_salary) * 100
        remaining = monthly_salary - total_spending

        if spending_ratio > 90:
            insights.append(
                f"⚠️ You've spent {spending_ratio:.1f}% of your monthly income in {month_name}. "
                "Consider reducing expenses to maintain your savings goals.")
        elif spending_ratio < 60:
            potential_savings = monthly_salary * 0.3
            insights.append(
                f"🎯 Great job! You're on track to save ${remaining:.2f} this month. "
                f"Consider setting aside ${potential_savings:.2f} (30% of your income) for long-term savings.")

    # Savings analysis
    if current_savings > 0:
        # Calculate months of emergency fund
        emergency_fund_months = current_savings / monthly_salary if monthly_salary > 0 else 0
        if emergency_fund_months < 3:
            insights.append(
                f"💰 Your current savings (${current_savings:.2f}) could cover {emergency_fund_months:.1f} months of expenses. "
                "Aim to build a 3-6 month emergency fund.")
        elif emergency_fund_months > 6:
            insights.append(
                f"🌟 Excellent! Your savings (${current_savings:.2f}) could cover {emergency_fund_months:.1f} months of expenses. "
                "Consider investing any additional savings for long-term growth.")

    # Category analysis
    if category_spending:
        # Find highest spending category
        highest_category = max(category_spending.items(), key=lambda x: x[1])
        insights.append(
            f"📊 Your highest spending category in {month_name} is {highest_category[0]} "
            f"(${highest_category[1]:.2f}).")

        # Check category distribution
        for category, amount in category_spending.items():
            percentage = (amount / total_spending) * 100
            if percentage > 40:
                insights.append(
                    f"⚖️ You spent {percentage:.1f}% of your budget on {category}. "
                    "Consider diversifying your expenses.")

    # Frequency analysis
    daily_expenses = {}
    for expense in expenses:
        day = expense.date.day
        daily_expenses[day] = daily_expenses.get(day, 0) + 1

    high_frequency_days = [
        day for day, count in daily_expenses.items() if count > 3
    ]
    if high_frequency_days:
        insights.append(
            f"📅 You had multiple transactions on {len(high_frequency_days)} days this month. "
            "Consider consolidating purchases to reduce impulse spending.")

    # Small expenses analysis
    small_expenses = [e for e in expenses if e.amount < 10]
    if len(small_expenses) > 5:
        small_total = sum(e.amount for e in small_expenses)
        insights.append(
            f"🔍 You had {len(small_expenses)} small expenses (<$10) totaling ${small_total:.2f}. "
            "These small purchases can add up quickly!")

    # End of month projection
    if selected_month and selected_year:
        current_date = datetime.now()
        if (selected_year == current_date.year
                and selected_month == current_date.month):
            days_left = calendar.monthrange(selected_year,
                                         selected_month)[1] - current_date.day
            if days_left > 0:
                daily_average = total_spending / current_date.day
                projected_total = daily_average * calendar.monthrange(
                    selected_year, selected_month)[1]
                projected_savings = monthly_salary - projected_total

                if projected_savings > 0:
                    insights.append(
                        f"📈 At your current rate, you might save ${projected_savings:.2f} "
                        f"by the end of {month_name}!")
                else:
                    insights.append(
                        f"📉 At your current spending rate, you might exceed your monthly income "
                        f"by ${-projected_savings:.2f} by the end of {month_name}.")

    if not insights:
        insights.append(
            f"✨ Your spending patterns in {month_name} look reasonable. Keep up the good work!"
        )

    return "\n".join(insights)