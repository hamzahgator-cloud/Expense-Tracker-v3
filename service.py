from expense import Expense


class ExpenseService:
    def __init__(self, repo):
        self.repo = repo

   
    def add_expense(self, name, amount, category, user_id):
        max_length = 254

        if not isinstance(name, str) or not isinstance(category, str):
            return {"success": False, "message": "Name and category must be text"}

        name = name.strip()
        category = category.strip()

        if not name:
            return {"success": False, "message": "Name cannot be empty"}

        if not category:
            return {"success": False, "message": "Category cannot be empty"}

        if len(name) > max_length or len(category) > max_length:
            return {"success": False, "message": "Name or category is too long"}

        if name.isdigit():
            return {"success": False, "message": "Name cannot be in figures"}

        if category.isdigit():
            return {"success": False, "message": "Category cannot be in figures"}

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return {"success": False, "message": "Amount must be a number"}

        if amount <= 0:
            return {"success": False, "message": "Invalid amount"}

        name = name.upper()
        category = category[0].upper() + category[1:]

        expense = Expense(
            name=name,
            amount=amount,
            category=category,
            user_id=user_id
        )

        saved_expense = self.repo.save_expense_to_db(expense)

        return {
            "success": True,
            "message": "Expense added successfully",
            "expense": {
                "id": saved_expense.id,
                "name": saved_expense.name,
                "amount": saved_expense.amount,
                "category": saved_expense.category,
                "date": saved_expense.date
            }
        }

    
    def get_expenses_by_user(self, user_id):
     return {"success": True, "data": self.repo.get_expenses_by_user(user_id)}
    

    
    def update_expense(self, expense_id, name, amount, category, user_id):
        max_length = 254

        if not self.repo.get_expense_by_id(expense_id, user_id):
            return {"success": False, "message": "Expense not found"}

        if not isinstance(name, str) or not isinstance(category, str):
            return {"success": False, "message": "Name and category must be text"}

        name = name.strip()
        category = category.strip()

        if not name:
            return {"success": False, "message": "Name cannot be empty"}

        if not category:
            return {"success": False, "message": "Category cannot be empty"}

        if len(name) > max_length or len(category) > max_length:
            return {"success": False, "message": "Name or category is too long"}

        if name.isdigit():
            return {"success": False, "message": "Name cannot be in figures"}

        if category.isdigit():
            return {"success": False, "message": "Category cannot be in figures"}

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return {"success": False, "message": "Amount must be a number"}

        if amount <= 0:
            return {"success": False, "message": "Invalid amount"}

        name = name.upper()
        category = category[0].upper() + category[1:]

        self.repo.update_expense(expense_id, name, amount, category, user_id)
        return {"success": True, "message": "Expense updated successfully"}



   
    def delete_expense(self,expense_id,user_id):

        if not self.repo.get_expense_by_id(expense_id,user_id):
            return {"success": False, "message": "ID not found"}

        self.repo.delete_expense_by_id(expense_id,user_id)

        return {"success": True, "message": "Expense deleted successfully"}

    

   
    def search_by_name(self, name,user_id):

        if not name:
            return {"success": False, "message": "Name cannot be empty"}

        rows = self.repo.search_by_name(name,user_id)

        if not rows:
           return {"success": False, "message": "Name not found"}

        return {"success": True, "data": rows}

        

    
    def search_by_id(self, user_id, expense_id):

        if not expense_id:
            return {"success": False, "message": "ID cannot be empty"}

        row = self.repo.get_expense_by_id(expense_id,user_id)

        if not row:
            return {"success": False, "message": "Expense not found"}

        return {"success": True, "data": row}

  
    def filter_by_category(self, category,user_id):

        if not category:
            return {"success": False, "message": "Category cannot be empty"}

        if category.isdigit():
            return {"success": False, "message": "Category should not be numbers"}

        rows = self.repo.get_expenses_by_category(category,user_id)

        if not rows:
            return {"success": False, "message": "No expenses found in this category"}

        return {"success": True, "data": rows}

  

    def get_total_expenses(self,user_id):
        return {"success": True, "data": self.repo.get_total_expenses(user_id)}

    def get_expense_count(self,user_id):
        return {"success": True, "data": self.repo.get_expense_count(user_id)}

    def get_average_amount(self,user_id):
        return {"success": True, "data": self.repo.get_average_amount(user_id)}

    def get_amount_by_category(self, user_id):
        rows = self.repo.get_amount_by_category(user_id)

        return {
            "success": True,
            "data": [
                [row[0],
                  row[1]]
                for row in rows
            ]
        }


    def get_min_max(self, user_id):
        rows = self.repo.get_min_max(user_id)

        return {
            "success": True,
            "data": [
                [row[0], 
                row[1]]
                for row in rows
            ]
        }

    def close_db(self):
        return self.repo.close_db()




        #for admin only 

    def get_total_users(self):
        return {"success": True, "data": self.repo.get_total_users()}


    def admin_summary(self):
        row = self.repo.admin_summary()
        return {
                    "success": True,
                    "data": {
                        "total_expenses":row [0],
                        "total_amount": row [1],
                        "average_amount": row [2]
                    }
                    
                }


    def delete_user(self, user_id):
        rowcount = self.repo.delete_user(user_id)

        if rowcount == 0:
            return {
                "success": False,
                "message": "User not found or already deleted"
            }

        return {
            "success": True,
            "message": "User deleted successfully"
        }

    def get_all_users(self):
        rows = self.repo.get_all_users()
        return {
            "success": True,
            "data": [
                {
                    "id": row[0],
                    "email": row[1],
                    "role": row[2],
                    "is_verified": row[3],
                    "created_at": row[4],
                    "is_active": row[5]
                }
                for row in rows
            ]
        }

    
    def deactivate_user(self, user_id):
            rowcount = self.repo.deactivate_user(user_id)
    
            if rowcount == 0:
                return {
                    "success": False,
                    "message": "User not found or already deactivated"
                }
    
            return {
                "success": True,
                "message": "User deactivated successfully"
            }

    
    def activate_user(self, user_id):
                rowcount = self.repo.activate_user(user_id)
        
                if rowcount == 0:
                    return {
                        "success": False,
                        "message": "User not found or already activated"
                    }
        
                return {
                    "success": True,
                    "message": "User activated successfully "
                }

    