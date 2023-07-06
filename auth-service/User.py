class User:
    def __init__(self, idUser, UserName, Password, Hoten, email, phoneNumber, typeUser, LevelUser):
        self.idUser = idUser
        self.UserName = UserName
        self.Password = Password
        self.Hoten = Hoten
        self.email = email
        self.phoneNumber = phoneNumber
        self.typeUser = typeUser
        self.LevelUser = LevelUser

    def get(self, field):
        return getattr(self, field, None)

    def to_dict(self):
        return {
            'idUser': self.idUser,
            'UserName': self.UserName,
            'Password': self.Password,
            'Hoten': self.Hoten,
            'email': self.email,
            'phoneNumber': self.phoneNumber,
            'typeUser': self.typeUser,
            'LevelUser': self.LevelUser
        }
