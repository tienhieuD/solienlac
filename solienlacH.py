# ﻿# -*- coding: utf-8 -*-
import datetime
import time
import random
from odoo import models, fields, api, exceptions, _
from odoo.http import request
import json
import hashlib
import re

def _validate_diem(mark):
    parten = "(^[0-9](,|\.)?[0-9]*$|^10(,|.)?0*$)"
    return re.match(parten, mark)

class hocky(models.Model):
    _name = 'solienlac.hocky'
    _rec_name = 'hocky' # optional
    # _order = 'namhoc, hocky, ' # optional

    @api.model
    def _get_list_namhoc(self):
        return [str(k) + '-' + str(k+1) for k in range(1990,2020)]

    @api.model
    def _get_namhoc_now(self):
        now = datetime.datetime.now()
        year = now.year
        if now.month < 8:
            year -= 1
        return str(year) + "-" + str(year+1)

    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_namhoc_now,
        required=True
    )
    #---------- end define fields namhoc ------------

    hocky = fields.Selection(
        required=True,
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
        ],default = 'i')
    trangthai = fields.Selection([
        ('HienTai', 'Hiện tại'),
        ('DaKetThuc', 'Đã kết thúc')
    ],string='Trạng thái', default='HienTai')
    # ketthuchocky = fields.Boolean('Kết thúc học kỳ', default=False)
    truong = fields.Many2one('solienlac.truong', string='Trường', default=lambda self:self.env.user.truong, required=True,)
    # groups='solienlac.group_schooladmin_l1'
    # truong_sa = fields.Many2one('solienlac.truong', string='Trường', required=True)
    ghichu = fields.Char('Ghi chú')

    @api.model
    def create(self, values):
        if values['trangthai'] == 'HienTai':
            hk = self.env['solienlac.hocky'].search([
                ('truong', '=', values['truong']),
            ])
            # print hk
            # print len(hk)
            if len(hk) > 1:
                for val in hk:
                    self.env['solienlac.hocky'].browse(val.id).write({'trangthai':'DaKetThuc'})

            # Deo lien quan dau kemeno
        hk = super(hocky, self).create(values)
        return hk
    @api.multi
    def write(self, values):
        # print values.get('trangthai')
        if values.get('trangthai') == 'HienTai':
            hk = self.env['solienlac.hocky'].search([
                ('truong', '=', self.truong.id),
            ])
            # print hk
            # print len(hk)
            if len(hk) > 1:
                for val in hk:
                    self.env['solienlac.hocky'].browse(val.id).write({'trangthai':'DaKetThuc'})

            # Deo lien quan dau kemeno
        hk = super(hocky, self).write(values)
        return hk

    @api.constrains('truong', 'namhoc', 'hocky')
    def hocky_cont(self):
        count_record = self.env['solienlac.hocky'].search_count([
            ('namhoc', '=', self.namhoc),
            ('hocky', '=', self.hocky),
            ('truong.id', '=', self.truong.id),
        ])
        if(count_record > 1):
            raise exceptions.ValidationError("Học kỳ đã tồn tại!")
class caphoc(models.Model):
    _name = 'solienlac.caphoc'
    _rec_name = 'tencaphoc'

    macaphoc = fields.Integer('Mã cấp học', required=True,)
    tencaphoc = fields.Char('Tên cấp học', required=True,)
    # tencaphoc = fields.Selection([
    #     ('1', 'Nhà trẻ'),
    #     ('2', 'Mẫu giáo'),
    #     ('3', 'Tiểu học'),
    #     ('4', 'Trung học cơ sở'),
    #     ('5', 'Trung học phổ thông'),
    #     ('6', 'Trung cấp chuyên nghiệp'),
    #     ('7', 'Cao đẳng'),
    #     ('8', 'Đại học'),
    #     ('9', 'Sau đại học'),
    # ],default='1', string='Tên cấp học')
    ghichu = fields.Char('Ghi chú')
    # _sql_constraints = [
    #     ('macaphoc_uniq', 'unique(macaphoc)', ' Mã cấp học đã tồn tại.'),
    # ]
    @api.constrains('macaphoc')
    def _macaphoc_uniq(self):
        lst_mach = self.env['solienlac.caphoc'].search([])
        lst_mach = map(lambda x : x.macaphoc, lst_mach)
        lst_mach.remove(self.macaphoc)
        # print lst_mach
        if self.macaphoc in lst_mach:
            raise exceptions.ValidationError("Mã cấp học đã tồn tại")
        else:
            pass

class captruong(models.Model):
    _name = 'solienlac.captruong'
    _rec_name = 'tencaptruong'

    macaptruong = fields.Integer('Mã cấp trường', required=True)
    tencaptruong = fields.Char(string="Tên cấp trường", required=True)
    # tencaptruong = fields.Selection([
    #     ('1', 'Nhà trẻ'),
    #     ('2', 'Trường Mẫu giáo'),
    #     ('3', 'Trường Mầm non'),
    #     ('4', 'Trường Tiểu học'),
    #     ('5', 'Trường Trung học cơ sở'),
    #     ('6', 'Trường Trung học phổ thông'),
    #     ('7', 'Trường đa cấp (Tiểu học và THCS)'),
    #     ('8', 'Trường đa cấp (THCS và THPT)'),
    #     ('9', 'Trường đa cấp (Tiểu học,THCS và THPT)'),
    #     ('10', 'Trung tâm Giáo dục thường xuyên'),
    #     ('11', 'Trung tâm Kỹ thuật tổng hợp - Hướng nghiệp'),
    #     ('12', 'Trung cấp chuyên nghiệp'),
    #     ('13', 'Cao đẳng'),
    #     ('14', 'Đại học'),
    #     ('15', 'Nhóm trẻ độc lập'),
    #     ('16', 'Lớp mẫu giáo độc lập'),
    #     ('17', 'Lớp mầm non độc lập'),
    #     ('18', 'Khác'),
    # ],default='1', string='Tên cấp trường')
    ghichu = fields.Char('Ghi chú')

    @api.constrains('macaptruong')
    def _macaptruong_uniq(self):
        lst = self.env['solienlac.captruong'].search([])
        lst = map(lambda x : x.macaptruong, lst)
        lst.remove(self.macaptruong)
        # print lst
        if self.macaptruong in lst:
            raise exceptions.ValidationError("Mã cấp trường đã tồn tại")
        else:
            pass
class hangtruong(models.Model):
    _name = 'solienlac.hangtruong'
    _rec_name = 'tenhangtruong' # optional
    # _description = 'Hạng trường'

    mahangtruong = fields.Integer('Mã hạng trường', required=True)
    tenhangtruong = fields.Char(string="Tên hạng trường",  required=True)
    # tenhangtruong = fields.Selection([
    #     ('1', 'Hạng I'),
    #     ('2', 'Hạng II'),
    #     ('3', 'Hạng III'),
    #     ('4', 'Hạng IV'),
    # ], default='1', string='Tên hạng trường')
    ghichu = fields.Char('Ghi chú')

    @api.constrains('mahangtruong')
    def _mahangtruong_uniq(self):
        lst = self.env['solienlac.hangtruong'].search([])
        lst = map(lambda x : x.mahangtruong, lst)
        lst.remove(self.mahangtruong)
        # print lst
        if self.mahangtruong in lst:
            raise exceptions.ValidationError("Mã hạng trường đã tồn tại")
        else:
            pass
class loaihinhtruong(models.Model):
    _name = 'solienlac.loaihinhtruong'
    _rec_name = 'tenloahinhtruong' # optional
    # _description = 'Loại hình trường'

    maloaihinhtruong = fields.Integer('Loại hình trường', required=True)
    tenloahinhtruong = fields.Selection([
        ('1',	'Công lập'),
        ('2', 	'Bán công'),
        ('3',	'Dân lập'),
        ('4',	'Tư thục'),
        ('5',	'Chuyên'),
        ('6',	'Chuyên ban'),
        ('7',	'Kỹ thuật'),
        ('8',	'Khác'),
    ], default='4', string='Tên loại hình trường', required=True)
    ghichu = fields.Char('Ghi chú')

    @api.constrains('maloaihinhtruong')
    def _maloaihinhtruong_uniq(self):
        lst = self.env['solienlac.loaihinhtruong'].search([])
        lst = map(lambda x : x.maloaihinhtruong, lst)
        lst.remove(self.maloaihinhtruong)
        # print lst
        if self.maloaihinhtruong in lst:
            raise exceptions.ValidationError("Mã loại hình trường đã tồn tại")
        else:
            pass

class truongchuyenbiet(models.Model):
    _name = 'solienlac.truongchuyenbiet'
    _rec_name = 'tentruongchuyenbiet' # optional
    # _description = 'Trường chuyên biệt'

    matruongchuyenbiet = fields.Integer('Mã trường chuyên biệt', required=True)
    tentruongchuyenbiet = fields.Char('Tên trường chuyên biệt', required=True)
    # tentruongchuyenbiet = fields.Selection([
    #     ('1',	'Năng khiếu TDTT'),
    #     ('2', 	'Khuyết tật'),
    #     ('3',	'Năng khiếu nghệ thuật'),
    #     ('4',	'Chuyên'),
    #     ('5',	'Dân tộc nội trú'),
    #     ('6',	'THPT Kỹ thuật'),
    #     ('7',	'Dự bị đại học'),
    # ], default='4', string='Tên trường chuyên biệt')
    ghichu = fields.Char('Ghi chú')

    @api.constrains('matruongchuyenbiet')
    def _truongchuyenbiet_uniq(self):
        lst = self.env['solienlac.truongchuyenbiet'].search([])
        lst = map(lambda x : x.matruongchuyenbiet, lst)
        lst.remove(self.matruongchuyenbiet)
        # print lst
        if self.matruongchuyenbiet in lst:
            raise exceptions.ValidationError("Mã trường chuyên biệt đã tồn tại")
        else:
            pass
class loailopnho(models.Model):
    _name = 'solienlac.loailopnho'
    _rec_name = 'tenloailopnho' # optional

    maloailopnho = fields.Integer('Mã loại lớp nhô', required=True)
    tenloailopnho = fields.Char('Tên loại lớp nhô', required=True)
    # tenloailopnho = fields.Selection([
    #     ('khong', 'Không'),
    #     ('nhotren', 'Nhô trên'),
    #     ('nhoduoi', 'Nhô duoi'),
    #     ('nhotrenduoi', 'Nhô trên và dưới')],default='khong',string="Lớp nhô")
    ghichu = fields.Char('Ghi chú')

class truong(models.Model):
    _name = 'solienlac.truong'
    _rec_name = 'tentruong'

    matruong = fields.Char('Mã trường', required=True)
    tentruong = fields.Char('Tên trường', required=True)
    hieutruong = fields.Char(string='Hiệu trưởng')
    namthanhlap = fields.Char('Năm thành lập')
    @api.constrains('namthanhlap')
    def _validate_namthanhlap(self):
        now = datetime.datetime.now()
        current_year = int(now.year)
        if self.namthanhlap != False:
            if len(str(self.namthanhlap)) == 4:
                try:
                    print(self.namthanhlap)
                    d = int(self.namthanhlap)
                    if d < 1930 or d > current_year:
                        print 12
                        raise exceptions.ValidationError("Giá trị năm thành lập không hợp lệ!")
                except ValueError:
                    raise exceptions.ValidationError("Giá trị năm thành lập không hợp lệ!")
            else:
                raise exceptions.ValidationError("Giá trị năm thành lập không hợp lệ!")
    fax = fields.Char('Fax')
    email = fields.Char('Email')
    sodienthoai = fields.Char('Số điện thoại')
    @api.constrains('sodienthoai')
    def check_number(self):
        if self.sodienthoai != False:
            if len(str(self.sodienthoai)) < 10:
                raise exceptions.ValidationError("Số điện thoại không hợp lệ!")
            try:
                int(self.sodienthoai)
            except ValueError:
              raise exceptions.ValidationError("Số điện thoại không hợp lệ!")
    website = fields.Char('Website')


    tinhthanhpho = fields.Many2one('solienlac.tinhthanhpho', string='Tỉnh/Thành phố')
    quanhuyen = fields.Many2one('solienlac.quanhuyen', string='Quận/Huyện')
    phuongxa = fields.Many2one('solienlac.phuongxa', string='Xã/Phường')
    @api.onchange('tinhthanhpho')
    def set_value_huyen(self):
        self.quanhuyen = []
        tmp1 = self.env['solienlac.quanhuyen'].search([
                    ('matinhthanhpho', '=', self.tinhthanhpho.matinhthanhpho),
                ])
        lst = map(lambda x:x.matinhthanhpho, tmp1)
        return {'domain':{'quanhuyen': [('matinhthanhpho', 'in', lst)]}}

    @api.onchange('tinhthanhpho', 'quanhuyen')
    def set_value_xa(self):
        self.phuongxa = []
        tmp1 = self.env['solienlac.phuongxa'].search([
                    ('TinhID', '=', self.tinhthanhpho.matinhthanhpho),
                    ('QuanHuyenID', '=', self.quanhuyen.maquanhuyen),
                ])
        lst = map(lambda x: x.QuanHuyenID, tmp1)
        return {'domain':{'phuongxa': [('QuanHuyenID', 'in', lst)]}}
    # matinhthanhpho = fields.Integer('Tỉnh/Thành phố ID')
    # maquanhuyen = fields.Integer('Quận/Huyện ID')
    # maphuongxa = fields.Integer('Xã/Phường ID')
    diachi = fields.Char('Địa chỉ')

    hethonggiaoduc = fields.Integer('Hệ thống giáo dục ID')
    hangtruong = fields.Many2one('solienlac.hangtruong', string='Hạng trường')

    captruong = fields.Many2one('solienlac.captruong', string='Cấp trường ID')
    caphoc = fields.Many2one('solienlac.caphoc', string='Cấp học ID')
    truongchuyenbiet = fields.Many2one('solienlac.truongchuyenbiet', string='Trường chuyên biệt')
    loaihinhtruong = fields.Many2one('solienlac.loaihinhtruong', string='Loại hình trường')

    # loailopnho = fields.Integer('Loại lớp nhô')
    loailopnho = fields.Many2one('solienlac.loailopnho', string='Loại lớp nhô')
    donviID = fields.Integer('Đơn vị')
    thanhthi = fields.Boolean('Thành thị')
    chatluongcao = fields.Boolean('Chất lượng cao')
    bdkk = fields.Boolean('BDKK')
    trangthai = fields.Boolean('Trạng thái')

    toado_x = fields.Integer('Tọa độ x')
    toado_y = fields.Integer('Tọa độ y')
    biengioi = fields.Boolean('Biên giới')


    giaovien = fields.One2many(string="Giáo viên của trường", comodel_name="solienlac.giaovien", inverse_name="truong")
    # hocsinh = fields.One2many(string="Học sinh của trường", comodel_name="solienlac.hocsinh", inverse_name="truong")
    khoi = fields.One2many(string="Khối", comodel_name="solienlac.khoi", inverse_name="truong")

    @api.constrains('matruong')
    def _truong_uniq(self):
        lst = self.env['solienlac.truong'].search([])
        lst = map(lambda x : x.matruong, lst)
        lst.remove(self.matruong)
        # print lst
        if self.matruong in lst:
            raise exceptions.ValidationError("Mã trường đã tồn tại")
        else:
            pass

