import logging
from functools import wraps

import requests
from flask import Flask, jsonify, request
# from flask_sqlalchemy import SQLAlchemy
import json
import csv
from dotenv import load_dotenv
from sqlalchemy import and_
import os
from flask_cors import CORS
from models.PhanCongGanNhan import PhanCongGanNhan
from models.Nhan import Nhan
from models.LoaiNhan import LoaiNhan
from models.NguoiDung import NguoiDung
from models.DuAn import DuAn
from models.VanBan import VanBan
from models.Database import db
from models.DuLieu import DuLieu
from models.ThucThe import ThucThe
from models.CauHoiDongNghia import CauHoiDongNghia
from models.ThucThe_Nhan import ThucThe_Nhan
from models.NgonNgu import NgonNgu

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


@app.route('/core-service/du-an/tao', methods=['POST'])
@authenticated
def create_duan():
    user = request.user.get('idUser')
    data = request.get_json()
    TenDA = data['TenDA']
    idLoaiNhan = data['idLoaiNhan']
    idQuanLi = user

    duan = DuAn(TenDA=TenDA, idLoaiNhan=idLoaiNhan, idQuanLi=idQuanLi)
    db.session.add(duan)
    db.session.commit()

    duan_info = {
        'idDuAn': duan.idDuAn,
        'TenDA': duan.TenDA,
        'idLoaiNhan': duan.idLoaiNhan,
        'idQuanLi': duan.idQuanLi
    }

    return jsonify({'duan': duan_info,'message': 'Dự án đã được khởi tạo thành công!'})


@app.route('/core-service/du-an/danh-sach', methods=['GET'])
@authenticated
def get_danhsachduan():
    try:
        user_id = request.user.get('idUser')

        user = NguoiDung.query.get(user_id)
        if user.typeUser == 1:
            duan_list = db.session.query(DuAn.idDuAn, DuAn.TenDA,LoaiNhan.idLoaiNhan, LoaiNhan.LoaiNhan)\
                .join(DuLieu, DuLieu.idDuAn == DuAn.idDuAn)\
                .join(PhanCongGanNhan, PhanCongGanNhan.idDuLieu == DuLieu.idDuLieu)\
                .join(NguoiDung, NguoiDung.idUser == PhanCongGanNhan.idNguoiGanNhan)\
                .join(LoaiNhan, LoaiNhan.idLoaiNhan == DuAn.idLoaiNhan)\
                .filter(NguoiDung.typeUser== 1).all()
        elif user.typeUser == 2:
            duan_list = db.session.query(DuAn.idDuAn, DuAn.TenDA,LoaiNhan.idLoaiNhan, LoaiNhan.LoaiNhan)\
                .join(DuLieu, DuLieu.idDuAn == DuAn.idDuAn)\
                .join(LoaiNhan, LoaiNhan.idLoaiNhan == DuAn.idLoaiNhan)\
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
        return jsonify({ 'status': 'error', 'message':str(e)}), 400


@app.route('/core-service/import-vanban', methods=['POST'])
def import_vanban():
    file = request.files['file']
    data = file.read().decode('utf-8')

    # Kiểm tra định dạng file (json hoặc csv) dựa trên phần mở rộng tệp
    if file.filename.endswith('.json'):
        try:
            json_data = json.loads(data)
            for item in json_data:
                vanban = VanBan(
                    VanBan=item['VanBan'],
                    idNgonNgu=item['idNgonNgu'],
                    idDuAn=item['idDuAn'],
                    idVanBan2=item['idVanBan2']
                )
                db.session.add(vanban)
            db.session.commit()
            return jsonify({'message': 'Dữ liệu đã được import thành công từ tệp JSON!'})
        except json.JSONDecodeError:
            return jsonify({'status':'error','message': 'Định dạng JSON không hợp lệ!'}),400

    elif file.filename.endswith('.csv'):
        try:
            csv_data = csv.reader(data.splitlines(), delimiter=',')
            next(csv_data)  # Bỏ qua header của file CSV
            for row in csv_data:
                vanban = VanBan(
                    VanBan=row[0],
                    idNgonNgu=int(row[1]),
                    idDuAn=int(row[2]),
                    idVanBan2=int(row[3])
                )
                db.session.add(vanban)
            db.session.commit()
            return jsonify({'message': 'Dữ liệu đã được import thành công từ tệp CSV!'})
        except csv.Error:
            return jsonify({'status':'error','message': 'Định dạng CSV không hợp lệ!'}),400

    else:
        return jsonify({'status':'error','message': 'Định dạng file không được hỗ trợ!'}),400


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
        return jsonify({'success': False, 'status':'error','message': str(e)}),400
