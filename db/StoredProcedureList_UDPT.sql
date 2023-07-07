USE UDPT_G8;

DELIMITER //
create procedure sp_Xem_DuAn(IN p_iduser int)
BEGIN
DECLARE Role int;
SELECT @Role := TypeUser FROM NguoiDung WHERE idUser = @p_iduser;
IF (@Role = 2)
THEN
-- Câu cho Quản Lí
SELECT  DA.idDuAn, DA.TenDA, LN.idLoaiNhan, LN.LoaiNhan 
FROM DuAn DA 
JOIN LoaiNhan LN ON LN.idLoaiNhan = DA.idLoaiNhan
ORDER BY DA.idDuAn;
END IF;
IF (@Role = 1)
THEN
-- Câu cho Người Gán Nhãn
SELECT DA.IDDuAn, DA.TenDA, LN.IDLoaiNhan, LN.LoaiNhan 
FROM DuAn DA 
JOIN LoaiNhan LN ON LN.IDLoaiNhan = DA.IDLoaiNhan
JOIN DuLieu DL ON DL.IDDuAn = DA.IDDuAn
JOIN PhanCongGanNhan PC ON PC.IDDuLieu = DL.IDDuLieu 
WHERE PC.IDNguoiGanNhan = @p_iduser
ORDER BY DA.IDDuAn;
END IF;
END //
DELIMITER //

DELIMITER //
create procedure sp_Them_DuLieu_PhanLoaiVanBan(IN idduan int, IN vanban nvarchar(1000))
BEGIN
INSERT INTO DuLieu (IDDuAn) VALUES (@idduan);
SELECT @IDDuLieu := IDDuLieu FROM DuLieu ORDER BY IDDuLieu DESC LIMIT 1;
INSERT INTO VanBan (VanBan, IDNgonNgu, IDDuLieu, IDVanBan2_CauHoi) VALUES (@vanban, 1, @IDDuLieu, NULL);
END //
DELIMITER //

DELIMITER //
create procedure sp_Them_PhanCong(IN p_iduser int)
BEGIN
SELECT @idDuLieu := idDuLieu FROM DuLieu ORDER BY idDuLieu DESC LIMIT 1;
INSERT INTO PhanCongGanNhan (idDuLieu, idNguoiGanNhan, TrangThai) VALUES ( @idDuLieu, p_iduser, 'NONE');
END //
DELIMITER //


DELIMITER //
create procedure sp_Xem_ChiTietGanNhan(IN p_iduser int, IN p_iddulieu int)
BEGIN
SELECT @IDLoaiNhan := LN.idLoaiNhan 
FROM DuLieu DL 
JOIN DuAn DA ON DL.IDDuAn = DA.idDuAn
JOIN LoaiNhan LN ON LN.idLoaiNhan = DA.idLoaiNhan
WHERE DL.IDDuLieu = p_iddulieu;
IF (@IDLoaiNhan = 'Phan_Loai_Van_Ban')
THEN
SELECT ND.UserName, ND.Hoten, VB.VanBan, N.NoiDung, PC.TrangThai
FROM Nhan N
JOIN PhanCongGanNhan PC ON N.idDuLieu = PC.idDuLieu AND N.idNguoiGanNhan = PC.idNguoiGanNhan
JOIN NguoiDung ND ON ND.idUser = PC.idNguoiGanNhan
JOIN DuLieu DL ON PC.idDuLieu = DL.IDDuLieu
JOIN VanBan VB ON VB.idDuLieu = DL.IDDuLieu
WHERE DL.IDDuLieu = p_iddulieu  AND ND.idUser = p_iduser;
END IF;
IF (@IDLoaiNhan = 'Hoi_Dap' OR @IDLoaiNhan = 'Cap_Cau_Hoi_Van_Ban')
THEN
SELECT ND.UserName, ND.Hoten, CH.VanBan CauHoi, VB.VanBan, N.NoiDung, PC.TrangThai
FROM Nhan N
JOIN PhanCongGanNhan PC ON N.idDuLieu = PC.idDuLieu AND N.idNguoiGanNhan = PC.idNguoiGanNhan
JOIN NguoiDung ND ON ND.idUser = PC.idNguoiGanNhan
JOIN DuLieu DL ON PC.idDuLieu = DL.IDDuLieu
JOIN VanBan VB ON VB.idDuLieu = DL.IDDuLieu AND VB.idVanBan2_CauHoi IS NOT NULL
JOIN VanBan CH ON VB.idVanBan2_CauHoi = CH.idVanBan
WHERE DL.IDDuLieu = p_iddulieu AND ND.idUser = p_iduser;
END IF;
IF (@IDLoaiNhan = 'Dich_May')
THEN
SELECT ND.UserName, ND.Hoten, VB.VanBan, NNGoc.NgonNgu, N.NoiDung, NNDich.NgonNgu, PC.TrangThai
FROM Nhan N
JOIN PhanCongGanNhan PC ON N.idDuLieu = PC.idDuLieu AND N.idNguoiGanNhan = PC.idNguoiGanNhan
JOIN NguoiDung ND ON ND.idUser = PC.idNguoiGanNhan
JOIN DuLieu DL ON PC.idDuLieu = DL.IDDuLieu
JOIN VanBan VB ON VB.idDuLieu = DL.IDDuLieu
JOIN NgonNgu NNGoc ON VB.idNgonNgu = NNGoc.idNgonNgu
JOIN NgonNgu NNDich ON N.idNgonNgu = NNDich.idNgonNgu
WHERE DL.IDDuLieu = p_iddulieu AND ND.idUser = p_iduser;
END IF;
IF (@IDLoaiNhan = 'Tim_Cau_Hoi_Dong_Nghia')
THEN
SELECT ND.UserName, ND.Hoten, VB.VanBan CauHoi, PC.TrangThai
FROM Nhan N
JOIN PhanCongGanNhan PC ON N.IDDuLieu = PC.IDDuLieu AND N.idNguoiGanNhan = PC.idNguoiGanNhan
JOIN NguoiDung ND ON ND.idUser = PC.IDNguoiGanNhan
JOIN DuLieu DL ON PC.IDDuLieu = DL.IDDuLieu
JOIN VanBan VB ON VB.IDDuLieu = DL.IDDuLieu
WHERE DL.IDDuLieu = p_iddulieu AND ND.idUser = p_iduser;