class giaovien(models.Model):
    _name = 'solienlac.giaovien'
    _rec_name = 'hoten' # optional
    lop = fields.One2many(string="Lớp", comodel_name="solienlac.lop", inverse_name="gvcn")
    magiaovien = fields.Char("Mã giáo viên", required=True)
    hoten = fields.Char("Họ tên", required=True)
    gioitinh = fields.Selection([
            ('Nam', 'Nam'),
            ('Nu', 'Nữ'),
            ('KXD', 'Không xác định')], string = "Giới tính")
    ngaysinh = fields.Date(string="Ngày sinh")
    noisinh = fields.Char('Nơi sinh')
    sodienthoai = fields.Char("Số điện thoại")
    @api.constrains('sodienthoai')
    def check_number(self):
        if self.sodienthoai != False:
            if len(str(self.sodienthoai)) < 10:
                raise exceptions.ValidationError("Số điện thoại không hợp lệ!")
            try:
                int(self.sodienthoai)
            except ValueError:
              raise exceptions.ValidationError("Số điện thoại không hợp lệ!")
    socmnd = fields.Char("Số chứng minh thư/căn cước")
    email = fields.Char("Email",required=True)
    matkhau = fields.Char("Mật khẩu")
    chucvu = fields.Many2one('solienlac.chucvu', "Chức vụ")
    dien = fields.Selection([
            ('cohuu', 'Cơ hữu'),
            ('thinhgiang', 'Thỉnh giảng')], string="Diện")
    vanbang = fields.Selection([
            ('trunghoccoso', 'Trung học cơ sở'),
            ('trunghocphothong', 'Trung học phổ thông'),
            ('trungcap', 'Trung cấp'),
            ('caodang', 'Cao đẳng'),
            ('daihoc', 'Đại học'),
            ('thacsi', 'Thạc sĩ'),
            ('tiensi', 'Tiến sĩ')], string="Văn bằng")
    namvaonganh = fields.Date('Năm vào ngành')
    tinhtranghonnhan = fields.Selection(
        string="Tình trạng hôn nhân",
        selection=[
                ('chualapgiadinh', 'Chưa lập gia đình'),
                ('dalapgiadinh', 'Đã lập gia đình'),
                ('lyhon', 'Ly hôn'),
        ],
    )
    phuongxa = fields.Many2one('solienlac.phuongxa', string='Phường\Xã')
    quanhuyen = fields.Many2one('solienlac.quanhuyen', string='Quận\Huyện')
    tinhthanhpho = fields.Many2one('solienlac.tinhthanhpho', string='Tỉnh\Thành phố')
    @api.multi
    @api.onchange('tinhthanhpho')
    def set_value_huyen(self):
        self.quanhuyen = []
        tmp1 = self.env['solienlac.quanhuyen'].search([
                    ('matinhthanhpho', '=', self.tinhthanhpho.matinhthanhpho),
                ])
        lst = map(lambda x:x.matinhthanhpho, tmp1)
        return {'domain':{'quanhuyen': [('matinhthanhpho', 'in', lst)]}}
    @api.multi
    @api.onchange('tinhthanhpho', 'quanhuyen')
    def set_value_xa(self):
        self.phuongxa = []
        tmp1 = self.env['solienlac.phuongxa'].search([
                    ('TinhID', '=', self.tinhthanhpho.matinhthanhpho),
                    ('QuanHuyenID', '=', self.quanhuyen.maquanhuyen),
                ])
        lst = map(lambda x: x.QuanHuyenID, tmp1)
        return {'domain':{'phuongxa': [('QuanHuyenID', 'in', lst)]}}
    diachi = fields.Char('Địa chỉ')
    dantoc = fields.Many2one('solienlac.dantoc', string = "Dân tộc")
    tongiao = fields.Many2one('solienlac.tongiao', string = "Tôn giáo")
    to = fields.Many2one('solienlac.to', string = "Tổ")
    phongban = fields.Many2one('solienlac.phongban', string = "Phòng ban")
    bomon = fields.Many2many('solienlac.bomon', string = "Bộ môn")
    monhoc = fields.One2many('solienlac.monhoc_has_giaovien', 'giaovien', string = "Lớp")
    lops = fields.One2many(string="Lớp", comodel_name="solienlac.monhoc_has_giaovien", inverse_name="giaovien")
    truong = fields.Many2one('solienlac.truong', string = "Trường", required=True, readonly = False, default=lambda self: self.env.user.truong.id)
    @api.constrains('magiaovien')
    def _validate_magiaovien(self):
        lst_magiaovien = self.env['solienlac.giaovien'].search([])
        lst_magiaovien = map(lambda x : x.magiaovien, lst_magiaovien)
        lst_magiaovien.remove(self.magiaovien)
        # print lst_magiaovien
        if self.magiaovien in lst_magiaovien:
            raise exceptions.ValidationError("Mã giáo viên đã tồn tại")
        else:
            pass
    @api.constrains('email')
    def _validate_email(self):
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", self.email) != None:
            # return True
            pass
        else:
            raise exceptions.ValidationError("Email không hợp lệ!")


class monhoc_has_giaovien(models.Model):
    _name = 'solienlac.monhoc_has_giaovien'
    _rec_name = 'lop'
    # namhoc = fields.Char('Năm học')

    #---------- define fields namhoc ------------
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc

    @api.model
    def _get_current_namhoc(self):
        try:
            namhoc = self.env['solienlac.hocky'].search([
                ('trangthai' , '=', 'HienTai'),
                ('truong.id', '=', self.env.user.truong.id)
            ])[-1]
            return namhoc.namhoc
        except:
            now = datetime.datetime.now()
            year = now.year
            if now.month <= 9:
                year -= 1
            return str(year) + "-" + str(year+1)

    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_current_namhoc,
        required=True,
        readonly=True
    )
    #---------- end define fields namhoc ------------
    @api.model
    def _get_current_hocky(self):
        try:
            hocky = self.env['solienlac.hocky'].search([
                ('trangthai' , '=', 'HienTai'),
                ('truong.id', '=', self.env.user.truong.id)
            ])[-1]
            return hocky.hocky
        except:
            now = datetime.datetime.now()
            month = now.month
            if month in [1,2,3,4,5,6,7]:
                return 'ii'
            else:
                return 'i'

    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
        ],required=True, default = _get_current_hocky, readonly=True )
    monhoc = fields.Many2one('solienlac.monhoc', string='Môn học',required=True)
    giaovien = fields.Many2one('solienlac.giaovien', string='Giáo viên')
    lop = fields.Many2one('solienlac.lop', string='Lớp',required=True)

    @api.constrains('hocky','namhoc','lop','monhoc')
    def _validate_phancong(self):
        obj = self.env['solienlac.monhoc_has_giaovien'].search([
            ('hocky','=',self.hocky),
            ('namhoc','=',self.namhoc),
            ('lop.id','=',self.lop.id),
            ('monhoc.id','=',self.monhoc.id),
        ])
        n = len(obj)
        if n>1:
            obj = map(lambda x: x.giaovien, obj)
            obj.remove(self.giaovien)
            s=u'Dữ liệu đã tồn tại !.'
            raise exceptions.ValidationError(s)
        else:
            pass

class lop_has_giaovien(models.Model):
    _name = 'solienlac.lop_has_giaovien'
    _rec_name = 'giaovien'
    lop = fields.Many2one('solienlac.lop', string='Lớp')
    giaovien = fields.Many2one('solienlac.giaovien', string='Giáo viên')
    # namhoc = fields.Char('Năm học')
    #---------- define fields namhoc ------------
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc

    @api.model
    def _get_namhoc_now(self):
        now = datetime.datetime.now()
        year = now.year
        if now.month <= 9:
            year -= 1
        return str(year) + "-" + str(year+1)

    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_namhoc_now,
    )
    #---------- end define fields namhoc ------------
    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                # ('iii', 'Cả năm'),
        ],default = 'i')
    ngaybatdau = fields.Date('Ngày bắt đầu:')
    ngayketthuc = fields.Date('Ngày kết thúc: ')

class to(models.Model):
    _name = 'solienlac.to'
    _rec_name = 'tento' # optional
    mato = fields.Char("Mã tổ", required=True)
    tento = fields.Char("Tên tổ", required=True)
    ghichu = fields.Char("Ghi chú")
    totruong = fields.Many2one('solienlac.giaovien', string = "Tổ trưởng")

    @api.constrains('mato')
    def _to_uniq(self):
        lst = self.env['solienlac.to'].search([])
        lst = map(lambda x : x.mato, lst)
        lst.remove(self.mato)
        # print lst
        if self.mato in lst:
            raise exceptions.ValidationError("Mã tổ đã tồn tại")
        else:
            pass

class phuongxa(models.Model):
    _name = 'solienlac.phuongxa'
    _rec_name = 'tenphuongxa' # optional
    # maphuongxa = fields.Char("Mã phường/xã")
    tenphuongxa = fields.Char("Tên phường/xã", required=True)
    ghichu = fields.Char("Ghi chú")
    # quanhuyen = fields.Many2one('solienlac.quanhuyen', string = "Quận/Huyện")
    TinhID = fields.Integer('Tỉnh ID', required=True)
    QuanHuyenID = fields.Integer('Quận huyện ID', required=True)
    PhuongXaID = fields.Integer('Phường xã ID', required=True)
    VungDiaLyID = fields.Integer('Vùng địa lý ID')
    TenPhuongXa_VT=fields.Integer('Tên phường xã VT')
    KhoKhan=fields.Boolean('Khó khăn')
    BienGioi =fields.Boolean('Biên giới')
    HspcKvuc=fields.Char('Hệ số phụ cấp khu vực')

    @api.constrains('PhuongXaID')
    def _phuong_xa_uniq(self):
        lst = self.env['solienlac.phuongxa'].search([])
        lst = map(lambda x : x.PhuongXaID, lst)
        lst.remove(self.PhuongXaID)
        # print lst/
        if self.PhuongXaID in lst:
            raise exceptions.ValidationError("Mã phường/xã đã tồn tại")
        else:
            pass

class quanhuyen(models.Model):
    _name = 'solienlac.quanhuyen'
    _rec_name = 'tenquanhuyen' # optional
    _description = 'Module description'
    maquanhuyen = fields.Integer("Mã quận/huyện", required=True)
    tenquanhuyen = fields.Char("Tên quận/huyện", required=True)
    ghichu = fields.Char("Ghi chú")
    # tinhthanhpho = fields.Many2one('solienlac.tinhthanhpho', string = "Tỉnh/Thành phố")
    tenquanhuyenVT=fields.Integer("Tên quận/huyện viết tắt")
    vungdialy = fields.Integer(string="Vùng địa lý")
    matinhthanhpho = fields.Integer(string="Mã tỉnh/thành phố", required=True)

    @api.constrains('maquanhuyen')
    def _quan_huyen_uniq(self):
        lst = self.env['solienlac.quanhuyen'].search([])
        lst = map(lambda x : x.maquanhuyen, lst)
        lst.remove(self.maquanhuyen)
        # print lst
        if self.maquanhuyen in lst:
            raise exceptions.ValidationError("Mã Quận/Huyện đã tồn tại")
        else:
            pass


class tinhthanhpho(models.Model):
    _name = 'solienlac.tinhthanhpho'
    _rec_name = 'tentinhthanhpho' # optional
    matinhthanhpho = fields.Integer("Mã tỉnh/thành phố", required=True)
    tentinhthanhpho = fields.Char("Tên tỉnh/thành phố", required=True)
    tentinhviettat = fields.Char('Tên tỉnh viết tắt')
    vungdialy = fields.Integer("Vùng địa lý")
    vungkinhte = fields.Integer("Vùng kinh tế")
    ghichu = fields.Char("Ghi chú")

    @api.constrains('matinhthanhpho')
    def _tinh_thanhpho_uniq(self):
        lst = self.env['solienlac.tinhthanhpho'].search([])
        lst = map(lambda x : x.matinhthanhpho, lst)
        lst.remove(self.matinhthanhpho)
        # print lst

        if self.matinhthanhpho in lst:
            raise exceptions.ValidationError("Mã Tỉnh/Thành phố đã tồn tại")
        else:
            pass

class dantoc(models.Model):
    _name = 'solienlac.dantoc'
    _rec_name = 'tendantoc' # optional
    madantoc = fields.Integer("Mã dân tộc", required=True)
    tendantoc = fields.Char("Tên dân tộc", required=True)
    ghichu = fields.Char("Ghi chú")

    @api.constrains('madantoc')
    def _dantoc_uniq(self):
        lst = self.env['solienlac.dantoc'].search([])
        lst = map(lambda x : x.madantoc, lst)
        lst.remove(self.madantoc)
        # print lst
        if self.madantoc in lst:
            raise exceptions.ValidationError("Mã dân tộc đã tồn tại")
        else:
            pass
class tongiao(models.Model):
    _name = 'solienlac.tongiao'
    _rec_name = 'tentongiao' # optional
    matongiao = fields.Integer("Mã tôn giáo", required=True)
    tentongiao = fields.Char("Tên tôn giáo", required=True)
    ghichu = fields.Char("Ghi chú")

    @api.constrains('matongiao')
    def _tongiao_uniq(self):
        lst = self.env['solienlac.tongiao'].search([])
        lst = map(lambda x : x.matongiao, lst)
        lst.remove(self.matongiao)
        # print lst
        if self.matongiao in lst:
            raise exceptions.ValidationError("Mã tôn giáo đã tồn tại")
        else:
            pass

class phongban(models.Model):
    """docstring for phongban."""
    _name = 'solienlac.phongban'
    _rec_name = 'tenphongban' # optional
    maphongban = fields.Char("Mã phòng ban", required=True)
    tenphongban = fields.Char("Tên phòng ban", required=True)
    sodienthoai = fields.Char("Số điện thoại")
    @api.constrains('sodienthoai')
    def check_number(self):
        if self.sodienthoai != False:
            if len(str(self.sodienthoai)) < 10:
                raise exceptions.ValidationError("Số điện thoại không hợp lệ!")
            try:
                int(self.sodienthoai)
            except ValueError:
              raise exceptions.ValidationError("Số điện thoại không hợp lệ!")

    ghichu = fields.Char("Ghi chú")
    truongphong = fields.Many2one('solienlac.giaovien', string = "Trưởng phòng")
    @api.constrains('maphongban')
    def _dantoc_uniq(self):
        lst = self.env['solienlac.phongban'].search([])
        lst = map(lambda x : x.maphongban, lst)
        lst.remove(self.maphongban)
        # print lst
        if self.maphongban in lst:
            raise exceptions.ValidationError("Mã phòng ban đã tồn tại")
        else:
            pass

class doituongchinhsach(models.Model):
    _name = 'solienlac.doituongchinhsach'
    _rec_name = 'tendoituongchinhsach' # optional
    madoituongchinhsach = fields.Integer('Mã đối tượng chính sách')
    tendoituongchinhsach = fields.Char(string='Tên đối tượng chính sách', required=True)
    miengiam = fields.Float(string='Miễn Giảm')
    ghichu = fields.Char(string='Ghi Chú')

