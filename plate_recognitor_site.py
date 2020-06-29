# pip install requests
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
directory = "C:/Users/ataranov/Downloads/check (2)/check/check_1/"
directory = "C:/Users/ataranov/Downloads/from_crimea_night/"

files = os.listdir(directory)
plt_marg = 5 # plate bbox margin, px

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
    if ans["results"] != []:
        plt_pt1 =   ans["results"][0]["box"]["xmin"]-plt_marg, \
                    ans["results"][0]["box"]["ymin"]-plt_marg
        plt_pt2 =   ans["results"][0]["box"]["xmax"]+plt_marg, \
                    ans["results"][0]["box"]["ymax"]+plt_marg
        # print(f'pt1 {pt1}')
        plate_text = ans["results"][0]["plate"].upper()
        vecl_type = ans["results"][0]["vehicle"]["type"]
        score = ans["results"][0]["score"]
        car_pt1 = ans["results"][0]["vehicle"]["box"]["xmin"], \
                ans["results"][0]["vehicle"]["box"]["ymin"]
        car_pt2 = ans["results"][0]["vehicle"]["box"]["xmax"], \
                ans["results"][0]["vehicle"]["box"]["ymax"]

        print("plate ", plate_text)
        print("type ", vecl_type)
        print("score ", score)

        full_text = plate_text + ' ' + vecl_type

        # draw car bbox
        cv2.rectangle(pic, car_pt1, car_pt2, blue, 2)
        
        # draw license plate bbox
        cv2.rectangle(pic, plt_pt1, plt_pt2, green, 2)
        cv2.putText(pic, vecl_type + " " + str(score),
                    (plt_pt1[0], plt_pt1[1]-42), cv2.FONT_HERSHEY_SIMPLEX, 0.6, blue, 2)
        cv2.putText(pic, plate_text, (plt_pt1[0], plt_pt1[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, red, 2)
        cv2.imshow(fname, pic)
        # cv2.imshow('pic', pic)
        k = cv2.waitKey(100)
        if k == 27:
            break
    else:
        print(f"bad picture {short_file_name}")
        continue
