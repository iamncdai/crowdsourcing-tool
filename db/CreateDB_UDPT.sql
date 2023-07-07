-- DROP DATABASE crowdsourcing_tool;
-- CREATE DATABASE crowdsourcing_tool;
-- USE crowdsourcing_tool;

CREATE TABLE DuAn
(
    idDuAn INT AUTO_INCREMENT,
    TenDA NVARCHAR(1000) NOT NULL,
	idLoaiNhan varchar(100) NOT NULL,
    idQuanLi INT NOT NULL,
    CONSTRAINT PK_DA PRIMARY KEY (idDuAn)
);

CREATE TABLE VanBan
(
    idVanBan INT auto_increment,
	VanBan NVARCHAR(1000) NOT NULL,
    idNgonNgu INT,
    idDuLieu INT NOT NULL,
    idVanBan2_CauHoi INT,
    CONSTRAINT PK_VB PRIMARY KEY (idVanBan)
);

CREATE TABLE NgonNgu
(
    idNgonNgu INT auto_increment,
    NgonNgu NVARCHAR(30) NOT NULL,
    CONSTRAINT PK_NN PRIMARY KEY (idNgonNgu)
);

CREATE TABLE Nhan
(
    idNhan INT auto_increment,
    idDuLieu INT NOT NULL,
    idNguoiGanNhan INT NOT NULL,
    NoiDung NVARCHAR(1000),
    idNgonNgu INT,
    -- TrangThai INT check(TrangThai IN(1,2,3)),								-- 1: Pending	2: Approved		3: Rejected
    CONSTRAINT PK_N PRIMARY KEY (idNhan)
);

CREATE TABLE DuLieu
(
	idDuLieu int auto_increment,
    idDuAn int,
    CONSTRAINT PK_DL PRIMARY KEY (idDuLieu)
);

CREATE TABLE NguoiDung
(
    idUser INT auto_increment,
    UserName VARCHAR(30) UNIQUE NOT NULL,
    Password VARCHAR(200) NOT NULL,
    Hoten VARCHAR(30) NOT NULL,
    email VARCHAR(50),
    phoneNumber VARCHAR(10) unique,
    typeUser TINYINT check(typeUser IN(1,2)),							-- 2:Quan Li    1:Nguoi gan nhan
    LevelUser TINYINT,  check((typeUser = 2 AND LevelUser IS NULL) OR (typeUser = 1 AND LevelUser IN(1,2,3) AND LevelUser Is Not NULL)) ,
    CONSTRAINT PK_ND PRIMARY KEY (idUser)
);

CREATE TABLE PhanCongGanNhan
(
    idDuLieu INT,
    idNguoiGanNhan INT,
    TrangThai varchar(30) check (TrangThai IN('NONE', 'PENDING', 'DONE', 'APPROVED', 'REJECTED') AND TrangThai <> NULL),
    CONSTRAINT PK_PCGN PRIMARY KEY (idDuLieu, idNguoiGanNhan)
);

CREATE TABLE ThucThe
(
    idThucThe INT AUTO_INCREMENT,
    TenThucThe NVARCHAR(50) UNIQUE NOT NULL,
    CONSTRAINT PK_TT PRIMARY KEY (idThucThe)
);


CREATE TABLE ThucThe_Nhan
(
    idThucThe INT,
    idNhan INT,
    CONSTRAINT PK_TT_N PRIMARY KEY (idThucThe, idNhan)
);

CREATE TABLE CauHoiDongNghia
(
    idCauHoiDongNghia INT auto_increment,
    idNhan INT NOT NULL,
    CauHoi NVARCHAR(1000) NOT NULL,
    CONSTRAINT PK_CHDN PRIMARY KEY (idCauHoiDongNghia)
);

CREATE TABLE LoaiNhan
(
	idLoaiNhan varchar(100),
    LoaiNhan nvarchar(100) NOT NULL,
    CONSTRAINT PK_LN PRIMARY KEY (idLoaiNhan)
)
;

-- Tao khoa ngoai cho bang CauHoi
ALTER TABLE DuLieu ADD CONSTRAINT FK_DL_DA FOREIGN KEY (idDuAn) REFERENCES DuAn(idDuAn);
-- Tao khoa ngoai cho bang DuAn
ALTER TABLE DuAn 
ADD CONSTRAINT FK_DA_ND FOREIGN KEY (idQuanLi) REFERENCES NguoiDung(idUser),
ADD CONSTRAINT FK_DA_LN FOREIGN KEY (idLoaiNhan) REFERENCES LoaiNhan(idLoaiNhan);

-- Tao khoa ngoai cho bang VanBan
ALTER TABLE VanBan 
ADD CONSTRAINT FK_VB_DL FOREIGN KEY (idDuLieu) REFERENCES DuLieu(idDuLieu),
ADD CONSTRAINT FK_VB_VB FOREIGN KEY (idVanBan2_CauHoi) REFERENCES VanBan(idVanBan),
ADD CONSTRAINT FK_VB_NN FOREIGN KEY (idNgonNgu) REFERENCES NgonNgu(idNgonNgu);

ALTER TABLE PhanCongGanNhan 
ADD CONSTRAINT FK_PCGN_ND FOREIGN KEY (idNguoiGanNhan) REFERENCES NguoiDung(idUser),
ADD CONSTRAINT FK_PCGN_DL FOREIGN KEY (idDuLieu) REFERENCES DuLieu(idDuLieu);

-- Tao khoa ngoai cho bang ThucThe_Nhan
ALTER TABLE ThucThe_Nhan 
ADD CONSTRAINT FK_TT_N_TT FOREIGN KEY (idThucThe) REFERENCES ThucThe(idThucThe),
ADD CONSTRAINT FK_TT_N_N FOREIGN KEY (idNhan) REFERENCES Nhan(idNhan);

-- Tao khoa ngoai cho bang Nhan
ALTER TABLE Nhan ADD CONSTRAINT FK_N_PCGN FOREIGN KEY (idDuLieu, idNguoiGanNhan) REFERENCES PhanCongGanNhan(idDuLieu, idNguoiGanNhan);

-- Tao khoa ngoai cho bang CauHoiDongNghia
ALTER TABLE CauHoiDongNghia ADD CONSTRAINT FK_CHDN_N FOREIGN KEY (idNhan) REFERENCES Nhan(idNhan);