# @app.route('/core-service/du-an/<int:idDuAn>/ds-du-lieu,', methods=['GET'])
# def get_data(idDuAn):
    try:
        data_list = DuLieu.query.filter_by(idDuAn=idDuAn).all()

        result = []
        for data in data_list:
            vanban_list = VanBan.query.filter_by(idDuLieu=data.idDuLieu).all()

            vanban_data = []
            for vanban in vanban_list:
                vanban_data.append({
                    'idVanBan': vanban.idVanBan,
                    'VanBan': vanban.VanBan,
                    'idNgonNgu': vanban.idNgonNgu,
                    'idVanBan2': vanban.idVanBan2
                })

            result.append({
                'idDuLieu': data.idDuLieu,
                'idDuAn': data.idDuAn,
                'VanBan': vanban_data
            })

        return jsonify({'data': result})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/core-service/du-an/<int:idDuAn>/ds-du-lieu', methods=['GET'])
@authenticated
def get_dulieuduan(idDuAn):
    try:
        user_id = request.user.get('idUser')
        user = NguoiDung.query.get(user_id)
        duan = DuAn.query.get(idDuAn)
        dulieutest = DuLieu.query.filter(DuLieu.idDuAn == idDuAn).all()

        if user.typeUser == 2:
            if duan.idQuanLi != user_id:
                return jsonify({'status': 'error', 'message': 'Người dùng không được quản lý dự án'}),400
            dulieu = DuLieu.query.filter_by(idDuAn=idDuAn).all()
        elif user.typeUser == 1:
            phancong = PhanCongGanNhan.query.filter_by(idNguoiGanNhan=user_id).first()
            if phancong is None:
                return jsonify({'status': 'error', 'message': 'Người dùng không được phân công trong dự án!'}),400

            dulieu = DuLieu.query.filter(DuLieu.idDuAn == idDuAn).all()
        else:
            return jsonify({'status': 'error', 'message': 'Loại người dùng không hợp lệ!'}),400

        vanban_list = []
        for du_lieu in dulieu:
            vanban = VanBan.query.filter_by(idDuLieu=du_lieu.idDuLieu).all()
            phancong = PhanCongGanNhan.query.filter_by(idDuLieu=du_lieu.idDuLieu).all()
            for vb in vanban:
                for pc in phancong:
                    vanban_data = {
                        'idDuAn': duan.idDuAn,
                        'tenDuAn': duan.TenDA,
                        'idDuLieu': du_lieu.idDuLieu,
                        'vanBan': vb.VanBan,
                        'trangThai': pc.TrangThai,
                        'HoTen': user.Hoten
                    }
                    vanban_list.append(vanban_data)
        return jsonify(vanban_list)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}),400

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
        return jsonify({'success': False, 'status':'error', 'message': str(e)}),400
    
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
        return jsonify({'success': False, 'status':'error', 'message': str(e)}),400
    
