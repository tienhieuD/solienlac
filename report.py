﻿# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime

class xlhkhshnkt(models.Model):
    '''Xếp loại hạnh kiểm học sinh hòa nhập, khuyết tật'''
    _name = 'solienlac.baocao.xlhkhshnkt'
    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],
    )
    namhoc = fields.Char('Năm học')
    khoi = fields.Many2one(
        string="Khối",
        comodel_name="solienlac.khoi",
    )
    tongsohs = fields.Integer('Tổng số học sinh')
    tot_sl = fields.Integer('Số lượng HK Tốt')
    tot_pt = fields.Float('Phần trăm HK Tốt')
    kha_sl = fields.Integer('Số lượng HK Khá')
    kha_pt = fields.Float('Phần trăm HK Khá')
    tb_sl = fields.Integer('Số lượng HK Trung bình')
    tb_pt = fields.Float('Phần trăm HK Trung bình')
    y_sl = fields.Integer('Số lượng HK Yếu')
    y_pt = fields.Float('Phần trăm HK Yếu')

    @api.multi
    @api.onchange('khoi')
    def _compute_model(self):
        def laysoluong_hs(hanhkiem):
            return self.env['solienlac.hocsinh'].search_count(
                [
                    ('lop.khoi.id','=',self.khoi.id),
                    ('khuyettat','!=','value1'),
                    ('hanhkiem.xeploai','=', hanhkiem),
                    ('hanhkiem.hocky', '=', self.hocky),
                    ('hanhkiem.namhoc', '=', self.namhoc),
                    ('tinhtranghocsinh', '=?', 'value1'),
                ]
            )
        def layphantram_hs(x,y):
            try:
                return round(float(x)/float(y)*100, 2)
            except:
                return 0.0
        _tongsohs = self.env['solienlac.hocsinh'].search_count([
                ('lop.khoi.id','=',self.khoi.id),
                ('khuyettat','!=','value1'),
                ('tinhtranghocsinh', '=?', 'value1'),
            ])
        _tot_sl = laysoluong_hs('tot')
        _kha_sl = laysoluong_hs('kha')
        _tb_sl  = laysoluong_hs('tb')
        _y_sl   = laysoluong_hs('yeu')
        _tot_pt = layphantram_hs(_tot_sl,_tongsohs)
        _kha_pt = layphantram_hs(_kha_sl,_tongsohs)
        _tb_pt = layphantram_hs(_tb_sl,_tongsohs)
        _y_pt = layphantram_hs(_y_sl,_tongsohs)

        self.tongsohs = _tongsohs
        self.tot_sl = _tot_sl
        self.tot_pt = _tot_pt
        self.kha_sl = _kha_sl
        self.kha_pt = _kha_pt
        self.tb_sl = _tb_sl
        self.tb_pt = _tb_pt
        self.y_sl = _y_sl
        self.y_pt = _y_pt

class xlhkhsdt(models.Model):
    '''Xếp loại hạnh kiểm học sinh dân tộc'''
    _name = 'solienlac.baocao.xlhkhsdt'
    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],
    )
    namhoc = fields.Char('Năm học')
    khoi = fields.Many2one(
        string="Khối",
        comodel_name="solienlac.khoi",
    )
    tongsohs = fields.Integer('Tổng số học sinh')
    tot_sl = fields.Integer('Số lượng HK Tốt')
    tot_pt = fields.Float('Phần trăm HK Tốt')
    kha_sl = fields.Integer('Số lượng HK Khá')
    kha_pt = fields.Float('Phần trăm HK Khá')
    tb_sl = fields.Integer('Số lượng HK Trung bình')
    tb_pt = fields.Float('Phần trăm HK Trung bình')
    y_sl = fields.Integer('Số lượng HK Yếu')
    y_pt = fields.Float('Phần trăm HK Yếu')

    @api.multi
    @api.onchange('khoi')
    def _compute_model(self):
        def laysoluong_hs(hanhkiem):
            return self.env['solienlac.hocsinh'].search_count(
                [
                    ('lop.khoi.id','=',self.khoi.id),
                    ('dantoc.tendantoc','not like','Kinh'),
                    ('hanhkiem.xeploai','=', hanhkiem),
                    ('hanhkiem.hocky', '=', self.hocky),
                    ('hanhkiem.namhoc', '=', self.namhoc),
                    ('tinhtranghocsinh', '=?', 'value1'),
                ]
            )
        def layphantram_hs(x,y):
            try:
                return round(float(x)/float(y)*100, 2)
            except:
                return 0.0
        _tongsohs = self.env['solienlac.hocsinh'].search_count([
                ('lop.khoi.id','=',self.khoi.id),
                ('dantoc.tendantoc','not like','Kinh'),
                ('tinhtranghocsinh', '=?', 'value1'),
            ])
        _tot_sl = laysoluong_hs('tot')
        _kha_sl = laysoluong_hs('kha')
        _tb_sl  = laysoluong_hs('tb')
        _y_sl   = laysoluong_hs('yeu')
        _tot_pt = layphantram_hs(_tot_sl,_tongsohs)
        _kha_pt = layphantram_hs(_kha_sl,_tongsohs)
        _tb_pt = layphantram_hs(_tb_sl,_tongsohs)
        _y_pt = layphantram_hs(_y_sl,_tongsohs)

        self.tongsohs = _tongsohs
        self.tot_sl = _tot_sl
        self.tot_pt = _tot_pt
        self.kha_sl = _kha_sl
        self.kha_pt = _kha_pt
        self.tb_sl = _tb_sl
        self.tb_pt = _tb_pt
        self.y_sl = _y_sl
        self.y_pt = _y_pt

