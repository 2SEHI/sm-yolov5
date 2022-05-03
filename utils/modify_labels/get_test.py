import os, glob
import re

def get_test_results(label_path):
    obj_list = ['person', 'helmet_on', 'vest_on', 'shoes_on',
                'helmet_off', 'vest_off', 'shoes_off']
    # 라벨링 파일 리스트 가져오기
    label_list = glob.glob(os.path.join(label_path, '*.txt'))
    newlines = ''
    # print(label_list)
    for i, obj in enumerate(obj_list):
        print('==========================')
        print(f'<{obj}>')
        person_cnt = 0
        helmet_cnt = 0
        vest_cnt = 0
        shoes_cnt = 0
        else_cnt = 0
        newlines += f'\n<{obj}>\n'
        # 반복문
        for label_file in label_list:
            # 파일명 취득
            filename = os.path.basename(label_file)

            if filename.startswith(obj):
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                    # newlines += f'{filename}\n'
                    # print(lines)
                    for line in lines:
                        cls = re.split(r' ', line)[0]
                        # pred = re.split(r' ', line)[-1]
                        newline = ''
                        if line.startswith('0'):
                            person_cnt += 1
                        elif line.startswith('1'):
                            helmet_cnt += 1
                        elif line.startswith('2'):
                            vest_cnt += 1
                        elif line.startswith('3'):
                            shoes_cnt += 1
                        else:
                            else_cnt += 1
                        # newline = f'{cls}\t{pred}'
                        newlines += newline
                    f.close()
        newlines += f'person:\t\t{person_cnt}\n' \
                    f'helmet_on:\t{helmet_cnt}\n'\
                      f'vest_on:\t{vest_cnt}\n'\
                      f'shoes_on:\t{shoes_cnt}\n'\
                      f'else_on:\t{else_cnt}\n'
        # with open('./runs/detect_result.txt', 'w') as f:
        with open('./runs/test_dataset_obj.txt', 'w') as f:
            f.writelines(newlines)
            f.close()




if __name__ == '__main__' :
    # label path
    # path = './runs/detect/exp16/labels'
    path = './data/test-data'
    get_test_results(path)