@app.route('/core-service/du-lieu/ds-can-duyet', methods=['GET'])
@authenticated
def get_ds_can_duyet():
    try:
        idUser = request.user.get('idUser')
        user = NguoiDung.query.get(idUser)

        if user.LevelUser == 1:
            du_lieu_can_duyet = db.session.query(DuAn.idDuAn, DuAn.TenDA, DuLieu.idDuLieu, VanBan.VanBan, PhanCongGanNhan.TrangThai, NguoiDung.Hoten)\
                .join(DuLieu, DuAn.idDuAn == DuLieu.idDuAn)\
                .join(PhanCongGanNhan, PhanCongGanNhan.idDuLieu == DuLieu.idDuLieu)\
                .join(NguoiDung, NguoiDung.idUser == PhanCongGanNhan.idNguoiGanNhan)\
                .join(VanBan, VanBan.idDuLieu == DuLieu.idDuLieu)\
                .filter(PhanCongGanNhan.idNguoiGanNhan == idUser)\
                .all()
        elif user.LevelUser == 2:
            du_lieu_can_duyet = db.session.query(DuAn.idDuAn, DuAn.TenDA, DuLieu.idDuLieu, VanBan.VanBan, PhanCongGanNhan.TrangThai, NguoiDung.Hoten)\
                .join(DuLieu, DuAn.idDuAn == DuLieu.idDuAn)\
                .join(PhanCongGanNhan, PhanCongGanNhan.idDuLieu == DuLieu.idDuLieu)\
                .join(NguoiDung, NguoiDung.idUser == PhanCongGanNhan.idNguoiGanNhan)\
                .join(VanBan, VanBan.idDuLieu == DuLieu.idDuLieu)\
                .filter(DuLieu.idDuAn == DuAn.idDuAn, PhanCongGanNhan.TrangThai != 'DONE')\
                .all()
        else:
            return jsonify({'success': False, 'status': 'error' ,'message': 'Loại người dùng không hợp lệ!'}),400

        response = []
        for item in du_lieu_can_duyet:
            du_an_data = {
                'idDuAn': item.idDuAn,
                'tenDuAn': item.TenDA,
                'idDuLieu': item.idDuLieu,
                'vanBan': item.VanBan,
                'trangThai': item.TrangThai,
                'HoTen': item.Hoten
            }
            response.append(du_an_data)

        return jsonify(response)
    except Exception as e:
        return jsonify({'success': False, 'status':'error','message': str(e)}),400



@app.route('/core-service/du-lieu/<int:idDuLieu>', methods=['PUT'])
@authenticated
def update_statusdulieu(idDuLieu):
    try:
        data = request.get_json()
        idNguoiGanNhan = data['idNguoiGanNhan']
        trangThai = data['TrangThai']

        # Kiểm tra xem bản ghi PhanCongGanNhan có tồn tại hay không
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if not phancong:
            return jsonify({'success': False, 'error': 'Người gán nhãn và dữ liệu không tồn tại'}),400

        phancong.TrangThai = trangThai
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'status':'error','message': str(e)}),400


