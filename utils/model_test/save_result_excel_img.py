import pandas as pd
import numpy as np
import argparse
import glob, os

__row_num = '번호'
__image_name = '이미지_이름'
__server_name = '서버명'
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

# 이미지단위로 detect결과를 엑셀에 저장하는 처리
def save_test_result(opt, num):
    gt_root = f'{opt.gt_root}{num}'
    pred_root = f'{opt.pred_root}{num}/labels'
    excel_root = f'{opt.excel_root}{num}'
    model_name = f'{opt.model_name}{num}'
    # model_name = os.path.basename(os.path.dirname(pred_root))
    img_wh = list(map(float, opt.img_wh))

    # 엑셀 저장폴더가 존재하지 않을 경우, 폴더 생성
    if not os.path.exists(f'{excel_root}'):
        os.makedirs(f'{excel_root}')

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

    gt_columns = [__gt_class, __gt_x, __gt_y, __gt_w, __gt_h]
    pred_columns = [__pred_class, __pred_x, __pred_y, __pred_w, __pred_h, __pred_conf]

    for gt_file in gt_list:
        gt_filename, exp = os.path.splitext(gt_file)
        # 엑셀파일 불러오기
        excel_pd = get_excel(excel_root, f'{gt_filename}.xlsx')
        old_model_name_list = excel_pd[__model_name].drop_duplicates().tolist()

        if model_name in old_model_name_list :
            print(f'기존 저장여부 확인 : 모델명 [{model_name}]은 엑셀에 이미 저장되어 있습니다.')
            break
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
        pred_cnt = 0
        if os.path.exists(pred_path):
            print('pred 파일 내용이 존재합니다.')
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
        results_df = pd.merge(gt_data, pred_data, left_on=__gt_class, right_on=__pred_class, how='outer', copy=False)

        # 모델명 컬럼 추가
        result_cnt = len(results_df)
        if result_cnt < 2:
            result_cnt = 1
        model_df = pd.DataFrame(np.array([model_name] * result_cnt), columns=[__model_name])
        img_df = pd.DataFrame(np.array([gt_filename] * result_cnt), columns=[__image_name])
        results_df = pd.concat([model_df, img_df, results_df], axis=1)

        # 좌표가 NaN인 경우 0으로 채우기(계산을 위해)
        results_df.fillna({__gt_x: 0, __pred_x: 0, __gt_y: 0, __pred_y: 0,
                           __gt_w: 0, __pred_w: 0, __gt_h: 0, __pred_h: 0}, inplace=True)
        # 절대좌표로 되돌리기
        new_coo_df = convert_abs_values(results_df, img_wh).copy()
        # 좌표거리 계산
        results_df[__coo_dist] = coo_dist(new_coo_df, img_wh)
        # 영역크기차이 계산
        results_df[__sub_area] = subtract_area(new_coo_df, img_wh)
        # gt데이터의 개수구하기
        results_df[__gt_obj_cnt] = len(gt_data)
        # 탐지객체 수 계산
        results_df[__pred_ogj_cnt] = pred_cnt

        # 클래스 일치도 구하는 처리
        gt_class = list(gt_data[__gt_class])
        pred_class = list(pred_data[__pred_class])
        obj_cnt = cnt_dupl_obj(gt_class, pred_class)
        results_df[__class_coincidence] = obj_cnt

        # 실제 클래스 혹은 예측 클래스 가 NaN일 경우에 실제클래스~신뢰도까지 -1로 채우기
        gt_cl_mask = results_df[__gt_class].isnull()
        # results_df.loc[gt_cl_mask, [__gt_obj_cnt]] = 0
        results_df.loc[gt_cl_mask, [__gt_class, __gt_x, __gt_y, __gt_w, __gt_h, __coo_dist, __sub_area]] = -1

        pred_cl_mask = results_df[__pred_class].isnull()
        # results_df.loc[pred_cl_mask, [__pred_ogj_cnt]] = 0
        results_df.loc[pred_cl_mask, [__pred_class, __pred_x, __pred_y, __pred_w, __pred_h, __pred_conf, __coo_dist, __sub_area]] = -1

        # 행의 개수가 1보다 클 경우,  실제객체_수~클래스 일치도 까지를 NaN으로 채우기
        if len(results_df) > 1:
            results_df.loc[1:, [__gt_obj_cnt, __pred_ogj_cnt, __class_coincidence]] = np.NaN

        # gt_pred_or_mask = gt_cl_mask | pred_cl_mask
        # results_df.loc[gt_pred_or_mask, [__coo_dist, __sub_area]] = np.NaN

        # 기존 엑셀데이터와 합치기
        dfs = [excel_pd, results_df]
        result3_in = pd.concat(dfs, axis=0, join='inner', ignore_index=True)
        result3_in.insert(0, __row_num, np.arange(len(result3_in))+1)
        # 엑셀파일로 저장
        result3_in.to_excel(f'{excel_root}/{gt_filename}.xlsx', float_format='%.4f')

