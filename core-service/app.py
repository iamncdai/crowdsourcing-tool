import csv
# from flask_sqlalchemy import SQLAlchemy
import json
import logging
import os
import uuid
from functools import wraps

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from models.CauHoiDongNghia import CauHoiDongNghia
from models.Database import db
from models.DuAn import DuAn
from models.DuLieu import DuLieu
from models.LoaiNhan import LoaiNhan
from models.NgonNgu import NgonNgu
from models.NguoiDung import NguoiDung
from models.Nhan import Nhan
from models.PhanCongGanNhan import PhanCongGanNhan
from models.ThucThe import ThucThe
from models.ThucThe_Nhan import ThucThe_Nhan
from models.VanBan import VanBan
from sqlalchemy import and_

load_dotenv()

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def authenticate_token(token):
    auth_service_url = "http://auth_service:5000/auth-service/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(auth_service_url, headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        return user_info
    else:
        return None


def authenticated(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Missing token'}), 401

        token = token.split()[1] if len(token.split()) == 2 else token

        user = authenticate_token(token)

        if user is None:
            return jsonify({'message': 'User does not exist'}), 401

        request.user = user

        return f(*args, **kwargs)

    return decorated


@app.route('/core-service/du-an/them', methods=['POST'])
@authenticated
def create_duan():
    try:
        user = request.user.get('idUser')
        data = request.get_json()
        TenDA = data['tenDuAn']
        idLoaiNhan = data['idLoaiNhan']
        idQuanLi = user

        duan = DuAn(TenDA=TenDA, idLoaiNhan=idLoaiNhan, idQuanLi=idQuanLi)
        db.session.add(duan)
        db.session.commit()

        # duan_info = {
        #     'idDuAn': duan.idDuAn,
        #     'TenDA': duan.TenDA,
        #     'idLoaiNhan': duan.idLoaiNhan,
        #     'idQuanLi': duan.idQuanLi
        # }

        return jsonify({'status': 'success', 'message': 'Dự án đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/du-an/danh-sach', methods=['GET'])
@authenticated
def get_danhsachduan():
    try:
        user_id = request.user.get('idUser')
        user = NguoiDung.query.get(user_id)

        if user.typeUser == 1:
            duan_list = db.session.query(DuAn.idDuAn, DuAn.TenDA, LoaiNhan.idLoaiNhan, LoaiNhan.LoaiNhan)\
                .join(PhanCongGanNhan, PhanCongGanNhan.idDuLieu == DuLieu.idDuLieu)\
                .join(NguoiDung, NguoiDung.idUser == PhanCongGanNhan.idNguoiGanNhan)\
                .join(LoaiNhan, LoaiNhan.idLoaiNhan == DuAn.idLoaiNhan)\
                .filter(NguoiDung.typeUser == 1).all()
        elif user.typeUser == 2:
            duan_list = db.session.query(DuAn.idDuAn, DuAn.TenDA, LoaiNhan.idLoaiNhan, LoaiNhan.LoaiNhan)\
                .join(LoaiNhan, LoaiNhan.idLoaiNhan == DuAn.idLoaiNhan)\
                .filter(DuAn.idQuanLi == user_id)\
                .all()
        else:
            return jsonify({'status': 'error', 'message': 'Loại người dùng không hợp lệ!'}), 400

        response = []
        for item in duan_list:
            project_data = {
                'idDuAn': item.idDuAn,
                'TenDA': item.TenDA,
                'idLoaiNhan': item.idLoaiNhan,
                'LoaiNhan': item.LoaiNhan,
            }
            response.append(project_data)

        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/du-an/<int:idDuAn>/chi-tiet', methods=['GET'])
@authenticated
def get_duan_chitiet(idDuAn):
    try:
        duan = db.session.query(DuAn.idDuAn, DuAn.TenDA, LoaiNhan.idLoaiNhan, LoaiNhan.LoaiNhan)\
            .join(LoaiNhan, LoaiNhan.idLoaiNhan == DuAn.idLoaiNhan)\
            .filter(DuAn.idDuAn == idDuAn)\
            .first()

        response = {
            'idDuAn': duan.idDuAn,
            'TenDA': duan.TenDA,
            'idLoaiNhan': duan.idLoaiNhan,
            'LoaiNhan': duan.LoaiNhan,
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/them-nguoidung-duan', methods=['POST'])
def them_nguoidung_duan():
    try:
        data = request.get_json()
        idDuAn = data.get('idDuAn')
        idNguoiGanNhan = data.get('idNguoiGanNhan')

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/du-an/<int:idDuAn>/ds-phancong', methods=['GET'])
@authenticated
def get_dulieuphancong(idDuAn):
    try:
        user_id = request.user.get('idUser')
        user = NguoiDung.query.get(user_id)
        duan = DuAn.query.get(idDuAn)
        # dulieutest = DuLieu.query.filter(DuLieu.idDuAn == idDuAn).all()

        if user.typeUser == 2:
            if duan.idQuanLi != user_id:
                return jsonify({'status': 'error', 'message': 'Người dùng không được quản lý dự án'}), 400
            dulieu = DuLieu.query.filter_by(idDuAn=idDuAn).all()
        elif user.typeUser == 1:
            phancong = PhanCongGanNhan.query.filter_by(
                idNguoiGanNhan=user_id).first()
            if phancong is None:
                return jsonify({'status': 'error', 'message': 'Người dùng không được phân công trong dự án!'}), 400

            dulieu = DuLieu.query.filter(DuLieu.idDuAn == idDuAn).all()
        else:
            return jsonify({'status': 'error', 'message': 'Loại người dùng không hợp lệ!'}), 400

        vanban_list = []
        for du_lieu in dulieu:
            vanban = VanBan.query.filter_by(
                idDuLieu=du_lieu.idDuLieu, idVanBan2_CauHoi=None).all()
            phancong = PhanCongGanNhan.query.filter_by(
                idDuLieu=du_lieu.idDuLieu).all()
            for vb in vanban:
                for pc in phancong:
                    nguoidung = NguoiDung.query.filter_by(
                        idUser=pc.idNguoiGanNhan).first()
                    vanban_data = {
                        '_id': str(uuid.uuid4()),
                        'idDuAn': duan.idDuAn,
                        'tenDuAn': duan.TenDA,
                        'idDuLieu': du_lieu.idDuLieu,
                        'vanBan': vb.VanBan,
                        'trangThai': pc.TrangThai,
                        'HoTen': nguoidung.Hoten
                    }
                    vanban_list.append(vanban_data)
        return jsonify(vanban_list)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/du-an/<int:idDuAn>/ds-du-lieu', methods=['GET'])
@authenticated
def get_dulieuduan(idDuAn):
    try:
        user_id = request.user.get('idUser')
        user = NguoiDung.query.get(user_id)
        duan = DuAn.query.get(idDuAn)
        # dulieutest = DuLieu.query.filter(DuLieu.idDuAn == idDuAn).all()

        if user.typeUser == 2:
            if duan.idQuanLi != user_id:
                return jsonify({'status': 'error', 'message': 'Người dùng không được quản lý dự án'}), 400
            dulieu = DuLieu.query.filter_by(idDuAn=idDuAn).all()
        elif user.typeUser == 1:
            phancong = PhanCongGanNhan.query.filter_by(
                idNguoiGanNhan=user_id).first()
            if phancong is None:
                return jsonify({'status': 'error', 'message': 'Người dùng không được phân công trong dự án!'}), 400

            dulieu = DuLieu.query.filter(DuLieu.idDuAn == idDuAn).all()
        else:
            return jsonify({'status': 'error', 'message': 'Loại người dùng không hợp lệ!'}), 400

        vanban_list = []
        for du_lieu in dulieu:
            vanban = VanBan.query.filter_by(
                idDuLieu=du_lieu.idDuLieu, idVanBan2_CauHoi=None).all()
            phancong = PhanCongGanNhan.query.filter_by(
                idDuLieu=du_lieu.idDuLieu).all()

            for vb in vanban:
                vanban_data = {
                    '_id': str(uuid.uuid4()),
                    'idDuAn': duan.idDuAn,
                    'tenDuAn': duan.TenDA,
                    'idLoaiNhan': duan.idLoaiNhan,
                    'idDuLieu': du_lieu.idDuLieu,
                    'vanBan': vb.VanBan,
                    'dsPhanCong': [NguoiDung.query.get(phan_cong.idNguoiGanNhan).Hoten for phan_cong in phancong]
                }
                vanban_list.append(vanban_data)
        return jsonify(vanban_list)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/ds-phancong', methods=['GET'])
def get_ds_phancong():
    try:
        ds_phancong = NguoiDung.query.filter_by(typeUser=1).all()
        response = []
        for user in ds_phancong:
            user_data = {
                'idUser': user.idUser,
                'HoTen': user.Hoten,
                'userName': user.UserName
            }
            response.append(user_data)

        return jsonify(response)
    except Exception as e:
        return jsonify({'success': False, 'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/ds-ngonngu', methods=['GET'])
def get_ds_ngonngu():
    try:
        ds_ngonngu = NgonNgu.query.all()
        response = []
        for ngonngu in ds_ngonngu:
            ngonngu_data = {
                'idNgonNgu': ngonngu.idNgonNgu,
                'NgonNgu': ngonngu.NgonNgu,
            }
            response.append(ngonngu_data)

        return jsonify(response)
    except Exception as e:
        return jsonify({'success': False, 'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/du-lieu/ds-cong-viec', methods=['GET'])
@authenticated
def get_ds_nhiemvu():
    try:
        idUser = request.user.get('idUser')
        user = NguoiDung.query.get(idUser)

        if user.LevelUser == 1:
            du_lieu_can_duyet = db.session.query(DuAn.idDuAn, DuAn.TenDA, DuLieu.idDuLieu, VanBan.VanBan, VanBan.idVanBan2_CauHoi, PhanCongGanNhan.TrangThai, NguoiDung.Hoten)\
                .join(DuLieu, DuAn.idDuAn == DuLieu.idDuAn)\
                .join(PhanCongGanNhan, PhanCongGanNhan.idDuLieu == DuLieu.idDuLieu)\
                .join(NguoiDung, NguoiDung.idUser == PhanCongGanNhan.idNguoiGanNhan)\
                .join(VanBan, VanBan.idDuLieu == DuLieu.idDuLieu)\
                .filter(PhanCongGanNhan.idNguoiGanNhan == idUser, VanBan.idVanBan2_CauHoi == None)\
                .all()

        elif user.LevelUser == 2:
            du_lieu_can_duyet = db.session.query(DuAn.idDuAn, DuAn.TenDA, DuLieu.idDuLieu, VanBan.VanBan, PhanCongGanNhan.TrangThai, NguoiDung.Hoten)\
                .join(DuLieu, DuAn.idDuAn == DuLieu.idDuAn)\
                .join(PhanCongGanNhan, PhanCongGanNhan.idDuLieu == DuLieu.idDuLieu)\
                .join(NguoiDung, NguoiDung.idUser == PhanCongGanNhan.idNguoiGanNhan)\
                .join(VanBan, VanBan.idDuLieu == DuLieu.idDuLieu)\
                .filter(DuLieu.idDuAn == DuAn.idDuAn, PhanCongGanNhan.TrangThai == 'DONE', VanBan.idVanBan2_CauHoi == None)\
                .all()
        else:
            return jsonify({'success': False, 'status': 'error', 'message': 'Loại người dùng không hợp lệ!'}), 400

        response = []
        for item in du_lieu_can_duyet:
            du_an_data = {
                '_id': str(uuid.uuid4()),
                'idDuAn': item.idDuAn,
                'tenDuAn': item.TenDA,
                'idDuLieu': item.idDuLieu,
                'vanBan': item.VanBan,
                'trangThai': item.TrangThai,
                'phanCong': item.Hoten
            }
            response.append(du_an_data)

        return jsonify(response)
    except Exception as e:
        return jsonify({'success': False, 'status': 'error', 'message': str(e)}), 400

@app.route('/core-service/du-lieu/ds-can-duyet', methods=['GET'])
@authenticated
def get_ds_can_duyet():
    try:
        idUser = request.user.get('idUser')
        user = NguoiDung.query.get(idUser)

        # user.LevelUser == 1:
        #     du_lieu_can_duyet = db.session.query(DuAn.idDuAn, DuAn.TenDA, DuLieu.idDuLieu, VanBan.VanBan, PhanCongGanNhan.TrangThai, NguoiDung.Hoten)\
        #         .join(DuLieu, DuAn.idDuAn == DuLieu.idDuAn)\
        #         .join(PhanCongGanNhan, PhanCongGanNhan.idDuLieu == DuLieu.idDuLieu)\
        #         .join(NguoiDung, NguoiDung.idUser == PhanCongGanNhan.idNguoiGanNhan)\
        #         .join(VanBan, VanBan.idDuLieu == DuLieu.idDuLieu)\
        #         .filter(PhanCongGanNhan.idNguoiGanNhan == idUser)\
        #         .all()

        # elif

        if user.LevelUser == 2:
            du_lieu_can_duyet = db.session.query(DuAn.idDuAn, DuAn.TenDA, DuLieu.idDuLieu, VanBan.VanBan, PhanCongGanNhan.TrangThai, NguoiDung.Hoten)\
                .join(DuLieu, DuAn.idDuAn == DuLieu.idDuAn)\
                .join(PhanCongGanNhan, PhanCongGanNhan.idDuLieu == DuLieu.idDuLieu)\
                .join(NguoiDung, NguoiDung.idUser == PhanCongGanNhan.idNguoiGanNhan)\
                .join(VanBan, VanBan.idDuLieu == DuLieu.idDuLieu)\
                .filter(DuLieu.idDuAn == DuAn.idDuAn, PhanCongGanNhan.TrangThai != 'DONE')\
                .all()
        else:
            return jsonify({'success': False, 'status': 'error', 'message': 'Loại người dùng không hợp lệ!'}), 400

        response = []
        for item in du_lieu_can_duyet:
            if item.TrangThai != "APPROVED":
                du_an_data = {
                    'idDuAn': item.idDuAn,
                    'tenDuAn': item.TenDA,
                    'idDuLieu': item.idDuLieu,
                    'vanBan': item.VanBan,
                    'trangThai': item.TrangThai,
                    'phanCong': item.Hoten
                }
                response.append(du_an_data)

        return jsonify(response)
    except Exception as e:
        return jsonify({'success': False, 'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/du-lieu/<int:idDuLieu>/duyet-gan-nhan', methods=['PUT'])
@authenticated
def update_statusdulieu(idDuLieu):
    try:
        data = request.get_json()
        idNguoiGanNhan = data['idNguoiGanNhan']
        trangThai = data['trangThai']

        # Kiểm tra xem bản ghi PhanCongGanNhan có tồn tại hay không
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()

        if not phancong:
            return jsonify({'status': 'error', 'message': 'Người gán nhãn và dữ liệu không tồn tại'}), 400

        phancong.TrangThai = trangThai
        db.session.commit()

        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/du-lieu/<int:idDuLieu>/chi-tiet-gan-nhan', methods=['GET'])
def get_dulieu(idDuLieu):
    try:
        dulieu = DuLieu.query.filter_by(idDuLieu=idDuLieu).first()
        duan = DuAn.query.get(dulieu.idDuAn)
        nhan = Nhan.query.filter_by(idDuLieu=idDuLieu).first()
        if nhan is None:
            return jsonify({'status': 'error', 'message': 'Không tìm thấy dữ liệu!'}), 400
        loainhan = LoaiNhan.query.get(duan.idLoaiNhan)
        vanban = VanBan.query.filter_by(idDuLieu=nhan.idDuLieu).first()
        phancong = PhanCongGanNhan.query.filter_by(idDuLieu=nhan.idDuLieu, idNguoiGanNhan=nhan.idNguoiGanNhan).first()
        ngonngu = NgonNgu.query.filter_by(idNgonNgu=nhan.idNgonNgu).first()
        nguoidung = NguoiDung.query.filter_by(idUser=nhan.idNguoiGanNhan)

        response = {}
        response['idDuLieu'] = dulieu.idDuLieu
        response['idLoaiNhan'] = loainhan.idLoaiNhan
        response['tenLoaiNhan'] = loainhan.LoaiNhan
        response['idNguoiGanNhan'] = nguoidung.first().idUser
        response['trangThai'] = phancong.TrangThai

        if loainhan.idLoaiNhan == "Phan_Loai_Van_Ban":
            response['vanBan'] = vanban.VanBan
            response['noiDung'] = nhan.NoiDung

        elif loainhan.idLoaiNhan == "Hoi_Dap":
            vanban = VanBan.query.filter(
                VanBan.idDuLieu == dulieu.idDuLieu, VanBan.idVanBan2_CauHoi != None).first()
            response['vanBan'] = vanban.VanBan
            vanban2_cauhoi = VanBan.query.filter_by(
                idVanBan=vanban.idVanBan2_CauHoi).first()
            response['cauHoi'] = vanban2_cauhoi.VanBan if vanban2_cauhoi else None
            response['noiDung'] = nhan.NoiDung

        elif loainhan.idLoaiNhan == "Tim_Cau_Hoi_Dong_Nghia":
            cauhoidongnghia = CauHoiDongNghia.query.filter_by(
                idNhan=nhan.idNhan).all()
            response['cauHoi'] = vanban.VanBan
            response['dsCauHoiDongNghia'] = [
                cau_hoi_dong_nghia.CauHoi for cau_hoi_dong_nghia in cauhoidongnghia]

        elif loainhan.idLoaiNhan == "Cap_Cau_Hoi_Van_Ban":
            vanban = VanBan.query.filter(
                VanBan.idDuLieu == dulieu.idDuLieu, VanBan.idVanBan2_CauHoi != None).first()
            response['vanBan'] = vanban.VanBan
            vanban2 = VanBan.query.filter_by(
                idVanBan=vanban.idVanBan2_CauHoi).first()
            response['cauHoi'] = vanban2.VanBan
            response['noiDung'] = nhan.NoiDung

        elif loainhan.idLoaiNhan == "Gan_Nhan_Thuc_The":
            thucthenhan = ThucThe_Nhan.query.filter_by(
                idNhan=nhan.idNhan).all()
            response['vanBan'] = vanban.VanBan
            response['dsThucThe'] = [ThucThe.query.get(
                thuc_the.idThucThe).TenThucThe for thuc_the in thucthenhan]

        elif loainhan.idLoaiNhan == "Gan_Nhan_Cap_Van_Ban":
            vanban = VanBan.query.filter(
                idDuLieu == dulieu.idDuLieu, VanBan.idVanBan2_CauHoi != None).first()
            response['vanBan1'] = vanban.VanBan
            vanban2 = VanBan.query.filter_by(
                idVanBan=vanban.idVanBan2_CauHoi).first()
            response['vanBan2'] = vanban2.VanBan
            response['noiDung'] = nhan.NoiDung

        elif loainhan.idLoaiNhan == "Dich_May":
            ngonngugoc = NgonNgu.query.filter_by(
                idNgonNgu=vanban.idNgonNgu).first()
            response['vanBanGoc'] = vanban.VanBan
            response['idNgonNguGoc'] = ngonngugoc.idNgonNgu
            response['tenNgonNguGoc'] = ngonngugoc.NgonNgu
            response['vanBanDich'] = nhan.NoiDung
            response['idNgonNguDich'] = ngonngu.idNgonNgu
            response['tenNgonNguDich'] = ngonngu.NgonNgu

        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/du-lieu/<int:idDuLieu>/chi-tiet', methods=['GET'])
def get_dulieu_chitiet(idDuLieu):
    try:
        dulieu = DuLieu.query.filter_by(idDuLieu=idDuLieu).first()
        duan = DuAn.query.get(dulieu.idDuAn)

        loainhan = LoaiNhan.query.get(duan.idLoaiNhan)
        vanban = VanBan.query.filter_by(idDuLieu=idDuLieu).first()

        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=dulieu.idDuLieu).all()

        response = {}
        response['idDuLieu'] = dulieu.idDuLieu
        response['idLoaiNhan'] = loainhan.idLoaiNhan
        response['tenLoaiNhan'] = loainhan.LoaiNhan
        response['dsPhanCong'] = [NguoiDung.query.get(
            pc.idNguoiGanNhan).Hoten for pc in phancong]

        if loainhan.idLoaiNhan == "Phan_Loai_Van_Ban":
            response['vanBan'] = vanban.VanBan

        elif loainhan.idLoaiNhan == "Hoi_Dap":
            vanban = VanBan.query.filter(
                VanBan.idDuLieu == dulieu.idDuLieu, VanBan.idVanBan2_CauHoi != None).first()
            response['vanBan'] = vanban.VanBan
            vanban2_cauhoi = VanBan.query.filter_by(
                idVanBan=vanban.idVanBan2_CauHoi).first()
            response['cauHoi'] = vanban2_cauhoi.VanBan if vanban2_cauhoi else None

        elif loainhan.idLoaiNhan == "Tim_Cau_Hoi_Dong_Nghia":
            response['cauHoi'] = vanban.VanBan

        elif loainhan.idLoaiNhan == "Cap_Cau_Hoi_Van_Ban":
            vanban = VanBan.query.filter(
                idDuLieu == dulieu.idDuLieu, VanBan.idVanBan2_CauHoi != None).first()
            response['vanBan'] = vanban.VanBan
            vanban2 = VanBan.query.filter_by(
                idVanBan=vanban.idVanBan2_CauHoi).first()
            response['cauHoi'] = vanban2.VanBan

        elif loainhan.idLoaiNhan == "Gan_Nhan_Thuc_The":
            response['vanBan'] = vanban.VanBan

        elif loainhan.idLoaiNhan == "Gan_Nhan_Cap_Van_Ban":
            vanban = VanBan.query.filter(
                VanBan.idDuLieu == dulieu.idDuLieu, VanBan.idVanBan2_CauHoi != None).first()
            response['vanBan1'] = vanban.VanBan
            vanban2 = VanBan.query.filter_by(
                idVanBan=vanban.idVanBan2_CauHoi).first()
            response['vanBan2'] = vanban2.VanBan

        elif loainhan.idLoaiNhan == "Dich_May":
            ngonngugoc = NgonNgu.query.filter_by(
                idNgonNgu=vanban.idNgonNgu).first()
            response['vanBanGoc'] = vanban.VanBan
            response['idNgonNguGoc'] = ngonngugoc.idNgonNgu
            response['tenNgonNguGoc'] = ngonngugoc.NgonNgu

        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/phan-loai-van-ban/them', methods=['POST'])
def create_phanloaivanban():
    try:
        data = request.get_json()

        idDuAn = data['idDuAn']
        vanban = data['vanBan']
        idNguoiGanNhan = data['dsPhanCong']

        duan = DuAn.query.get(idDuAn)

        if duan.idLoaiNhan != "Phan_Loai_Van_Ban":
            return jsonify({'status': 'error', 'message': 'Dự Án nhập vào không thuộc loại nhãn này!'}), 400

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        vanban = VanBan(vanban, None, dulieu.idDuLieu, None)
        db.session.add(vanban)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/phan-loai-van-ban/gan-nhan', methods=['POST'])
@authenticated
def create_gannhanphanloaivanban():
    try:
        data = request.get_json()
        iddulieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        NoiDung = data['noiDung']

        nhan = Nhan(iddulieu, idNguoiGanNhan, NoiDung, None)
        db.session.add(nhan)
        db.session.commit()

        # Cập nhật trạng thái của PhanCongGanNhan thành 'DONE'
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=iddulieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if phancong:
            phancong.TrangThai = 'DONE'
            db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/hoi-dap/them', methods=['POST'])
def create_hoidap():
    try:
        data = request.get_json()
        cauhoi = data['cauHoi']
        idDuAn = data['idDuAn']
        vanban = data['vanBan']
        idNguoiGanNhan = data['dsPhanCong']

        duan = DuAn.query.get(idDuAn)
        if duan.idLoaiNhan != "Hoi_Dap":
            return jsonify({'status': 'error', 'message': 'Dự Án nhập vào không thuộc loại nhãn này!'}), 400

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        cauhoi = VanBan(cauhoi, idNgonNgu=None,
                        idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=None)
        db.session.add(cauhoi)
        db.session.commit()

        vanban = VanBan(vanban, idNgonNgu=None,
                        idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=cauhoi.idVanBan)
        db.session.add(vanban)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/hoi-dap/gan-nhan', methods=['POST'])
@authenticated
def create_gannhanhoidap():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        NoiDung = data['noiDung']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu=None)
        db.session.add(nhan)
        db.session.commit()

        # Cập nhật trạng thái của PhanCongGanNhan thành 'DONE'
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if phancong:
            phancong.TrangThai = 'DONE'
            db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/core-service/dich-may/them', methods=['POST'])
def create_dichmay():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        vanban = data['vanBan']
        idNgonNgu = data['idNgonNgu']
        idNguoiGanNhan = data['dsPhanCong']

        duan = DuAn.query.get(idDuAn)

        if duan.idLoaiNhan != "Dich_May":
            return jsonify({'status': 'error', 'message': 'Dự Án nhập vào không thuộc loại nhãn này!'}), 400

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        vanban = VanBan(vanban, idNgonNgu=idNgonNgu,
                        idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=None)
        db.session.add(vanban)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/dich-may/gan-nhan', methods=['POST'])
@authenticated
def create_gannhandichmay():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        NoiDung = data['noiDung']
        idNgonNgu = data['idNgonNguDich']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu=idNgonNgu)
        db.session.add(nhan)
        db.session.commit()

        # Cập nhật trạng thái của PhanCongGanNhan thành 'DONE'
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if phancong:
            phancong.TrangThai = 'DONE'
            db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/core-service/thuc-the/them', methods=['POST'])
def create_thucthe():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        VanBan_text = data['vanBan']
        idNguoiGanNhan = data['dsPhanCong']

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        vanban = VanBan(VanBan_text, idNgonNgu=None,
                        idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=None)
        db.session.add(vanban)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/thuc-the/gan-nhan', methods=['POST'])
@authenticated
def create_gannhanthucthe():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        dsThucThe = data['dsTenThucThe']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, None, idNgonNgu=None)
        db.session.add(nhan)
        db.session.commit()

        for thucthe in dsThucThe:
            ten_thucthe = thucthe

            # Kiểm tra xem ThucThe đã tồn tại trong cơ sở dữ liệu chưa
            existing_thucthe = ThucThe.query.filter_by(
                TenThucThe=ten_thucthe).first()

            if existing_thucthe:
                id_thucthe = existing_thucthe.idThucThe
            else:
                # Nếu ThucThe chưa tồn tại, thêm mới vào cơ sở dữ liệu
                new_thucthe = ThucThe(ten_thucthe)
                db.session.add(new_thucthe)
                db.session.commit()
                id_thucthe = new_thucthe.idThucThe

            thucthe_nhan = ThucThe_Nhan(id_thucthe, idDuLieu)
            db.session.add(thucthe_nhan)
            db.session.commit()

        # Cập nhật trạng thái của PhanCongGanNhan thành 'DONE'
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if phancong:
            phancong.TrangThai = 'DONE'
            db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/van-ban-dong-nghia/them', methods=['POST'])
def create_vanbandongnghia():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        VanBan1 = data['vanBan1']
        VanBan2 = data['vanBan2']
        idNguoiGanNhan = data['dsPhanCong']
        duan = DuAn.query.get(idDuAn)
        if duan.idLoaiNhan != "Gan_Nhan_Cap_Van_Ban":
            return jsonify({'status': 'error', 'message': 'Dự Án nhập vào không thuộc loại nhãn này!'}), 400
        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        VanBan1 = VanBan(VanBan1, idNgonNgu=None,
                         idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=None)
        db.session.add(VanBan1)
        db.session.commit()

        VanBan2 = VanBan(VanBan2, idNgonNgu=None,
                         idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=VanBan1.idVanBan)
        db.session.add(VanBan2)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/van-ban-dong-nghia/gan-nhan', methods=['POST'])
@authenticated
def create_gannhanvanbandongnghia():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        NoiDung = data['noiDung']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu=None)
        db.session.add(nhan)
        db.session.commit()

        # Cập nhật trạng thái của PhanCongGanNhan thành 'DONE'
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if phancong:
            phancong.TrangThai = 'DONE'
            db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/cap-cau-hoi-van-ban/them', methods=['POST'])
def create_capcauhoivanban():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        vanban_text = data['vanBan']
        cauhoi_text = data['cauHoi']
        idNguoiGanNhan = data['dsPhanCong']
        duan = DuAn.query.get(idDuAn)
        if duan.idLoaiNhan != "Cap_Cau_Hoi_Van_Ban":
            return jsonify({'status': 'error', 'message': 'Dự Án nhập vào không thuộc loại nhãn này!'}), 400
        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        vanban = VanBan(vanban_text, idNgonNgu=None,
                        idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=None)
        db.session.add(vanban)
        db.session.commit()

        cauhoi = VanBan(cauhoi_text, idNgonNgu=None,
                        idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=vanban.idVanBan)
        db.session.add(cauhoi)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/cap-cau-hoi-van-ban/gan-nhan', methods=['POST'])
@authenticated
def create_gannhancapcauhoivanban():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        NoiDung = data['noiDung']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu=None)
        db.session.add(nhan)
        db.session.commit()

        # Cập nhật trạng thái của PhanCongGanNhan thành 'DONE'
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if phancong:
            phancong.TrangThai = 'DONE'
            db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/core-service/cau-hoi-dong-nghia/them', methods=['POST'])