class xlhlhshnkt(models.Model):
    '''Xếp loại học lực học sinh hòa nhập, khuyết tật'''
    _name = 'solienlac.baocao.xlhlhshnkt'
    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],
    )
    namhoc = fields.Char('Năm học')
    khoi = fields.Many2one(
        string="Khối",
        comodel_name="solienlac.khoi",
    )
    tongsohs = fields.Integer('Tổng số học sinh')
    tot_sl = fields.Integer('Số lượng HK Giỏi')
    tot_pt = fields.Float('Phần trăm HK Giỏi')
    kha_sl = fields.Integer('Số lượng HK Khá')
    kha_pt = fields.Float('Phần trăm HK Khá')
    tb_sl = fields.Integer('Số lượng HK Trung bình')
    tb_pt = fields.Float('Phần trăm HK Trung bình')
    y_sl = fields.Integer('Số lượng HK Yếu')
    y_pt = fields.Float('Phần trăm HK Yếu')
    k_sl = fields.Integer('Số lượng HK Kém')
    k_pt = fields.Float('Phần trăm HK Kém')

    @api.multi
    @api.onchange('khoi')
    def _compute_model(self):
        def laysoluong_hs(hocluc):
            return self.env['solienlac.hocsinh'].search_count(
                [
                    ('lop.khoi.id','=',self.khoi.id),
                    ('khuyettat','!=','value1'),
                    ('bangdiem.xeploai','=', hocluc),
                    ('bangdiem.kyhoc', '=', self.hocky),
                    ('bangdiem.namhoc', '=', self.namhoc),
                    ('tinhtranghocsinh', '=?', 'value1'),
                ]
            )
        def layphantram_hs(x,y):
            try:
                return round(float(x)/float(y)*100, 2)
            except:
                return 0.0
        _tongsohs = self.env['solienlac.hocsinh'].search_count([
                ('lop.khoi.id','=',self.khoi.id),
                ('khuyettat','!=','value1'),
                ('tinhtranghocsinh', '=?', 'value1'),
            ])
        _tot_sl = laysoluong_hs('gioi')
        _kha_sl = laysoluong_hs('kha')
        _tb_sl  = laysoluong_hs('tb')
        _y_sl   = laysoluong_hs('yeu')
        _k_sl   = laysoluong_hs('kem')
        _tot_pt = layphantram_hs(_tot_sl,_tongsohs)
        _kha_pt = layphantram_hs(_kha_sl,_tongsohs)
        _tb_pt = layphantram_hs(_tb_sl,_tongsohs)
        _y_pt = layphantram_hs(_y_sl,_tongsohs)
        _k_pt = layphantram_hs(_k_sl,_tongsohs)

        self.tongsohs = _tongsohs
        self.tot_sl = _tot_sl
        self.tot_pt = _tot_pt
        self.kha_sl = _kha_sl
        self.kha_pt = _kha_pt
        self.tb_sl = _tb_sl
        self.tb_pt = _tb_pt
        self.y_sl = _y_sl
        self.y_pt = _y_pt
        self.k_sl = _k_sl
        self.k_pt = _k_pt

