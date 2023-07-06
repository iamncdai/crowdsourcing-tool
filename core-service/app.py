import logging
from functools import wraps

import requests
from flask import Flask, jsonify, request
# from flask_sqlalchemy import SQLAlchemy
import json
import csv
from dotenv import load_dotenv
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
    idQuanLi = request.decoded_token.get('idQuanLi')

    duan = DuAn(TenDA=TenDA, idLoaiNhan=idLoaiNhan, idQuanLi=idQuanLi)
    db.session.add(duan)
    db.session.commit()

    return jsonify({'message': 'Dự án đã được khởi tạo thành công!'})


@app.route('/core-service/du-an/danh-sach', methods=['GET'])
@authenticated
def get_danhsachduan():
    try:
        user_id = request.user.get('idUser')

        user = NguoiDung.query.get(user_id)
        if user.typeUser == 1:
            assigned_projects = PhanCongGanNhan.query.filter_by(
                idNguoiGanNhan=user_id).all()
            project_ids = [project.idDuAn for project in assigned_projects]
            projects = DuAn.query.filter(DuAn.idDuAn.in_(project_ids)).all()
        elif user.typeUser == 2:
            projects = DuAn.query.all()
        else:
            return jsonify({'status': 'error', 'message': 'Loại người dùng không hợp lệ!'}), 400

        project_list = []
        for project in projects:
            project_data = {
                'idDuAn': project.idDuAn,
                'TenDA': project.TenDA,
                'idLoaiNhan': project.idLoaiNhan,
                'idQuanLi': project.idQuanLi
            }
            project_list.append(project_data)

        return jsonify({'projects': project_list})
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
            return jsonify({'error': 'Định dạng JSON không hợp lệ!'})

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
            return jsonify({'error': 'Định dạng CSV không hợp lệ!'})

    else:
        return jsonify({'error': 'Định dạng file không được hỗ trợ!'})


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
        return jsonify({'success': False, 'error': str(e)})
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


@app.route('/core-service/du-an/<int:idDuAn>/ds-du-lieu,', methods=['GET'])
@authenticated
def get_dulieuduan(idDuAn):
    try:
        user_id = request.user.get('idUser')
        user = NguoiDung.query.get(user_id)

        if user.typeUser == '2':
            dulieu = DuLieu.query.filter_by(idDuAn=idDuAn).all()
        elif user.typeUser == '1':
            phancong = PhanCongGanNhan.query.filter_by(
                idDuAn=idDuAn, idNguoiDung=user_id).first()

            if phancong is None:
                return jsonify({'error': 'Người dùng không được phân công trong dự án!'})

            dulieu = DuLieu.query.filter_by(idDuAn=idDuAn).all()
        else:
            return jsonify({'error': 'Loại người dùng không hợp lệ!'})

        vanban_list = []
        for du_lieu in dulieu:
            vanban = VanBan.query.with_entities(
                VanBan.VanBan).filter_by(idDuLieu=du_lieu.idDuLieu).all()
            for vb in vanban:
                vanban_data = {
                    'VanBan': vb[0],
                    'HoTen': user.Hoten
                }
                vanban_list.append(vanban_data)

        return jsonify({'dulieu': vanban_list})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/core-service/du-lieu/ds-can-duyet', methods=['GET'])
@authenticated
def get_ds_can_duyet():
    try:
        idUser = request.decoded_token.get('idUser')

        du_lieu_can_duyet = db.session.query(DuAn.idDuAn, DuAn.tenDuAn, DuLieu.idDuLieu, DuLieu.vanBan, DuLieu.trangThai, NguoiDung.HoTen)\
            .join(DuLieu, DuAn.idDuAn == DuLieu.idDuAn)\
            .join(PhanCongGanNhan, PhanCongGanNhan.idDuLieu == DuLieu.idDuLieu)\
            .join(NguoiDung, NguoiDung.idUser == PhanCongGanNhan.idNguoiGanNhan)\
            .filter(PhanCongGanNhan.idNguoiGanNhan == idUser)\
            .all()

        response = []
        for item in du_lieu_can_duyet:
            du_an_data = {
                'idDuAn': item.idDuAn,
                'tenDuAn': item.tenDuAn,
                'idDuLieu': item.idDuLieu,
                'vanBan': item.vanBan,
                'trangThai': item.trangThai,
                'HoTen': item.HoTen
            }
            response.append(du_an_data)

        return jsonify(response)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/core-service/du-lieu/<int:idDuLieu>t', methods=['PUT'])
