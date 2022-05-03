import glob, os

def create_test_label(img_path, txt_path):
    img_list = glob.glob(os.path.join(img_path, '*.jpg'))
    with open(os.path.join(txt_path, 'test.txt'), 'w') as f :

        for img_file in img_list:
            filename = os.path.basename(img_file)
            f.write(f'./test-data/{filename}\n')
            print(filename)
        f.close()

if __name__ == "__main__" :
    path = "/Users/lfin/Downloads/safety_yolov5_dataset_v20220127/20_test/safety_test_416size.v1i.yolov5pytorch/test/images"
    save_path = "/Users/lfin/Downloads/safety_yolov5_dataset_v20220127/20_test/safety_test_416size.v1i.yolov5pytorch/test"
    create_test_label(path, save_path)
