
import glob, os, re

def change_index(label_path):
    index_dict = {"0": "1"}
    # old_helmet = "0"
    # # old_vest = "1"
    # new_helmet = "1"
    # # new_vest = "2"


    label_list = glob.glob(os.path.join(label_path, "*.txt"))
    print(len(label_list))

    for file in label_list:
        new_lines = []
        with open(os.path.join(label_path, file), 'r') as f:
            lines = f.readlines()
            for line in lines:
                new_line = ''
                for index_key, index_value in index_dict.items():
                    if line.startswith(index_key):
                        new_line = re.sub(f'^{index_key}', index_value, line)
                        print(new_line)
                    new_lines += new_line
            f.close()

        with open(file, 'w') as f:
            f.writelines(new_lines)
            f.close()

if __name__ == "__main__" :
    path = "/Users/lfin/Downloads/kaggle_helmet-person.v5-original_onlyhelmet.yolov5pytorch/train/labels"
    # new_label_path = "/Users/lfin/Downloads/safety_train_kaggle-helmet-vest.v1-original.yolov5pytorch/train/new_label_path"
    change_index(path)