class doituonguutien(models.Model):
    _name = 'solienlac.doituonguutien'
    _rec_name = 'tendoituonguutien' # optional
    madoituonguutien = fields.Integer(string='Mã đối tượng ưu tiên', required=True)
    tendoituonguutien = fields.Char(string='Tên đối tượng ưu tiên')
    ghichu = fields.Char(string='Ghi Chú')

class khenthuongkyluat(models.Model):
    _name = 'solienlac.khenthuongkyluat'
    _rec_name = 'tenkhenthuongkyluat' # optional
    tenkhenthuongkyluat = fields.Char(string='Tên Khen Thưởng Kỷ Luật')
    hinhthuckhenthuongkyluat = fields.Char(string='Hình Thức Khen Thưởng Kỷ Luật')
    ghichu = fields.Char(string='Ghi Chú')

class kyluathocsinh(models.Model):
    _name = 'solienlac.kyluathocsinh'
    _rec_name = 'lydokyluat' # optional
    lydokyluat = fields.Char(string='Lý do kỷ luật', required=True)
    hinhthuckyluat = fields.Selection(
        string="Hình thức kỷ luật",
        selection=[
                ('1', 'Phê bình trước lớp, trước trường'),
                ('2', 'Khiển trách và thông cáo với gia đình'),
                ('3', 'Cảnh cáo, ghi học bạ'),
                ('4', 'Buộc thôi học có thời hạn'),
                ('5', 'Khác'),
        ], required=True)
    thoihantu = fields.Date(string="Thời hạn từ", )
    thoihanden = fields.Date(string="Thời hạn đến", )
    ghichu = fields.Char(string='Ghi Chú')
    hocsinh = fields.Many2many("solienlac.hocsinh",string="Học sinh")

    @api.constrains('hocsinh')
    def _kyluat_constrains(self):
        if(len(self.hocsinh) <= 0):
            raise exceptions.ValidationError('Hãy thêm ít nhất một học sinh!')
# class khenthuonghocsinh(models.Model):
#     _name = 'solienlac.khenthuonghocsinh'
#     _rec_name = 'lydokhenthuong' # optional
#     lydokhenthuong = fields.Char(string="Lý do khen thưởng", )
#     hinhthuckhenthuong = fields.Selection(
#         string="Hình thức khen thưởng",
#         selection=[
#                 ('1', 'Khen trước lớp, trước trường'),
#                 ('2', 'Được tặng danh hiệu'),
#                 ('3', 'Được ghi tên vào bảng danh dự của trường'),
#                 ('4', 'Được khen thưởng đặc biệt'),
#                 ('5', 'Khác'),
#         ],
#     )
#     ghichu = fields.Char(string="Ghi chú", )
#
#     ngaykhenthuong = fields.Date(string="Ngày khen thưởng", )
#     lop = fields.Many2many("solienlac.lop", string="Học sinh")
#
# class chitietkhenthuong(models.Model):
#     _name = 'solienlac.chitietkhenthuong'
#     lydokhenthuong = fields.Char(string="Lý do khen thưởng", )
#     hinhthuckhenthuong = fields.Selection(
#         string="Hình thức khen thưởng",
#         selection=[
#                 ('1', 'Khen trước lớp, trước trường'),
#                 ('2', 'Được tặng danh hiệu'),
#                 ('3', 'Được ghi tên vào bảng danh dự của trường'),
#                 ('4', 'Được khen thưởng đặc biệt'),
#                 ('5', 'Khác'),
#         ],
#     )
#     ghichu = fields.Char(string="Ghi chú", )
#
#     ngaykhenthuong = fields.Date(string="Ngày khen thưởng", )
#     lop = fields.Many2many("solienlac.lop", string="Học sinh")

class khenthuongkyluat_hocsinh(models.Model):
    _name = 'solienlac.khenthuongkyluat_hocsinh'
    _rec_name = 'ngay_ktkl' # optional
    ktkl = fields.Many2one('solienlac.khenthuongkyluat', string='ID Khen Thưởng Kỷ Luật', required=True)
    hocsinh = fields.Many2one('solienlac.hocsinh', string='ID Học Sinh', required=True)
    ngay_ktkl = fields.Date(string='Ngày Khen Thưởng Kỷ Luật')

class tuyenhoc(models.Model):
    _name = 'solienlac.tuyenhoc'
    _rec_name = 'tentuyen' # optional
    matuyen = fields.Char(string='Mã Tuyến', required=True)
    tentuyen = fields.Char(string='Tên Tuyến', required=True)
    ghichu = fields.Char(string='Ghi Chú')

    @api.constrains('matuyen')
    def _tuyenhoc_uinq(self):
        lst = self.env['solienlac.tuyenhoc'].search([])
        lst = map(lambda x: x.matuyen, lst)
        lst.remove(self.matuyen)
        if self.matuyen in lst:
            raise exceptions.ValidationError(' Mã tuyến học đã tồn tại. ')
        else:
            pass
class khoi(models.Model):
    _name = 'solienlac.khoi'
    _rec_name = 'tenkhoi' # optional
    @api.model
    def _get_curret_truong(self):
        # lấy ra id trường
        # uid = self.env.id
        try:
            current_user = self.env.user
            login_name = current_user.login
            current_magv = login_name
            current_gv = self.env['solienlac.giaovien'].search([
                ('magiaovien','=',current_magv),
            ])[0]
            current_truong_id = current_gv.truong.id
            # trả về domain
            # print current_truong_id
            return [('id','=',current_truong_id)]
        except:
            return [('id','!=',-1)]

    makhoi = fields.Integer(string='Mã Khối', required=True)
    tenkhoi = fields.Char(string='Tên Khối', required=True)
    ghichu = fields.Char('Ghi Chú')
    # truong = fields.Many2one(
    # 'solienlac.truong', string = "Trường",
    # domain = _get_curret_truong )
    truong = fields.Many2one(
        string="Trường",
        comodel_name="solienlac.truong",
        # domain="[('field', '=', other)]",
        domain=_get_curret_truong,
        default= lambda self: self.env.user.truong,
    )

    lop = fields.One2many(
        string="Lớp trong khối",
        comodel_name="solienlac.lop",
        inverse_name="khoi",
    )

    @api.constrains('makhoi')
    def _khoi_uinq(self):
        lst = self.env['solienlac.khoi'].search([])
        lst = map(lambda x: x.makhoi, lst)
        lst.remove(self.makhoi)
        if self.makhoi in lst:
            raise exceptions.ValidationError(' Mã khối học đã tồn tại.')
        else:
            pass

class hanhkiem(models.Model):
    _name = 'solienlac.hanhkiem'
    _rec_name = 'xeploai' # optional

    @api.model
    def _get_current_hocky(self):
        try:
            hocky = self.env['solienlac.hocky'].search([
                ('trangthai' , '=', 'HienTai'),
                ('truong.id', '=', self.env.user.truong.id)
            ])[-1]
            return hocky.hocky
        except:
            now = datetime.datetime.now()
            month = now.month
            if month in [1,2,3,4,5,6,7]:
                return 'ii'
            else:
                return 'i'
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc
    @api.model
    def _get_current_namhoc(self):
        try:
            namhoc = self.env['solienlac.hocky'].search([
                ('trangthai' , '=', 'HienTai'),
                ('truong.id', '=', self.env.user.truong.id)
            ])[-1]
            return namhoc.namhoc
        except:
            now = datetime.datetime.now()
            year = now.year
            if now.month <= 9:
                year -= 1
            return str(year) + "-" + str(year+1)

    namhoc = fields.Selection( string="Năm học",
        selection= _get_list_namhoc, default = _get_current_namhoc, readonly=True, required=True)
    hocky = fields.Selection(selection=[
        ('i', 'Học kỳ I'), ('ii', 'Học kỳ II'), ('iii', 'Cả năm'), ],
        default = _get_current_hocky, readonly=True, string="Học kỳ", required=True)
    xeploai = fields.Selection(
        string="Xếp loại",
        selection=[
                ('tot', 'Tốt'),
                ('kha', 'Khá'),
                ('tb', 'Trung bình'),
                ('yeu', 'Yếu'),
                # ('kem', 'Kém'),
        ], required=True)
    nhanxetcuagiaovien = fields.Text('Nhận Xét Của Giáo Viên', required=True)
    giaovien = fields.Many2one('solienlac.giaovien', string='Giáo viên nhận xét',
        default=lambda self: self.env.user.giaovien, required=True)
    ghichu = fields.Char('Ghi Chú')
    hocsinh = fields.Many2one('solienlac.hocsinh', string='Học sinh',
        domain=['id','=',-1], required=True)
    lop = fields.Many2one(string="Lớp", comodel_name="solienlac.lop",
        domain=['id','=',-1], required=True)
    khoi = fields.Many2one(string="Khối", comodel_name="solienlac.khoi", required=True)
    truong = fields.Many2one(string="Trường", comodel_name="solienlac.truong",
        default=lambda self: self.env.user.truong.id,  required=True)
    @api.onchange('khoi')
    def _lop_baseon_khoi(self):
        lops = self.env['solienlac.lop'].search([('khoi.id','=',self.khoi.id)])
        lops = [lop.id for lop in lops]
        return {'domain':{'lop': [('id', 'in', lops)]}}
    @api.onchange('lop')
    def _hs_baseon_lop(self):
        hss = self.env['solienlac.hocsinh'].search([('lop.id','=',self.lop.id)])
        hss = [hs.id for hs in hss]
        return {'domain':{'hocsinh': [('id', 'in', hss)]}}
    @api.constrains('namhoc', 'hocky', 'hocsinh')
    def _validate_hanhkiem(self):
        obj = self.env['solienlac.hanhkiem'].search([
            ('hocky','=',self.hocky),
            ('namhoc','=',self.namhoc),
            ('hocsinh','=',self.hocsinh.id),
        ])
        n = len(obj)
        if n>1:
            s=u'Đã xét hạnh kiểm cho học sinh vào kỳ học này rồi'
            raise exceptions.ValidationError(s)
        else:
            pass

class phuhuynh(models.Model):
    _name = 'solienlac.phuhuynh'
    _rec_name = 'hoten' # optional
    hoten = fields.Char('Họ Tên', required=True)
    gioitinh = fields.Selection([
            ('Nam', 'Nam'),
            ('Nu', 'Nữ'),
            ('KXD', 'Không xác định')], string = "Giới tính", required=True)
    ngaysinh = fields.Date('Ngày Sinh')
    sodienthoai = fields.Char('Số Điện Thoại', required=True)
    @api.constrains('sodienthoai')
    def check_number(self):
        if self.sodienthoai != False:
            if len(str(self.sodienthoai)) < 10:
                raise exceptions.ValidationError("Số điện thoại không hợp lệ!")
            try:
                int(self.sodienthoai)
            except ValueError:
              raise exceptions.ValidationError("Số điện thoại không hợp lệ!")
    ghichu = fields.Char('Ghi Chú')

    diachi = fields.Char('Địa chỉ', )
    phuongxa = fields.Many2one('solienlac.phuongxa', string='Phường\Xã')
    quanhuyen = fields.Many2one('solienlac.quanhuyen', string='Quận\Huyện',)
    tinhthanhpho = fields.Many2one('solienlac.tinhthanhpho', string='Tỉnh\Thành phố', )

    @api.multi
    @api.onchange('tinhthanhpho')
    def set_value_huyen(self):
        self.quanhuyen = []
        tmp1 = self.env['solienlac.quanhuyen'].search([
                    ('matinhthanhpho', '=', self.tinhthanhpho.matinhthanhpho),
                ])
        lst = map(lambda x:x.matinhthanhpho, tmp1)
        return {'domain':{'quanhuyen': [('matinhthanhpho', 'in', lst)]}}
    @api.multi
    @api.onchange('tinhthanhpho', 'quanhuyen')
    def set_value_xa(self):
        self.phuongxa = []
        tmp1 = self.env['solienlac.phuongxa'].search([
                    ('TinhID', '=', self.tinhthanhpho.matinhthanhpho),
                    ('QuanHuyenID', '=', self.quanhuyen.maquanhuyen),
                ])
        lst = map(lambda x: x.QuanHuyenID, tmp1)
        return {'domain':{'phuongxa': [('QuanHuyenID', 'in', lst)]}}

    dantoc = fields.Many2one('solienlac.dantoc', string='Dân Tộc')
    tongiao = fields.Many2one('solienlac.tongiao', string='Tôn Giáo')

    nghenghiep = fields.Selection([
          	('value1', 'Công chức'),
            ('value2', 'Viên chức'),
            ('value3', 'Công nhân'),
            ('value4', 'Nông dân'),
            ('value5', 'Công an'),
            ('value6', 'Bộ đội'),
            ('value7', 'Doanh nhân'),
            ('value8', 'Lao động tự do'),
            ('value9', 'Nội trợ'),
            ('value10', 'Khác'),
        ], string = "Nghề nghiệp")
    quanhe = fields.Selection([
          	('value1', 'Bố đẻ'),
            ('value2', 'Mẹ đẻ'),
            ('value3', 'Anh ruột'),
            ('value4', 'Chị ruột'),
            ('value5', 'Em trai ruột'),
            ('value6', 'Em gái ruột'),
            ('value7', 'Bố dượng'),
            ('value8', 'Mẹ dượng'),
            ('value9', 'Bố nuôi'),
            ('value10', 'Mẹ nuôi'),
            ('value11', 'Vợ'),
            ('value12', 'Chồng'),
        ], string = "Nghề nghiệp")

    hocsinh = fields.Many2one('solienlac.hocsinh', string='Học Sinh')


class bomon(models.Model):
    _name = 'solienlac.bomon'
    _rec_name = 'tenbomon' # optional
    mabomon = fields.Integer('Mã bộ môn', required=True)
    tenbomon = fields.Char('Tên bộ môn', required=True)
    ghichu = fields.Char('Ghi chú')
    truongbomon = fields.Many2one('solienlac.giaovien', string = "Trưởng bộ môn")

    @api.constrains('mabomon')
    def _bomon_uinq(self):
        lst = self.env['solienlac.bomon'].search([])
        lst = map(lambda x: x.mabomon, lst)
        lst.remove(self.mabomon)
        if self.mabomon in lst:
            raise exceptions.ValidationError(' Mã bộ môn đã tồn tại.')
        else:
            pass
class bangdiemdanh(models.Model):
    _name = 'solienlac.bangdiemdanh'
    _rec_name = 'mabangdiemdanh' # optional
    mabangdiemdanh= fields.Char('Mã bảng điểm danh', required=True)
    ngayvang= fields.Date('Ngày vắng')
    tietvang= fields.Integer('Tiết vắng')
    ghichu= fields.Char('Ghi chú')
    hocsinh= fields.Many2one('solienlac.hocsinh', string='Học sinh')
    monhoc= fields.Many2one('solienlac.monhoc', string = 'Môn học')
    giaoviendiemdanh= fields.Many2one('solienlac.giaovien', string = 'Giáo viên điểm danh')

    @api.constrains('mabangdiemdanh')
    def _bangdiemdanh_uinq(self):
        lst = self.env['solienlac.bangdiemdanh'].search([])
        lst = map(lambda x: x.mabangdiemdanh, lst)
        lst.remove(self.mabangdiemdanh)
        if self.mabangdiemdanh in lst:
            raise exceptions.ValidationError(' Mã bảng điểm danh đã tồn tại.')
        else:
            pass