@authenticated
def update_statusdulieu(idDuLieu):
    try:
        idNguoiGanNhan = request.json['idNguoiGanNhan']
        trangThai = request.json['trangThai']

        # Kiểm tra xem bản ghi PhanCongGanNhan có tồn tại hay không
        phancong = PhanCongGanNhan.query.filter_by(
            idDuLieu=idDuLieu, idNguoiGanNhan=idNguoiGanNhan).first()
        if not phancong:
            return jsonify({'success': False, 'error': 'Người gán nhãn và dữ liệu không tồn tại'})

        phancong.TrangThai = trangThai
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/core-service/du-lieu/<int:idDuLieu>', methods=['GET'])
def get_dulieu(idDuLieu):
    try:
        nhan = Nhan.query.filter_by(idDuLieu=idDuLieu).first()
        if nhan is None:
            return jsonify({'error': 'Không tìm thấy dữ liệu!'})
        vanban = VanBan.query.filter_by(idDuLieu=idDuLieu).first()
        phancong = PhanCongGanNhan.query.filter_by(
            idDuAn=vanban.idDuLieu).first()
        dulieu = DuLieu.query.filter_by(idDuLieu=vanban.idDuLieu).first()
        loainhan = LoaiNhan.query.filter_by(
            idLoaiNhan=vanban.idLoaiNhan).first()
        ngonngu = NgonNgu.query.filter_by(idNgonNgu=nhan.idNgonNgu).first()
        nguoidung = NguoiDung.query.filter_by(idUser=nhan.idNguoiGanNhan)

        response = {}

        if loainhan.LoaiNhan == "Phan_Loai_Van_Ban":
            response['HoTen'] = nguoidung.HoTen
            response['VanBan'] = vanban.VanBan
            response['NoiDung'] = loainhan.LoaiNhan
            response['TrangThai'] = phancong.TrangThai
        elif loainhan.LoaiNhan == "Hoi_Dap":
            response['HoTen'] = nguoidung.HoTen
            response['VanBan'] = vanban.VanBan
            response['CauHoi'] = vanban.CauHoi
            response['NoiDung'] = "Có" if nhan.NoiDung else "Không"
            response['TrangThai'] = phancong.TrangThai
        elif loainhan.LoaiNhan == "Dich_May":
            response['HoTen'] = nguoidung.HoTen
            response['VanBanGoc'] = vanban.VanBanGoc
            response['NgonNguGoc'] = ngonngu.NgonNguGoc
            response['VanBanDich'] = nhan.NoiDung
            response['NgonNguDich'] = ngonngu.NgonNguDich
            response['TrangThai'] = phancong.TrangThai
        elif loainhan.LoaiNhan == "Tim_Cau_Hoi_Dong_Nghia":
            response['HoTen'] = nguoidung.Hoten
            response['VanBan'] = vanban.VanBan
            response['Ds Cau hoi dong nghia'] = CauHoiDongNghia.query.filter_by(
                idNhan=nhan.idNhan).all()
            response['TrangThai'] = phancong.TrangThai
        elif loainhan.LoaiNhan == "Cap_Cau_Hoi_Van_Ban":
            response['HoTen'] = nguoidung.HoTen
            response['CauHoi'] = nhan.CauHoi
            response['VanBan'] = vanban.VanBan
            response['NoiDung'] = nhan.NoiDung
            response['TrangThai'] = phancong.TrangThai
        elif loainhan.LoaiNhan == "Gan_Nhan_Thuc_The":
            response['HoTen'] = nguoidung.HoTen
            response['VanBan'] = vanban.VanBan
            response['Ds ThucThe'] = ThucThe.query.filter_by(
                idNhan=nhan.idNhan).all()
            response['TrangThai'] = phancong.TrangThai
        elif loainhan.LoaiNhan == "Gan_Nhan_Cap_Van_Ban":
            response['HoTen'] = nguoidung.HoTen
            response['VanBan1'] = vanban.VanBan1
            response['VanBan2'] = vanban.VanBan2
            response['NoiDung'] = "Có" if nhan.NoiDung else "Không"
            response['TrangThai'] = phancong.TrangThai

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/core-service/phan-loai-van-ban/them', methods=['POST'])
def create_phanloaivanban():
    try:
        data = request.get_json()

        idDuAn = data['idDuAn']
        vanban = data['vanban']
        idNguoiGanNhan = data['idNguoiGanNhan']

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.flush()

        vanban = VanBan(vanban, dulieu.idDuLieu)
        db.session.add(vanban)

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/core-service/phan-loai-van-ban/gan-nhan', methods=['POST'])
@authenticated
def create_gannhanphanloaivanban():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.decoded_token.get('idUser')
        NoiDung = data['NoiDung']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu='Null')
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


