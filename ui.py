class ExpenseUI:
    def show_menu(self):
        print("\n==== WELCOME TO THE EXPENSES APP TRACKER======\n")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Update Expense")
        print("4. Delete Expense")
        print("5. Search Expense")
        print("6. Filter Expenses")
        print("7. Total Expenses")
        print("8. Expenses full report")
        print("9. Exit\n")


    
    def get_expense_name(self):
        return input(
            "Whats the name of the expenses \n"
        ).strip()
    
    def get_expense_amount(self):
        try:
            amount = float(input("Whats the amount you spent on the items \n"))
            return amount
        except ValueError:
            return None
        
    def get_expense_category(self):
        category = input("Whats the category of the expenses\n").strip()
        if not category:
            return None
        return category
    
    def get_search_option(self):
        return input("Press 1 to search by name or 2 to search by id\n").strip()

    def get_search_name(self):
        return input("Whats the name you want to search?\n").strip()
    
    
    def get_search_id(self):
        return input("Whats the id you want to search?\n").strip()
    
    def get_update_id(self):
        return input(
            "Whats the id you want to update it's amount\n"
        ).strip()
    
    def get_updated_amount(self):
        try:
            amount = float(
                input("Whats the new amount you want to update with?\n")
            )
            return amount
        except ValueError:
            return None
        
    def get_delete_id(self):
        return input(
            "Whats the id of the expense you want to delete\n"
        ).strip()
    
    def get_filter_category(self):
        category = input("Enter the expenses category you want  to filter:\n").strip()

        if not category:
            return None

        return category
    
    def get_menu_choice(self):
         return input("Enter choice:\n").strip()
    
    def exit_app(self):
        print('THANK YOU FOR USING THE APP\n') 
