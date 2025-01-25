import argparse
import json
import os
import sys
from datetime import datetime

class ExpenseTracker:
    def __init__(self):
        self.expenses = {}
        self.filename = 'expenses.json'
        self.next_id = 1
        self.init_json()
        self.load_expenses()

    def init_json(self):
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
            self.save_expenses()
    
    def load_expenses(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.expenses = data.get('expenses', {})
                self.next_id = data.get('next_id', 1)
        except (json.JSONDecodeError, FileNotFoundError):
            self.expenses = {}
            self.next_id = 1
            self.save_expenses()
    
    def save_expenses(self):
        data = {
            'expenses': self.expenses,
            'next_id': self.next_id
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def add_expense(self, description, amount):
        expense_id = str(self.next_id)
        date = datetime.now().strftime("%Y-%m-%d")
        
        self.expenses[expense_id] = {
            'id': expense_id,
            'description': description,
            'amount': float(amount),
            'date': date
        }
        self.next_id += 1
        self.save_expenses()
        return expense_id

    def delete_expense(self, expense_id):
        if expense_id in self.expenses:
            del self.expenses[expense_id]
            self.save_expenses()
            return True
        return False

    def list_expenses(self):
        if not self.expenses:
            print('no expenses found')
            return
        
        print("\nID  Date       Description  Amount")
        print("------------------------------------")
        for exp in self.expenses.values():
            print(f"{exp['id']:2}  {exp['date']}  {exp['description'][:15]:15} ${exp['amount']:>7.2f}")

    def get_summary(self, month=None):
        total = 0.0
        for exp in self.expenses.values():
            if month:
                exp_month = datetime.strptime(exp['date'], "%Y-%m-%d").month
                if exp_month == month:
                    total += exp['amount']
            else:
                total += exp['amount']
        return total

def main():
    tracker = ExpenseTracker()
    
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(prog='expense-tracker')
        subparsers = parser.add_subparsers(dest='command', required=True)
        
        add_parser = subparsers.add_parser('add')
        add_parser.add_argument('--description', required=True)
        add_parser.add_argument('--amount', type=float, required=True)
        add_parser.add_argument('--date')
        
        subparsers.add_parser('list')
        
        del_parser = subparsers.add_parser('delete')
        del_parser.add_argument('--id', required=True)
        
        sum_parser = subparsers.add_parser('summary')
        sum_parser.add_argument('--month', type=int, choices=range(1,13))
        
        args = parser.parse_args()
        
        try:
            if args.command == 'add':
                expense_id = tracker.add_expense(args.description, args.amount)
                print(f"Expense added successfully (ID: {expense_id})")
                
            elif args.command == 'list':
                tracker.list_expenses()
                
            elif args.command == 'delete':
                if tracker.delete_expense(args.id):
                    print("Expense deleted successfully")
                else:
                    print("Error: Invalid expense ID")
                    
            elif args.command == 'summary':
                total = tracker.get_summary(args.month)
                if args.month:
                    month_name = datetime(1900, args.month, 1).strftime('%B')
                    print(f"Total expenses for {month_name}: ${total:.2f}")
                else:
                    print(f"Total expenses: ${total:.2f}")
                    
        except Exception as e:
            print(f"Error: {str(e)}")
        return
    
    while True:
        try:
            print('\n1. add expense\n2. delete expense\n3. list expenses\n4. summary\n5. exit')
            choice = input('enter choice: ')

            if choice == '1':
                desc = input("enter expense description (or 'back' to return): ")
                if desc.lower() == 'back':
                    continue
                amount = float(input('enter expense amount: '))
                expense_id = tracker.add_expense(desc, amount)
                print(f'expense added with id: {expense_id}')
            
            elif choice == '2':
                expense_id = input('enter expense id (or "back" to return): ')
                if expense_id.lower() == 'back':
                    continue
                if tracker.delete_expense(expense_id):
                    print('expense deleted')
                else:
                    print('invalid expense id')
            
            elif choice == '3':
                tracker.list_expenses()
            
            elif choice == '4':
                month = input('enter month number (1-12) or leave blank: ')
                if month.isdigit() and 1 <= int(month) <= 12:
                    total = tracker.get_summary(int(month))
                    month_name = datetime(1900, int(month), 1).strftime('%B')
                    print(f"total expenses for {month_name}: ${total:.2f}")
                else:
                    total = tracker.get_summary()
                    print(f"total expenses: ${total:.2f}")
            
            elif choice == '5':
                print('exiting...')
                break

        except KeyboardInterrupt:
            print('\nexiting...')
            break
        except:
            print('invalid input')

if __name__ == "__main__":
    main()