class hocsinh(models.Model):
    _name = 'solienlac.hocsinh'
    _rec_name = 'hoten' # optional

    mahocsinh = fields.Char('Mã học sinh', required=True)
    # @api.constrains('mahocsinh')
    # def _hocsinh_uinq(self):
    #     lst = self.env['solienlac.hocsinh'].search([])
    #     lst = map(lambda x: x.mahocsinh, lst)
    #     lst.remove(self.mahocsinh)
    #     if self.mahocsinh in lst:
    #         raise exceptions.ValidationError(' Mã học sinh đã tồn tại.')
    #     else:
    #         pass
    hoten = fields.Char('Họ tên', required=True)
    gioitinh = fields.Selection([
        ('Nam', 'Nam'),
        ('Nu', 'Nữ'),
        ('KXD', 'Không xác định')], string="Giới tính")
    ngaysinh = fields.Date(string="Ngày sinh")
    # noisinh = fields.Char('Nơi sinh')
    noisinh = fields.Char('Nơi sinh')

    username = fields.Char('Username')
    @api.onchange('mahocsinh')
    def set_username(self):
        self.username = self.mahocsinh

    password = fields.Char('Password', default='1234567890')
    # @api.onchange('mahocsinh')
    # def set_password(self):
    #     self.password = '1234567890'
        # self.password = hashlib.sha224(self.mahocsinh).hexdigest()[0:10]

    diachi = fields.Char('Địa chỉ')
    quequan = fields.Char('Quê quán')
    lop = fields.Many2one('solienlac.lop', string='Lớp', required=True)
    # truong = fields.Many2one('solienlac.truong', string = "Trường")
    tuyenhoc = fields.Many2one('solienlac.tuyenhoc', string='Tuyến học')

    phuongxa = fields.Many2one('solienlac.phuongxa', string='Phường\Xã')
    quanhuyen = fields.Many2one('solienlac.quanhuyen', string='Quận\Huyện')
    tinhthanhpho = fields.Many2one('solienlac.tinhthanhpho', string='Tỉnh\Thành phố')

    danhhieuhocsinh = fields.One2many('solienlac.danhhieuhocsinh', 'hocsinh', string = 'Danh hiệu học sinh')
    khenthuonghocsinh = fields.One2many('solienlac.khenthuongchitiet', 'hocsinh', string = 'Thành tích khen thưởng')
    kyluathocsinh = fields.Many2many('solienlac.kyluathocsinh', string = 'Kỷ luật học sinh')

    dantoc = fields.Many2one('solienlac.dantoc', string='Dân tộc')
    tongiao = fields.Many2one('solienlac.tongiao', string='Tôn giáo')
    @api.model
    def set_chucvu(self):
        return self.env['solienlac.chucvu'].browse([4,])
    chucvu = fields.Many2many('solienlac.chucvu', string='Chức vụ')#, default=set_chucvu

    doituongchinhsach = fields.Many2many('solienlac.doituongchinhsach', string='Đối tượng chính sách')
    doituonguutien = fields.Many2many('solienlac.doituonguutien', string='Đối tượng ưu tiên')
    phuhuynh = fields.Many2many('solienlac.phuhuynh', string='Phụ huynh')
    hanhkiem = fields.One2many("solienlac.hanhkiem", "hocsinh", string="Hạnh kiểm")
    ketquahoctap = fields.One2many('solienlac.ketquahoctap', 'hocsinh', string="Kết quả học tập", readonly=True)
    bangdiem = fields.One2many('solienlac.nhapdiemchitiet', 'hocsinh', string="Bảng điểm")
    nenep = fields.One2many('solienlac.nenep', 'hocsinh', string="Nề nếp")
    noitru = fields.Boolean('Nội trú', default=False)
    # @api.onchange('noitru')
    # def set_chucvu(self):
    #     print(self.chucvu)
    tinhtranghocsinh = fields.Selection(
        string="Tình trạng học sinh",
        selection=[
                ('value1', 'Học bình thường'),
                ('value2', 'Đã nghỉ học'),
        ],default='value1'
    )
    nguongochocsinh = fields.Many2one('solienlac.nguongochocsinh', string='Nguồn gốc học sinh')
    nangkhieu = fields.Selection(
        string="Năng khiếu",
        selection=[
                ('value1', 'Không có năng khiếu'),
                ('value2', 'Thể dục, thể thao'),
                ('value3', 'Âm nhạc'),
                ('value4', 'Mỹ thuật'),
                ('value5', 'Toán'),
                ('value6', 'Lý'),
                ('value7', 'Hóa'),
                ('value8', 'Sinh'),
                ('value9', 'Văn'),
                ('value10', 'Sử'),
                ('value11', 'Địa'),
                ('value12', 'Ngoại ngữ'),
                ('value13', 'Tin'),
                ('value14', 'Tự nhiên'),
                ('value15', 'Xã hội'),
                ('value16', 'Hoạt động xã hội'),
                ('value17', 'Khác'),
                ('value18', 'Không xác định'),
        ],default='value1',)
    monhocnghe = fields.Many2one(string="Môn học nghề",comodel_name="solienlac.monhocnghe")
    loaihocsinhnhaptruong = fields.Selection(
        string="Loại học sinh nhập trường",
        selection=[
                ('value1', 'Tuyển mới'),
                ('value2', 'Chuyển đến'),
                ('value3', 'Lên lớp'),
                ('value4', 'Ở lại lớp'),
                ('value5', 'Thí sinh tự do	Trong thi tốt nghiệp'),
                ('value6', 'Thi lại	Xét lên lớp'),
                ('value7', 'Rèn luyện lại	Xét lên lớp'),
                ('value8', 'TL&RLL	Xét lên lớp'),
        ],default='value1'
    )
    khuyettat = fields.Selection(
        string="Khuyết tật",
        selection=[
                ('value1', 'Không'),
                ('value2', 'Khiếm thính'),
                ('value3', 'Khiếm thị'),
                ('value4', 'Khó khăn vê hoạt động'),
                ('value5', 'Khó khăn về trí tuệ'),
                ('value6', 'Đa tật'),
                ('value7', 'Khuyết tật khác'),
                ('value8', 'Không xác định'),
        ],default='value1'
    )
    tochucdoanthe = fields.Many2one('solienlac.tochucdoanthe', string='Tổ chức')
    thoihoc = fields.Selection(
        string="Thôi học",
        selection=[
                ('value1', 'Không'),
                ('value2', 'Khiếm thính'),
                ('value3', 'Khiếm thị'),
                ('value4', 'Khó khăn vê hoạt động'),
                ('value5', 'Khó khăn về trí tuệ'),
                ('value6', 'Đa tật'),
                ('value7', 'Khuyết tật khác'),
                ('value8', 'Không xác định'),
        ],
    )
    lydothoihoc = fields.Many2one(string="Lý do thôi học",comodel_name="solienlac.lydothoihoc")
    # user_login = fields.Char('Login')
    # test = fields.Char('test', compute='set_acc')
    # user_login = fields.Char('Login', compute='set_acc')
    # user_id = fields.Many2one(
    #     'res.users', string='User', default=lambda self:self.env.user)

    @api.multi
    def set_acc(self):
        uid = self.env.uid
        user = self.env['res.users'].search([('id', '=', uid)])
        if(self.mahocsinh == user.login):
            self.user_login = "True"
        else:
            self.user_login = "False"

    @api.multi
    @api.onchange('tinhthanhpho')
    def set_value_huyen(self):
        self.quanhuyen = []
        tmp1 = self.env['solienlac.quanhuyen'].search([
                    ('matinhthanhpho', '=', self.tinhthanhpho.matinhthanhpho),
                ])
        lst = map(lambda x:x.matinhthanhpho, tmp1)
        return {'domain':{'quanhuyen': [('matinhthanhpho', 'in', lst)]}}
    @api.multi
    @api.onchange('tinhthanhpho', 'quanhuyen')
    def set_value_xa(self):
        self.phuongxa = []
        tmp1 = self.env['solienlac.phuongxa'].search([
                    ('TinhID', '=', self.tinhthanhpho.matinhthanhpho),
                    ('QuanHuyenID', '=', self.quanhuyen.maquanhuyen),
                ])
        lst = map(lambda x: x.QuanHuyenID, tmp1)
        return {'domain':{'phuongxa': [('QuanHuyenID', 'in', lst)]}}

    khoi = fields.Many2one(store = True,readonly = True , string="Khối học", comodel_name="solienlac.khoi", compute='_get_khoi')
    @api.depends('lop')
    def _get_khoi(self):
        for r in self:
            r.khoi = r.lop.khoi

    truong = fields.Many2one(store = True,readonly = True , string="Trường học", comodel_name="solienlac.truong", compute='_get_truong')
    @api.depends('lop')
    def _get_truong(self):
        for r in self:
            r.truong = r.lop.khoi.truong

    @api.model
    def create(self, values):
        groups1 = self.env['res.groups'].search([
            ('name','ilike','CUST:'),
        ])[0].id
        lop_id = values['lop']
        truong_id = self.env['solienlac.lop'].search([
            ('id','=',lop_id),
        ])[0].khoi.truong.id
        quyen_da_chon = []
        quyen_da_chon.append(1)
        quyen_da_chon.append(groups1)
        vals = {
            'name': values['hoten'],
            'login': values['username'],
            'password' : values['password'],
            'company_ids': [1],
            'company_id': 1,
            'groups_id': quyen_da_chon,
            'truong' : truong_id,
        }
        # print vals
        self.env['res.users'].sudo().create(vals)

        user = super(hocsinh, self).create(values)
        return user

    @api.multi
    def write(self, vals):
        '''Chi giao vien chu nhiem moi sua duoc hocsinh lop minh'''

        flag = True

        id_gvhientai = self.env.user.giaovien.id
        id_gvcn = self.lop.gvcn.id

        if id_gvhientai == id_gvcn:
            obj = super(hocsinh, self).write(vals)
            return obj
        else:
            raise exceptions.ValidationError("Error1: Không thể sửa thông tin học sinh ngoài lớp chủ nhiệm!")
            return

class lydothoihoc(models.Model):
    _name = 'solienlac.lydothoihoc'
    _rec_name = 'lydothoihoc'
    lydothoihoc = fields.Selection(
        string="Lý do thôi học",
        selection=[
                ('value1', 'Không'),
                ('value2', 'Chuyển đi'),
                ('value3', 'Kỷ luật buộc thôi học 1 năm'),
                ('value4', 'Học lực yếu kém'),
                ('value5', 'Xa nhà'),
                ('value6', 'Gia đình hoàn cảnh khó khăn'),
                ('value7', 'Lý do khác: tai nạn, ốm đau'),
        ],default='value1'
    )
    thoidiemthoihoc = fields.Date('Thời điểm thôi học')
    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],default = 'i')
    # namhoc = fields.Char('Năm học')

    #---------- define fields namhoc ------------
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc

    @api.model
    def _get_namhoc_now(self):
        now = datetime.datetime.now()
        year = now.year
        if now.month <= 9:
            year -= 1
        return str(year) + "-" + str(year+1)

    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_namhoc_now,
    )
    #---------- end define fields namhoc ------------

    ghichu = fields.Char('Ghi chú')
    hocsinh = fields.One2many('solienlac.hocsinh', 'lydothoihoc', string='Học sinh')
class nguongochocsinh(models.Model):
    _name = 'solienlac.nguongochocsinh'
    _rec_name = 'nguongochocsinh'
    nguongochocsinh = fields.Selection(
        string="Nguồn gốc học sinh",
        selection=[
                ('TuyenSinh', 'Tuyển sinh'),
                ('DuocLenLop', 'Được lên lớp'),
                ('OlaiLop', 'Ở lại lớp'),
                ('ChuyenDen', 'Chuyển đến'),
        ],default='value1',
    )
    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
        ],default = 'i')
    # namhoc = fields.Char('Năm học')
    #---------- define fields namhoc ------------
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc

    @api.model
    def _get_namhoc_now(self):
        now = datetime.datetime.now()
        year = now.year
        if now.month <= 9:
            year -= 1
        return str(year) + "-" + str(year+1)

    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_namhoc_now,
    )
    #---------- end define fields namhoc ------------

    thoidiemnhaptruong = fields.Date('Thời điểm nhập trường')
    hocsinh = fields.One2many('solienlac.hocsinh', 'nguongochocsinh', string='Học sinh')
    ghichu = fields.Char('Ghi chú')
class monhocnghe(models.Model):
    _name = 'solienlac.monhocnghe'
    _rec_name = 'tenmonhocnghe'
    mamonhocnghe = fields.Char("Mã môn học ", required=True)
    tenmonhocnghe = fields.Selection(
        string="Môn học nghề",
        selection=[
                ('value1', 'Không học nghề'),
                ('value2', 'Tin học ứng dụng'),
                ('value3', 'Mộc'),
                ('value4', 'May'),
                ('value5', 'Nấu ăn'),
                ('value6', 'Nhiếp ảnh'),
                ('value7', 'Điện dân dụng'),
                ('value8', 'Điện tử'),
                ('value9', 'Thêu'),
                ('value10', 'Nề'),
                ('value11', 'Đan len'),
                ('value12', 'Đan lưới'),
                ('value13', 'Lâm sinh'),
        ],default='value1'
    )
    ghichu = fields.Char('Ghi chú')
class tochucdoanthe(models.Model):
    _name = 'solienlac.tochucdoanthe'
    _rec_name = 'vitridoanthe'
    vitridoanthe = fields.Selection(
        string="Vị trí đoàn thể",
        selection=[
                ('value1', 'Không'),
                ('value2', 'Đội viên'),
                ('value3', 'Đoàn viên'),
                ('value4', 'Đảng viên'),
                ('value5', 'Không xác định'),
        ],default='value1'
    )
    chucvudoanthe = fields.Selection(
        string="Field name",
        selection=[
                ('value1', 'Không'),
                ('value2', 'Liên đội trưởng'),
                ('value3', 'Liên đội phó'),
                ('value4', 'Bí thư đoàn trường'),
                ('value5', 'Phó Bí thư đoàn trường'),
                ('value6', 'Bí thư chi đoàn'),
                ('value7', 'Phó Bí thư chi đoàn'),
                ('value8', 'Chi đội trưởng'),
                ('value9', 'Chi đội phó'),
        ],
    )
    ngaygianhap = fields.Date('Ngày gia nhập')
    ghichu = fields.Char('Ghi chú')

