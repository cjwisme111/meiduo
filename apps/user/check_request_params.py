# -*- coding: utf-8 -*-
ADDRESS_CREATE_FIELDS = [
    # 0           1        2          3          4     5
    #[field_name,Must,type,fix_len_flag,max_length,value,re]
    ['receiver',    1, 0, 20, '', ''],
    ['province_id', 1, 0, 20, '', ''],
    ['city_id',     1, 0, 20, '', ''],
    ['district_id', 1, 0, 20, '', ''],
    ['place',       1, 0, 20, '', ''],
    ['mobile',      1, 0, 11, '', '^1[3-9]\d{9}$'],
    ['tel',         0, 0, 11, '', '^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$'],
    ['email',       0, 0, 20, '', '^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$'],
]

ADDRESS_FIELDS = [
    ['receiver', 1, 0, 20, '', ''],
]
