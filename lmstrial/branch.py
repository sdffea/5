from database import CursorFromConnectionFromPool
class Branch:
    def __init__(self,location,id, address):
        self.location=location
        self.address=address
        self.id=id
    def __repr__(self):
        return "Branch: {}\n{}".format(self.location,self.address)

    def new_branch(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('insert into public.branch(branch_name,branch_address) values(%s.%s);',(self.location,self.address))
    @classmethod
    def searchbranch(cls,id):
        with CursorFromConnectionFromPool() as cursor:
            print(type(id))
            cursor.execute("select branch_name, branch_address from public.branch where branch_id=%s",(id,))
            user_date=cursor.fetchone()
        return user_date