class lop(models.Model):
    _name = 'solienlac.lop'
    # _inherit = 'solienlac.hocsinh'
    _rec_name = 'tenlop' # optional
    malop = fields.Char('Mã lớp', required=True)
    tenlop = fields.Char('Tên lớp', required=True)
    nienkhoa = fields.Char('Niên khóa')
    ghichu = fields.Char('Ghi chú')
    khoi = fields.Many2one('solienlac.khoi', string='Khối')
    gvcn = fields.Many2one(
        string="Giáo viên chủ nhiệm",
        comodel_name="solienlac.giaovien",
    )
    # truong = fields.Many2one('solienlac.truong', string = "Trường")
    hocsinh = fields.One2many('solienlac.hocsinh', 'lop', string='Học sinh')
    monhoc = fields.One2many('solienlac.monhoc_has_giaovien', 'lop', string='Môn học')
    giaovien = fields.One2many('solienlac.lop_has_giaovien', 'lop', string='Giáo viên')

    siso = fields.Integer(string='Sĩ số')
    lopdacbiet = fields.Selection(
        string="Lớp đặc biệt",
        selection=[
                ('khong', 'Không'),
                ('nhomghep', 'Nhóm ghép'),
                ('nhombantru', 'Nhóm bán trú'),
                ('nhom1buoi', 'Nhóm 1 buổi/ngày'),
                ('nhom2buoi', 'Nhóm 2 buổi/ngày'),
                ('nhomhoanhapchotrekhuyettat', 'Nhóm hòa nhập cho trẻ khuyết tật'),
                ('lopghep', 'Lớp ghép'),
                ('lopbantru', 'Lớp bán trú'),
                ('lop1buoi', 'Lớp 1 buổi/ngày'),
                ('lop2buoi', 'Lớp 2 buổi/ngày'),
                ('lophoanhap', 'Lớp hòa nhập '),
                ('lopchotrekhuyettat', 'Lớp cho trẻ Khuyết tật'),
                ('lopdantocnoitru', 'Lớp dân tộc nội trú'),
                ('lophocnghephothong', 'Lớp học nghề phổ thông'),
                ('lopnoitru', 'Lớp nội trú'),
                ('loptinhthuong', 'Lớp tình thương'),
                ('lopsauxoamuchu', 'Lớp sau xoá mù chữ'),
        ], default = 'khong'
    )
    lopnho = fields.Selection(
        string="Lớp nhô",
        selection=[
                ('khong', 'Không'),
                ('nhotren', 'Nhô trên'),
                ('nhoduoi', 'Nhô duoi'),
                ('nhotrenduoi', 'Nhô trên và dưới'),
        ],default='khong'
    )
    hengoaingu = fields.Selection(
        string="Hệ ngoại ngữ",
        selection=[
                ('1', 'Tiếng Anh'),
                ('2', 'Tiếng Pháp'),
                ('3', 'Tiếng Trung'),
                ('4', 'Tiếng Nga'),
                ('5', 'Tiếng Nhật'),
                ('6', 'Tiếng Đức'),
                ('7', 'Tiếng Hàn'),
                ('8', 'Tiếng khác'),
                ('9', 'Không học'),
        ],
    )
    banhoc = fields.Many2one('solienlac.banhoc', string='Phân ban', required=True)

    @api.constrains('malop')
    def _lop_uinq(self):
        lst = self.env['solienlac.lop'].search([])
        lst = map(lambda x: x.malop, lst)
        lst.remove(self.malop)
        if self.malop in lst:
            raise exceptions.ValidationError('Mã lớp đã tồn tại.')
        else:
            pass

class banhoc(models.Model):
    _name = 'solienlac.banhoc'
    _rec_name = 'tenban' # optional
    maban = fields.Char('Mã ban', required=True)
    tenban = fields.Selection([
        ('coban', 'Ban cơ bản'),
        ('tunhien', 'Ban tự nhiên'),
        ('xahoi', 'Ban xã hội'),
        ('coban_kpb', 'Không phân ban'),
        ('coban_a', 'Ban cơ bản A'),
        ('coban_b', 'Ban cơ bản B'),
        ('coban_c', 'Ban cơ bản C'),
        ('coban_d', 'Ban cơ bản D'),
        ('coban_e', 'Ban cơ bản nâng cao 1-2 môn'),
        ('coban_f', 'Ban cơ bản không nâng cao'),
        ('coban_g', 'Ban cơ bản văn địa'),
    ], default = 'coban_kpb' ,string='Phân ban', required=True)
    lop = fields.One2many('solienlac.lop', 'banhoc', string='Lớp')
    ghichu = fields.Char('Ghi chú')

class monhoc(models.Model):
    _name = 'solienlac.monhoc'
    _rec_name = 'tenmonhoc' # optional

    mamonhoc = fields.Integer('Mã môn học', required=True)
    tenmonhoc = fields.Char('Tên môn học', required=True)
    heso = fields.Float('Hệ số')
    ghichu = fields.Char('Ghi chú')
    bomon = fields.Many2one('solienlac.bomon', string='Bộ môn')
    banhoc = fields.Many2many('solienlac.banhoc', string='Ban hoc')
    giaovien = fields.One2many('solienlac.monhoc_has_giaovien', 'monhoc', string='Giáo viên')

class ketquahoctap(models.Model):
    _name = 'solienlac.ketquahoctap'
    _rec_name = 'monhoc' # optional
    hocsinh = fields.Many2one('solienlac.hocsinh', string='Học sinh', required=True)
    monhoc = fields.Many2one('solienlac.monhoc', string='Môn học', required=True)
    giaovien = fields.Many2one('solienlac.giaovien', string='Giáo viên')
    diemtongket = fields.Float('Điểm tổng kết')
    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],default = 'i')
    # namhoc = fields.Char('Năm học')

    #---------- define fields namhoc ------------
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc

    @api.model
    def _get_namhoc_now(self):
        now = datetime.datetime.now()
        year = now.year
        if now.month <= 9:
            year -= 1
        return str(year) + "-" + str(year+1)

    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_namhoc_now,
    )
    #---------- end define fields namhoc ------------

    ngaycapnhat = fields.Date('Ngày cập nhật')
    ykiengiaovien = fields.Char('Ý kiến giáo viên')

class loaidiem(models.Model):
    _name = 'solienlac.loaidiem'
    _rec_name = 'tenloai' # optional
    maloai = fields.Char('Mã loai', required=True)
    tenloai = fields.Char('Tên loai', required=True)
    heso = fields.Float('Hệ số')
    ghichu = fields.Char('Ghi chú')

class diem(models.Model):
    _name = 'solienlac.diem'
    _rec_name = 'diem' # optional
    diem = fields.Float('Điểm')
    ngaynhap = fields.Date('Ngày nhập')
    ghichu = fields.Char('Ghi chú')
    ketquahoctap = fields.Many2one('solienlac.ketquahoctap', string='Kết quả học tập')
    loaidiem = fields.Many2one('solienlac.loaidiem', string='Loại điểm')
    giaovien = fields.Many2one('solienlac.giaovien', string='Giáo viên')

class chucvu(models.Model):
    _name = 'solienlac.chucvu'
    _rec_name = 'ghichu' # optional
    machucvu = fields.Integer('Mã chức vụ', required=True)
    tenchucvu = fields.Selection([
                ('value1', 'Không'),
                ('value2', 'Liên đội trưởng'),
                ('value3', 'Liên đội phó'),
                ('value4', 'Bí thư đoàn trường'),
                ('value5', 'Phó Bí thư đoàn trường'),
                ('value6', 'Bí thư chi đoàn'),
                ('value7', 'Phó Bí thư chi đoàn'),
                ('value8', 'Chi đội trưởng'),
                ('value9', 'Chi đội phó'),
                ('value10', 'Lớp trưởng'),
                ('value11', 'Lớp phó'),
        ],string="Tên chức vụ", required=True)
    ghichu = fields.Char('Chức vụ')

    @api.constrains('machucvu')
    def _validate_machucvu(self):
        lst_macv = self.env['solienlac.chucvu'].search([])
        lst_macv = map(lambda cv : cv.machucvu, lst_macv)
        lst_macv.remove(self.machucvu)
        if self.machucvu in lst_macv:
            raise exceptions.ValidationError("Mã chức vụ đã tồn tại")
        else:
            pass

    @api.onchange('tenchucvu')
    def _get_tencv(self):
        def f(x):
            return {
                'value1': 'Không',
                'value2': 'Liên đội trưởng',
                'value3': 'Liên đội phó',
                'value4': 'Bí thư đoàn trường',
                'value5': 'Phó Bí thư đoàn trường',
                'value6': 'Bí thư chi đoàn',
                'value7': 'Phó Bí thư chi đoàn',
                'value8': 'Chi đội trưởng',
                'value9': 'Chi đội phó',
                'value10': 'Lớp trưởng',
                'value11': 'Lớp phó',
            }[x]
        try:
            self.ghichu = f(self.tenchucvu)
        except:
            self.ghichu = 'Không'

class nenep(models.Model):

    _name = 'solienlac.nenep'
    _rec_name = 'namhoc'

    @api.model
    def _get_current_hocky(self):
        try:
            hocky = self.env['solienlac.hocky'].search([
                ('trangthai' , '=', 'HienTai'),
                ('truong.id', '=', self.env.user.truong.id)
            ])[-1]
            return hocky.hocky
        except:
            now = datetime.datetime.now()
            month = now.month
            if month in [1,2,3,4,5,6,7]:
                return 'ii'
            else:
                return 'i'
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc
    @api.model
    def _get_current_namhoc(self):
        try:
            namhoc = self.env['solienlac.hocky'].search([
                ('trangthai' , '=', 'HienTai'),
                ('truong.id', '=', self.env.user.truong.id)
            ])[-1]
            return namhoc.namhoc
        except:
            now = datetime.datetime.now()
            year = now.year
            if now.month <= 9:
                year -= 1
            return str(year) + "-" + str(year+1)

    namhoc = fields.Selection( string="Năm học",
        selection= _get_list_namhoc, default = _get_current_namhoc, readonly=True, required=True )
    hocky = fields.Selection(selection=[
        ('i', 'Học kỳ I'), ('ii', 'Học kỳ II'), ('iii', 'Cả năm'), ],
        default = _get_current_hocky, readonly=True, string="Học kỳ", required=True)
    hocsinh = fields.Many2one('solienlac.hocsinh', string='Học sinh',
        domain=['id','=',-1], required=True)
    lop = fields.Many2one(string="Lớp", comodel_name="solienlac.lop",
        domain=['id','=',-1], required=True)
    khoi = fields.Many2one(string="Khối", comodel_name="solienlac.khoi", required=True)
    truong = fields.Many2one(string="Trường", comodel_name="solienlac.truong",
        default=lambda self: self.env.user.truong.id, required=True)
    dongphuc = fields.Integer('Đồng phục')
    dihocmuon = fields.Integer('Đi học muộn')
    noichuyen = fields.Integer('Nói chuyện')
    noituc = fields.Integer('Nói tục')
    truybai = fields.Integer('Truy bài')
    ntvt = fields.Integer('NTVT')

    @api.onchange('khoi')
    def _lop_baseon_khoi(self):
        lops = self.env['solienlac.lop'].search([('khoi.id','=',self.khoi.id)])
        lops = [lop.id for lop in lops]
        return {'domain':{'lop': [('id', 'in', lops)]}}
    @api.onchange('lop')
    def _hs_baseon_lop(self):
        hss = self.env['solienlac.hocsinh'].search([('lop.id','=',self.lop.id)])
        hss = [hs.id for hs in hss]
        return {'domain':{'hocsinh': [('id', 'in', hss)]}}

class diemthanhphan(models.Model):
    _name = 'solienlac.diemthanhphan'
    bangdiem_thanhphan = fields.Many2one('solienlac.bangdiem_thanhphan', string='Kết quả thành phần')
    diem = fields.Float(string="Điểm sô")
    heso = fields.Float(string="Hệ số")
    ngaycapnhat = fields.Datetime(string="Ngày cập nhật")
    loaidiem = fields.Selection(
        string="Loại điểm",
        selection=[
                ('mieng', 'Điểm kiểm tra miệng'),
                ('15p', 'Điểm kiểm tra HS1'),
                ('1t', 'Điểm kiểm tra HS2'),
                ('hk', 'Điểm kiểm tra Học kỳ'),
                ('tn', 'Điểm kiểm tra khác'),
        ],
    )

class bangdiem_thanhphan(models.Model):
    _name = 'solienlac.bangdiem_thanhphan'
    monhoc = fields.Many2one('solienlac.monhoc', string='Môn học', required=True)
    bangdiem = fields.Many2one('solienlac.bangdiem', string='Kết quả học tập', required=True)
    diemthanhphan = fields.One2many("solienlac.diemthanhphan", "bangdiem_thanhphan", string="Điểm thành phần")
    diemtongket = fields.Float(string="Điểm tổng kết môn")
    ghichu = fields.Char(string="Ghi chú")
    giaovien = fields.Many2one('solienlac.giaovien', string='Giáo viên bộ môn', required=True)
    ykiengiaovien = fields.Char('Ý kiến giáo viên bộ môn')
    ngaycapnhat = fields.Datetime(string="Ngày cập nhật")

class bangdiem(models.Model):
    _name = 'solienlac.bangdiem'
    kyhoc = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],
        default = 'i'
    )
    # namhoc = fields.Char('Năm học')
    #---------- define fields namhoc ------------
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc

    @api.model
    def _get_namhoc_now(self):
        now = datetime.datetime.now()
        year = now.year
        if now.month <= 9:
            year -= 1
        return str(year) + "-" + str(year+1)

    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_namhoc_now,
    )
    #---------- end define fields namhoc ------------

    kythi = fields.Selection(
        string="Kỳ thi",
        selection=[
                ('1', 'Học kỳ'),
                ('2', 'Thi Tốt nghiệp'),
                ('3', 'Thi HSG'),
                ('4', 'Thi nghề phổ thông'),
                ('99', 'Thi khác'),
        ],
    )
    bangdiem_thanhphan = fields.One2many("solienlac.bangdiem_thanhphan", "bangdiem", string="Bảng điểm thành phần")
    diemtongket = fields.Float('Điểm tổng kết')
    xeploai = fields.Selection([
        ('tot', 'Tốt'),
        ('kha', 'Khá'),
        ('tb', 'Trung bình'),
        ('yeu', 'Yếu'),
        # ('kem', 'Kém'),
    ],string='Xếp loại học lực')
    giaovien = fields.Many2one('solienlac.giaovien', string='Giáo viên chủ nhiệm')
    ykiengiaovien = fields.Char('Ý kiến giáo viên chủ nhiệm')
    hocsinh = fields.Many2one('solienlac.hocsinh', string='Học sinh')
    ghichu = fields.Char(string="Ghi chú", )
    ngaycapnhat = fields.Date('Ngày cập nhật')

