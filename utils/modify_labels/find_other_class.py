import glob, os

def find_other_class(label_path, new_label_path) :
    label_list = glob.glob(os.path.join(label_path, "*.txt"))
    print(len(label_list))

    for file in label_list:
        new_lines = []
        with open(os.path.join(label_path, file), 'r') as f :
            lines = f.readlines()
            for line in lines :
                if line.startswith('0') :
                    continue
                new_lines += line

            f.close()

        print(os.path.join(new_label_path, file))
        with open(os.path.join(new_label_path, file), 'w') as f:
            f.writelines(new_lines)
            f.close()

if __name__ == "__main__":
    path = "/Users/lfin/Downloads/wini7_yolov5_backup/yolov5_dataset/kaggle-hardhat/train/labels"
    new_path = "/Users/lfin/Downloads/wini7_yolov5_backup/yolov5_dataset/kaggle-hardhat/train/new_labels"
    find_other_class(path, new_path)