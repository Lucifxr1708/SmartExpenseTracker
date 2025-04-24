from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app
from models import User, Expense
from ai_insights import get_ai_insights
from datetime import datetime
import calendar
import logging

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please fill in all fields')
            return render_template('login.html')

        user = User.get_by_email(email)
        logging.debug(f"Login attempt for email: {email}")

        if user and user.check_password(password):
            login_user(user)
            logging.info(f"User {email} logged in successfully")
            return redirect(url_for('dashboard'))

        logging.warning(f"Failed login attempt for email: {email}")
        flash('Invalid email or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([username, email, password, confirm_password]):
            flash('Please fill in all fields')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')

        if User.get_by_email(email):
            flash('Email already registered')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return render_template('register.html')

        user = User(username, email)
        user.set_password(password)
        user.save()
        login_user(user)
        logging.info(f"New user registered: {email}")
        flash('Registration successful! Welcome to Expense Tracker.')
        return redirect(url_for('dashboard'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logging.info(f"User {current_user.email} logged out")
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Get selected month and year, default to current month
    selected_year = int(request.args.get('year', datetime.now().year))
    selected_month = int(request.args.get('month', datetime.now().month))

    # Get expenses for selected month
    user_expenses = current_user.get_monthly_expenses(selected_year,
                                                    selected_month)

    # Calculate totals
    total_expenses = sum(expense.amount for expense in user_expenses)
    expenses_by_category = {}
    for expense in user_expenses:
        expenses_by_category[expense.category] = expenses_by_category.get(
            expense.category, 0) + expense.amount

    # Get month name for display
    month_name = calendar.month_name[selected_month]

    # Calculate balance
    balance = current_user.get_balance()

    # Update user's savings based on previous month's data
    current_user.update_savings()

    # Generate insights if requested
    insights = get_ai_insights(user_expenses,
                             generate=True,  # Always generate insights
                             selected_month=selected_month,
                             selected_year=selected_year,
                             monthly_salary=current_user.monthly_salary,
                             current_savings=current_user.current_savings)

    return render_template(
        'dashboard.html',
        expenses=user_expenses,
        total_expenses=total_expenses,
        expenses_by_category=expenses_by_category,
        monthly_salary=current_user.monthly_salary,
        balance=balance,
        insights=insights,
        current_month=selected_month,
        current_year=selected_year,
        month_name=month_name,
        months=list(enumerate(calendar.month_name))[1:],  # Skip empty first item
        years=range(datetime.now().year - 2, datetime.now().year + 1))


@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    try:
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Amount must be greater than 0')
            return redirect(url_for('dashboard'))

        category = request.form.get('category')
        description = request.form.get('description')
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else None

        expense = Expense(current_user.id, amount, category, description, date)
        expense.save()
        logging.info(f"New expense added by user {current_user.email}")
        flash('Expense added successfully')
    except ValueError:
        logging.error(f"Invalid amount entered by user {current_user.email}")
        flash('Invalid amount entered')
    except Exception as e:
        logging.error(f"Error adding expense: {str(e)}")
        flash(f'Error adding expense: {str(e)}')

    return redirect(url_for('dashboard'))


@app.route('/generate_insights', methods=['POST'])
@login_required
def generate_insights():
    selected_year = int(request.form.get('year', datetime.now().year))
    selected_month = int(request.form.get('month', datetime.now().month))

    user_expenses = current_user.get_monthly_expenses(selected_year,
                                                    selected_month)
    insights = get_ai_insights(user_expenses,
                             generate=True,
                             selected_month=selected_month,
                             selected_year=selected_year,
                             monthly_salary=current_user.monthly_salary,
                             current_savings=current_user.current_savings)
    logging.info(f"Generated insights for user {current_user.email}")
    flash('AI insights generated')

    return redirect(
        url_for('dashboard', year=selected_year, month=selected_month))


@app.route('/update_salary', methods=['POST'])
@login_required
def update_salary():
    try:
        monthly_salary = float(request.form.get('monthly_salary', 0))
        current_savings = float(request.form.get('current_savings', 0))

        if monthly_salary < 0:
            flash('Salary cannot be negative')
            return redirect(url_for('dashboard'))

        if current_savings < 0:
            flash('Savings cannot be negative')
            return redirect(url_for('dashboard'))

        current_user.monthly_salary = monthly_salary
        current_user.current_savings = current_savings
        current_user.save()
        logging.info(f"Financial info updated for user {current_user.email}")
        flash('Financial information updated successfully')
    except ValueError:
        logging.error(f"Invalid amount entered by user {current_user.email}")
        flash('Please enter valid numbers for salary and savings')
    except Exception as e:
        logging.error(f"Error updating financial info: {str(e)}")
        flash('An error occurred while updating your financial information')

    return redirect(url_for('dashboard'))


@app.route('/edit_expense/<expense_id>', methods=['POST'])
@login_required
def edit_expense(expense_id):
    try:
        expense = Expense.get_by_id(current_user.id, expense_id)
        if not expense:
            logging.warning(f"Attempt to edit non-existent expense {expense_id}")
            return 'Expense not found', 404

        data = request.get_json()
        if not data:
            logging.warning(f"Invalid data received for expense edit {expense_id}")
            return 'Invalid request data', 400

        # Validate input data
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return 'Amount must be greater than 0', 400

            date = datetime.strptime(data['date'], '%Y-%m-%d')
            if date > datetime.now():
                return 'Cannot add future expenses', 400

        except ValueError:
            return 'Invalid amount or date format', 400

        # Update expense details
        expense.date = date
        expense.category = data['category']
        expense.description = data['description']
        expense.amount = amount

        # Save changes
        expense.save()
        logging.info(f"Expense {expense_id} updated by user {current_user.email}")
        return 'Expense updated successfully', 200

    except Exception as e:
        logging.error(f"Error updating expense: {str(e)}")
        return f'Error updating expense: {str(e)}', 500


@app.route('/delete_expense/<expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    try:
        expense = Expense.get_by_id(current_user.id, expense_id)
        if not expense:
            return 'Expense not found', 404

        expense.delete()
        logging.info(f"Expense {expense_id} deleted by user {current_user.email}")
        return 'Expense deleted successfully', 200
    except Exception as e:
        logging.error(f"Error deleting expense: {str(e)}")
        return f'Error deleting expense: {str(e)}', 500