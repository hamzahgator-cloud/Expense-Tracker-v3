from datetime import date


class Expense:
    def __init__(self,name,amount,category,expense_date=None,user_id=None,expense_id=None):
        self.id = expense_id
        self.name = name
        self.amount = amount
        self.category = category
        self.date = expense_date or str(date.today())
        self.user_id = user_id

    def __str__(self):
        return (
            f"ID: {self.id}, "
            f"Name: {self.name}, "
            f"Amount: ${self.amount}, "
            f"Category: {self.category}, "
            f"Date: {self.date}"
        )