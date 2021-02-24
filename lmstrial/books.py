from database import CursorFromConnectionFromPool
from isbn_maker import makefunc as isbn_creator
import operator
import functools


def convertTuple(tup):
    str = functools.reduce(operator.add, (tup))
    return str

class Books:
    def __init__(self, isbn, copy_no, name, author, language, publisher, branch_id,edition):
        self.isbn = isbn
        self.copy_no = copy_no
        self.author = author
        self.edition=edition
        self.name = name
        self.language = language
        self.publisher = publisher
        self.issued_by = 0
        self.branch_id = branch_id

    def __repr__(self):
        return "Book: \n{}\n{} {}\n{}\n{}".format(self.isbn,
                                                  self.name,
                                                  self.author,
                                                  self.publisher,
                                                  self.language)
    @classmethod
    def newcopy(cls, isbn):
        with CursorFromConnectionFromPool() as crsor:
            crsor.execute("select COUNT(*) FROM public.books where isbn=%s;", (isbn,))
            rowcount = crsor.fetchone()[0]
            return rowcount
    @classmethod
    def newisbn(cls, name, author, publisher, language,edition):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                "select count(*) from public.books where name=%s and author=%s and publisher=%s and language=%s and edition=%s;",
                (name, author, publisher, language,edition))
            rowcount = cursor.fetchone()[0]
            if rowcount == 0:
                return isbn_creator()
            else:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(
                        'select * from public.books where name=%s and author=%s and publisher=%s and language=%s and edition=%s;',
                        (name, author, publisher, language,edition))
                    user_data = cursor.fetchone()
                    return user_data[0]



    def deletebook(self, isbn, copy_no):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("delete from public.books where books_pkey=%s;", (str(isbn) + str(copy_no)))




    @classmethod
    def search(cls, name='', isbn='', author='', language='', publisher='', edition=''):
        query = 'SEL'+'ECT DISTINCT (isbn, name, author, language, publisher, edition, branch_id) FROM public.books WHERE '

        count = 0
        if name != "":
            if count != 0:
                query = query + "and "

            data="name LIKE '%{}%' ".format(name)
            count += 1
            query = query + data
        if isbn != "":
            if count != 0:
                query = query + "and "

            data="isbn LIKE '%{}%' ".format(isbn)
            count += 1
            query = query + data
        if author != "":
            if count != 0:
                query = query + "and "

            data="author LIKE '%{}%' ".format(author)
            count += 1
            query = query + data
        if language != "":
            if count != 0:
                query = query + "and "

            data="language LIKE '%{}%' ".format(language)
            count += 1
            query = query + data
        if publisher != '':
            if count != 0:
                query = query + "and "

            data="publisher LIKE '%{}%' ".format(publisher)
            count += 1
            query = query + data
        if edition != '':
            if count != 0:
                query = query + "and "

            data="edition LIKE '%{}%' ".format(edition)
            count += 1
            query = query + data
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(query)
            user_data = cursor.fetchall()

        return user_data
    @classmethod
    def copiesavailable(cls,isbn):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                "select count(*) from public.books where isbn=%s and issued_by=0;",
                (isbn,))
            rowcount = cursor.fetchone()[0]
            if rowcount == 0:
                return False
            else:
                return True
    @classmethod
    def issuethis(cls,isbn):

            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select copy_no from public.books where isbn= %s and issued_by=0", (isbn,))
                strx = cursor.fetchone()
                strx = str(strx)

                strx = strx.replace('(', '')
                strx = strx.replace(')', '')
                strx = strx.replace(',', '')

                strx=int(strx)
                cursor.execute("update public.books set issued_by=1 where isbn=%s and copy_no=%s",(isbn,strx))
    @classmethod
    def returnthis(cls,isbn):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select copy_no from public.books where isbn= %s and issued_by=1", (isbn,))
            strx = cursor.fetchone()
            strx = str(strx)

            strx = strx.replace('(', '')
            strx = strx.replace(')', '')
            strx = strx.replace(',', '')

            strx = int(strx)

            cursor.execute("update public.books set issued_by=0 where isbn=%s and copy_no=%s",(isbn,strx))