class danhhieuhocsinh(models.Model):
    _name = 'solienlac.danhhieuhocsinh'
    _rec_name = 'hocky' # optional
    # _description = 'Danh hiệu của học sinh tính theo kỳ'
    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],default = 'i')
    # namhoc = fields.Char(string="Năm học", )

    #---------- define fields namhoc ------------
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc

    @api.model
    def _get_namhoc_now(self):
        now = datetime.datetime.now()
        year = now.year
        if now.month <= 9:
            year -= 1
        return str(year) + "-" + str(year+1)

    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_namhoc_now,
    )
    #---------- end define fields namhoc ------------

    danhhieu = fields.Selection(
        string="Danh hiệu",
        selection=[
                ('kc', 'Chưa đạt danh hiệu gì'),
                ('hsxs', 'Học sinh xuất sắc'),
                ('hsg', 'Học sinh giỏi'),
                ('hstt', 'Học sinh tiên tiến'),
        ],
    )
    ykiengiaovien = fields.Char('Ý kiến giáo viên')
    ghichu = fields.Char('Ghi chú')
    hocsinh = fields.Many2one('solienlac.hocsinh', string='Học sinh')

    @api.constrains('hocky','namhoc','hocsinh')
    def _validate_1_ky_1_danhhieu(self):
        n = self.env['solienlac.danhhieuhocsinh'].search_count([
            ('hocky','=',self.hocky),
            ('namhoc','=',self.namhoc),
            ('hocsinh.id','=',self.hocsinh.id),
        ])
        # lst_macv = map(lambda cv : cv.machucvu, lst_macv)
        # print '(%s,%s,%s,%s)' % (self.hocky,self.namhoc,self.hocsinh.id,n)
        if n>1:
            raise exceptions.ValidationError("Học sinh không thể nhận 2 danh hiệu trong kỳ này")
        else:
            pass

class nhapdiemhocsinh(models.Model):
    _name = 'solienlac.nhapdiemhocsinh'
    _rec_name = 'giaovien' # optional

    test1 = fields.Char()
    napdulieu = fields.Boolean('Tải danh sách học sinh')
    @api.model
    def _get_current_gv(self):
        dmain = [('id', '=', self.env.user.giaovien.id)]
        return dmain

    @api.model
    def _read_ol(self):
        return True

    giaovien = fields.Many2one(
        string="Giáo viên",
        comodel_name="solienlac.giaovien",
        default = lambda self: self.env.user.giaovien,
        readonly = _read_ol,
    )
    lop = fields.Many2one(
        string="Lớp",
        comodel_name="solienlac.lop",
        domain="[('id','=',0)]",
    )
    @api.model
    def _get_current_hocky(self):
        try:
            hocky = self.env['solienlac.hocky'].search([
                ('trangthai' , '=', 'HienTai'),
                ('truong.id', '=', self.env.user.truong.id)
            ])[-1]
            return hocky.hocky
        except:
            now = datetime.datetime.now()
            month = now.month
            if month in [1,2,3,4,5,6,7]:
                return 'ii'
            else:
                return 'i'

    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II')
        ],default = _get_current_hocky, readonly=True)

    #---------- define fields namhoc ------------
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc

    @api.model
    def _get_current_namhoc(self):
        try:
            namhoc = self.env['solienlac.hocky'].search([
                ('trangthai' , '=', 'HienTai'),
                ('truong.id', '=', self.env.user.truong.id)
            ])[-1]
            return namhoc.namhoc
        except:
            now = datetime.datetime.now()
            year = now.year
            if now.month <= 9:
                year -= 1
            return str(year) + "-" + str(year+1)

    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_current_namhoc,
        readonly = True)

    #---------- end define fields namhoc ------------
    @api.model
    def _get_current_list_monhoc(self):
        lst = [x.monhoc.id for x in self.env.user.giaovien.monhoc]
        lst = list(set(lst))
        # print 'Danh sach mon dang day'
        # print lst
        return [('id', 'in', lst)]

    monhoc = fields.Many2one(
        string="Môn học",
        comodel_name="solienlac.monhoc",
        domain = _get_current_list_monhoc,)

    nhapdiemchitiet = fields.Many2many(
        comodel_name='solienlac.nhapdiemchitiet',
        string='Chi tiết',
        store=True,)

    @api.multi
    @api.onchange('monhoc')
    def _get_lop(self):
        self.lop = []
        current_monhoc_id = self.monhoc.id
        lst_phanban = self.env['solienlac.monhoc_has_giaovien'].search([
            ('monhoc.id','=',current_monhoc_id),
            ('hocky','=',self.hocky),
            ('namhoc','=',self.namhoc),
            ('giaovien.id','=',self.env.user.giaovien.id)
        ])
        lst_lop = map(lambda x: x.lop.id, lst_phanban)
        # print 'id lop cua giao vien dang giang day mon nay:'
        # print lst_lop
        return {'domain':{'lop': [('id', 'in', lst_lop)]}}
    print ('-----------------------------------')
    @api.constrains('monhoc', 'hocky', 'namhoc')
    def _nhapdiemhocsinh_uniq(self):
        print ('-----------------------------------')
        mycount = self.env['solienlac.nhapdiemhocsinh'].search_count([
            ('hocky','=',self.hocky), # notice, how about a year
            ('namhoc','=',self.namhoc),
            ('monhoc.id','=',self.monhoc.id),
            ('lop.id','=',self.lop.id),
            ('giaovien.id','=',self.giaovien.id),
        ])
        print mycount
        if mycount > 1:
            raise exceptions.ValidationError("Dữ liệu đã tồn tại.")
    @api.multi
    # @api.onchange('lop','namhoc','hocky','napdulieu')
    def compute_model(self):
        self.test1 = str(self.env.uid) + str(random.randint(0,10))
        # Get hocsinh object
        def get_hs(self, id):
            return self.env['solienlac.hocsinh'].search([('id','=',id)])[0]

        # Load data
        self.napdulieu = False

        # Get (hocsinh object list)
        lst_hs = self.env['solienlac.hocsinh'].search([
            ('tinhtranghocsinh', '=', 'value1'), #value1 = học bình thường
            ('lop.id', '=', self.lop.id),
        ])

        # Get (nhapdiemchitiet object list)
        lst_hs_nhapdiem = self.env['solienlac.nhapdiemchitiet'].search([
            ('hocsinh.lop.id','=',self.lop.id),
            ('hocsinh.tinhtranghocsinh', '=', 'value1'), # value1 = học bình thường
            ('hocky','=',self.hocky), # notice, how about a year
            ('namhoc','=',self.namhoc),
            ('monhoc.id','=',self.monhoc.id),
        ])

        # Get (hocsinh object list) just hocsinh id
        lst_hs_id = map(lambda x: x.id, lst_hs)

        # Get (nhapdiemchitiet object list) just hocsinh id
        lst_hs_nhapdiem_id = map(lambda x: x.hocsinh.id, lst_hs_nhapdiem)

        # Get hocsinh id is not exsit in nhapdiemchitiet
        lst_hs_thieu = filter(lambda x: x not in lst_hs_nhapdiem_id, lst_hs_id)

        if len(lst_hs_thieu) == 0:
            # In case the teacher wanna edit the score
            # hocsinh(s) are created before (at the else case)
            self.nhapdiemchitiet = lst_hs_nhapdiem
        else:
            # Adding hocsinh at lst_hs_thieu into nhapdiemchitiet and show it
            self.nhapdiemchitiet = [] # important
            flag = True

            # Create list for checking null value
            lst_chk = [self.hocky, self.namhoc, self.monhoc, self.lop, self.giaovien] # notice: how about self.giaovien

            # Check for all fields are inputed
            for item in lst_chk:
                if str(item) == '':
                    flag = False
                elif str(item) == 'False':
                    flag = False
                elif item == False:
                    flag = False

            if flag:
                # Create objects nhapdiemchitiet
                for id in lst_hs_thieu:
                    vals = {
                        'hocsinh'     : id,
                        'giaovien'    : self.giaovien.id,
                        'hocky'       : self.hocky,
                        'namhoc'      : self.namhoc,
                        'monhoc'      : self.monhoc.id,
                        'lop'         : self.lop.id,
                        'khoi'        : self.lop.khoi.id,
                        'truong'      : self.lop.khoi.truong.id,
                    }
                    self.env['solienlac.nhapdiemchitiet'].sudo().create(vals)

                # Reload lst_hs_nhapdiem
                lst_hs_nhapdiem = self.env['solienlac.nhapdiemchitiet'].search([
                    ('hocsinh.lop.id','=',self.lop.id),
                    ('hocsinh.tinhtranghocsinh', '=', 'value1'), # value1 = học bình thường
                    ('hocky','=',self.hocky), # notice, how about a year
                    ('namhoc','=',self.namhoc),
                    ('monhoc.id','=',self.monhoc.id),
                ])
                # Show objects nhapdiemchitiet has just created
                self.nhapdiemchitiet = lst_hs_nhapdiem


class nhapdiemchitiet(models.Model):
    _name = 'solienlac.nhapdiemchitiet'

    lop = fields.Many2one(
        string="Lớp",
        comodel_name="solienlac.lop",
    )
    khoi = fields.Many2one(
        string="Khối",
        comodel_name="solienlac.khoi",
    )
    truong = fields.Many2one(
        string="Trường",
        comodel_name="solienlac.truong",
    )

    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc
    @api.model
    def _get_namhoc_now(self):
        now = datetime.datetime.now()
        year = now.year
        if now.month <= 9:
            year -= 1
        return str(year) + "-" + str(year+1)

    giaovien = fields.Many2one(
        string="Giáo viên",
        comodel_name="solienlac.giaovien",
    )

    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],default = 'i')
    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_namhoc_now,
    )
    monhoc = fields.Many2one(
        string="Môn học",
        comodel_name="solienlac.monhoc",
    )
    hocsinh = fields.Many2one('solienlac.hocsinh', string='Học sinh')
    diemmieng1 = fields.Char('Điểm miệng', readonly=True)
    diemmieng2 = fields.Char('1')
    diemmieng3 = fields.Char('2')
    diemmieng4 = fields.Char('3')
    diemmieng5 = fields.Char('4')
    diemmieng6 = fields.Char('5')
    diem15phut1 = fields.Char('Điểm hệ số 1', readonly=True)
    diem15phut2 = fields.Char('1')
    diem15phut3 = fields.Char('2')
    diem15phut4 = fields.Char('3')
    diem15phut5 = fields.Char('4')
    diem15phut6 = fields.Char('5')
    diem1tiet1 = fields.Char('Điểm hệ số 2', readonly=True)
    diem1tiet2 = fields.Char('1')
    diem1tiet3 = fields.Char('2')
    diem1tiet4 = fields.Char('3')
    diem1tiet5 = fields.Char('4')
    diem1tiet6 = fields.Char('5')
    diemhocky = fields.Char('Điểm học kỳ')
    diemtongket = fields.Float(string='Tổng kểt', store=True, compute='_compute_final')
    xephang = fields.Integer('#')

    @api.onchange('diemhocky',)
    @api.multi
    def _check_diem1(self):
        tmp = _validate_diem(self.diemhocky)
        if not tmp:
            self.diemhocky = ''
        else:
            pass
    @api.onchange('diemmieng2',)
    def _check_diem2(self):
        tmp = _validate_diem(self.diemmieng2)
        if not tmp:
            self.diemmieng2 = ''
        else:
            pass
    @api.onchange('diemmieng3',)
    def _check_diem3(self):
        tmp = _validate_diem(self.diemmieng3)
        if not tmp:
            self.diemmieng3 = ''
        else:
            pass
    @api.onchange('diemmieng4',)
    def _check_diem4(self):
        tmp = _validate_diem(self.diemmieng4)
        if not tmp:
            self.diemmieng4 = ''
        else:
            pass
    @api.onchange('diemmieng5',)
    def _check_diem5(self):
        tmp = _validate_diem(self.diemmieng5)
        if not tmp:
            self.diemmieng5 = ''
        else:
            pass
    @api.onchange('diemmieng6',)
    def _check_diem6(self):
        tmp = _validate_diem(self.diemmieng6)
        if not tmp:
            self.diemmieng6 = ''
        else:
            pass
    @api.onchange('diem15phut2',)
    def _check_diem7(self):
        tmp = _validate_diem(self.diem15phut2)
        if not tmp:
            self.diem15phut2 = ''
        else:
            pass
    @api.onchange('diem15phut3',)
    def _check_diem8(self):
        tmp = _validate_diem(self.diem15phut3)
        if not tmp:
            self.diem15phut3 = ''
        else:
            pass
    @api.onchange('diem15phut4',)
    def _check_diem9(self):
        tmp = _validate_diem(self.diem15phut4)
        if not tmp:
            self.diem15phut4 = ''
        else:
            pass
    @api.onchange('diem15phut5',)
    def _check_diem10(self):
        tmp = _validate_diem(self.diem15phut5)
        if not tmp:
            self.diem15phut5 = ''
        else:
            pass
    @api.onchange('diem15phut6',)
    def _check_diem11(self):
        tmp = _validate_diem(self.diem15phut6)
        if not tmp:
            self.diem15phut6 = ''
        else:
            pass
    @api.onchange('diem1tiet2',)
    def _check_diem12(self):
        tmp = _validate_diem(self.diem1tiet2)
        if not tmp:
            self.diem1tiet2 = ''
        else:
            pass
    @api.onchange('diem1tiet3',)
    def _check_diem13(self):
        tmp = _validate_diem(self.diem1tiet3)
        if not tmp:
            self.diem1tiet3 = ''
        else:
            pass
    @api.onchange('diem1tiet4',)
    def _check_diem14(self):
        tmp = _validate_diem(self.diem1tiet4)
        if not tmp:
            self.diem1tiet4 = ''
        else:
            pass
    @api.onchange('diem1tiet5',)
    def _check_diem15(self):
        tmp = _validate_diem(self.diem1tiet5)
        if not tmp:
            self.diem1tiet5 = ''
        else:
            pass
    @api.onchange('diem1tiet6',)
    def _check_diem16(self):
        tmp = _validate_diem(self.diem1tiet6)
        if not tmp:
            self.diem1tiet6 = ''
        else:
            pass

    @api.depends(
    'diemhocky',
    'diemmieng1','diemmieng2','diemmieng3','diemmieng4','diemmieng5','diemmieng6',
    'diem15phut1','diem15phut2','diem15phut3','diem15phut4','diem15phut5','diem15phut6',
    'diem1tiet1','diem1tiet2','diem1tiet3','diem1tiet4','diem1tiet5','diem1tiet6'
    )
    def _compute_final(self):
        def convert_to_float(n):
            try:
                n = str(n)
                n = n.replace(',','.')
                num = float(n)
                if num <0.0:
                    num = 0.0
                if num > 10.0:
                    num = 10.0
                return num
            except ValueError:
                return -1.0

        for record in self:
            lst_diem_mieng = [
                record.diemmieng1, record.diemmieng2, record.diemmieng6,
                record.diemmieng3, record.diemmieng4, record.diemmieng5
            ]
            lst_diem_15 = [
                record.diem15phut1, record.diem15phut2, record.diem15phut6,
                record.diem15phut3, record.diem15phut4, record.diem15phut5
            ]
            lst_diem_1t = [
                record.diem1tiet1, record.diem1tiet2, record.diem1tiet6,
                record.diem1tiet3, record.diem1tiet4, record.diem1tiet5
            ]

            lst_diem_mieng = [convert_to_float(x) for x in lst_diem_mieng]
            lst_diem_mieng = filter(lambda x: x != -1.0, lst_diem_mieng)
            lst_diem_15 = [convert_to_float(x) for x in lst_diem_15]
            lst_diem_15 = filter(lambda x: x != -1.0, lst_diem_15)
            lst_diem_1t = [convert_to_float(x) for x in lst_diem_1t]
            lst_diem_1t = filter(lambda x: x != -1.0, lst_diem_1t)
            diemhk = convert_to_float(record.diemhocky) if convert_to_float(record.diemhocky) != -1.0 else 0

            he_so = len(lst_diem_mieng) + len(lst_diem_15) + 2*len(lst_diem_1t) + 3
            tong  = sum(lst_diem_mieng) + sum(lst_diem_15) + 2*sum(lst_diem_1t) + 3*convert_to_float(record.diemhocky)
            diemtk = str(float(tong)/float(he_so))[0:4]

            record.diemtongket = float(diemtk)

    @api.multi
    def write(self, vals):
        # kiem tra co phai hoc ky hien tai khong moi cho sua diem
        # print '----------------------------------------'
        # try:
            hocky = self.env['solienlac.hocky'].search([
                ('trangthai' , '=', 'HienTai'),
                ('truong.id', '=', self.env.user.truong.id)
            ])[-1]
            hk_hientai = hocky.hocky
            nh_hientai = hocky.namhoc

            print hk_hientai,nh_hientai

            if (self.hocky == hk_hientai) and (self.namhoc == nh_hientai):
                print 'True-------------------------------'
                obj = super(nhapdiemchitiet, self).write(vals)
                return obj
            else:
                print 'False--------------------------------'
                raise exceptions.ValidationError("Error1: Không thể sửa điểm học kỳ mà hiệu trưởng không cho phép!")
                return
        # except:
        #     raise exceptions.ValidationError("Error2: Không thể sửa điểm khi mà hiệu trưởng trường này chưa chưa cho phép sửa điểm trong kỳ!")
    # lop = fields.Many2one(
    #     string="Lớp",
    #     comodel_name="solienlac.lop",
    #     compute = '_get_lop_ato',
    #     store=True,
    # )
    # @api.depends('hocsinh')
    # def _get_lop_ato(self):
    #     for r in self:
    #         r.lop = hocsinh.lop

    # khoi = fields.Many2one(
    #     string="Khối",
    #     comodel_name="solienlac.khoi",
    #     compute = '_get_khoi_ato',
    #     store=True,
    # )
    # @api.depends('hocsinh')
    # def _get_khoi_ato(self):
    #     for r in self:
    #         r.khoi = hocsinh.lop.khoi
    #
    # truong = fields.Many2one(
    #     string="Trường",
    #     comodel_name="solienlac.truong",
    #     compute = '_get_truong_ato',
    #     store=True,
    # )
    # @api.depends('hocsinh')
    # def _get_truong_ato(self):
    #     for r in self:
    #         r.truong = hocsinh.lop.khoi.truong


