import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from tracker import*
import time
from math import dist
model=YOLO('yolov8s.pt')



def RGB(event, x, y, flags, param):                # Defines a callback function RGB which will be triggered when a mouse event occurs.
    if event == cv2.EVENT_MOUSEMOVE :  
        colorsBGR = [x, y]
        print(colorsBGR)
        

cv2.namedWindow('RGB')                             # Creates a named window for displaying the video frames.
cv2.setMouseCallback('RGB', RGB)                   # Associates the callback function RGB with the 'RGB' window.

cap=cv2.VideoCapture('stock-footage-traffic-on-the-indian-roads.WEBM')


my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n") 
#print(class_list)

count=0    # count cars which satisfy both conditions

tracker=Tracker()

cy1=322    # line 1
cy2=360    # line 2

offset=6

vh_down={}    # dictionary to store id and location
counter=[]    # going down


vh_up={}      # dictionary to store id and location
counter1=[]   # going up

high_speed_cars = []


while True:    
    ret,frame = cap.read()           #  Reads the next frame from the video capture.
    if not ret:
        break
    count += 1
    if count % 3 != 0: 
        continue
    frame=cv2.resize(frame,(1020,500))       # Resizes the frame to a specific width and height using OpenCV's resize function.
   

    results=model.predict(frame)
    #print(results)                       # We have bounding box co-ordinates of rectangle [0,1,2,3]
                                          # We have confidence level [4] and class [5]

    a=results[0].boxes.data
    px=pd.DataFrame(a).astype("float")
    #print(px)
    list=[]
             
    for index,row in px.iterrows():
        #print(row)
         
 
        x1=int(row[0])                    # top left
        y1=int(row[1])                    # top right
        x2=int(row[2])                    # bottom left
        y2=int(row[3])                    # bottom right
        d=int(row[5])                     # class (car)
        c=class_list[d]
        if 'car' in c:
            list.append([x1,y1,x2,y2])
    bbox_id=tracker.update(list)
    for bbox in bbox_id:
        x3,y3,x4,y4,id=bbox
        cx=int(x3+x4)//2       #centre point of car x
        cy=int(y3+y4)//2       #centre point of car y
        
        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
        


        if cy1<(cy+offset) and cy1 > (cy-offset):      #condition for cy1 : car centre touches the line1  : generate ID and current time
           vh_down[id]=time.time()
        
        if id in vh_down:                              # if ID in our ductionary count only those
          
           if cy2<(cy+offset) and cy2 > (cy-offset):   #condition for cy2 : car centre touches the line2  : generate current position
             elapsed_time=time.time() - vh_down[id]    # current time(line2) - time at line 1
             if counter.count(id)==0:
                counter.append(id)
                distance = 10                               # dist between L1 and L2 meters 
                a_speed_ms = distance / elapsed_time        # calculate speed
                a_speed_kh = a_speed_ms * 3.6               # Km/Hr        
                cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                cv2.putText(frame,str(id),(x3,y3),cv2.FONT_HERSHEY_COMPLEX,0.6,(255,255,255),1)
                if a_speed_kh < 40:
                    cv2.putText(frame,str(int(a_speed_kh))+'Km/h',(x4,y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,0),2) # green text for speed < 25
                else:
                    cv2.putText(frame,str(int(a_speed_kh))+'Km/h',(x4,y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),2)  # Red Text
                    if id not in high_speed_cars:
                        high_speed_cars.append(id)
                    if a_speed_kh > 40:
                        with open("over_speeding_cars_ID.txt", "a") as f:       # create file to store IDS
                            f.write(str(id) + "\n")
            
        #####going UP#####     
        if cy2<(cy+offset) and cy2 > (cy-offset):          #condition for cy2 : car centre touches the line2  : generate ID and current time
           vh_up[id]=time.time()
        if id in vh_up:

           if cy1<(cy+offset) and cy1 > (cy-offset):
             elapsed1_time=time.time() - vh_up[id]

 


             if counter1.count(id)==0:
                counter1.append(id)      
                distance1 = 10 # meters
                a_speed_ms1 = distance1 / elapsed1_time
                a_speed_kh1 = a_speed_ms1 * 3.6
               
                cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                cv2.putText(frame,str(id),(x3,y3),cv2.FONT_HERSHEY_COMPLEX,0.6,(255,255,255),1)
                if a_speed_kh1 < 40:
                    cv2.putText(frame,str(int(a_speed_kh1))+'Km/h',(x4,y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,0),2) # green text
                else:
                    cv2.putText(frame,str(int(a_speed_kh1))+'Km/h',(x4,y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),2) # red text
                    if id not in high_speed_cars:
                        high_speed_cars.append(id)                    
                    
                    if a_speed_kh1 > 40:
                        with open("over_speeding_cars_ID.txt", "a") as f:
                            f.write(str(id) + "\n")

      

    cv2.line(frame,(100,cy1),(963,cy1),(255,255,255),1)

    cv2.putText(frame,('L1'),(100,320),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)


    cv2.line(frame,(10,cy2),(1019,cy2),(255,255,255),1)
 
    cv2.putText(frame,('L2'),(10,360),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
    d=(len(counter))
    u=(len(counter1))
    cv2.putText(frame,('goingdown:-')+str(d),(60,90),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

    cv2.putText(frame,('goingup:-')+str(u),(60,130),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
    

    
    cv2.imshow("RGB", frame)
    if cv2.waitKey(1)&0xFF==27:
        break
cap.release()
cv2.destroyAllWindows()