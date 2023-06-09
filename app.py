import cv2 #เรียกใช้ open cv
import streamlit as st #เรียกใช้ streamlit เพื่อใช้ในการเขียนเว็บไซต์
import pandas as pd #เรียกใช้ pandas ไลบรารี Python แบบ open-source ที่มีเครื่องมือจัดการและวิเคราะห์ข้อมูลประสิทธิภาพสูงโดยใช้โครงสร้างข้อมูลที่
import numpy as np #เรียกใช้ไลบารี่ numpy เพื่อช่วยในการคำนวนอาเรย์
from PIL import Image #เรียกใช้ไลบารี่ Pillow 
from datetime import datetime #เรียกใช้ datetime เพื่อกำหนดเวลาที่ใช้งาน ณ เวลานั้น
from deta import Deta  # pip install deta


TOKEN = "c0pkmexkqcy_1fdytr6rdvyW6TyGjr9qR7w6VEk5E2qu" #tokendeta
# Initialize with a project key
deta = Deta(TOKEN)
# This is how to create/connect a database
db = deta.Base("imagesdata") 

def insert_imagesdata(add_name, gender, age, user_time): #กำหนดตัวแปรเพื่อรับค่าที่จะนำไปเก็บใน table
    """Returns the report on a successful creation, otherwise raises an error""" #ส่งกลับรายงานเกี่ยวกับการสร้างที่สำเร็จ มิฉะนั้น จะทำให้เกิดข้อผิดพลาด
    return db.put({"key": add_name, "gender": gender, "age": age, "datetime": user_time})


def fetch_all_imagesdata():  #ส่งคืน dict ของ imagesdata ทั้งหมด
    """Returns a dict of all imagesdata""" 
    res = db.fetch() 
    return res.items


def get_imagesdata(imagesdata): #หากไม่พบ ฟังก์ชันจะคืนค่า None
    """If not found, the function will return None"""
    return db.get(imagesdata)

class Detectface(): #เขียนอยู่ในรูปแบบ oop โดยการเรียกใช้ฟังก์ชั่น
    def get_face_box(net, frame, conf_threshold=0.7):#โค๊ด Python สำหรับการตรวจจับใบหน้า ตั้งแต่ 32-50
        opencv_dnn_frame = frame.copy()
        frame_height = opencv_dnn_frame.shape[0]
        frame_width = opencv_dnn_frame.shape[1]
        blob_img = cv2.dnn.blobFromImage(opencv_dnn_frame, 1.0, (300, 300), [104, 117, 123], True, False)

        net.setInput(blob_img)
        detections = net.forward()
        b_boxes_detect = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold:
                x1 = int(detections[0, 0, i, 3] * frame_width)
                y1 = int(detections[0, 0, i, 4] * frame_height)
                x2 = int(detections[0, 0, i, 5] * frame_width)
                y2 = int(detections[0, 0, i, 6] * frame_height)
                b_boxes_detect.append([x1, y1, x2, y2])
                cv2.rectangle(opencv_dnn_frame, (x1, y1), (x2, y2), (0, 255, 0), int(round(frame_height / 150)), 8)
        return opencv_dnn_frame, b_boxes_detect

st.write("# Age and Gender prediction "+":robot_face:") #โชว์ข้อความการทำนายอายุและเพศ และอีโมจิ🌟
st.write("### Upload a picture that contains a face "+":camera:") #อัปโหลดรูปภาพที่มีใบหน้า และอีโมจิ📷

bytes_data = None #กำหนดให้ bytes_data ให้เป็นค่าว่าง
input_mode = st.radio("# Input mode", ["Camera", "File upload"]) #กำหนดให้สามารถเลือกได้ว่าจะใช้ กล้อง หรือ อัพโหลดรูปภาพ

if input_mode == "Camera": #เรียกใช้กล้อง
    img_file_buffer = st.camera_input("Take a picture")
    photo = img_file_buffer #กำหนดตัวแปลให้ photo เป็น img_file_buffer
    if img_file_buffer is not None:
        bytes_data = img_file_buffer.getvalue() #จากนั้นทำหนดให้ img_file_buffer ไปเก็บไว้ใน bytes_data
