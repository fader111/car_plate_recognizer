#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import os 
import argparse
import io
import json
import time
from pprint import pprint

import requests
from PIL import Image

import cv2

green = (0, 255, 0)
red = (0, 0, 255)
blue = (255, 0, 0)

car_marg = 0 # car bbox margin, px
plt_marg = 5  # plate bbox margin, px

#video_f_name = "4.avi"
video_f_number = 0
directory = "video/"
v_files = os.listdir(directory)
# src_video = directory + video_f_name

# files = os.listdir(directory)
car_marg = 0 # car bbox margin, px
plt_marg = 5  # plate bbox margin, px

car_num = 0
car_pict_path = directory[:-1] + '_cars'
plate_pict_path = directory[:-1] + '_plates'
car_zoom = 2
plate_text = ''

frame_step = 3

# token = '3abb1b15297967bb1c10375342b10d1d87514425' # почти кончился
# token = '7276fe3a5d2e9bbbec54882cf1a74187bee2f8cf' # и этот 
# token = '9f18f00c2c7d3368c45f6216a09b619f0226a3bd' # и все
token = 'a65f261760e19000dcf808dfec86d5f3de9e5f5a'


def save_car_pic(pic, i):
    ''' '''
    global car_num
    f_name = f'{car_pict_path}/{video_f_number}_{car_num}_{i}.bmp'
    # crop_img = img[y:y+h, x:x+w]
    #car_pict = pic[pt1[1]:pt2[1], pt1[0]:pt2[0]]
    cv2.imwrite(f_name, pic)
    # cv2.imshow('car1', car_pict)
    # cv2.waitKey()
    car_num += 1


def save_plate_pic(pic, i, pt1, pt2):
    ''' '''
    # plate_text = 
    f_name = f'{plate_pict_path}/{video_f_number}n{car_num}_{i}_{plate_text}.bmp'
    plate_pict = pic[pt1[1]:pt2[1], pt1[0]:pt2[0]]
    cv2.imwrite(f_name, plate_pict)
    # cv2.imshow('car1', plate_pict)
    # cv2.waitKey()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        'Read license plates from a video and output the result as JSON.',
        epilog=
        'For example: python alpr_video.py --api MY_API_KEY --start 900 --end 2000 --skip 3 "/path/to/cars.mp4"'
    )
    # parser.add_argument('--api', help='Your API key.', required=True)
    parser.add_argument('--start', default =0, 
                        help='Start reading from this frame.',
                        type=int)
    # parser.add_argument('--end', help='End reading after this frame.', type=int)
    parser.add_argument('--skip', help='Read 1 out of N frames.', type=int, default = frame_step) # шаг кадров
    # parser.add_argument('FILE', help='Path to video.')
    return parser.parse_args()


