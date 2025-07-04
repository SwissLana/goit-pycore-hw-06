from collections import UserDict # Імпортуємо UserDict для створення адресної книги


class Field: # Базовий клас для полів
    def __init__(self, value): # Ініціалізація поля
        self.value = value # Значення поля

    def __str__(self): # Повертає рядкове представлення поля
        return str(self.value)


class Name(Field): # Клас для імені
    pass


class Phone(Field): # Клас для телефонного номера
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10: # Перевірка на 10-значний номер
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value) # Виклик конструктора базового класу


class Record: # Клас для запису контакту
    def __init__(self, name): # Ініціалізація запису з іменем
        self.name = Name(name)
        self.phones = [] # Список телефонних номерів

    def add_phone(self, phone): # Додає телефонний номер до запису
        self.phones.append(Phone(phone))

    def remove_phone(self, phone): # Видаляє телефонний номер з запису
        phone_obj = self.find_phone(phone) # Пошук телефонного номера
        if phone_obj:
            self.phones.remove(phone_obj) # Видаляємо знайдений номер
            return True
        return False

    def edit_phone(self, old_phone, new_phone): # Змінює телефонний номер в записі
        phone_obj = self.find_phone(old_phone) # Пошук старого номера
        if phone_obj:
            self.phones.remove(phone_obj) # Видаляємо старий номер
            self.phones.append(Phone(new_phone)) # Додаємо новий номер
            return True
        return False

    def find_phone(self, phone): # Пошук телефонного номера в записі
        for p in self.phones: # Проходимо по всіх номерах
            if p.value == phone: # Порівнюємо значення номера
                return p
        return None

    def __str__(self):
        phones_str = "; ".join(str(p) for p in self.phones) # Формуємо рядок з телефонів
        return f"{self.name.value}: {phones_str}" # Повертає рядкове представлення запису


class AddressBook(UserDict): # Клас для адресної книги
    def add_record(self, record): # Додає запис до адресної книги
        self.data[record.name.value] = record # Використовує ім'я як ключ

    def find(self, name): # Пошук контакту за іменем
        return self.data.get(name)

    def delete(self, name): # Видаляє контакт з адресної книги
        if name in self.data:
            del self.data[name]

    def search(self, query): # Пошук контактів за іменем або телефоном
        result = []
        query = query.lower() # Нормалізація запиту
        for record in self.data.values():
            name_match = record.name.value.lower().startswith(query)
            phone_match = any(query in phone.value for phone in record.phones)
            if name_match or phone_match:
                result.append(str(record))
        return result


def parse_input(user_input): # Розбір введення користувача
    cmd, *args = user_input.strip().split()
    return cmd.strip().lower(), args


def normalize_name(name): # Нормалізує ім'я: видаляє зайві пробіли, перетворює на рядок з великої літери
    return name.strip().capitalize()


def input_error(func): # Декоратор для обробки помилок введення
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Missing input. Please provide valid arguments."
    return inner


@input_error
def add_contact(args, book):   # Додає новий контакт до адресної книги
    if len(args) < 2: # Перевірка наявності імені та телефонів
        raise ValueError("Please enter name and at least one phone number.")
    name = normalize_name(args[0])
    phones = args[1:]
    if book.find(name): # Перевірка наявності контакту
        return "Contact already exists. Use 'change' or 'addphone' to modify it."
    record = Record(name) # Створення нового запису
    for phone in phones:
        record.add_phone(phone)
    book.add_record(record) # Додавання запису до адресної книги
    return "Contact added."


@input_error
def change_contact(args, book): # Змінює телефонний номер контакту
    if len(args) < 3: # Перевірка наявності імені, старого та нового номерів телефонів
        raise ValueError("Please provide name, old phone, and new phone.")
    name = normalize_name(args[0])
    old_phone = args[1]
    new_phone = args[2]
    record = book.find(name) # Пошук контакту
    if not record or not record.edit_phone(old_phone, new_phone):
        raise KeyError
    return "Phone number updated."


@input_error
def add_phone_to_contact(args, book): # Додає новий телефонний номер до існуючого контакту
    if len(args) < 2: # Перевірка наявності імені та телефонного номера
        raise ValueError("Please provide name and phone number to add.")
    name = normalize_name(args[0])
    phone = args[1]
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_phone(phone)
    return "Phone number added."


@input_error
def remove_phone(args, book): # Видаляє телефонний номер з контакту
    if len(args) < 2:
        raise ValueError("Please provide name and phone number to remove.")
    name = normalize_name(args[0])
    phone = args[1]
    record = book.find(name)
    if not record or not record.remove_phone(phone):
        raise KeyError
    return "Phone number removed."


@input_error
def show_phone(args, book): # Показує телефонний номер контакту
    name = normalize_name(args[0])
    record = book.find(name)
    if not record:
        raise KeyError
    return str(record)


@input_error
def search_contacts(args, book): # Пошук контактів за іменем або телефоном
    if not args:
        raise ValueError("Please enter a name or phone to search.")
    results = book.search(args[0])
    return "\n".join(results) if results else "No matching contacts found."


def show_all(book): # Показує всі контакти в адресній книзі
    if not book.data:
        return "No contacts saved."
    return "\n".join(str(record) for record in book.data.values())


def main():
    book = AddressBook() # Ініціалізація адресної книги
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            continue

        command, args = parse_input(user_input)

        if command in ["exit", "close"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "addphone":
            print(add_phone_to_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "remove":
            print(remove_phone(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "search":
            print(search_contacts(args, book))
        elif command == "all":
            print(show_all(book))
        else:
            print("Unknown command. Try: hello, add, addphone, change, remove, phone, search, all, exit, close.")


if __name__ == "__main__":
    main()