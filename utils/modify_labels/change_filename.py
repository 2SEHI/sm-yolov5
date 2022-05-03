import glob, os, re
import shutil

def change_filename(save_root, datatype):
    img_root = f'{save_root}/images'
    label_root = f'{save_root}/labels'
    if not os.path.exists(save_root):
        os.makedirs(save_root)
    elif not os.path.exists(img_root):
        os.makedirs(img_root)
    elif not os.path.exists(label_root):
        os.makedirs(label_root)

    old_img_file_list = os.listdir(img_root)
    old_label_list = os.listdir(label_root)
    for idx, old_img_file in enumerate(old_img_file_list):
        old_filename, exp = os.path.splitext(os.path.basename(old_img_file))

        new_filename = f'{datatype}_{idx}'

        old_img_path = f'{img_root}/{old_img_file}'
        old_label_path = f'{label_root}/{old_filename}.txt'

        new_img_path = f'{new_filename}{exp}'
        new_label_path = f'{new_filename}.txt'
        if not os.path.exists(old_label_path):
            continue
        print(old_img_path)
        newone = shutil.move(old_img_path, new_img_path)
        print(newone)
        shutil.move(old_label_path, new_label_path)
        #
        # new_img_path = os.path.join(new_img_root, f'{new_filename}.jpg')
        #
        # old_label_path = os.path.join(label_root, "OldFileName.txt")
        # new_label_path = os.path.join(new_label_root, "NewFileName.NewExtension")
        #
        # newFileName = shutil.copy(old_img_path, new_img_path)
        # print("The renamed file has the name:", newFileName)
        #
        # if old_img_path not in old_label_list:
        #     print(f'{old_img_path} 와 동일한 파일명이 labels에 존재하지 않습니다.')
        #     continue
        # old_path = f'{old_img}/{old_img}'
        # new_path = f'{save_root}'
        # # shutil.copyfile(old_path, os.path.join(save_root, ))
        # new_filename = f'{datatype}_{idx}'

def get_idx(path, exptype):
    file_list = os.listdir(path)

    file_list = [re.sub(f'{exptype}', '', i) for i in file_list]

    print(sorted(file_list, reverse=True))
    if '.DS_Store' in file_list:
        file_list.remove('.DS_Store')

    # print(sorted(file_list, reverse=True))
    result = list(map(lambda x: (x.split('_')[0], int(x.split('_')[1])), file_list))
    print(result)
    # f = sorted(result, key=lambda x:int(x[1]), reverse=True)




if __name__ == '__main__':
    datatype = 'kdn'
    new_root = '/Users/lfin/Documents/Lfin/SM/data/All/10_kdn(noRenamed)/train'
    # old_img_root = '/Users/lfin/Downloads/safety_yolov5_dataset_v20220127/00_original/safety_train_cropped_original/train/images'
    # old_label_root = '/Users/lfin/Downloads/safety_yolov5_dataset_v20220127/00_original/safety_train_cropped_original/train/labels'

    # get_idx(f'{new_root}/images', '.jpg')
    change_filename(new_root, datatype)
