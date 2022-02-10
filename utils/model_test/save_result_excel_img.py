import pandas as pd
from datetime import datetime
import numpy as np
import argparse
import glob, os
from math import *

# 이미지단위로 detect결과를 엑셀에 저장하는 처리
def save_test_result(opt):

    gt_root = opt.gt_root
    pred_root = opt.pred_root
    excel_root = opt.excel_root
    model_name = opt.model_name
    img_size = float(opt.img_size)

    # ground truth 파일 리스트 취득
    gt_list = glob.glob(os.path.join(gt_root, '*.txt'))
    gt_list = [os.path.basename(i) for i in gt_list]
    gt_list.sort(reverse=False)
    # print(gt_list)

    # pred 파일 리스트 취득
    pred_list = glob.glob(os.path.join(pred_root, '*.txt'))
    # 파일명 리스트 취득
    pred_list = [os.path.basename(i) for i in pred_list]
    pred_list.sort(reverse=False)
    # print(pred_list)

    gt_columns = ['실제 클래스', '실제_x', '실제_y', '실제_w', '실제_h']
    pred_columns = ['예측 클래스', '예측_x', '예측_y', '예측_w', '예측_h', '신뢰도']

    for gt_file in gt_list:
        # print(f'\n{gt_file}')
        gt_filename, exp = os.path.splitext(gt_file)
        # gt 파일명의 엑셀파일 불러옴
        excel_pd = get_excel(excel_root, f'{gt_filename}.xlsx')
        # print(excel_pd)

        gt_path = f'{gt_root}/{gt_file}'

        gt_data = pd.DataFrame(columns=gt_columns, dtype=np.float64)
        # gt 파일내용이 있을 경우 내용 읽어오기
        if not os.stat(gt_path).st_size == 0:
            print('gt 파일 내용이 존재합니다.')
            gt_data = pd.read_csv(gt_path, sep=' ', header=None, dtype=np.float64)
        gt_data.columns = gt_columns

        # predict 파일 내용 읽어오기
        pred_path = f'{pred_root}/{gt_file}'
        pred_data = pd.DataFrame(columns=pred_columns, dtype=np.float64)

        if os.path.exists(pred_path):
            pred_data = pd.read_csv(pred_path, sep=' ', header=None, dtype=np.float64)
            pred_cnt = len(pred_data)
            if pred_cnt < 2:
                pred_cnt = 1

            pred_data.columns = pred_columns
        # gt와 pred 합치기
        results_df = pd.merge(gt_data, pred_data, left_on='실제 클래스', right_on='예측 클래스', how='outer')

        # 모델명 컬럼 추가
        gt_cnt = len(results_df)
        if gt_cnt < 2:
            gt_cnt = 1
        model_df = pd.DataFrame(np.array([model_name] * gt_cnt), columns=["모델명"])
        results_df = pd.concat([model_df, results_df], axis=1)

        if len(pred_data) > 0:
            # 신뢰도로 sort
            grouped = results_df.groupby(['모델명', '예측 클래스'])
            def conf_sort(df, column='신뢰도'):
                return df.sort_values(by=column, ascending=False)
            results_df = grouped.apply(conf_sort)
        # TODO 좌표가 -1인 경우 0으로 채우기
        results_df.fillna({'실제_x': 0, '예측_x': 0, '실제_y': 0, '예측_y': 0,
                           '실제_w': 0, '예측_w': 0, '실제_h': 0, '예측_h': 0}, inplace=True)

        # 좌표거리 계산
        new_result = coo_dist(results_df, img_size)
        # 영역크기차이 계산
        new_result = coo_dist(results_df, img_size)


        # 기존 엑셀데이터와 합치기
        dfs = [excel_pd, results_df]
        # df = pd.concat( dfs,axis=0,ignore_index=True)
        result3_in = pd.concat(dfs, axis=0, join='inner', ignore_index=True)
        result3_in.insert(0, 'num', np.arange(len(result3_in))+1)
        print('<<<<<<<<<<<result3_in>>>>>>>>>>>>>')

        result3_in.to_excel(f'{excel_root}/{gt_filename}.xlsx')

def coo_dist(coo_df, img_size):
    new_coo_df = coo_df.copy()
    new_coo_df['실제_x'] = new_coo_df['실제_x'] * img_size
    new_coo_df['실제_y'] = new_coo_df['실제_y'] * img_size
    new_coo_df['실제_w'] = new_coo_df['실제_w'] * img_size
    new_coo_df['실제_h'] = new_coo_df['실제_h'] * img_size
    new_coo_df['예측_x'] = new_coo_df['예측_x'] * img_size
    new_coo_df['예측_y'] = new_coo_df['예측_y'] * img_size
    new_coo_df['예측_w'] = new_coo_df['예측_w'] * img_size
    new_coo_df['예측_h'] = new_coo_df['예측_h'] * img_size
    # new_coo_df.fillna(0, inplace=True)
    print(new_coo_df[['실제_x', '실제_y', '예측_x', '예측_y']])
    x = new_coo_df['실제_x']-new_coo_df['예측_x']
    y = new_coo_df['실제_y']-new_coo_df['예측_y']
    new_coo_df['각 중심점의 차이'] = np.sqrt(x ** 2 + y ** 2)
    return new_coo_df

# def get_area():

def get_excel(excel_root, file_name):
    if os.path.exists(f'{excel_root}/{file_name}') :
        print(f'excel 파일 존재유부 확인 : {file_name}이  존재합니다')
        old_df = pd.read_excel(f'{excel_root}/{file_name}',  header=0, index_col=0)
    else :
        print(f'excel 파일 존재유부 확인 : {file_name}이  존재하지 않습니다')

        index = ['번호', '모델명', '실제 클래스', '실제_x', '실제_y', '실제_w', '실제_h',
                                '예측 클래스', '예측_x', '예측_y', '예측_w', '예측_h', '신뢰도']
        old_df = pd.DataFrame(columns=index)
    return old_df

def get_pred(pred_root, gt_filename):
    if os.path.isfile(f'{pred_root}/{gt_filename}'):
        pred_data = pd.read_csv(f'{pred_root}/{gt_filename}', sep=" ", header=None)
        print(pred_data)


# python utils/model_test/save_excel2.py --gt_root /Users/lfin/Downloads/model_test/00_gt_labels --pred_root /Users/lfin/Downloads/model_test/20__3090_20220207_kaggle_helmet_vest --excel_root /Users/lfin/Downloads/model_test/10_excel
if __name__ == "__main__" :
    excel_path = './YOLO테스트결과_양식.xlsx'
    parser = argparse.ArgumentParser()
    parser.add_argument('--gt_root', type=str, default='/Users/lfin/Downloads/model_test/00_gt_labels' , help='정답txt파일이 저장된 위치')
    parser.add_argument('--pred_root', type=str, default='/Users/lfin/Downloads/model_test/20__3090_20220207_kaggle_helmet_vest/labels', help='예측txt파일이 저장된 위치')
    parser.add_argument('--excel_root', type=str, default='/Users/lfin/Downloads/model_test/10_excel',  help="excel파일을 저장할 위치")
    parser.add_argument('--model_name', type=str, default='3090_kdn2',  help="모델명")
    parser.add_argument('--img_size', type=str, default='416', help="이미지사이즈")
    opt = parser.parse_args()
    # get_multicolumns()
    save_test_result(opt)


