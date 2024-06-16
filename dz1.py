from collections import UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Invalid phone number")
        super().__init__(value)

    @staticmethod
    def validate_phone(phone):
        return len(phone) == 10 and phone.isdigit()

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format")
        super().__init__(value)

class Record:
    def __init__(self, name, phone, birthday=None):
        self.name = Name(name)
        self.phones = [Phone(phone)]
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        if Phone.validate_phone(phone):
            new_phone = Phone(phone)
            self.phones.append(new_phone)
            return new_phone
        else:
            raise ValueError("Invalid phone number")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def remove_phone(self, phone):
        del_phone = self.find_phone(phone)
        if del_phone:
            self.phones.remove(del_phone)
        return del_phone

    def edit_phone(self, old_phone, new_phone):
        if len(new_phone) != 10:
           raise ValueError("Invalid phone number: must be 10 digits.")
    
        phone = self.find_phone(old_phone)
        if phone:
            phone.value = new_phone(Phone)
        else:
            raise ValueError("Phone number not found")

    def edit_birthday(self, new_birthday):
        self.birthday = Birthday(new_birthday)

    def __str__(self):
        phones = "; ".join(str(p.value) for p in self.phones)
        birthday_str = str(self.birthday) if self.birthday else "No birthday set"
        return f"Contact name: {self.name}, phones: {phones}, birthday: {birthday_str}"

class AddressBook(UserDict):
    def __str__(self):
        if not self.data:
            return "No contacts found."
        return "\n".join([str(record) for record in self.data.values()])
    
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)

    def string_to_date(self, date_string):
        return datetime.strptime(date_string, "%Y.%m.%d").date()

    def date_to_string(self, date):
        return date.strftime("%Y.%m.%d")

    def prepare_user_list(self):
        prepared_list = []
        for record in self.data.values():
            if record.birthday:
                prepared_list.append({"name": record.name.value, "birthday": self.string_to_date(record.birthday.value)})
        return prepared_list
    
    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)
    
    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 4:
            return self.find_next_weekday(birthday, 0)
        return birthday

    def get_upcoming_birthdays(self, days=7):
     today = datetime.now().date()
     upcoming_birthdays = []
 
     for record in self.data.values():
         if record.birthday:
             birth_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date().replace(year=today.year)
             if birth_date < today:
                 birth_date = birth_date.replace(year=today.year + 1)
             adjusted_birthday = self.adjust_for_weekend(birth_date)
             
             if 0 <= (adjusted_birthday - today).days <= days:
                 upcoming_birthdays.append({"name": record.name.value, "birthday": adjusted_birthday})
     return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Please provide a name to lookup the phone number."
        except KeyError:
            return "Name not found"
        except FileNotFoundError:
            return AddressBook()
    return inner

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.edit_birthday(birthday)
        return f"Birthday for {name} added."
    else:
        return f"Contact {name} not found."

@input_error
def show_birthday(name, book: AddressBook):
    record = book.find(name)
    if record:
        if record.birthday:
            return f"Birthday for {name}: {record.birthday.value}"
        else:
            return f"Birthday for {name} not added."
    else:
        return f"Contact {name} not found."

@input_error
def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join([f"Greeting for {user['name']} for {user['birthday']}" for user in upcoming_birthdays])
    else:
        return "Users not found."

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split(' ', 1)
    if args:
        args = args[0].split()
    return cmd.strip().lower(), args

@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return f"Phone added."
    else:
        if len(phone) == 10:
            book.add_record(Record(name, phone))
            return f"Contact added."
        else:
            raise ValueError

@input_error
def change_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    if record:
        record.edit_phone(record.phones[0].value, phone)
        return 'Contact updated.'
    else:
        return 'Contact not found.'

@input_error
def show_phone(name, book: AddressBook):
    record = book.find(name)
    if record:
        return f"Phone number for {name}: {record.phones[0].value}"
    else:
        return f"Contact {name} not found."

@input_error 
def save_data(book, filename="addressbook.pkl"):
    with open( filename,'wb') as file:
        pickle.dump(book, file)

@input_error
def load_data(filename="addressbook.pkl"):
    with open(filename, "rb") as file:
        return pickle.load(file)


@input_error
def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "all":
            print(book)
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            if args:
                print(show_phone(args[0], book))
            else:
                print("Please provide a name to lookup the phone number.")
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args[0], book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()