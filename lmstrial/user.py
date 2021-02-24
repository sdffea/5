from database import CursorFromConnectionFromPool


class User:
    def __init__(self, email, first_name, id, last_name, phone_number, password):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.id = id
        self.password = password


    def __repr__(self):
        return "User: \n{}\n{} {}\n{}\n{}".format(self.email,
                                                  self.first_name,
                                                  self.last_name,
                                                  self.id,
                                                  self.phone_number)

    def new_user(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                'INSERT INTO users(first_name, last_name,email,phone_number,password,admintest,returndate,issuedbyisbn) VALUES (%s,%s,%s,%s,%s,FALSE,0,0);',
                (self.first_name, self.last_name, self.email, self.phone_number, self.password))

    def assignid(self, email):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from public.users where email=%s;', (email,))
            user_data = cursor.fetchone()
            return user_data[1]

    @classmethod
    def get_user_by_email(cls, email):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from public.users where email=%s;', (email,))
            user_data = cursor.fetchone()
            return cls(email=user_data[3],
                       first_name=user_data[2],
                       last_name=user_data[0],
                       id=user_data[1],
                       phone_number=user_data[4],
                       password=user_data[5])
    @classmethod
    def check_user(cls, email, password):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from public.users where email=%s and password=%s;",(email,password))

            user_data=cursor.fetchone()
            if user_data !=None:
                return True
            else:
                return False
    @classmethod
    def check_admin(cls,email,password):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from public.users where email=%s and password=%s and admintest=TRUE ;",(email,password))
            user_data=cursor.fetchone()
            if user_data==None:
                return False
            else:
                return True
    @classmethod
    def get_all_users(cls):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from public.users")
            user_data=cursor.fetchall()
        return user_data