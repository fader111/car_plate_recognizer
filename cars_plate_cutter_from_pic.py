# saves car pictures and plates pictures prom big frame in folders

import requests
import cv2
import numpy as np
import os

from pprint import pprint

green = (0, 255, 0)
red = (0, 0, 255)
blue = (255, 0, 0)

regions = ['ru']  # Change to your country
# directory = "C:/Users/ataranov/Downloads/check (1)/check/check_1/"
# directory = "C:/Users/ataranov/Projects/datasets/cars2_corrected/"
# directory = "C:/Users/ataranov/Downloads/check (2)/check/check_1/"
directory = "from_crimea_night2/"

files = os.listdir(directory)
car_marg = 0 # car bbox margin, px
plt_marg = 5  # plate bbox margin, px

car_num = 0
car_pict_path = directory[:-1] + '_cars'
plate_pict_path = directory[:-1] + '_plates'

# if there is no dir for cars pictures, 
# create it
if not os.path.exists(car_pict_path):
    os.mkdir(car_pict_path)
    print('car pictures directory created...')

# if there is no dir for car license plates pictures, 
# create it
if not os.path.exists(plate_pict_path):
    os.mkdir(plate_pict_path)
    print('plates pictures directory created...')


def save_car_pic(pt1, pt2):
    ''' '''
    global car_num
    f_name = f'{car_pict_path}/{car_num}.bmp'
    # crop_img = img[y:y+h, x:x+w]
    car_pict = pic[pt1[1]:pt2[1], pt1[0]:pt2[0]]
    cv2.imwrite(f_name, car_pict)
    # cv2.imshow('car1', car_pict)
    # cv2.waitKey()
    car_num += 1


def save_plate_pic(pt1, pt2):
    ''' '''
    # plate_text = 
    f_name = f'{plate_pict_path}/{car_num}_X_{plate_text}.bmp'
    plate_pict = pic[pt1[1]:pt2[1], pt1[0]:pt2[0]]
    cv2.imwrite(f_name, plate_pict)
    # cv2.imshow('car1', plate_pict)
    # cv2.waitKey()

def pic_recognizer():
    for short_file_name in files:
        # print(short_file_name)
        fname = directory + short_file_name
        with open(fname, 'rb') as fp:
            response = requests.post(
                'https://api.platerecognizer.com/v1/plate-reader/',
                data=dict(regions=regions),  # Optional
                files=dict(upload=fp),
                headers={'Authorization': 'Token 3abb1b15297967bb1c10375342b10d1d87514425'})
            # pic = cv2.imread(fp)
        pprint(response.json())
        ans = response.json()
        pic = cv2.imread(fname)
        if "results" in ans:
            if ans["results"] != []:
                plt_pt1 = ans["results"][0]["box"]["xmin"]-plt_marg, \
                    ans["results"][0]["box"]["ymin"]-plt_marg
                plt_pt2 = ans["results"][0]["box"]["xmax"]+plt_marg, \
                    ans["results"][0]["box"]["ymax"]+plt_marg
                # print(f'pt1 {pt1}')
                plate_text = ans["results"][0]["plate"].upper()
                vecl_type = ans["results"][0]["vehicle"]["type"]
                score = ans["results"][0]["score"]
                car_pt1 = ans["results"][0]["vehicle"]["box"]["xmin"]-car_marg, \
                    ans["results"][0]["vehicle"]["box"]["ymin"]-car_marg
                car_pt2 = ans["results"][0]["vehicle"]["box"]["xmax"]+car_marg, \
                    ans["results"][0]["vehicle"]["box"]["ymax"]+car_marg

                print("plate ", plate_text)
                print("type ", vecl_type)
                print("score ", score)

                full_text = plate_text + ' ' + vecl_type

                # save car pict
                save_car_pic(car_pt1, car_pt2)

                # save plate pict
                save_plate_pic(plt_pt1, plt_pt2)

                # draw car bbox
                cv2.rectangle(pic, car_pt1, car_pt2, blue, 2)

                # draw license plate bbox
                cv2.rectangle(pic, plt_pt1, plt_pt2, green, 2)
                cv2.putText(pic, vecl_type + " " + str(score),
                            (plt_pt1[0], plt_pt1[1]-42), cv2.FONT_HERSHEY_SIMPLEX, 0.6, blue, 2)
                cv2.putText(pic, plate_text, (plt_pt1[0], plt_pt1[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, red, 2)
                # cv2.imshow(fname, pic)
                cv2.imshow('pic', pic)
                k = cv2.waitKey(100)
                if k == 27:
                    break
            else:
                print(f"bad picture {short_file_name}")
                continue
        else:
            print(f"bad picture {short_file_name}")
            continue
    # print ('NO MORE FILES..')


for short_video_file_name in files:
    cap = cv2.VideoCapture(directory + short_video_file_name)
    ret, pic = cap.read()
    # print('', ret, pic)
    