class Users(models.Model):
    _name = 'solienlac.taikhoan'
    _rec_name = 'login'

    @api.model
    def _get_test(self):
        #get list domain
        idc = self.env['ir.module.category'].sudo().search([('name','like','solienlac')])[0].id
        solienlac_groups = self.env['res.groups'].sudo().search([('category_id','=',idc)])
        solienlac_groups_name = map(lambda x: x.name, solienlac_groups)
        solienlac_groups_id = map(lambda x: x.id, solienlac_groups)

        user_groups_id = self.env.user.groups_id
        user_groups_id = map(lambda x: x.id, user_groups_id)

        system_admin_level_1_id = self.env['res.groups'].sudo().search([('name','like','SYA1:')])[0].id
        system_admin_level_2_id = self.env['res.groups'].sudo().search([('name','like','SYA2:')])[0].id
        system_admin_level_3_id = self.env['res.groups'].sudo().search([('name','like','SYA3:')])[0].id
        school_admin_level_1_hieu_truong_id = self.env['res.groups'].sudo().search([('name','like','SCA1:')])[0].id
        cus = self.env['res.groups'].sudo().search([('name','like','CUST:')])[0].id

        result = solienlac_groups_id

        # print 'system_admin_level_1_id'
        # print system_admin_level_1_id
        # print user_groups_id

        if (system_admin_level_1_id in user_groups_id):
            pass

        if (system_admin_level_2_id in user_groups_id):
            result.remove(system_admin_level_1_id)

        if (system_admin_level_3_id in user_groups_id):
            result.remove(system_admin_level_1_id)
            result.remove(system_admin_level_2_id)

        if (school_admin_level_1_hieu_truong_id in user_groups_id):
            result.remove(system_admin_level_1_id)
            result.remove(system_admin_level_2_id)
            result.remove(system_admin_level_3_id)
            result.remove(school_admin_level_1_hieu_truong_id)

        return [('id', 'in', result)]


    name = fields.Char(string="Họ tên người dùng", required = True)
    login = fields.Char(string='Tài khoản đăng nhập',required = True)
    password = fields.Char(string='Mật khẩu đăng nhập',required = True)
    quyen = fields.Many2many(
        string="Quyền",
        comodel_name="res.groups",
        # domain="[('id', 'not in', [1,2,3,4,5,6,7,8,9,10])]",
        domain= _get_test,
    )
    truong = fields.Many2one(
        string="Trường",
        comodel_name="solienlac.truong",
    )
    string = fields.Char(default=_get_test)
    giaovien = fields.Many2one(
        string="Giáo viên",
        comodel_name="solienlac.giaovien",
        # domain= [('truong.id', '=', lambda)],
    )
    @api.multi
    @api.onchange('truong')
    def _get_id_truong(self):
        return {'domain':{'giaovien': [('truong.id', '=', self.truong.id)]}}

    @api.model
    def create(self, values):
        system_admin_level_1_id = self.env['res.groups'].sudo().search([('name','like','SYA1:')])[0].id
        system_admin_level_2_id = self.env['res.groups'].sudo().search([('name','like','SYA2:')])[0].id
        system_admin_level_3_id = self.env['res.groups'].sudo().search([('name','like','SYA3:')])[0].id
        school_admin_level_1_hieu_truong_id = self.env['res.groups'].sudo().search([('name','like','SCA1:')])[0].id

        # user_groups_id = self.env.user.groups_id
        # user_groups_id = map(lambda x: x.id, user_groups_id)

        quyen_da_chon = values['quyen'][0][2]
        quyen_da_chon.append(1)
        if (system_admin_level_1_id in quyen_da_chon) or (system_admin_level_2_id in quyen_da_chon) or (system_admin_level_3_id in quyen_da_chon) or (school_admin_level_1_hieu_truong_id in quyen_da_chon):
            quyen_da_chon.append(3)
        vals = {
            'name': values['name'],
            'login': values['login'],
            'password' : values['password'],
            'company_ids': [1],
            'company_id': 1,
            'groups_id': quyen_da_chon,
            'truong' : values['truong'],
            'giaovien' : values['giaovien'],
        }
        self.env['res.users'].sudo().create(vals)
        user = super(Users, self).create(values)
        return user

#taikhoan test ke thua.
class taikhoannguoidung(models.Model):
    # _name = 'solienlac.taikhoannguoidung' # optional
    _inherit = 'res.users'
    truong = fields.Many2one(
        string="Trường học",
        comodel_name="solienlac.truong",
    )
    giaovien = fields.Many2one(
        string="Giáo viên",
        comodel_name="solienlac.giaovien",
        # domain= [('truong.id', '=', lambda)],
    )

################################################################################

class diemdanhhocsinh(models.Model):
    _name = 'solienlac.diemdanhhocsinh'
    _rec_name = 'giaovien' # optional



    test1 = fields.Char()
    ngayvang = fields.Date(string="Ngày", default = datetime.datetime.now())
    @api.onchange('ngayvang')
    def _validate_ngay(self):
        mindate = datetime.datetime(int(self.namhoc[0:4]), 8, 1, 0, 0, 0, 0)
        maxdate = datetime.datetime(int(self.namhoc[-4:]), 7, 31, 0, 0, 0, 0)
        current_date = datetime.datetime.strptime(self.ngayvang,'%Y-%m-%d')
        # print self.ngayvang
        if current_date < mindate:
            current_date = mindate
        elif current_date > maxdate:
            current_date = maxdate
        self.ngayvang = current_date

    napdulieu = fields.Boolean('Tải danh sách học sinh')
    @api.model
    def _get_current_gv(self):
        dmain = [('id', '=', self.env.user.giaovien.id)]
        return dmain
    giaovien = fields.Many2one(
        string="Giáo viên",
        comodel_name="solienlac.giaovien",
        default = lambda self: self.env.user.giaovien,
        readonly = True,
    )
    lop = fields.Many2one(
        string="Lớp",
        comodel_name="solienlac.lop",
        domain="[('id','=',0)]",
    )

    @api.model
    def _get_current_hocky(self):
        try:
            hocky = self.env['solienlac.hocky'].search([
                ('trangthai' , '=', 'HienTai'),
                ('truong.id', '=', self.env.user.truong.id)
            ])[-1]
            return hocky.hocky
        except:
            now = datetime.datetime.now()
            month = now.month
            if month in [1,2,3,4,5,6,7]:
                return 'ii'
            else:
                return 'i'

    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],default = _get_current_hocky, readonly=True)

    #---------- define fields namhoc ------------
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc

    @api.model
    def _get_current_namhoc(self):
        try:
            namhoc = self.env['solienlac.hocky'].search([
                ('trangthai' , '=', 'HienTai'),
                ('truong.id', '=', self.env.user.truong.id)
            ])[-1]
            return namhoc.namhoc
        except:
            now = datetime.datetime.now()
            year = now.year
            if now.month <= 9:
                year -= 1
            return str(year) + "-" + str(year+1)

    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_current_namhoc,
        readonly = True)

    #---------- end define fields namhoc ------------
    @api.model
    def _get_current_list_monhoc(self):
        lst = [x.monhoc.id for x in self.env.user.giaovien.monhoc]
        lst = list(set(lst))
        return [('id', 'in', lst)]
    @api.multi
    @api.onchange('giaovien')
    def _get_monhoc(self):
        lst = [x.monhoc.id for x in self.giaovien.monhoc]
        return {'domain':{'monhoc': [('id', 'in', lst)]}}

    monhoc = fields.Many2one(
        string="Môn học",
        comodel_name="solienlac.monhoc",
        # domain = _get_current_list_monhoc,
    )

    diemdanhchitiet = fields.Many2many(
        comodel_name='solienlac.diemdanhchitiet',
        string='Chi tiết',
        store=True,)

    @api.multi
    @api.onchange('monhoc')
    def _get_lop(self):
        self.lop = []
        current_monhoc_id = self.monhoc.id
        lst_phanban = self.env['solienlac.monhoc_has_giaovien'].search([
            ('monhoc.id','=',current_monhoc_id),
            ('hocky','=',self.hocky),
            ('namhoc','=',self.namhoc),
        ])
        lst_lop = map(lambda x: x.lop.id, lst_phanban)
        return {'domain':{'lop': [('id', 'in', lst_lop)]}}

    @api.multi
    @api.onchange('lop','namhoc','hocky','napdulieu','ngayvang')
    def compute_model(self):
        self.test1 = str(self.env.uid) + str(random.randint(0,10))
        # Get hocsinh object
        def get_hs(self, id):
            return self.env['solienlac.hocsinh'].search([('id','=',id)])[0]

        # Load data
        self.napdulieu = False

        # Get (hocsinh object list)
        lst_hs = self.env['solienlac.hocsinh'].search([
            ('tinhtranghocsinh', '=', 'value1'), #value1 = học bình thường
            ('lop.id', '=', self.lop.id),
        ])

        # Get (diemdanhchitiet object list)
        lst_hs_nhapdiem = self.env['solienlac.diemdanhchitiet'].search([
            ('hocsinh.lop.id','=',self.lop.id),
            ('hocsinh.tinhtranghocsinh', '=', 'value1'), # value1 = học bình thường
            ('hocky','=',self.hocky), # notice, how about a year
            ('namhoc','=',self.namhoc),
            ('monhoc.id','=',self.monhoc.id),
            ('ngayvang','=',self.ngayvang),
        ])

        # Get (hocsinh object list) just hocsinh id
        lst_hs_id = map(lambda x: x.id, lst_hs)

        # Get (diemdanhchitiet object list) just hocsinh id
        lst_hs_nhapdiem_id = map(lambda x: x.hocsinh.id, lst_hs_nhapdiem)

        # Get hocsinh id is not exsit in diemdanhchitiet
        lst_hs_thieu = filter(lambda x: x not in lst_hs_nhapdiem_id, lst_hs_id)

        if len(lst_hs_thieu) == 0:
            # In case the teacher wanna edit the score
            # hocsinh(s) are created before (at the else case)
            self.diemdanhchitiet = lst_hs_nhapdiem
        else:
            # Adding hocsinh at lst_hs_thieu into diemdanhchitiet and show it
            self.diemdanhchitiet = [] # important
            flag = True

            # Create list for checking null value

            lst_chk = [self.hocky, self.namhoc, self.monhoc, self.lop, self.giaovien, self.ngayvang] # notice: how about self.giaovien

            # Check for all fields are inputed
            for item in lst_chk:
                if str(item) == '':
                    flag = False
                elif str(item) == 'False':
                    flag = False
                elif item == False:
                    flag = False

            if flag:
                # Create objects diemdanhchitiet
                for id in lst_hs_thieu:
                    vals = {
                        'hocsinh'     : id,
                        'giaovien'    : self.giaovien.id,
                        'hocky'       : self.hocky,
                        'namhoc'      : self.namhoc,
                        'monhoc'      : self.monhoc.id,
                        'ngayvang'    : self.ngayvang,
                        'lop'         : self.lop.id,
                        'khoi'        : self.lop.khoi.id,
                        'truong'      : self.lop.khoi.truong.id,
                    }
                    self.env['solienlac.diemdanhchitiet'].sudo().create(vals)

                # Reload lst_hs_nhapdiem
                lst_hs_nhapdiem = self.env['solienlac.diemdanhchitiet'].search([
                    ('hocsinh.lop.id','=',self.lop.id),
                    ('hocsinh.tinhtranghocsinh', '=', 'value1'), # value1 = học bình thường
                    ('hocky','=',self.hocky), # notice, how about a year
                    ('namhoc','=',self.namhoc),
                    ('monhoc.id','=',self.monhoc.id),
                    ('ngayvang','=',self.ngayvang),
                ])
                # Show objects diemdanhchitiet has just created
                self.diemdanhchitiet = lst_hs_nhapdiem