@app.route('/core-service/du-lieu/<int:idDuLieu>', methods=['GET'])
def get_dulieu(idDuLieu):
    try:
        dulieu = DuLieu.query.filter_by(idDuLieu=idDuLieu).first()
        duan = DuAn.query.get(dulieu.idDuLieu)
        nhan = Nhan.query.filter_by(idDuLieu=idDuLieu).first()
        if nhan is None:
            return jsonify({'status':'error','message': 'Không tìm thấy dữ liệu!'}), 400
        loainhan = LoaiNhan.query.get(duan.idLoaiNhan)
        vanban = VanBan.query.filter_by(idDuLieu=nhan.idDuLieu).first()
        phancong = PhanCongGanNhan.query.filter_by(idDuLieu=nhan.idDuLieu).first()
        ngonngu = NgonNgu.query.filter_by(idNgonNgu=nhan.idNgonNgu).first()
        nguoidung = NguoiDung.query.filter_by(idUser=nhan.idNguoiGanNhan)
        
        response = {}
        if loainhan.idLoaiNhan == "Phan_Loai_Van_Ban":
            response['HoTen'] = nguoidung.first().Hoten
            response['VanBan'] = vanban.VanBan
            response['NoiDung'] = nhan.NoiDung
            response['TrangThai'] = phancong.TrangThai
        elif loainhan.idLoaiNhan == "Hoi_Dap":
            vanban = VanBan.query.filter(VanBan.idDuLieu == dulieu.idDuLieu,VanBan.idVanBan2_CauHoi != None).first()
            response['HoTen'] = nguoidung.first().Hoten
            response['VanBan'] = vanban.VanBan
            vanban2_cauhoi = VanBan.query.filter_by(idVanBan=vanban.idVanBan2_CauHoi).first()
            response['CauHoi'] = vanban2_cauhoi.VanBan if vanban2_cauhoi else None
            response['NoiDung'] = "Có" if nhan.NoiDung else "Không"
            response['TrangThai'] = phancong.TrangThai
        elif loainhan.idLoaiNhan == "Tim_Cau_Hoi_Dong_Nghia":
            cauhoidongnghia = CauHoiDongNghia.query.filter_by(idNhan=nhan.idNhan).all()
            response['HoTen'] = nguoidung.first().Hoten
            response['CauHoi'] = vanban.VanBan
            response['DsCauHoiDongNghia'] = [cau_hoi_dong_nghia.CauHoi for cau_hoi_dong_nghia in cauhoidongnghia]
            response['NoiDung'] = nhan.NoiDung
            response['TrangThai'] = phancong.TrangThai
        elif loainhan.idLoaiNhan == "Cap_Cau_Hoi_Van_Ban":
            vanban = VanBan.query.filter(VanBan.idDuLieu == dulieu.idDuLieu,VanBan.idVanBan2_CauHoi !=  None).first()
            response['HoTen'] = nguoidung.first().Hoten
            response['VanBan'] = vanban.VanBan
            vanban2= VanBan.query.filter_by(idVanBan=vanban.idVanBan2_CauHoi).first()
            response['CauHoi'] = vanban2.VanBan
            response['NoiDung'] = nhan.NoiDung
            response['TrangThai'] = phancong.TrangThai
        elif loainhan.idLoaiNhan == "Gan_Nhan_Thuc_The":
            thucthenhan = ThucThe_Nhan.query.filter_by(idNhan=nhan.idNhan).all()
            response['HoTen'] = nguoidung.first().Hoten
            response['VanBan'] = vanban.VanBan
            response['DsThucThe'] = [ThucThe.query.get(thuc_the.idThucThe).TenThucThe for thuc_the in thucthenhan]
            response['TrangThai'] = phancong.TrangThai
        elif loainhan.idLoaiNhan == "Gan_Nhan_Cap_Van_Ban":
            vanban = VanBan.query.filter(VanBan.idDuLieu == dulieu.idDuLieu,VanBan.idVanBan2_CauHoi !=  None).first()
            response['HoTen'] = nguoidung.first().Hoten
            response['VanBan1'] = vanban.VanBan
            vanban2 = VanBan.query.filter_by(idVanBan=vanban.idVanBan2_CauHoi).first()
            response['VanBan2'] = vanban2.VanBan
            response['NoiDung'] = "Có" if nhan.NoiDung else "Không"
            response['TrangThai'] = phancong.TrangThai
        elif loainhan.idLoaiNhan == "Dich_May":
            ngonngugoc = NgonNgu.query.filter_by(idNgonNgu= vanban.idNgonNgu).first()
            response['HoTen'] = nguoidung.first().Hoten
            response['VanBanGoc'] = vanban.VanBan
            response['NgonNguGoc'] = ngonngugoc.NgonNgu
            response['VanBanDich'] = nhan.NoiDung
            response['NgonNguDich'] = ngonngu.NgonNgu
            response['TrangThai'] = phancong.TrangThai

        return jsonify(response)
    except Exception as e:
        return jsonify({'status':'error','message': str(e)}),400


@app.route('/core-service/phan-loai-van-ban/them', methods=['POST'])
def create_phanloaivanban():
    try:
        data = request.get_json()

        idDuAn = data['idDuAn']
        vanban = data['VanBan']
        idNguoiGanNhan = data['idNguoiGanNhan']
        duan = DuAn.query.get(idDuAn)
        if duan.idLoaiNhan != "Phan_Loai_Van_Ban":
            return jsonify({'success': False, 'status':'error', 'message':'Dự Án nhập vào không thuộc loại nhãn này!'}),400
        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        vanban = VanBan(vanban,None, dulieu.idDuLieu,None)
        db.session.add(vanban)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'status':'error','message': str(e)}),400