SELECT CHDN.CauHoi CauHoiDongNghia
FROM CauHoiDongNghia CHDN
JOIN Nhan N ON N.IDNhan = CHDN.IDNhan
WHERE N.idDuLieu = p_iddulieu AND N.idNguoiGanNhan = p_iduser;
END IF;
IF (@IDLoaiNhan = 'Gan_Nhan_Thuc_The')
THEN
SELECT ND.UserName, ND.Hoten, VB.VanBan, PC.TrangThai
FROM Nhan N
JOIN PhanCongGanNhan PC ON N.IDDuLieu = PC.IDDuLieu AND N.idNguoiGanNhan = PC.idNguoiGanNhan
JOIN NguoiDung ND ON ND.idUser = PC.IDNguoiGanNhan
JOIN DuLieu DL ON PC.IDDuLieu = DL.IDDuLieu
JOIN VanBan VB ON VB.IDDuLieu = DL.IDDuLieu
WHERE DL.IDDuLieu = p_iddulieu AND ND.idUser = p_iduser;

SELECT CHDN.CauHoi CauHoiDongNghia
FROM ThucThe TT
JOIN ThucThe_Nhan TTN ON TT.IDThucThe = TTN.IDThucThe
JOIN Nhan N ON N.IDNhan = TTN.IDNhan
WHERE N.idDuLieu = p_iddulieu AND N.idNguoiGanNhan = p_iduser;
END IF;
IF (@IDLoaiNhan = 'Gan_Nhan_Cap_Van_Ban')
THEN
SELECT ND.UserName, ND.Hoten, VB.VanBan VanBan1, VB2.VanBan VanBan2, N.NoiDung, PC.TrangThai
FROM Nhan N
JOIN PhanCongGanNhan PC ON N.idDuLieu = PC.idDuLieu AND N.idNguoiGanNhan = PC.idNguoiGanNhan
JOIN NguoiDung ND ON ND.idUser = PC.idNguoiGanNhan
JOIN DuLieu DL ON PC.idDuLieu = DL.IDDuLieu
JOIN VanBan VB ON VB.idDuLieu = DL.IDDuLieu AND VB.idVanBan2_CauHoi IS NOT NULL
JOIN VanBan VB2 ON VB.idVanBan2_CauHoi = VB2.idVanBan
WHERE DL.IDDuLieu = p_iddulieu AND ND.idUser = p_iduser;
END IF;
END //
DELIMITER //

DELIMITER //
create procedure sp_Them_DuLieu_HoiDap(IN p_idduan int, IN p_vanban nvarchar(1000), IN p_cauhoi nvarchar(1000))
BEGIN
INSERT INTO DuLieu (IDDuAn) VALUES (p_idduan);

SELECT @IDDuLieu := idDuLieu FROM DuLieu ORDER BY idDuLieu DESC LIMIT 1;
INSERT INTO VanBan (VanBan, idNgonNgu, idDuLieu, idVanBan2_CauHoi) VALUES (p_cauhoi, 1, @IDDuLieu, NULL);

SELECT @IDCauHoi := idVanBan FROM VanBan ORDER BY idVanBan DESC LIMIT 1;
INSERT INTO VanBan (VanBan, idNgonNgu, idDuLieu, idVanBan2_CauHoi) VALUES (p_vanban, 1, @IDDuLieu, @IDCauHoi);
END //
DELIMITER //

DELIMITER //
create procedure sp_Them_DuLieu_DichMay(IN p_idduan int, IN p_vanban nvarchar(1000), IN p_idngonngu int)
BEGIN
INSERT INTO DuLieu (IDDuAn) VALUES (p_idduan);

