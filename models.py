from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import pickle
from typing import List, Dict, Optional, Union
import logging
import calendar

# File paths for persistence
USERS_FILE = "users_data.pkl"
EXPENSES_FILE = "expenses_data.pkl"
COUNTER_FILE = "counters_data.pkl"

# In-memory storage
users: Dict[str, 'User'] = {}
expenses: Dict[str, List['Expense']] = {}
next_user_id = 1
next_expense_id = 1


def load_data() -> None:
    global users, expenses, next_user_id, next_expense_id

    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'rb') as f:
                users = pickle.load(f)

        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, 'rb') as f:
                expenses = pickle.load(f)

        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, 'rb') as f:
                counters = pickle.load(f)
                next_user_id = counters.get('next_user_id', 1)
                next_expense_id = counters.get('next_expense_id', 1)

        logging.info(
            f"Loaded {len(users)} users and expenses for {len(expenses)} users")
    except Exception as e:
        logging.error(f"Error loading data: {e}")


class User(UserMixin):

    def __init__(self, username: str, email: str):
        global next_user_id
        self.id = str(next_user_id)
        next_user_id += 1
        self.username = username
        self.email = email
        self.password_hash: Optional[str] = None
        self.monthly_salary: float = 0.0
        self.current_savings: float = 0.0
        self.last_savings_update = datetime.now()

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
        logging.debug(f"Password set for user {self.email}")

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            logging.warning(f"No password hash found for user {self.email}")
            return False
        return check_password_hash(self.password_hash, password)

    def get_monthly_expenses(self, year: int, month: int) -> List['Expense']:
        """Get expenses for a specific month and year"""
        all_expenses = Expense.get_user_expenses(self.id)
        return [
            expense for expense in all_expenses
            if expense.date.year == year and expense.date.month == month
        ]

    def get_monthly_total(self, year: int, month: int) -> float:
        """Calculate total expenses for a specific month"""
        monthly_expenses = self.get_monthly_expenses(year, month)
        return sum(expense.amount for expense in monthly_expenses)

    def get_balance(self) -> float:
        """Calculate current month's balance"""
        now = datetime.now()
        monthly_expenses = self.get_monthly_total(now.year, now.month)
        return self.monthly_salary - monthly_expenses

    def update_savings(self) -> None:
        """Update savings based on previous month's balance"""
        now = datetime.now()
        # If we're in a new month since last update
        if (now.year > self.last_savings_update.year or
            now.month > self.last_savings_update.month):
            # Get previous month's data
            if now.month == 1:
                prev_month = 12
                prev_year = now.year - 1
            else:
                prev_month = now.month - 1
                prev_year = now.year

            prev_expenses = self.get_monthly_total(prev_year, prev_month)
            savings_increase = self.monthly_salary - prev_expenses
            if savings_increase > 0:
                self.current_savings += savings_increase
                self.last_savings_update = now
                self.save()
                logging.info(f"Updated savings for user {self.email}: +${savings_increase:.2f}")

    @staticmethod
    def get(user_id: str) -> Optional['User']:
        return users.get(user_id)

    @staticmethod
    def get_by_email(email: str) -> Optional['User']:
        """Find user by email"""
        for user in users.values():
            if user.email == email:
                return user
        return None

    def save(self) -> None:
        users[self.id] = self
        # Save to file
        try:
            with open(USERS_FILE, 'wb') as f:
                pickle.dump(users, f)

            with open(COUNTER_FILE, 'wb') as f:
                pickle.dump({
                    'next_user_id': next_user_id,
                    'next_expense_id': next_expense_id
                }, f)
            logging.debug(f"User {self.email} saved successfully")
        except Exception as e:
            logging.error(f"Error saving user data: {e}")


class Expense:

    def __init__(self, user_id: str, amount: float, category: str,
                 description: str, date: Optional[datetime] = None):
        global next_expense_id
        self.id = str(next_expense_id)
        next_expense_id += 1
        self.user_id = user_id
        self.amount = float(amount)
        self.category = category
        self.description = description
        self.date = date or datetime.now()

    def save(self) -> None:
        if self.user_id not in expenses:
            expenses[self.user_id] = []
        expenses[self.user_id].append(self)
        # Save to file
        try:
            with open(EXPENSES_FILE, 'wb') as f:
                pickle.dump(expenses, f)

            with open(COUNTER_FILE, 'wb') as f:
                pickle.dump({
                    'next_user_id': next_user_id,
                    'next_expense_id': next_expense_id
                }, f)
            logging.debug(f"Expense {self.id} saved successfully")
        except Exception as e:
            logging.error(f"Error saving expense data: {e}")

    def delete(self) -> None:
        """Delete this expense"""
        if self.user_id in expenses:
            expenses[self.user_id] = [e for e in expenses[self.user_id] if e.id != self.id]
            try:
                with open(EXPENSES_FILE, 'wb') as f:
                    pickle.dump(expenses, f)
                logging.debug(f"Expense {self.id} deleted successfully")
            except Exception as e:
                logging.error(f"Error deleting expense: {e}")

    @staticmethod
    def get_user_expenses(user_id: str) -> List['Expense']:
        """Get all expenses for a user"""
        return expenses.get(user_id, [])

    @staticmethod
    def get_by_id(user_id: str, expense_id: str) -> Optional['Expense']:
        """Find a specific expense by ID"""
        user_expenses = expenses.get(user_id, [])
        for expense in user_expenses:
            if expense.id == expense_id:
                return expense
        return None


# Initialize by loading data
load_data()