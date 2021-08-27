import sqlite3
from Account import Account
class Bank:
    def __init__(self):
        self.Accounts = []
        self.Accounts_details = {}
        self.conn = sqlite3.connect('AccountInfo.s3db')
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS card (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL,
            pin TEXT NOT NULL,
            balance INTEGER DEFAULT 0
            );
            ''')
        self.conn.commit()

    def run(self):
        while True:
            option = input('1. Create an account \n2. Log into account\n0. Exit\n')
            if option == '1':
                Bank.create_account(self)
            elif option == '2':
                card = input('Enter your card number:\n')
                pin = input('Enter your PIN:\n')
                if Bank.check_account(self, card, pin):
                    print('You have successfully logged in!')
                    Bank.login(self, card)
                else:
                    print('Wrong card number or PIN!')
            else:
                print('Bye!')
                exit()

    def check_account(self, card_number, pin):
        self.cur.execute('SELECT * FROM card')
        bank_data = self.cur.fetchall()
        for a in bank_data:
            if a[1] == card_number:
                if a[2] == pin:
                    return True
                else:
                    return False

    def check_card(self, card_number):
        self.cur.execute('SELECT * FROM card')
        bank_data = self.cur.fetchall()
        for a in bank_data:
            if a[1] == card_number:
                return True
        return False

    def check_receiver(self, card_number):
        temp = list(card_number).copy()
        check_digit = temp.pop()
        index = 0
        for digit in temp:
            if (index + 1) % 2 != 0:
                temp[index] = int(digit) * 2
            index += 1
        index = 0
        for digit in temp:
            if int(digit) > 9:
                temp[index] = int(digit) - 9
            index += 1
        total = 0
        for digit in temp:
            total += int(digit)
        return int(check_digit) == ((total * 9) % 10)

    def create_account(self):
        account = Account()
        self.cur.execute(f"INSERT INTO card(number, pin, balance) VALUES({account.get_card_number()}, {account.get_pin()}, 0)")
        self.conn.commit()
        print('Your card number:')
        print(account.get_card_number() + '\n')
        print('Your card PIN:')
        print(account.get_pin() + '\n')

    def add_income(self, card_number, amt):
        self.cur.execute(f'SELECT * FROM card WHERE number = {card_number}')
        card = self.cur.fetchall()
        self.cur.execute(f'UPDATE card SET balance = {card[0][3] + amt} WHERE number = {card_number}')
        self.conn.commit()

    def withdraw(self, card_number, amt):
        self.cur.execute(f'SELECT * FROM card WHERE number = {card_number}')
        card = self.cur.fetchall()
        self.cur.execute(f'UPDATE card SET balance = {card[0][3] - amt} WHERE number = {card_number}')
        self.conn.commit()

    def transfer(self, source, destination):
        if source == destination:
            print('You can\'t transfer money to the same account!')
        elif Bank.check_receiver(self, destination) == False:
            print('Probably you made mistake in the card number. Please try again!')
        elif Bank.check_card(self, destination) == False:
            print("Such a card does not exist.")
        else:
            amt = int(input('Enter how much money you want to transfer:'))
            if amt > Bank.get_balance(self, source):
                print('Not enough money!')
            else:
                Bank.add_income(self, destination, amt)
                Bank.withdraw(self, source, amt)
                print('Success!')

    def get_balance(self, card_number):
        self.cur.execute(f'SELECT * FROM card WHERE number = {card_number}')
        card = self.cur.fetchall()
        return card[0][3]

    def login(self, card_number):
        while True:
            option = input('1. Balance \n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n')
            if option == '1':
                print('Balance:', Bank.get_balance(self, card_number))
            elif option == '2':
                amt = int(input('Enter income:'))
                Bank.add_income(self, card_number, amt)
            elif option == '3':
                destination = input('Enter card number:')
                Bank.transfer(self, card_number, destination)
            elif option == '4':
                self.cur.execute(f'DELETE FROM card WHERE number = {card_number}')
                self.conn.commit()
                print('The account has been closed!')
                break
            elif option == '5':
                print('You have successfully logged out!')
                break
            else:
                print('Bye!')
                exit()


B = Bank()

B.run()