def create_cauhoidongnghia():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        CauHoi = data['cauHoi']
        idNguoiGanNhan = data['dsPhanCong']
        duan = DuAn.query.get(idDuAn)
        if duan.idLoaiNhan != "Tim_Cau_Hoi_Dong_Nghia":
            return jsonify({'status': 'error', 'message': 'Dự Án nhập vào không thuộc loại nhãn này!'}), 400
        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        CauHoi = VanBan(CauHoi, idNgonNgu=1,
                        idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=None)
        db.session.add(CauHoi)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/core-service/cau-hoi-dong-nghia/gan-nhan', methods=['POST'])
@authenticated
def create_gannhancapcauhoidongnghia():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        dscauhoidongnghia = data['dsCauHoiDongNghia']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, None, None)
        db.session.add(nhan)
        db.session.commit()

        for cauhoidungnghia in dscauhoidongnghia:
            ten_cauhoi = cauhoidungnghia
            new_cauhoidungnghia = CauHoiDongNghia(nhan.idNhan, ten_cauhoi)
            db.session.add(new_cauhoidungnghia)
            db.session.commit()

        # Cập nhật trạng thái của PhanCongGanNhan thành 'DONE'
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if phancong:
            phancong.TrangThai = 'DONE'
            db.session.commit()

        return jsonify({'status': 'success', 'message': 'Dữ liệu đã được khởi tạo thành công!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