SELECT @IDDuLieu := IDDuLieu FROM DuLieu ORDER BY IDDuLieu DESC LIMIT 1;
INSERT INTO VanBan (VanBan, idNgonNgu, idDuLieu, idVanBan2_CauHoi) VALUES (p_vanban, p_idngonngu, @IDDuLieu, NULL);
END //
DELIMITER //

DELIMITER //
create procedure sp_Them_DuLieu_GanNhanThucThe(IN p_idduan int, IN p_vanban nvarchar(1000))
BEGIN
INSERT INTO DuLieu (IDDuAn) VALUES (p_idduan);

SELECT @IDDuLieu := IDDuLieu FROM DuLieu ORDER BY IDDuLieu DESC LIMIT 1;
INSERT INTO VanBan (VanBan, idNgonNgu, idDuLieu, idVanBan2_CauHoi) VALUES (p_vanban, 1, @IDDuLieu, NULL);
END //
DELIMITER //

DELIMITER //
create procedure sp_Them_DuLieu_GanNhanCapVanBan(IN p_idduan int, IN p_vanban1 nvarchar(1000), IN p_vanban2 nvarchar(1000))
BEGIN
INSERT INTO DuLieu (IDDuAn) VALUES (p_idduan);

SELECT @IDDuLieu := IDDuLieu FROM DuLieu ORDER BY IDDuLieu DESC LIMIT 1;
INSERT INTO VanBan (VanBan, idNgonNgu, idDuLieu, idVanBan2_CauHoi) VALUES (p_vanban2, 1, @IDDuLieu, NULL);
SELECT @IDVanBan := idVanBan FROM VanBan ORDER BY idVanBan DESC LIMIT 1;
INSERT INTO VanBan (VanBan, idNgonNgu, idDuLieu, idVanBan2_CauHoi) VALUES (p_vanban1, 1, @IDDuLieu, @IDVanBan);
END //
DELIMITER //

DELIMITER //
create procedure sp_Them_DuLieu_CapCauHoiVanBan(IN p_idduan int, IN p_vanban nvarchar(1000), IN p_cauhoi nvarchar(1000))
BEGIN
INSERT INTO DuLieu (IDDuAn) VALUES (p_idduan);

SELECT @IDDuLieu := IDDuLieu FROM DuLieu ORDER BY IDDuLieu DESC LIMIT 1;
INSERT INTO VanBan (VanBan, idNgonNgu, idDuLieu, idVanBan2_CauHoi) VALUES (p_cauhoi, 1, @IDDuLieu, NULL);
SELECT @IDVanBan := idVanBan FROM VanBan ORDER BY idVanBan DESC LIMIT 1;
INSERT INTO VanBan (VanBan, idNgonNgu, idDuLieu, idVanBan2_CauHoi) VALUES (p_vanban, 1, @IDDuLieu, @IDVanBan);
END //
DELIMITER //

DELIMITER //
create procedure sp_Them_DuLieu_CauHoiDongNghia(IN p_idduan int, IN p_cauhoi nvarchar(1000))
BEGIN
INSERT INTO DuLieu (IDDuAn) VALUES (p_idduan);

SELECT @IDDuLieu := IDDuLieu FROM DuLieu ORDER BY IDDuLieu DESC LIMIT 1;
INSERT INTO VanBan (VanBan, idNgonNgu, idDuLieu, idVanBan2_CauHoi) VALUES (p_cauhoi, 1, @IDDuLieu, NULL);
END //
DELIMITER //

DELIMITER //
create procedure sp_Them_Nhan_ThucThe(IN p_idThucThe int)
BEGIN
-- Chỗ này anh chạy câu riêng để lấy IDNhan cho câu INSERT ở dưới
SELECT @IDNhan := IDNhan FROM Nhan ORDER BY IDNhan DESC LIMIT 1;

-- Chỗ này anh viết loop chạy riêng nhe: input Ds ThựcTap:[IDThucThe, IDThucThe,...], @IDNhan
INSERT INTO ThucThe_Nhan VALUES (p_idThucThe, @IDNhan);
END //
DELIMITER //

DELIMITER //
create procedure sp_Them_Nhan_CauHoiDongNghia(IN p_CauHoiDongNghia nvarchar(1000))
BEGIN
-- Chỗ này anh chạy câu riêng để lấy IDNhan cho câu INSERT ở dưới
SELECT @IDNhan := IDNhan FROM Nhan ORDER BY IDNhan DESC LIMIT 1;

-- Chỗ này anh viết loop chạy riêng nhe: input Ds ThựcTap:[IDThucThe, IDThucThe,...], @IDNhan
INSERT INTO ThucThe_Nhan VALUES (@IDNhan, p_CauHoiDongNghia);
END //
DELIMITER //

DELIMITER //
create procedure sp_Sua_TrangThai_PhanCongGanNhan(IN p_idDuLieu int, IN p_idNguoiDung int, IN p_TrangThai varchar(50))
BEGIN
UPDATE PhanCongGanNan
SET TrangThai = p_TrangThai
WHERE idDuLieu = p_idDuLieu AND idNguoiGanNhan = p_idNguoiDung;
END //
DELIMITER //