class diemdanhchitiet(models.Model):
    _name = 'solienlac.diemdanhchitiet'
    _rec_name = 'hocsinh'

    lop = fields.Many2one(
        string="Lớp",
        comodel_name="solienlac.lop",
    )
    khoi = fields.Many2one(
        string="Khối",
        comodel_name="solienlac.khoi",
    )
    truong = fields.Many2one(
        string="Trường",
        comodel_name="solienlac.truong",
    )

    ngayvang = fields.Date(string="Ngày", )
    vang = fields.Boolean(string="Vắng", )
    ghichu = fields.Char(string="Ghi chú", )
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc
    @api.model
    def _get_namhoc_now(self):
        now = datetime.datetime.now()
        year = now.year
        if now.month <= 9:
            year -= 1
        return str(year) + "-" + str(year+1)

    giaovien = fields.Many2one(
        string="Giáo viên",
        comodel_name="solienlac.giaovien",
    )

    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],default = 'i')
    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_namhoc_now,
    )
    monhoc = fields.Many2one(
        string="Môn học",
        comodel_name="solienlac.monhoc",
    )
    hocsinh = fields.Many2one('solienlac.hocsinh', string='Học sinh')
    diemmieng1 = fields.Char('Điểm miệng', readonly=True)
    diemmieng2 = fields.Char('1')
    diemmieng3 = fields.Char('2')
    diemmieng4 = fields.Char('3')
    diemmieng5 = fields.Char('4')
    diemmieng6 = fields.Char('5')
    diem15phut1 = fields.Char('Điểm hệ số 1', readonly=True)
    diem15phut2 = fields.Char('1')
    diem15phut3 = fields.Char('2')
    diem15phut4 = fields.Char('3')
    diem15phut5 = fields.Char('4')
    diem15phut6 = fields.Char('5')
    diem1tiet1 = fields.Char('Điểm hệ số 2', readonly=True)
    diem1tiet2 = fields.Char('1')
    diem1tiet3 = fields.Char('2')
    diem1tiet4 = fields.Char('3')
    diem1tiet5 = fields.Char('4')
    diem1tiet6 = fields.Char('5')
    diemhocky = fields.Char('Điểm học kỳ')
    diemtongket = fields.Char(string='Tổng kểt', store=True, compute='_compute_final')
    xephang = fields.Integer('#')

    @api.onchange('diemmieng1','diem15phut1','diem1tiet1')
    def _block_text(self):
        self.diemmieng1 = ""
        self.diem15phut1 = ""
        self.diem1tiet1 = ""

    @api.depends('diemhocky',
    'diemmieng1','diemmieng2','diemmieng3','diemmieng4','diemmieng5','diemmieng6',
    'diem15phut1','diem15phut2','diem15phut3','diem15phut4','diem15phut5','diem15phut6',
    'diem1tiet1','diem1tiet2','diem1tiet3','diem1tiet4','diem1tiet5','diem1tiet6')
    def _compute_final(self):
        def convert_to_float(n):
            try:
                n = str(n)
                n = n.replace(',','.')
                return float(n)
            except:
                return -1.0

        for record in self:
            lst_diem_mieng = [
                record.diemmieng1, record.diemmieng2, record.diemmieng6,
                record.diemmieng3, record.diemmieng4, record.diemmieng5
            ]
            lst_diem_15 = [
                record.diem15phut1, record.diem15phut2, record.diem15phut6,
                record.diem15phut3, record.diem15phut4, record.diem15phut5
            ]
            lst_diem_1t = [
                record.diem1tiet1, record.diem1tiet2, record.diem1tiet6,
                record.diem1tiet3, record.diem1tiet4, record.diem1tiet5
            ]

            lst_diem_mieng = [convert_to_float(x) for x in lst_diem_mieng]
            lst_diem_mieng = filter(lambda x: x != -1.0, lst_diem_mieng)
            lst_diem_15 = [convert_to_float(x) for x in lst_diem_15]
            lst_diem_15 = filter(lambda x: x != -1.0, lst_diem_15)
            lst_diem_1t = [convert_to_float(x) for x in lst_diem_1t]
            lst_diem_1t = filter(lambda x: x != -1.0, lst_diem_1t)
            diemhk = convert_to_float(record.diemhocky) if convert_to_float(record.diemhocky) != -1.0 else 0

            he_so = len(lst_diem_mieng) + len(lst_diem_15) + 2*len(lst_diem_1t) + 3
            tong  = sum(lst_diem_mieng) + sum(lst_diem_15) + 2*sum(lst_diem_1t) + 3*convert_to_float(record.diemhocky)
            diemtk = str(float(tong)/float(he_so))[0:4]

            record.diemtongket = diemtk

################################################################################
# khenthuonghocsinh renew ######################################################
################################################################################
################################################################################

class khenthuonghocsinh(models.Model):
    _name = 'solienlac.khenthuonghocsinh'
    _rec_name = 'giaovien' # optional

    ngaykhenthuong = fields.Date(string="Ngày khen thưởng", default = datetime.datetime.now())
    lop = fields.Many2many("solienlac.lop", string="Học sinh")
    ghichukhenthuong = fields.Char('Ghi chú khen thưởng')

    test1 = fields.Char()
    ngayvang = fields.Date(string="Ngày", default = datetime.datetime.now())
    napdulieu = fields.Boolean('Tải danh sách học sinh')
    @api.model
    def _get_current_gv(self):
        print 'quyen giao vien'
        print self.env.user.quyen
        dmain = [('id', '=', self.env.user.giaovien.id)]
        return dmain
    giaovien = fields.Many2one(
        string="Giáo viên",
        comodel_name="solienlac.giaovien",
        default = lambda self: self.env.user.giaovien
    )
    @api.model
    def _set_gvcn(self):
        l = self.env['solienlac.lop'].search([('id', '=', self.lop.id)])
        return l.gvcn
    gvcn = fields.Many2one(
        string="Giáo viên chủ nhiệm",
        comodel_name="solienlac.giaovien",
        default = _set_gvcn
    )
    lop = fields.Many2one(
        string="Lớp",
        comodel_name="solienlac.lop",
        # domain=[('id','in',[l.lop.id for l in [lambda self: self.env.user.giaovien.monhoc]])],
    )


    #---------- define fields namhoc ------------
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc

    @api.model
    def _get_namhoc_now(self):
        now = datetime.datetime.now()
        year = now.year
        if now.month <= 9:
            year -= 1
        return str(year) + "-" + str(year+1)

    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_namhoc_now,)
    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],default = 'i')

    #---------- end define fields namhoc ------------
    @api.model
    def _get_current_list_monhoc(self):
        lst = [x.monhoc.id for x in self.env.user.giaovien.monhoc]
        lst = list(set(lst))
        return [('id', 'in', lst)]

    monhoc = fields.Many2one(
        string="Môn học",
        comodel_name="solienlac.monhoc",
        domain = _get_current_list_monhoc,)

    khenthuongchitiet = fields.Many2many(
        comodel_name='solienlac.khenthuongchitiet',
        string='Chi tiết',
        store=True,)

    @api.multi
    @api.onchange('monhoc')
    def _get_lop(self):
        self.lop = []
        current_monhoc_id = self.monhoc.id
        lst_phanban = self.env['solienlac.monhoc_has_giaovien'].search([
            ('monhoc.id','=',current_monhoc_id),
            ('hocky','=',self.hocky),
            ('namhoc','=',self.namhoc),
        ])
        lst_lop = map(lambda x: x.lop.id, lst_phanban)
        return {'domain':{'lop': [('id', 'in', lst_lop)]}}

    @api.multi
    @api.onchange('lop', 'ngaykhenthuong','napdulieu')
    def compute_model(self):
        self.test1 = str(self.env.uid) + str(random.randint(0,10))
        # Get hocsinh object
        def get_hs(self, id):
            return self.env['solienlac.hocsinh'].search([('id','=',id)])[0]

        # Load data
        self.napdulieu = False

        # Get (hocsinh object list)
        lst_hs = self.env['solienlac.hocsinh'].search([
            ('tinhtranghocsinh', '=', 'value1'), #value1 = học bình thường
            ('lop.id', '=', self.lop.id),
        ])
        # print 'lst_hs'
        # print lst_hs

        # Get (khenthuongchitiet object list)
        lst_hs_nhapdiem = self.env['solienlac.khenthuongchitiet'].search([
            ('hocsinh.lop.id','=',self.lop.id),
            ('hocsinh.tinhtranghocsinh', '=', 'value1'), # value1 = học bình thường
            ('ngaykhenthuong','=',self.ngaykhenthuong),
        ])

        # print 'lst_hs_nhapdiem'
        # print lst_hs_nhapdiem

        # Get (hocsinh object list) just hocsinh id
        lst_hs_id = map(lambda x: x.id, lst_hs)

        # Get (khenthuongchitiet object list) just hocsinh id
        lst_hs_nhapdiem_id = map(lambda x: x.hocsinh.id, lst_hs_nhapdiem)

        # Get hocsinh id is not exsit in khenthuongchitiet
        lst_hs_thieu = filter(lambda x: x not in lst_hs_nhapdiem_id, lst_hs_id)

        # print 'lst_hs_thieu'
        # print lst_hs_thieu

        if len(lst_hs_thieu) == 0:
            # In case the teacher wanna edit the score
            # hocsinh(s) are created before (at the else case)
            self.khenthuongchitiet = lst_hs_nhapdiem
        else:
            # Adding hocsinh at lst_hs_thieu into khenthuongchitiet and show it
            self.khenthuongchitiet = [] # important
            flag = True

            # Create list for checking null value

            lst_chk = [self.lop, self.ngaykhenthuong] # notice: how about self.giaovien

            # Check for all fields are inputed
            for item in lst_chk:
                if str(item) == '':
                    flag = False
                elif str(item) == 'False':
                    flag = False
                elif item == False:
                    flag = False

            # print 'flag'
            # print flag

            if flag:
                # Create objects khenthuongchitiet
                for id in lst_hs_thieu:
                    vals = {
                        'hocsinh'     : id,
                        'ngaykhenthuong'    : self.ngaykhenthuong,
                    }
                    self.env['solienlac.khenthuongchitiet'].sudo().create(vals)

                # Reload lst_hs_nhapdiem
                lst_hs_nhapdiem = self.env['solienlac.khenthuongchitiet'].search([
                    ('hocsinh.lop.id','=',self.lop.id),
                    ('hocsinh.tinhtranghocsinh', '=', 'value1'), # value1 = học bình thường
                    ('ngaykhenthuong','=',self.ngaykhenthuong),
                ])
                # Show objects khenthuongchitiet has just created
                self.khenthuongchitiet = lst_hs_nhapdiem

class khenthuongchitiet(models.Model):
    _name = 'solienlac.khenthuongchitiet'

    lydokhenthuong = fields.Char(string="Lý do khen thưởng", )
    hinhthuckhenthuong = fields.Selection(
        string="Hình thức khen thưởng",
        selection=[
                ('1', 'Khen trước lớp, trước trường'),
                ('2', 'Được tặng danh hiệu'),
                ('3', 'Được ghi tên vào bảng danh dự của trường'),
                ('4', 'Được khen thưởng đặc biệt'),
                ('5', 'Khác'),
        ],
    )
    ngaykhenthuong = fields.Date(string="Ngày khen thưởng", )


    ngayvang = fields.Date(string="Ngày", )
    vang = fields.Boolean(string="Vắng", )
    ghichu = fields.Char(string="Ghi chú", )
    @api.model
    def _get_list_namhoc(self):
        lst_namhoc=[]
        for year in range(1990,2050):
            item = str(year) + "-" + str(year+1)
            lst_namhoc.append( (item, item) )
        return lst_namhoc
    @api.model
    def _get_namhoc_now(self):
        now = datetime.datetime.now()
        year = now.year
        if now.month <= 9:
            year -= 1
        return str(year) + "-" + str(year+1)

    giaovien = fields.Many2one(
        string="Giáo viên",
        comodel_name="solienlac.giaovien",
    )

    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],default = 'i')
    namhoc = fields.Selection(
        string="Năm học",
        selection= _get_list_namhoc,
        default = _get_namhoc_now,
    )
    monhoc = fields.Many2one(
        string="Môn học",
        comodel_name="solienlac.monhoc",
    )
    hocsinh = fields.Many2one('solienlac.hocsinh', string='Học sinh')
    diemmieng1 = fields.Char('Điểm miệng', readonly=True)
    diemmieng2 = fields.Char('1')
    diemmieng3 = fields.Char('2')
    diemmieng4 = fields.Char('3')
    diemmieng5 = fields.Char('4')
    diemmieng6 = fields.Char('5')
    diem15phut1 = fields.Char('Điểm hệ số 1', readonly=True)
    diem15phut2 = fields.Char('1')
    diem15phut3 = fields.Char('2')
    diem15phut4 = fields.Char('3')
    diem15phut5 = fields.Char('4')
    diem15phut6 = fields.Char('5')
    diem1tiet1 = fields.Char('Điểm hệ số 2', readonly=True)
    diem1tiet2 = fields.Char('1')
    diem1tiet3 = fields.Char('2')
    diem1tiet4 = fields.Char('3')
    diem1tiet5 = fields.Char('4')
    diem1tiet6 = fields.Char('5')
    diemhocky = fields.Char('Điểm học kỳ')
    diemtongket = fields.Char(string='Tổng kểt', store=True, compute='_compute_final')
    xephang = fields.Integer('#')

    @api.onchange('diemmieng1','diem15phut1','diem1tiet1')
    def _block_text(self):
        self.diemmieng1 = ""
        self.diem15phut1 = ""
        self.diem1tiet1 = ""

    @api.depends('diemhocky',
    'diemmieng1','diemmieng2','diemmieng3','diemmieng4','diemmieng5','diemmieng6',
    'diem15phut1','diem15phut2','diem15phut3','diem15phut4','diem15phut5','diem15phut6',
    'diem1tiet1','diem1tiet2','diem1tiet3','diem1tiet4','diem1tiet5','diem1tiet6')
    def _compute_final(self):
        def convert_to_float(n):
            try:
                n = str(n)
                n = n.replace(',','.')
                return float(n)
            except:
                return -1.0

        for record in self:
            lst_diem_mieng = [
                record.diemmieng1, record.diemmieng2, record.diemmieng6,
                record.diemmieng3, record.diemmieng4, record.diemmieng5
            ]
            lst_diem_15 = [
                record.diem15phut1, record.diem15phut2, record.diem15phut6,
                record.diem15phut3, record.diem15phut4, record.diem15phut5
            ]
            lst_diem_1t = [
                record.diem1tiet1, record.diem1tiet2, record.diem1tiet6,
                record.diem1tiet3, record.diem1tiet4, record.diem1tiet5
            ]

            lst_diem_mieng = [convert_to_float(x) for x in lst_diem_mieng]
            lst_diem_mieng = filter(lambda x: x != -1.0, lst_diem_mieng)
            lst_diem_15 = [convert_to_float(x) for x in lst_diem_15]
            lst_diem_15 = filter(lambda x: x != -1.0, lst_diem_15)
            lst_diem_1t = [convert_to_float(x) for x in lst_diem_1t]
            lst_diem_1t = filter(lambda x: x != -1.0, lst_diem_1t)
            diemhk = convert_to_float(record.diemhocky) if convert_to_float(record.diemhocky) != -1.0 else 0

            he_so = len(lst_diem_mieng) + len(lst_diem_15) + 2*len(lst_diem_1t) + 3
            tong  = sum(lst_diem_mieng) + sum(lst_diem_15) + 2*sum(lst_diem_1t) + 3*convert_to_float(record.diemhocky)
            diemtk = str(float(tong)/float(he_so))[0:4]

            record.diemtongket = diemtk