@app.route('/core-service/phan-loai-van-ban/gan-nhan', methods=['POST'])
@authenticated
def create_gannhanphanloaivanban():
    try:
        data = request.get_json()
        iddulieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        NoiDung = data['NoiDung']
    
        nhan = Nhan(iddulieu, idNguoiGanNhan, NoiDung, None)
        db.session.add(nhan)
        db.session.commit()

        # Cập nhật trạng thái của PhanCongGanNhan thành 'DONE'
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=iddulieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if phancong:
            phancong.TrangThai = 'DONE'
            db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'status':'error','message': str(e)}),400


@app.route('/core-service/hoi-dap/them', methods=['POST'])
def create_hoidap():
    try:
        data = request.get_json()
        cauhoi = data['CauHoi']
        idDuAn = data['idDuAn']
        vanban = data['VanBan']
        idNguoiGanNhan = data['idNguoiGanNhan']

        duan = DuAn.query.get(idDuAn)
        if duan.idLoaiNhan != "Hoi_Dap":
            return jsonify({'success': False, 'status':'error', 'message':'Dự Án nhập vào không thuộc loại nhãn này!'}),400
        
        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        cauhoi = VanBan(cauhoi, idNgonNgu=None,idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=None)
        db.session.add(cauhoi)
        db.session.commit()

        vanban = VanBan(vanban, idNgonNgu=None,idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=cauhoi.idVanBan)
        db.session.add(vanban)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'status':'error', 'message': str(e)}),400


@app.route('/core-service/hoi-dap/gan-nhan', methods=['POST'])
@authenticated
def create_gannhanhoidap():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        NoiDung = data['NoiDung']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu=None)
        db.session.add(nhan)
        db.session.commit()

        # Cập nhật trạng thái của PhanCongGanNhan thành 'DONE'
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if phancong:
            phancong.TrangThai = 'DONE'
            db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/core-service/dich-may/them', methods=['POST'])
def create_dichmay():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        vanban = data['VanBan']
        idNgonNgu = data['idNgonNgu']
        idNguoiGanNhan = data['idNguoiGanNhan']

        duan = DuAn.query.get(idDuAn)
        if duan.idLoaiNhan != "Dich_May":
            return jsonify({'success': False, 'status':'error', 'message':'Dự Án nhập vào không thuộc loại nhãn này!'}), 400

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        vanban = VanBan(vanban, idNgonNgu=idNgonNgu, idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=None)
        db.session.add(vanban)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'status':'error','message': str(e)}),400

@app.route('/core-service/dich-may/gan-nhan', methods=['POST'])
@authenticated
def create_gannhandichmay():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        NoiDung = data['NoiDung']
        idNgonNgu = data['idNgonNgu']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu=idNgonNgu)
        db.session.add(nhan)
        db.session.commit()

        # Cập nhật trạng thái của PhanCongGanNhan thành 'DONE'
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if phancong:
            phancong.TrangThai = 'DONE'
            db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/core-service/thuc-the/them', methods=['POST'])
def create_thucthe():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        VanBan_text = data['VanBan']
        idNguoiGanNhan = data['idNguoiGanNhan']

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        vanban = VanBan(VanBan_text,idNgonNgu =None, idDuLieu = dulieu.idDuLieu,idVanBan2_CauHoi= None)
        db.session.add(vanban)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'status':'error','message': str(e)}),400


@app.route('/core-service/thuc-the/gan-nhan', methods=['POST'])
@authenticated
def create_gannhanthucthe():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        dsThucThe = data['ThucThe']

        nhan = Nhan(idDuLieu, idNguoiGanNhan,None,idNgonNgu=None)
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

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'status':'error','message': str(e)}),400


