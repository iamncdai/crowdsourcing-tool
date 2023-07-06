from .Database import db
class PhanCongGanNhan(db.Model):
    __tablename__ = 'PhanCongGanNhan'
    idDuLieu = db.Column(db.String(100), primary_key=True)
    idNguoiGanNhan = db.Column(db.Integer, primary_key=True)
    TrangThai = db.Column(db.String(30))

    def __init__(self, idDuLieu, idNguoiGanNhan,TrangThai):
        self.idDuLieu = idDuLieu
        self.idNguoiGanNhan = idNguoiGanNhan
        self.TrangThai = TrangThai
        
