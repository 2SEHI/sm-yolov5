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
    print(opt.img_wh)
    img_wh = list(map(float, opt.img_wh))

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
        gt_filename, exp = os.path.splitext(gt_file)
        # 엑셀파일 불러오기
        excel_pd = get_excel(excel_root, f'{gt_filename}.xlsx')

        # gt데이터 가져오기
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

            if pred_cnt > 0:
                # 신뢰도로 sort
                grouped = pred_data.groupby(0)
                def conf_sort(df, column=5):
                    return df.sort_values(by=column, ascending=False)
                pred_data = grouped.apply(conf_sort)

        pred_data.columns = pred_columns

        # gt와 pred 합치기
        # TODO gt데이터가 1개, pred데이터가 2개인 경우 merge할 때 gt데이터가 2개로 복사됨
        results_df = pd.merge(gt_data, pred_data, left_on='실제 클래스', right_on='예측 클래스', how='outer', copy=False)

        # 모델명 컬럼 추가
        result_cnt = len(results_df)
        if result_cnt < 2:
            result_cnt = 1
        model_df = pd.DataFrame(np.array([model_name] * result_cnt), columns=["모델명"])
        results_df = pd.concat([model_df, results_df], axis=1)

        # TODO 좌표가 -1인 경우 0으로 채우기
        results_df.fillna({'실제_x': 0, '예측_x': 0, '실제_y': 0, '예측_y': 0,
                           '실제_w': 0, '예측_w': 0, '실제_h': 0, '예측_h': 0}, inplace=True)

        # 좌표거리 계산
        new_coo_df = convert_abs_values(results_df, img_wh).copy()
        # 좌표거리 계산
        results_df['각 중심점의 차이'] = coo_dist(new_coo_df)
        # 영역크기차이 계산
        results_df['각 영역의 크기 차이'] = subtract_area(new_coo_df)
        # gt데이터의 개수
        results_df['실제객체 수'] = len(gt_data)
        # 탐지객체 수 계산
        results_df['탐지객체 수'] = len(pred_data)

        gt_class = list(gt_data['실제 클래스'])
        pred_class = list(pred_data['예측 클래스'])
        obj_cnt = cnt_dupl_obj(gt_class, pred_class)
        results_df['클래스 일치도'] = obj_cnt

        # 기존 엑셀데이터와 합치기
        dfs = [excel_pd, results_df]
        # df = pd.concat( dfs,axis=0,ignore_index=True)
        result3_in = pd.concat(dfs, axis=0, join='inner', ignore_index=True)
        result3_in.insert(0, 'num', np.arange(len(result3_in))+1)
        print('<<<<<<<<<<<result3_in>>>>>>>>>>>>>')

        result3_in.to_excel(f'{excel_root}/{gt_filename}.xlsx')


def convert_abs_values(coo_df, img_wh):
    new_coo_df = coo_df.copy()
    img_w, img_h = img_wh[0], img_wh[1]
    new_coo_df['실제_x'] = new_coo_df['실제_x'] * img_w
    new_coo_df['실제_y'] = new_coo_df['실제_y'] * img_h
    new_coo_df['실제_w'] = new_coo_df['실제_w'] * img_w
    new_coo_df['실제_h'] = new_coo_df['실제_h'] * img_h
    new_coo_df['예측_x'] = new_coo_df['예측_x'] * img_w
    new_coo_df['예측_y'] = new_coo_df['예측_y'] * img_h
    new_coo_df['예측_w'] = new_coo_df['예측_w'] * img_w
    new_coo_df['예측_h'] = new_coo_df['예측_h'] * img_h
    return new_coo_df

def coo_dist(coo_df):
    new_coo_df = coo_df.copy()
    x = (new_coo_df['실제_x']-new_coo_df['예측_x'])
    y = (new_coo_df['실제_y']-new_coo_df['예측_y'])
    new_coo_df['각 중심점의 차이'] = np.sqrt(x ** 2 + y ** 2)
    return new_coo_df['각 중심점의 차이']

def subtract_area(coo_df):
    new_coo_df = coo_df.copy()
    gt_area = new_coo_df['실제_w'] * new_coo_df['실제_h']
    pred_area = new_coo_df['예측_w'] * new_coo_df['예측_h']
    new_coo_df['각 영역의 크기 차이'] = abs(gt_area - pred_area)
    return new_coo_df['각 영역의 크기 차이']

def get_excel(excel_root, file_name):
    if os.path.exists(f'{excel_root}/{file_name}') :
        print(f'excel 파일 존재유부 확인 : {file_name}이  존재합니다')
        old_df = pd.read_excel(f'{excel_root}/{file_name}',  header=0, index_col=0)
    else :
        print(f'excel 파일 존재유부 확인 : {file_name}이  존재하지 않습니다')

        index = ['번호', '모델명', '실제 클래스', '실제_x', '실제_y', '실제_w', '실제_h',
                 '예측 클래스', '예측_x', '예측_y', '예측_w', '예측_h', '신뢰도', '각 중심점의 차이', '각 영역의 크기 차이',
                 '실제객체 수', '탐지객체 수', '클래스 일치도']
        old_df = pd.DataFrame(columns=index)
    return old_df

def get_pred(pred_root, gt_filename):
    if os.path.isfile(f'{pred_root}/{gt_filename}'):
        pred_data = pd.read_csv(f'{pred_root}/{gt_filename}', sep=" ", header=None)
        print(pred_data)

def cnt_dupl_obj(list1, list2):
    cnt = 0
    print(f'{list1}')
    print(f'{list2}')
    while list2 and list1:
        list2_pop = list2.pop()
        if list2_pop in list1:
            cnt += 1
            list1.remove(list2_pop)
        print(f'list1 : {list1}')
        print(f'list2 : {list2}')
    print(f'겹치는 객체 수 : {cnt}')
    return cnt

# python utils/model_test/save_excel2.py --gt_root /Users/lfin/Downloads/model_test/00_gt_labels --pred_root /Users/lfin/Downloads/model_test/20__3090_20220207_kaggle_helmet_vest --excel_root /Users/lfin/Downloads/model_test/10_excel
if __name__ == "__main__":
    excel_path = './YOLO테스트결과_양식.xlsx'
    parser = argparse.ArgumentParser()
    parser.add_argument('--gt_root', type=str, default='/Users/lfin/Downloads/model_test/00_gt_labels', help='정답txt파일이 저장된 위치')
    parser.add_argument('--pred_root', type=str, default='/Users/lfin/Downloads/model_test/20__3090_20220207_kaggle_helmet_vest/labels', help='예측txt파일이 저장된 위치')
    parser.add_argument('--excel_root', type=str, default='/Users/lfin/Downloads/model_test/10_excel',  help="excel파일을 저장할 위치")
    parser.add_argument('--model_name', type=str, default='3090_kdn2',  help="모델명")
    parser.add_argument('--img_wh', type=list, default=[416, 416], help="이미지 너비와 높이")
    opt = parser.parse_args()
    save_test_result(opt)


