
import glob, os, re

# 폴더안의 폴더내의 이미지파일에 대해 빈 라벨파일 생성
def create_empty_labels(label_path):
    folder_list = os.listdir(label_path)
    for folder_name in folder_list:
        print(folder_name)
        label_list = glob.glob(os.path.join(f'{label_path}/{folder_name}', '*.jpeg'))
        print(len(label_list))

        # for file in label_list:
        #     filename, exp = os.path.splitext(os.path.basename(file))
        #     print(filename)
        #     text_file_path = f'{label_path}/{folder_name}/{filename}.txt'
        #     # new_lines = []
        #     f = open(text_file_path, 'w')
        #     f.close()

# 폴더내의 이미지파일에 대해 빈 라벨파일 생성
def create_empty_labels2(label_path):
    images = f'{label_path}/images'
    labels = f'{label_path}/labels'
    label_list = os.listdir(images)
    print(len(label_list))

    for file in label_list:
        filename, exp = os.path.splitext(os.path.basename(file))

        if not os.path.exists(labels):
            os.makedirs(labels)
        text_file_path = f'{labels}/{filename}.txt'
        f = open(text_file_path, 'w')
        f.close()

if __name__ == "__main__" :
    path = "/Users/lfin/Documents/Lfin/SM/data/All/90_off/off_shoes_product"
    create_empty_labels2(path)