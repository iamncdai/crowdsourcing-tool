
insert into LoaiNhan (idLoaiNhan, LoaiNhan) values 
('Hoi_Dap', N'Hỏi đáp'),
('Tim_Cau_Hoi_Dong_Nghia', N'Tìm câu hỏi đồng nghĩa'),
('Cap_Cau_Hoi_Van_Ban', N'Gán nhãn câu trả lời của cặp câu hỏi và văn bản'),
('Gan_Nhan_Thuc_The', N'Gán nhãn thực thể'),
('Gan_Nhan_Cap_Van_Ban', N'Gán nhãn cặp văn bản (đồng nghĩa)'),
('Dich_May', N'Dịch máy'),
('Phan_Loai_Van_Ban', N'Phân loại văn bản');

insert into NguoiDung ( UserName, Password, Hoten, email, phoneNumber ,typeUser, LevelUser) values 
('admin1', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Merill', 'mwoffenden0@stumbleupon.com', '2847928376', 2, NULL),
('admin2', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Kit Pahl', 'kpahl1@blog.com', '4907682437', 2, NULL),
('admin3', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Jana Train', 'jtrain2@macromedia.com', '3933307263', 2, NULL),
('hungdoan', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Doan Nguyen Tan Hung', 'kdutton7@hibu.com', '1664045120', 1, 1),
('chanhdai', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Nguyen Chanh Dai', 'wnettleship8@nationalgeographic.com', '8528806294', 1, 2),
('anhtam', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Anh Tam', 'askaif9@addtoany.com', '9208448195', 1, 1),
('longle', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Nguyen Dai Long', 'mraymana@diigo.com', '5231213722', 1, 2),
('ahuller3', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Adolpho Huller', 'ahuller3@google.fr', '9008930127', 1, 2),
('lclaiton4', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Lissie Claiton', 'lclaiton4@yandex.ru', '6515355712', 1, 1),
('fmogford5', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Fedora Mogford', 'fmogford5@nps.gov', '6455550854', 1, 2),
('lmaudson6', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Lorelei Maudson', 'lmaudson6@sciencedaily.com', '3869762345', 1, 1),
('lzanussiib', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Luther Zanussii', 'lzanussiib@icio.us', '8032984816', 2, NULL),
('jsouthousec', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Joyann Southouse', 'jsouthousec@elegantthemes.com', '6189129050', 1, 1),
('mcorkerd', '$2b$12$mJ52rOqUG.KKX/gWEyE.kutiOglDwYlmSXAIS1Jz95CZ5wbf9v6AG', 'Madelon Corker', 'mcorkerd@sakura.ne.jp', '1264189065', 1, 1);


insert into DuAn (TenDA, idLoaiNhan, idQuanLi) values 
(N'Dự Án Ứng Dụng Phân Tán', 'Hoi_Dap', 3),
(N'Dự Án Gán Nhãn', 'Tim_Cau_Hoi_Dong_Nghia', 1),
(N'Dự Án AI', 'Cap_Cau_Hoi_Van_Ban', 1),
(N'Dự Án ChatGDT', 'Gan_Nhan_Thuc_The', 2),
(N'Dự Án HCMUS', 'Gan_Nhan_Cap_Van_Ban', 1),
(N'Dự Án Luận Văn Tốt Nghiệp', 'Dich_May', 3),
(N'Dự Án ABC', 'Hoi_Dap', 2),
(N'Dự Án Dịch lời bài hát', 'Dich_May', 1),
(N'Dự Án Robocon', 'Cap_Cau_Hoi_Van_Ban', 1),
(N'Dự Án Sate', 'Dich_May', 3),
(N'Dự Án Ứng Dụng Phân Tán new version', 'Hoi_Dap', 3),
(N'Dự Án HashTag', 'Tim_Cau_Hoi_Dong_Nghia', 2),
(N'Dự Án EmASI', 'Hoi_Dap', 1),
(N'Dự Án Chat AI', 'Gan_Nhan_Thuc_The', 1),
(N'Dự Án Ecorism', 'Phan_Loai_Van_Ban', 1),
(N'Dự Án Ecorism version 2', 'Phan_Loai_Van_Ban', 2);

insert into DuLieu (idDuAn) values
(1),
(2),
(3),
(4),
(5),
(6),
(7),
(8),
(9),
(10),
(11),
(12),
(13),
(14),
(15),
(16);


insert into NgonNgu (NgonNgu) values 
(N'Tiếng Việt'),
(N'English US'),
(N'English UK'),
(N'Portuguese'),
(N'Japanese'),
(N'French'),
(N'Chinese');

insert into VanBan (VanBan, idNgonNgu, idDuLieu, idVanBan2_CauHoi) values 
(N'1 + 1 = ?', 1, 1, NULL),
(N'1 + 1 = 2', 1, 1, 1),
(N'Ai đã đặt tên cho dòng sông', 1, 2, NULL),
(N'Hãy phân biệt các chất sau 3 lọ mất nhãn đựng dung dịch NaOH; H2SO4; Na2SO4', 1 ,3, NULL),
(N'Câu hỏi: 3 lọ mất nhãn đựng dung dịch NAOH, H2SO4,Na2SO4
Giải:
Lấy mẫu thử. Cho quỳ tím vào từng mẫu
- Mẫu làm cho quỳ tím hóa xanh là NaOH ( Bazơ làm quỳ tím hóa xanh )
- Mẫu làm cho quỳ tím hóa đỏ là H2SO4 ( Axit làm quỳ tím hóa đỏ )
- Mẫu mà quỳ tím không đổi màu là Na2SO4 ( Muối làm quỳ tím không đổi màu )
Đây là 1 cách giải cho câu hỏi này', 1, 3, 4),
(N'Mua túi Gucci tại Cresent Mall', 1, 4, NULL),
(N'Hôm qua tôi ăn cơm với cá', 1, 5, 2),
(N'Hôm qua tôi ăn cá với cơm', 1, 5, NULL),
(N'Hello', 2, 6, NULL),
(N'Hôm nay là thứ 7 phải không ?', 1, 7, NULL),
(N'Hôm nay có khách đến nhà', 1, 7, 10),
(N'Hôm nay là thứ 3', 1, 8, NULL),
(N'Este Metyl fomat có công thức là ?', 1, 9, NULL),
(N'Metyl fomat  có công thức hóa học là HCOOCH3, công thức phân tử là C2H4O2. Nó là một hóa chất hữu cơ , xuất hiện nhiều bài tập hóa học trung học phổ thông.', 1, 9, NULL),
(N' ありがとう', 5, 10, NULL),
(N'Một con lắc lò xo đang dao động điều hòa. Biên độ dao động phụ thuộc vào ?', 1, 11, NULL),
(N'Biên độ dao động phụ thuộc vào lực cưỡng bức', 1, 11, 16),
(N'Ai là triệu phú ?', 1, 12, NULL),
(N'How are you?', 1 ,13, NULL),
(N'I am fine. Thanks', 2, 13, 19),
(N'Lễ hội Festival AnualFes được tổ chức tại thành phố Vũng Tàu, tỉnh Bà rịa - Vũng Tàu với sự có mặt của DJ Mie', 1, 14, NULL),
(N'Hôm nay toàn bộ nhân viên được nghỉ', 1, 15, NULL),
(N'Câu hát căng buồm với gió khơi,
Đoàn thuyền chạy đua cùng mặt trời.
Mặt trời đội biển nhô màu mới,
Mắt cá huy hoàng muôn dặm phơi.', 1, 16, NULL);


insert into PhanCongGanNhan (idDuLieu, idNguoiGanNhan, TrangThai) values 
(1,4, 'PENDING'),
(1,5, 'REJECTED'),
(2,7, 'PENDING'),
(3,5, 'APPROVED'),
(4,6, 'NONE'),
(4,7, 'APPROVED'),
(4,8, 'REJECTED'),
(5,4, 'REJECTED'),
(5,5, 'APPROVED'),
(6,6, 'PENDING'),
(7,5, 'PENDING'),
(8,9, 'APPROVED'),
(9,6, 'APPROVED'),
(10,10, 'APPROVED'),
(10,11, 'DONE'),
(11,14, 'REJECTED'),
(12,8, 'REJECTED'),
(13,9, 'APPROVED'),
(14,5, 'PENDING'),
(14,9, 'APPROVED'),
(15,8, 'APPROVED'),
(16,11, 'APPROVED');

insert into Nhan (idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu) values 
(1,4, N'Có', 1),
(1,5, N'Không', 1),
(2,7, NULL, NULL),
(3,5, N'Lấy mẫu thử. Cho quỳ tím vào từng mẫu
- Mẫu làm cho quỳ tím hóa xanh là NaOH ( Bazơ làm quỳ tím hóa xanh )
- Mẫu làm cho quỳ tím hóa đỏ là H2SO4 ( Axit làm quỳ tím hóa đỏ )
- Mẫu mà quỳ tím không đổi màu là Na2SO4 ( Muối làm quỳ tím không đổi màu )', 1),
-- (4,6),
(4,7, NULL, NULL),
(4,8, NULL, NULL),
(5,4, N'Không', 1),
(5,5, N'Có', 1),
(6,6, N'Xin chào', 1),
(7,5, N'Không', 1),
(8,9, N'Today is Tuesday', 2),
(9,6, N'Metyl fomat  có công thức hóa học là HCOOCH3', 1),
(10,10, N'Thank you', 2),
-- (10,11),
(11,14, N'Có', 1),
(12,8, NULL, NULL),
(13,9, N'Có', 1),
(14,5, NULL, NULL),
(14,9, NULL, NULL),
(15,8, N'Thông báo', 1),
(16,11, N'Thơ', 1);

insert into ThucThe (TenThucThe) values
(N'Lễ hội'),
(N'Festival'),
(N'AnualFes'),
(N'VungTau'),
(N'Trip'),
(N'Chemisty'),
(N'Leave'),
(N'AngryBird'),
(N'Excel'),
(N'Office'),
(N'Thơ'),
(N'Truyện'),
(N'Ca dao'),
(N'Rap Việt'),
(N'Kellie'),
(N'Thông báo'),
(N'Notification'),
(N'Gucci'),
(N'Dior'),
(N'Chanel'),
(N'Cresent Mall'),
(N'HoChiMinhCity'),
(N'HCMUS'),
(N'UDPT'),
(N'MySQL'),
(N'Python')
;

insert into ThucThe_Nhan (idThucThe, idNhan) values
(17, 5),
(18, 5),
(21, 5),
(1, 17),
(2, 17),
(3, 17),
(4, 17);

insert into CauHoiDongNghia (idNhan, CauHoi) values
(3, N'Sông Hương do ai đặt tên ?'),
(3, N'Ai đặt tên cho sông Hương'),
(15, N'Ai là người giàu ?'),
(15, N'Phạm Nhật Vượng có phải triệu phú không ?'),
(15, N'Ai là tỷ phú ?')
;
