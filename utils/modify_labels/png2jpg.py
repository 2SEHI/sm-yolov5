from PIL import Image
import glob, os

## 폴더 내의 이미지를 jpg로 변환시키는 처리

def png2jpg(img_path):
    img_list = glob.glob(os.path.join(img_path, '*.*'))
    print(len(img_list))
    for file in img_list :
        filename, exp = os.path.splitext(os.path.basename(file))
        print(filename)
        im1 = Image.open(file)
        if im1.mode != 'RGB':
            im1 = im1.convert('RGB')
        # os.remove(file)
        im1.save(f'{img_path}/new/{filename}.jpg')

if __name__ == "__main__" :
    path = "/Users/lfin/Downloads/safety_yolov5/crop_3_off"
    png2jpg(path)