else:
    uploaded_file = st.file_uploader("อัพโหลดรูปภาพ", type=['png', 'jpg']) #กำหนดไฟล์ภาพ png และ jpg
    photo = uploaded_file # กำหนดตัวแปลให้ photo เป็น uploaded_file
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue() #จากนั้นทำหนดให้ uploaded_file ไปเก็บไว้ใน bytes_data
if bytes_data is None: #กำหนดให้ bytes_data ต้องมีตัวแปรอะไรสักอย่างถึงจะสั่งให้หยุด
    st.stop()
    
if photo: #เงื่อนไขรูปภาพ
    image = Image.open(photo) #เปิดใช้ photo
    cap = np.array(image) #กำหนดให้ cap = อาเรย์ของรูปภาพ
    cv2.imwrite('temp.jpg', cv2.cvtColor(cap, cv2.COLOR_BGR2GRAY)) #นำข้อมูลภาพจากอาเรย์มาบันทึกลงในไฟล์ , การนั้นทำเปลี่ยนรูปแบบสีให้เป็นแบบขาวเทาดำ
    cap=cv2.imread('temp.jpg')

    #78-85 เรียกใช้ข้อมูลมาเก็บไว้ในตัวแแปล เพื่อให้ใช้งานได้สะดวกขึ้น
    face_txt_path="opencv_face_detector.pbtxt"
    face_model_path="opencv_face_detector_uint8.pb"

    age_txt_path="age_deploy.prototxt"  #ไฟล์ที่ลงท้ายด้วย .prototxt ไฟล์นี้กำหนดเลเยอร์ในโครงข่ายประสาทเทียม อินพุต เอาต์พุต และฟังก์ชันของแต่ละเลเยอร์ 81 และ 82 #ไฟล์ CNN ที่ช่วย แยกอายุ
    age_model_path="age_net.caffemodel"

    gender_txt_path="gender_deploy.prototxt" #ไฟล์ CNN ที่ช่วย แยกเพศ
    gender_model_path="gender_net.caffemodel"
    #สร้าง 3 รายการแยกกันสำหรับจัดเก็บ Model_Mean_Values, Age และ Gender 87 - 89
    MODEL_MEAN_VALUES=(78.4263377603, 87.7689143744, 114.895847746)
    age_classes=['Age: ~1-2', 'Age: ~3-5', 'Age: ~6-14', 'Age: ~16-22', 'Age: ~23-30', 'Age: ~31-40', 'Age: ~41-50', 'Age: Greater than 50']
    gender_classes = ['Male', 'Female']

    age_net = cv2.dnn.readNet(age_model_path, age_txt_path) #cv2.dnn.readNet ทำการโหลดอัลกอริทึม จากไฟล์ age_net.caffemodel และ age_deploy.prototxt มาเก็บใน ageNet
    gender_net = cv2.dnn.readNet(gender_model_path, gender_txt_path) #cv2.dnn.readNet ทำการโหลดอัลกอริทึม จากไฟล์ gender_net.caffemodel และ gender_deploy.prototxt มาเก็บใน genderNet
    face_net = cv2.dnn.readNet(face_model_path, face_txt_path) #cv2.dnn.readNet ทำการโหลดอัลกอริทึม จากไฟล์ opencv_face_detector_uint8.pb และ opencv_face_detector.pbtxt มาเก็บใน faceNet

    padding = 20 #Padding กำหนดขอบในที่นี้กำหนดให้เท่ากับ 20 Pixels
    frameFace, b_boxes = Detectface.get_face_box(face_net, cap) #Detectface เรียกใช้ฟังก์ชั่น highlightFace นอกคลาส
    
    if not b_boxes: #กำหนดให้เงื่อนไขแสดงข้อความว่าไม่พบใบหน้าเมื่อตรวจไม่พบใบหน้า
        st.write("ไม่พบใบหน้าที่กำลังตรวจสอบ")

    for bbox in b_boxes: #กรอบใบหน้า
        face = cap[max(0, bbox[1] - padding): min(bbox[3] + padding, cap.shape[0] - 1), max(0, bbox[0] - padding): min(bbox[2] + padding, cap.shape[1] - 1)]
        blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
        gender_net.setInput(blob) #ทำนายเพศที่คาดการ ตั้งแต่บรรทัดที่ 104-107
        gender_pred_list = gender_net.forward()
        gender = gender_classes[gender_pred_list[0].argmax()]
        st.write(f"Gender : {gender}, [Confidence = {gender_pred_list[0].max() * 100:.3f}%]")

        age_net.setInput(blob) #ทำนายอายุที่คาดการ ตั้งแต่บรรทัดที่ 109-112
        age_pred_list = age_net.forward()
        age = age_classes[age_pred_list[0].argmax()]
        st.write(f"{age}, [Confidence = {age_pred_list[0].max() * 100:.3f}%]")

        label = "{}, {}".format(gender, age)
        cv2.putText(
            frameFace,
            label,
            (bbox[0],
            bbox[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA) #cv2.putText ระบุตำแน่งอักษรหรือข้อความที่จะเขียน
        
        st.image(frameFace) #โชว์รูปภาพที่มีการตรวจสอบผ่านเว็ป
        st.sidebar.header("บันทึกข้อมูลลงในฐานข้อมูล")
        
        df = pd.read_csv("data/test.csv") #กำหนดเส้นทางให้ df
        st.sidebar.table(df) #โชว์ตารางออกมา
        options_form = st.sidebar.form("options_form") #กำหนดตัวเลือก
        add_name = options_form.text_input("โปรดใส่ชื่อของคุณ") #กำหนดกล่องข้อความให้รับค่า ชื่อ
        now = datetime.now() #เซ็ตค่าให้เป็นเวลาปัจจุบัน
        user_time = now.strftime("%H:%M:%S") #กำหนด ชั่วโมง นาที วินาที
        add_data = options_form.form_submit_button("บันทึกข้อมูล") #กำหนดปุ่มบันทึก

        if add_data: #กำหนดให้ทำการบันทึกข้อมูลไปยัง CSV
            new_data = {"name": add_name , "gender": gender ,"age": age ,"time": user_time} #กำหนดให้บันทึกคอลัมน์
            df = df.append(new_data, ignore_index = True)
            df.to_csv("data/test.csv" , index = False)
            insert_imagesdata(add_name,gender,age,user_time) #รับค่าไปเก็บใน ฐานข้อมูลใน Deta
            st.sidebar.header("บันทึกข้อมูลสำเร็จ")  #แสดงข้อความทางแถบซ้าย
            
        im_pil = Image.fromarray(frameFace) #แปลงอาร์เรย์ numpy เป็น PIL Image
        im_pil.save('result.jpeg') #บันทึกรูปผลลัพธ์ลงได้ฐานข้อมูล
        with open("result.jpeg", "rb") as file: #เปิดรูป Result.jpeg เพื่อใช้ในการกำหนดปุ่มโหลดภาพ
                btn = st.download_button( #กำหนดปุ่มโหลดภาพ
                        label="ดาวน์โหลดรูปภาพ", #กำหนดตัวอักษรในปุ่ม
                        data=file, #กำหนดให้ data มีค่าเท่ากับ file
                        file_name="image_test.jpeg", #กำหนดชื่อภาพ
                    )
                if btn : #กำหนดเงื่อนไข ถ้าทำการกดให้แสดงข้อความว่า ดาวน์โหลดสำเร็จ
                    st.write('ดาวน์โหลดสำเร็จ')
                else : #ถ้าไม่มีการกดปุ่มให้แสดงข้อความว่า คุณยังไม่ได้ทำการดาวน์โหลดรูปภาพ
                    st.write("คุณยังไม่ได้ทำการดาวน์โหลดรูปภาพ")
                    
        if add_data is not None : #กำหนดให้แสดงข้อความเมื่อกดปุ่ม หน้ากลาง
            st.write('------------------------------------------------------------------------------------')
            st.write('กราฟเพศและอายุของผู้ใช้งานทั้งหมด')
            df2 = df.filter(regex= '(gender|age)', axis=1) #กำหนดให้แสดงแค่ตอลัมน์ เพศและอายุ ให้อยู่ในตัวแปร df2
            st.line_chart(df2) #กำหนดให้แสดงกราฟ