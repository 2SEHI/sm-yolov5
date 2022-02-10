from sklearn.model_selection import train_test_split
import glob, os
def split_data(img_dir, txt_dir):
    types = ('*.jpg', '*.jpeg')
    img_list = []
    for files in types:
        # print([p for p in glob.glob(os.path.join(img_dir, files), recursive=True) if os.path.isfile(p)])
        img_list.extend(glob.glob(os.path.join(img_dir, files)))
    X_train, X_val = train_test_split(img_list, test_size=0.1, random_state=42)
    print(len(X_train))
    print(len(X_val))

    f_train = open(os.path.join(txt_dir, 'train.txt'), 'w')
    for train_path in X_train :
        f_train.write(f"{img_root}/{os.path.basename(train_path)}\n")
    f_train.close()
    val_txt = open(os.path.join(txt_dir, 'val.txt'), 'w')
    for val_path in X_val :
        val_txt.write(f"{img_root}/{os.path.basename(val_path)}\n")
    f_train.close()

if __name__ == "__main__" :
    # 이미지 저장 폴더 경로
    img_root = "../20220211_kaggle2+kdn/train_data"
    # train.txt, val.txt 파일 저장 폴더 경로
    txt_root = "./data"
    split_data(img_root, txt_root)