class xlhlhsdt(models.Model):
    '''Xếp loại học lực học sinh dân tộc'''
    _name = 'solienlac.baocao.xlhlhsdt'
    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],
    )
    namhoc = fields.Char('Năm học')
    khoi = fields.Many2one(
        string="Khối",
        comodel_name="solienlac.khoi",
    )
    tongsohs = fields.Integer('Tổng số học sinh')
    tot_sl = fields.Integer('Số lượng HK Giỏi')
    tot_pt = fields.Float('Phần trăm HK Giỏi')
    kha_sl = fields.Integer('Số lượng HK Khá')
    kha_pt = fields.Float('Phần trăm HK Khá')
    tb_sl = fields.Integer('Số lượng HK Trung bình')
    tb_pt = fields.Float('Phần trăm HK Trung bình')
    y_sl = fields.Integer('Số lượng HK Yếu')
    y_pt = fields.Float('Phần trăm HK Yếu')
    k_sl = fields.Integer('Số lượng HK Kém')
    k_pt = fields.Float('Phần trăm HK Kém')

    @api.multi
    @api.onchange('khoi')
    def _compute_model(self):
        def laysoluong_hs(hocluc):
            return self.env['solienlac.hocsinh'].search_count(
                [
                    ('lop.khoi.id','=',self.khoi.id),
                    ('dantoc.tendantoc','not like','Kinh'),
                    ('bangdiem.xeploai','=', hocluc),
                    ('bangdiem.kyhoc', '=', self.hocky),
                    ('bangdiem.namhoc', '=', self.namhoc),
                    ('tinhtranghocsinh', '=?', 'value1'),
                ]
            )
        def layphantram_hs(x,y):
            try:
                return round(float(x)/float(y)*100, 2)
            except:
                return 0.0
        _tongsohs = self.env['solienlac.hocsinh'].search_count([
                ('lop.khoi.id','=',self.khoi.id),
                ('dantoc.tendantoc','not like','Kinh'),
                ('tinhtranghocsinh', '=?', 'value1'),
            ])
        _tot_sl = laysoluong_hs('tot')
        _kha_sl = laysoluong_hs('kha')
        _tb_sl  = laysoluong_hs('tb')
        _y_sl   = laysoluong_hs('yeu')
        _k_sl   = laysoluong_hs('kem')
        _tot_pt = layphantram_hs(_tot_sl,_tongsohs)
        _kha_pt = layphantram_hs(_kha_sl,_tongsohs)
        _tb_pt = layphantram_hs(_tb_sl,_tongsohs)
        _y_pt = layphantram_hs(_y_sl,_tongsohs)
        _k_pt = layphantram_hs(_k_sl,_tongsohs)

        self.tongsohs = _tongsohs
        self.tot_sl = _tot_sl
        self.tot_pt = _tot_pt
        self.kha_sl = _kha_sl
        self.kha_pt = _kha_pt
        self.tb_sl = _tb_sl
        self.tb_pt = _tb_pt
        self.y_sl = _y_sl
        self.y_pt = _y_pt
        self.k_sl = _k_sl
        self.k_pt = _k_pt

class thhsth(models.Model):
    '''Tình hình HS thôi học'''
    _name = 'solienlac.baocao.thhsth'

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
    khoi = fields.Many2one(
        string="Khối",
        comodel_name="solienlac.khoi",
    )
    hocky = fields.Selection(
        string="Học kỳ",
        selection=[
                ('i', 'Học kỳ I'),
                ('ii', 'Học kỳ II'),
                ('iii', 'Cả năm'),
        ],
        default='iii',
    )

    hs_daunam = fields.Integer(string="Tổng học sinh đầu năm", )
    hs_cuoinam = fields.Integer(string="Tổng học sinh cuối năm", )
    hs_chuyenden = fields.Integer(string="Tổng học sinh chuyển đến", )
    hs_chuyendi = fields.Integer(string="Tổng học sinh chuyển đi", )
    hs_thoihoc = fields.Integer(string="Tổng học sinh thôi học", )
    hs_thoihoc_hocluckem = fields.Integer(string="Tổng học sinh thôi học (học lực kém)", )
    hs_thoihoc_hoancanhkk = fields.Integer(string="Tổng học sinh thôi học (hoàn cảnh khó khăn)",)
    hs_thoihoc_xanha = fields.Integer(string="Tổng học sinh thôi học (xa nhà)", )
    hs_thoihoc_khac = fields.Integer(string="Tổng học sinh thôi học (lý do khác)", )
