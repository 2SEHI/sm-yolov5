import pandas as pd
import numpy as np
import argparse
import glob, os

__row_num = '번호'
__image_name = '이미지_이름'
__model_name = '모델명'
__gt_class = '실제_클래스'
__gt_x = '실제_x'
__gt_y = '실제_y'
__gt_w = '실제_w'
__gt_h = '실제_h'
__pred_class = '예측_클래스'
__pred_x = '예측_x'
__pred_y = '예측_y'
__pred_w = '예측_w'
__pred_h = '예측_h'
__pred_conf = '신뢰도'
__coo_dist = '각_중심점의_차이'
__sub_area = '각_영역의_크기_차이'
__gt_obj_cnt = '실제객체_수'
__pred_ogj_cnt = '탐지객체_수'
__class_coincidence = '클래스_일치도'

def combine_excel(excel_root):
    # ground truth 파일 리스트 취득
    excel_list = glob.glob(os.path.join(excel_root, '*.xlsx'))
    excel_list = [os.path.basename(i) for i in excel_list]
    excel_list.sort(reverse=False)
    print(len(excel_list))
    index = [__row_num, __model_name, __image_name, __gt_class, __gt_x, __gt_y, __gt_w, __gt_h,
             __pred_class, __pred_x, __pred_y, __pred_w, __pred_h, __pred_conf, __coo_dist, __sub_area,
             __gt_obj_cnt, __pred_ogj_cnt, __class_coincidence]
    new_df = pd.DataFrame(columns=index)
    for excel_file in excel_list:
        print(excel_file)

        old_df = pd.read_excel(f'{excel_root}/{excel_file}',  header=0, index_col=0)
        # 기존 엑셀데이터와 합치기
        dfs = [new_df, old_df]
        new_df = pd.concat(dfs, axis=0, join='inner', ignore_index=True)
    new_df.to_excel(f'{os.path.dirname(excel_root)}/total.xlsx', float_format='%.4f')

if __name__ == '__main__' :
    path = f'/Users/lfin/Documents/Lfin/SM/test_result/20_excel/00_이미지단위출력/이미지종류비교'
    combine_excel(path)