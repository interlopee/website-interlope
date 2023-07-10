from app import db, User

username = "interlope"
password = "bismillah2023"
level = "Admin"
db.session.add(User(username,password,level))
db.session.commit()