@app.route('/core-service/hoi-dap/them', methods=['POST'])
def create_hoidap():
    try:
        data = request.get_json()
        cauhoi = data['cauhoi']
        idDuAn = data['idDuAn']
        vanban = data['vanban']
        idNguoiGanNhan = data['idNguoiGanNhan']

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        cauhoi = VanBan(cauhoi, idNgonNgu=None,
                        idDuLieu=dulieu.idDuLieu, idVanBan2=None)
        db.session.add(cauhoi)
        db.session.commit()

        vanban = VanBan(vanban, idNgonNgu=None,
                        idDuLieu=dulieu.idDuLieu, idVanBan2=cauhoi.idVanBan)
        db.session.add(vanban)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/core-service/hoi-dap/gan-nhan', methods=['POST'])
@authenticated
def create_gannhanhoidap():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.decoded_token.get('idUser')
        NoiDung = data['NoiDung']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu='Null')
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
        VanBan = data['VanBan']
        idNgonNgu = data['idNgonNgu']
        idNguoiGanNhan = data['idNguoiGanNhan']

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        VanBan = Nhan(VanBan, idNgonNgu=idNgonNgu,
                      idDuLieu=dulieu.idDuLieu, idVanBan2=None)
        db.session.add(VanBan)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/core-service/dich-may/gan-nhan', methods=['POST'])
@authenticated
def create_gannhandichmay():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.decoded_token.get('idUser')
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
        VanBan = data['VanBan']
        idNguoiGanNhan = data['idNguoiGanNhan']

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        VanBan = Nhan(VanBan, dulieu.idDuLieu)
        db.session.add(VanBan)
        db.session.commit()

        for idNguoiGanNhan_item in idNguoiGanNhan:
            phancong = PhanCongGanNhan(
                dulieu.idDuLieu, idNguoiGanNhan_item, TrangThai='NONE')
            db.session.add(phancong)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/core-service/thuc-the/gan-nhan', methods=['POST'])
@authenticated
def create_gannhanthucthe():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.decoded_token.get('idUser')
        dsThucThe = data['ThucThe']

        nhan = Nhan(idDuLieu, idNguoiGanNhan)
        db.session.add(nhan)
        db.session.commit()

        for thucthe in dsThucThe:
            ten_thucthe = thucthe['TenThucThe']

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
        return jsonify({'success': False, 'error': str(e)})


@app.route('/core-service/van-ban-dong-nghia/them', methods=['POST'])
def create_vanbandongnghia():
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


@app.route('/core-service/van-ban-dong-nghia/gan-nhan', methods=['POST'])
@authenticated
def create_gannhanvanbandongnghia():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.decoded_token.get('idUser')
        NoiDung = data['NoiDung']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu='Null')
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


@app.route('/core-service/cap-cau-hoi-van-ban/them', methods=['POST'])
def create_capcauhoivanban():
    try:
        data = request.get_json()
        idDuAn = data['idDuAn']
        VanBan = data['VanBan']
        cauhoi = data['cauhoi']
        idNguoiGanNhan = data['idNguoiGanNhan']

        dulieu = DuLieu(idDuAn)
        db.session.add(dulieu)
        db.session.commit()

        VanBan = VanBan(VanBan, idNgonNgu=None,
                        idDuLieu=dulieu.idDuLieu, idVanBan2=None)
        db.session.add(VanBan)
        db.session.commit()

        cauhoi = VanBan(cauhoi, idNgonNgu=None,
                        idDuLieu=dulieu.idDuLieu, idVanBan2=VanBan.idVanBan)
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


@app.route('/core-service/cap-cau-hoi-van-ban/gan-nhan', methods=['POST'])
@authenticated
def create_gannhancapcauhoivanban():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.decoded_token.get('idUser')
        NoiDung = data['NoiDung']

        nhan = Nhan(idDuLieu, idNguoiGanNhan, NoiDung, idNgonNgu='Null')
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


@app.route('/core-service/cau-hoi-dong-nghia/them', methods=['POST'])
def create_cauhoidongnghia():
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


@app.route('/core-service/cap-cau-hoi-dong-nghia/gan-nhan', methods=['POST'])
@authenticated
def create_gannhancapcauhoidongnghia():
    try:
        data = request.get_json()
        idDuLieu = data['idDuLieu']
        idNguoiGanNhan = request.decoded_token.get('idUser')
        dscauhoidongnghia = data['dscauhoidongnghia']

        nhan = Nhan(idDuLieu, idNguoiGanNhan)
        db.session.add(nhan)
        db.session.commit()

        for cauhoidungnghia in dscauhoidongnghia:
            ten_cauhoi = CauHoiDongNghia['dscauhoidongnghia']
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
        return jsonify({'success': False, 'error': str(e)})


@app.route('/core-service/test')
@authenticated
def protected_route():
    idUser = request.user.get('idUser')
    return jsonify(idUser)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