# 절대좌표로 변환하는 처리
def convert_abs_values(coo_df, img_wh):
    new_coo_df = coo_df.copy()
    img_w, img_h = img_wh[0], img_wh[1]
    new_coo_df[__gt_x] = new_coo_df[__gt_x] * img_w
    new_coo_df[__gt_y] = new_coo_df[__gt_y] * img_h
    new_coo_df[__gt_w] = new_coo_df[__gt_w] * img_w
    new_coo_df[__gt_h] = new_coo_df[__gt_h] * img_h
    new_coo_df[__pred_x] = new_coo_df[__pred_x] * img_w
    new_coo_df[__pred_y] = new_coo_df[__pred_y] * img_h
    new_coo_df[__pred_w] = new_coo_df[__pred_w] * img_w
    new_coo_df[__pred_h] = new_coo_df[__pred_h] * img_h
    return new_coo_df

# gt와 pred 중심좌표의 거리차를 구하는 처리
def coo_dist(coo_df, img_wh):
    new_coo_df = coo_df.copy()
    img_w, img_h = img_wh[0], img_wh[1]
    x = (new_coo_df[__gt_x]-new_coo_df[__gt_x])
    y = (new_coo_df[__gt_y]-new_coo_df[__pred_y])
    new_coo_df[__coo_dist] = np.sqrt(x ** 2 + y ** 2) / img_w
    return new_coo_df[__coo_dist]

# gt와 pred 두 영역의 차를 구하는 처리
def subtract_area(coo_df, img_wh):
    new_coo_df = coo_df.copy()
    img_w, img_h = img_wh[0], img_wh[1]
    gt_area = new_coo_df[__gt_w] * new_coo_df[__gt_h]
    pred_area = new_coo_df[__pred_w] * new_coo_df[__pred_h]
    new_coo_df[__sub_area] = abs(gt_area - pred_area) / (img_w * img_h)
    return new_coo_df[__sub_area]

# 엑셀파일을 불러오거나 엑실파일이 없으면 dataframe을 생성
def get_excel(excel_root, file_name):
    if os.path.exists(f'{excel_root}/{file_name}') :
        print(f'excel 파일 존재유무 확인 : {file_name}이  존재합니다\n')
        old_df = pd.read_excel(f'{excel_root}/{file_name}',  header=0, index_col=0)
    else :
        print(f'excel 파일 존재유무 확인 : {file_name}이  존재하지 않습니다\n')
        index = [__row_num, __image_name, __model_name, __gt_class, __gt_x, __gt_y, __gt_w, __gt_h,
                 __pred_class, __pred_x, __pred_y, __pred_w, __pred_h, __pred_conf, __coo_dist, __sub_area,
                 __gt_obj_cnt, __pred_ogj_cnt, __class_coincidence]
        old_df = pd.DataFrame(columns=index)
    return old_df

# 두 리스트의 원소가 중복되는 개수를 구하는 처리
def cnt_dupl_obj(list1, list2):
    cnt = 0
    while list2 and list1:
        list2_pop = list2.pop()
        if list2_pop in list1:
            cnt += 1
            list1.remove(list2_pop)
    print(f'겹치는 클래스 수 : {cnt}')
    return cnt

# python utils/model_test/save_excel2.py --gt_root /Users/lfin/Downloads/model_test/00_gt_labels --pred_root /Users/lfin/Downloads/model_test/20__3090_20220207_kaggle_helmet_vest --excel_root /Users/lfin/Downloads/model_test/10_excel
if __name__ == "__main__":
    for n in range(1,6):
        parser = argparse.ArgumentParser()
        parser.add_argument('--gt_root', type=str, default='/Users/lfin/Documents/Lfin/SM/test_result/00_test/safety_test_20220214_originalsize.yolov5.pytorch/test_dataset_0', help='정답txt파일이 저장된 위치')
        parser.add_argument('--pred_root', type=str, default='/Users/lfin/Documents/Lfin/SM/test_result/10_detect/20220215_kdn_416S/kdn_416S_', help='예측txt파일이 저장된 위치')
        parser.add_argument('--excel_root', type=str, default='/Users/lfin/Documents/Lfin/SM/test_result/20_excel/00_이미지단위출력/이미지종류비교',  help="excel파일을 저장할 위치")
        parser.add_argument('--model_name', type=str, default='kdn_416S_',  help="모델명")
        parser.add_argument('--img_wh', type=list, default=[416, 416], help="이미지 너비와 높이")
        opt = parser.parse_args()
        save_test_result(opt, n)


