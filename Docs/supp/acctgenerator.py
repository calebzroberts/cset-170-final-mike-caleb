import os
import random
import hashlib as hash

pepper = hash.sha256("sparkles".encode()).hexdigest()

class Person():
    def __init__(self, username:str, password:str, first_name:str, last_name:str, isAdmin:bool):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.isAdmin = isAdmin
    def add_user_info(self, ssn:str, address:str, phone:str, isApproved:bool):
        self.ssn = ssn
        self.address = address
        self.phone = phone
        self.isApproved = isApproved
    def add_account_info(self, acct_num:int, balance:float):
        self.acct_num = acct_num
        self.balance = balance

first_names = [ "James", "Michael", "John", "Robert", "David", "William", "Richard", "Mary", "Patricia", "Jennifer", "Linda"]
last_names = [ "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodrigues", "Martinez", "Hernandez"]
street_names = [ "Main", "Park", "Fifth", "Oak", "Pine", "Queen", "Lincoln", "Walnut", "Sunset", "Church", "Highland", "Elm"]
street_suffixes = ["Ave", "Blvd", "Rd", "St", "Cir", "Ln"]
states = [ "CA", "TX", "FL", "NY", "PA", "IL", "OH", "GA", "NC", "MI", "AZ" ]


passwords_inp = """
123456	123456	123456	123456	123456	123456	123456 123456	123456	password	password	password	password	password	password	12345678912345678	12345678	12345678	12345	12345678	12345	12345678	123456789	qwertyqwerty	abc123	qwerty	12345678	qwerty	12345678	qwerty	12345678	passwordabc123	qwerty	abc123	qwerty	12345	football	12345	12345	1234567monkey	monkey	123456789	123456789	123456789	qwerty	123456789	111111	123456781234567	letmein	111111	1234	football	1234567890	letmein	1234567	12345letmein	dragon	1234567	baseball	1234	1234567	1234567	sunshine	iloveyoutrustno1	111111	iloveyou	dragon	1234567	princess	football	qwerty	111111dragon	baseball	adobe123[a]	football	baseball	1234	iloveyou	iloveyou	123123baseball	iloveyou	123123	1234567	welcome	login	admin	princess	abc123111111	trustno1	admin	monkey	1234567890	welcome	welcome	admin	qwerty123iloveyou	1234567	1234567890	letmein	abc123	solo	monkey	welcome	1q2w3e4rmaster	sunshine	letmein	abc123	111111	abc123	login	666666	adminsunshine	master	photoshop[a]	111111	1qaz2wsx	admin	abc123	abc123	qwertyuiopashley	123123	1234	mustang	dragon	121212	starwars	football	654321bailey	welcome	monkey	access	master	flower	123123	123123	555555passw0rd	shadow	shadow	shadow	monkey	passw0rd	dragon	monkey	lovelyshadow	ashley	sunshine	master	letmein	dragon	passw0rd	654321	7777777123123	football	12345	michael	login	sunshine	master	!@#$%^&*	welcome654321	jesus	password1	superman	princess	master	hello	charlie	888888superman	michael	princess	696969	qwertyuiop	hottie	freedom	aa123456	princessqazwsx	ninja	azerty	123123	solo	loveme	whatever	donald	dragonmichael	mustang	trustno1	batman	passw0rd	zaq1zaq1	qazwsx	password1	password1Football	password1	000000	trustno1	starwars	password1	trustno1	qwerty123 123456 123456789 qwerty 12345678 111111 1234567890 1234567 password 23123 987654321 qwertyuiop mynoob 123321 666666 18atcskd2w 7777777 1q2w3e4r 654321 555555 3rjs1la7qe google 1q2w3e4r5t 123qwe zxcvbnm 1q2w3e 123456 123456789 qwerty password 1111111 12345678 abc123 1234567 password1 12345 1234567890 123123 000000 Iloveyou 1234 1q2w3e4r5t Qwertyuiop 123 Monkey Dragon
"""
passwords = passwords_inp.split()
trimmed_pass = []
for i in range(len(passwords)):
    passwords[i] = passwords[i].strip()
passwords = list(dict.fromkeys(passwords))

random.shuffle(first_names)
random.shuffle(last_names)
random.shuffle(street_names)
random.shuffle(states)
random.shuffle(passwords)

users = [Person("admin", "re!p4SR", "Mister", "Sparkles", True)]

for i in range(9):
    f_name = first_names[i]
    l_name = last_names[i]
    u_name = (f_name[0]+l_name).lower()
    s_num = random.randint(10,999)
    s_name = street_names[i]
    state = states[i]
    z_code = random.randint(11111,99999)
    address = str(s_num) + ' ' + s_name + ' ' + random.choice(street_suffixes) + ', '
    address += state + ' ' + str(z_code)
    phone = f"({str(random.randint(10,999)).zfill(3)})-{str(random.randint(10,999)).zfill(3)}-{str(random.randint(10,9999)).zfill(4)}"
    ssn = str(random.randint(100,999)) + '-' + str(random.randint(10,99)) + '-' + str(random.randint(1000,9999))
    new_user = Person(u_name, passwords[i], f_name, l_name, False)
    new_user.add_user_info(ssn, address, phone, random.choice([True, False]))
    if new_user.isApproved:
        def generate_acct_num():
            return random.randint(11111111, 99999999)
        acct_num = generate_acct_num()
        while acct_num in [getattr(acct, 'acct_num', 0) for acct in users]:
            acct_num = generate_acct_num()
        balance = 0
        new_user.add_account_info(acct_num, balance)
    users.append(new_user)

peopletxt = 'username,password,first_name,last_name\n'
rolestxt = 'username,is_admin\n'
userstxt = 'ssn,username,address,phone,approved\n'
accountstxt = 'acct_num,ssn,balance\n'
testacctstxt = ''

for user in users:
    hashedpass = hash.sha256((user.password+pepper).encode()).hexdigest()
    peopletxt += f"{user.username},{hashedpass},{user.first_name},{user.last_name}\n"
    rolestxt += f"{user.username},{str(user.isAdmin).upper()}\n"
    if not user.isAdmin:
        hashedssn = hash.sha256((user.ssn+pepper).encode()).hexdigest()
        userstxt += f"{hashedssn},{user.username},\"{user.address}\",\"{user.phone}\",{str(user.isApproved).upper()}\n"
        if user.isApproved:
            accountstxt += f"{user.acct_num},{hashedssn},{user.balance:.2f}\n"
    testacctstxt += f"{user.first_name} {user.last_name}\n username: {user.username}\n password: {user.password}\n\n"

current_dir = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(current_dir, "people.txt")
with open(file_path, "w") as file:
    file.write(peopletxt)

file_path = os.path.join(current_dir, "roles.txt")
with open(file_path, "w") as file:
    file.write(rolestxt)

file_path = os.path.join(current_dir, "users.txt")
with open(file_path, "w") as file:
    file.write(userstxt)

file_path = os.path.join(current_dir, "accounts.txt")
with open(file_path, "w") as file:
    file.write(accountstxt)

file_path = os.path.join(current_dir, "testaccts.txt")
with open(file_path, "w") as file:
    file.write(testacctstxt)