def main():
    global plate_text, video_f_number
    args = parse_arguments()
    result = []
    v_file_index = 0
    src_video = directory + v_files[v_file_index]
    video_f_number = int(v_files[v_file_index].split('.')[0]) # the number of video file given from the name .avi

    cap = cv2.VideoCapture(src_video)
    frame_id = 0
    while (cap.isOpened()):
        
        ret, big_frame = cap.read()
        
        if not ret:
            # если кончился файл, надо взять следующий
            v_file_index+=1
            src_video = directory + v_files[v_file_index]
            video_f_number = int(v_files[v_file_index].split('.')[0]) # the number of video file given from the name .avi
            cap = cv2.VideoCapture(src_video)
            ret, big_frame = cap.read()
        
        y_size_new, x_size_new = big_frame.shape[:2]
        frame = cv2.resize(big_frame, (round(x_size_new/car_zoom), round(y_size_new/car_zoom)))
        
        # cv2.imshow("small_pic", frame)
        # cv2.waitKey(100)

        frame_id += 1
        if args.skip and frame_id % args.skip != 0:
            continue
        if args.start and frame_id < args.start:
            continue
        # if args.end and frame_id > args.end:
            # break
        print('Reading frame %s' % frame_id)
        # сначала подаем на сайт пережатую картинку, 
        # на полноразмерной рамка машины уезжает.
        imgByteArr = io.BytesIO()
        im = Image.fromarray(frame)
        im.save(imgByteArr, 'JPEG')
        imgByteArr.seek(0)
        response = requests.post(
            'https://api.platerecognizer.com/v1/plate-reader/',
            files=dict(upload=imgByteArr),
            headers={'Authorization': 'Token ' + token})
        # result.append(response.json())
        
        ans = response.json()
        print('car result')
        pprint(ans)

        # pic=frame # для совместимости чтоб не переименовывать везде
        if "results" in ans:
            if ans["results"] != []:
                for i, result in enumerate(ans["results"]):
                    vecl_type = result["vehicle"]["type"]
                    score = result["score"]
                    car_pt1 = result["vehicle"]["box"]["xmin"]-car_marg, \
                        result["vehicle"]["box"]["ymin"]-car_marg
                    car_pt2 = result["vehicle"]["box"]["xmax"]+car_marg, \
                        result["vehicle"]["box"]["ymax"]+car_marg
            
                    # потом находим координаты машины на нежатой картинке
                    big_car_pt1 = car_pt1[0]*car_zoom, car_pt1[1]*car_zoom
                    big_car_pt2 = car_pt2[0]*car_zoom, car_pt2[1]*car_zoom

                    car_frame_big = big_frame[big_car_pt1[1]:big_car_pt2[1], big_car_pt1[0]:big_car_pt2[0]]
                    
                    if not car_frame_big.shape[0] == 0:
                        cv2.imshow('big_car'+str(i), car_frame_big)
                        cv2.waitKey(1)
                    else:
                        continue

                    # сохраняем машину в файл
                    save_car_pic(car_frame_big, i)

                    # и опять ее кидаем сайту чтоб распознать позицию пластины и ее текст
                    imgByteArr2 = io.BytesIO()
                    im2 = Image.fromarray(car_frame_big)
                    im2.save(imgByteArr2, 'JPEG')
                    imgByteArr2.seek(0)
                    response2 = requests.post(
                        'https://api.platerecognizer.com/v1/plate-reader/',
                        files=dict(upload=imgByteArr2),
                        headers={'Authorization': 'Token ' + token})
                    # result.append(response.json())
                    
                    ans2 = response2.json()
                    # pprint(ans2)
                    
                    if "results" in ans2:
                        if ans2["results"] != []:
                            plt_pt1 = ans2["results"][0]["box"]["xmin"]-plt_marg, \
                                ans2["results"][0]["box"]["ymin"]-plt_marg
                            plt_pt2 = ans2["results"][0]["box"]["xmax"]+plt_marg, \
                                ans2["results"][0]["box"]["ymax"]+plt_marg
                            # print(f'pt1 {pt1}')
                            plate_text = ans2["results"][0]["plate"].upper()
                            vecl_type = ans2["results"][0]["vehicle"]["type"]
                            score = ans2["results"][0]["score"]
                            
                            print("plate ", plate_text)
                            print("type ", vecl_type)
                            print("score ", score)

                            # save plate pict 
                            save_plate_pic(car_frame_big, i, plt_pt1, plt_pt2)

                            full_text = plate_text + ' ' + vecl_type

                            # draw car bbox
                            # cv2.rectangle(pic, car_pt1, car_pt2, blue, 2)

                            # draw license plate bbox
                            cv2.rectangle(car_frame_big, plt_pt1, plt_pt2, green, 2)
                            cv2.putText(car_frame_big, vecl_type + " " + str(score),
                                        (plt_pt1[0], plt_pt1[1]-42), cv2.FONT_HERSHEY_SIMPLEX, 0.6, blue, 2)
                            cv2.putText(car_frame_big, plate_text, (plt_pt1[0], plt_pt1[1]-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, red, 2)

                            # cv2.imshow(fname, pic)
                            if not car_frame_big.shape[0] == 0:
                                cv2.imshow('big_car'+str(i), car_frame_big)
                                k = cv2.waitKey(100)
                                if k == 27:
                                    break
            else:
                continue
        else:
            continue

        ### !!! ###
        # time.sleep(0.1)

    # print(json.dumps(result, indent=2))
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()