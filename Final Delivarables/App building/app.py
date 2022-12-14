from flask import *
from datetime import date
import ibm_db
from flask import Flask, render_template, request
import numpy as np
import operator 
import cv2 # opencv library
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import load_img, img_to_array
from werkzeug.utils import secure_filename

app = Flask(__name__,template_folder="templates") 
model=load_model('gesture.h5')
print("Loaded model from disk")
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32733;SECURITY=SSL;PROTOCOL=TCPIP;UID=mml48790;PWD=dMMqquglkWltg4Jo", "", "")
print(conn)
print("Connecting Successful............")
user_id=0

@app.route("/", methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template("index.html",status="",colour="red")
    elif request.method=='POST':
        global retailer_id
        email=request.form["email"]
        password=request.form["password"]
        query = '''select * from user where email = \'{}\''''.format(email)
        exec_query = ibm_db.exec_immediate(conn, query)
        row = ibm_db.fetch_both(exec_query)
        if(row is not False):
            if(row['PASSWORD'] != password):
                return render_template("index.html",status="Invalid Password",colour="red")
            else:
                temp='''select id from user where email = \'{}\''''.format(email)
                exec_query = ibm_db.exec_immediate(conn, temp)
                dict= ibm_db.fetch_both(exec_query)
                user_id=dict["ID"]
                return render_template("home.html")

        return render_template("index.html",status="Invalid Email",colour="red")

@app.route("/signup", methods=['GET','POST'])
def signup():
    
    if request.method=='GET':
        return render_template("register.html",status="",colour="red")
    elif request.method=='POST':
        email=request.form["email"]
        password=request.form["password"]
        username=request.form["username"]
        query = '''select * from user where email = \'{}\''''.format(email)
        exec_query = ibm_db.exec_immediate(conn, query)
        row = ibm_db.fetch_both(exec_query)
        if(row is False):
            query = '''insert into user(email, password, username) values('{}', '{}', '{}')'''.format(email, password, username)
            exec_query = ibm_db.exec_immediate(conn, query)
            return render_template("index.html",status="Signup Success",colour="green")
        else:
            return render_template("register.html",status="User Already Exists",colour="red")
 
@app.route('/home') # routes to the intro page 
def home():
    return render_template('home.html') #rendering the intro page


@app.route('/intro') # routes to the intro page 
def intro():
    return render_template('intro.html') #rendering the intro page


@app.route('/image1',methods=['GET', 'POST']) # routes to the index html 
def index6():
    return render_template("index6.html")

@app.route('/predict', methods=['GET', 'POST'])  # route to show the predictions in a web UI
def launch():
    #Getting input and storing it
    if request.method == 'POST':
        print('inside launch function')
        f=request.files['image']

        basepath=os.path.dirname(__file__)
        file_path=os.path.join(basepath,'uploads',secure_filename(f.filename))
        f.save(file_path)
        print('img saved successfully')
        print(file_path)
        # test_image=cv2.imread(file_path,cv2.IMREAD_COLOR)
        # test_image=cv2.resize(test_image,(64,64))
        # result= model.predict(test_image.reshape(1,64,64,1))

        # img = load_img(file_path, grayscale=True, target_size=(64, 64))
        # x = img_to_array(img)
        # x = np.expand_dims(x, axis = 0)

    cap=cv2.VideoCapture(0)
    image1=cv2.imread(file_path)
    cv2.imshow("Output",image1)
    prev='NULL'
    while True:
        _, frame=cap.read()
        frame=cv2.flip(frame,1)

        x1=int(0.5*frame.shape[1])
        y1=10
        x2=frame.shape[1]-10
        y2=int(0.5*frame.shape[1])

        cv2.rectangle(frame,(x1-1,y1-1),(x2+1,y2+1),(255,0,0)),1
        roi = frame[y1:y2,x1:x2]

        roi=cv2.resize(roi,(64,64))
        roi=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
        _, test_image=cv2.threshold(roi,120,255,cv2.THRESH_BINARY)
        ##cv2.imshow("test",test_image)

        result = model.predict(test_image.reshape(1,64,64,1))
        print(result)
        prediction = {'ZERO':result[0][0],'ONE':result[0][1],'TWO':result[0][2],'THREE':result[0][3],'FOUR':result[0][4],'FIVE':result[0][5]}
        prediction=sorted(prediction.items(),key=operator.itemgetter(1),reverse=True)

        cv2.putText(frame,prediction[0][0],(10,120), cv2.FONT_HERSHEY_PLAIN,1,(0,255,255),1)
        cv2.imshow("frame",frame)


        interrupt=cv2.waitKey(10)
        if interrupt & 0xFF == 27: #Esc key to break from the while loop
            break
        
        if prev == prediction:
                continue

        prev = prediction


        image1=cv2.imread(file_path)
        image1=cv2.resize(image1,(255,255))
        if prediction[0][0]=='ONE':
            resized=cv2.resize(image1,(200,200))
            cv2.destroyWindow("Output")            
            cv2.imshow("Output",resized)
##            key=cv2.waitKey(3000)
##
##            if(key & 0xFF) == ord("1"):
##                cv2.destroyWindow("Fixed Resizing - One")

        elif prediction[0][0]=='ZERO':
            cv2.rectangle(image1,(480,170),(650,420),(0,0,255),2)
            cv2.destroyWindow("Output")            
            cv2.imshow("Output",image1)
            #cv2.imshow("Rectangle - Zero",image1)
            #cv2.waitKey(0)
##            key=cv2.waitKey(3000)
##
##            if(key & 0xFF)==ord("0"):
##             cv2.destroyWindow("Rectangle - Zero")

        elif prediction[0][0]=='TWO':
            (h,w,d)=image1.shape
            center=(w//2,h//2)
            M=cv2.getRotationMatrix2D(center,-45,1.0)
            rotated=cv2.warpAffine(image1,M,(w,h))
            cv2.destroyWindow("Output")            
            cv2.imshow("Output",rotated)
##            cv2.imshow("OpenCV Rotation - Two",rotated)
##            key=cv2.waitKey(3000)
##            if(key & 0xFF)==ord("2"):
##                cv2.destroyWindow("OpenCV Rotation - Two")

        elif prediction[0][0]=='THREE':
            blurred=cv2.GaussianBlur(image1,(11,11),0)
            cv2.destroyWindow("Output")            
            cv2.imshow("Output",blurred)
##            cv2.imshow("Blurred - Three",blurred)
##            key=cv2.waitKey(3000)
##            if(key & 0xFF)==ord("3"):
##                cv2.destroyWindow("Blurred - Three")

        elif prediction[0][0]=='FOUR':
            zoomed=cv2.resize(image1,(400,400))
            cv2.destroyWindow("Output")            
            cv2.imshow("Output",zoomed)
##            cv2.imshow("Zoomed - Four",zoomed)
##            key=cv2.waitKey(3000)
##            if(key & 0xFF)==ord("4"):
##                cv2.destroyWindow("Zoomed - Four")

        elif prediction[0][0]=='FIVE':
            neg=255-image1
            cv2.destroyWindow("Output")            
            cv2.imshow("Output",neg)
##            cv2.imshow("Negative - Five",neg)
##            key=cv2.waitKey(3000)
##            if(key & 0xFF)==ord("5"):
##                cv2.destroyWindow("Negative - Five")

        else:
            continue


    cap.release()
    cv2.destroyAllWindows()

    return render_template("home.html")

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