#@app.route('/core-service/van-ban-dong-nghia/them', methods=['POST'])
#def create_vanbandongnghia():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        VanBan1 = data['VanBan1']
        VanBan2 = data['VanBan2']
        idNguoiGanNhan = data['idNguoiGanNhan']

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        VanBan1 = VanBan(VanBan1, idNgonNgu=None,
                         idDuLieu=dulieu.idDuLieu, idVanBan2=None)
        db.session.add(VanBan1)
        db.session.commit()

        VanBan2 = VanBan(VanBan2, idNgonNgu=None,
                         idDuLieu=dulieu.idDuLieu, idVanBan2=VanBan1.idVanBan)
        db.session.add(VanBan2)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
@app.route('/core-service/van-ban-dong-nghia/them', methods=['POST'])
def create_vanbandongnghia():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        VanBan1 = data['VanBan1']
        VanBan2 = data['VanBan2']
        idNguoiGanNhan = data['idNguoiGanNhan']
        duan = DuAn.query.get(idDuAn)
        if duan.idLoaiNhan != "Gan_Nhan_Cap_Van_Ban":
            return jsonify({'success': False, 'status':'error', 'message':'Dự Án nhập vào không thuộc loại nhãn này!'}),400
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

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'status':'error','message': str(e)}),400

@app.route('/core-service/van-ban-dong-nghia/gan-nhan', methods=['POST'])
@authenticated
def create_gannhanvanbandongnghia():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        NoiDung = data['NoiDung']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu=None)
        db.session.add(nhan)
        db.session.commit()

        # Cập nhật trạng thái của PhanCongGanNhan thành 'DONE'
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if phancong:
            phancong.TrangThai = 'DONE'
            db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'status':'error','message': str(e)}),400


@app.route('/core-service/cap-cau-hoi-van-ban/them', methods=['POST'])
def create_capcauhoivanban():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        vanban_text = data['VanBan']
        cauhoi_text = data['CauHoi']
        idNguoiGanNhan = data['idNguoiGanNhan']
        duan = DuAn.query.get(idDuAn)
        if duan.idLoaiNhan != "Cap_Cau_Hoi_Van_Ban":
            return jsonify({'success': False, 'status': 'error', 'message': 'Dự Án nhập vào không thuộc loại nhãn này!'}), 400
        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        vanban = VanBan(vanban_text, idNgonNgu=None, idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=None)
        db.session.add(vanban)
        db.session.commit()

        cauhoi = VanBan(cauhoi_text, idNgonNgu=None, idDuLieu=dulieu.idDuLieu, idVanBan2_CauHoi=vanban.idVanBan)
        db.session.add(cauhoi)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/core-service/cap-cau-hoi-van-ban/gan-nhan', methods=['POST'])
@authenticated
def create_gannhancapcauhoivanban():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.user.get('idUser')
        NoiDung = data['NoiDung']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu=None)
        db.session.add(nhan)
        db.session.commit()

        # Cập nhật trạng thái của PhanCongGanNhan thành 'DONE'
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if phancong:
            phancong.TrangThai = 'DONE'
            db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


#@app.route('/core-service/cau-hoi-dong-nghia/them', methods=['POST'])
#def create_cauhoidongnghia():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        canhoi = data['cauhoi']
        idNguoiGanNhan = data['idNguoiGanNhan']

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        cauhoi = Nhan(cauhoi, dulieu.idDuLieu)
        db.session.add(cauhoi)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/core-service/cau-hoi-dong-nghia/them', methods=['POST'])
def create_cauhoidongnghia():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        CauHoi = data['CauHoi']
        idNguoiGanNhan = data['idNguoiGanNhan']
        duan = DuAn.query.get(idDuAn)
        if duan.idLoaiNhan != "Tim_Cau_Hoi_Dong_Nghia":
            return jsonify({'success': False, 'status':'error', 'message':'Dự Án nhập vào không thuộc loại nhãn này!'}),400
        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        CauHoi = VanBan(CauHoi,idNgonNgu=1, idDuLieu= dulieu.idDuLieu,idVanBan2_CauHoi= None)
        db.session.add(CauHoi)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'status':'error','message': str(e)}),400

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

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'status': 'error', 'message': str(e)}), 400

@app.route('/core-service/test')
@authenticated
def protected_route():
    idUser = request.user.get('idUser')
    return jsonify(idUser)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
