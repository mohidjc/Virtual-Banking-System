class Account:
    def __init__(self, account_number, account_holder):
        self.account_number=account_number
        self._balance=0
        self.account_holder=account_holder

    def deposit(self, amount):
        if amount>0:            
            self._balance+=amount
        
    def withdraw(self, amount):
        if 0< amount<=self._balance:
            self._balance-=amount
    
            
    def check_balance(self):
        return self.check_balance

class CheckingAccount(Account):
    pass
