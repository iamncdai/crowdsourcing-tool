from .Database import db

class Nhan(db.Model):
    __tablename__ = 'Nhan'
    idNhan = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idDuLieu = db.Column(db.String(100), nullable=False)
    idNguoiGanNhan = db.Column(db.Integer, nullable=False)
    NoiDung = db.Column(db.String(1000))
    idNgonNgu = db.Column(db.Integer)

    def __init__(self, idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu,):
        self.idDuLieu = idDuLieu
        self.idNguoiGanNhan = idNguoiGanNhan
        self.NoiDung = NoiDung
        self.idNgonNgu = idNgonNgu