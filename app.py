import os
import urllib
import uuid
import tensorflow as tf
import tensorflow_hub as hub

from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing.image import load_img , img_to_array


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = tf.keras.models.load_model(os.path.join(BASE_DIR , 'klasifikasi_makanan2.h5'), custom_objects={'KerasLayer':hub.KerasLayer})

ALLOWED_EXT = set(['jpg' , 'jpeg' , 'png' , 'jfif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT

classes = ['Bakso' ,'Cheesecake', 'Chicken Wings' , 'Churros' , 'Donuts' ,'Egg' ,'French fries', 'Fried rice' ,'Gado Gado' ,'Hamburger', 'Hot dog', 'Mac and Cheese', 'Pancakes', 'Pizza', 'Rendang', 'Sate', 'Soup', 'Spaghetti', 'Sushi', 'Takoyaki', 'Waffles']
calorie = ['218', '228', '458', '116', '198', '70', '196', '350', '132', '325', '242', '290', '100', '250', '193', '80', '70', '200', '150', '200', '150']

def predict(filename , model):
	img = tf.keras.preprocessing.image.load_img(filename , target_size = (224 , 224))
	img = tf.keras.preprocessing.image.img_to_array(img)
	img = img.reshape(1 , 224 ,224 ,3)

	img = img.astype('float32')
	img = img/255.0
	result = model.predict(img)

	dict_result = {}
	dict_calorie = {}

	for i in range(21):
		dict_result[result[0][i]] = classes[i]
		dict_calorie[result[0][i]] = calorie[i]

	res = result[0]
	res.sort()
	res = res[::-1]
	prob = res[:3]
    
	prob_result = []
	class_result = []
	calorie_result = []
	for i in range(3):
		prob_result.append((prob[i]*100).round(2))
		class_result.append(dict_result[prob[i]])
		calorie_result.append(dict_calorie[prob[i]])

	return class_result, prob_result, calorie_result


@app.route("/")
# @app.route("/index")
def home():
	return render_template("index.html")

@app.route("/success", methods=['GET','POST'])
def success():
	error = ''
	target_img = os.path.join(os.getcwd() , 'static/images')
	if request.method == 'POST':
		if(request.form):
			link = request.form.get('link')
			try :
				resource = urllib.request.urlopen(link)
				unique_filename = str(uuid.uuid4())
				filename = unique_filename+".jpg"
				img_path = os.path.join(target_img , filename)
				output = open(img_path , "wb")
				output.write(resource.read())
				output.close()
				img = filename

				class_result , prob_result, calorie_result = predict(img_path , model)

				predictions = {
                      "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
						"calorie": calorie_result[0]
                }

			except Exception as e : 
				print(str(e))
				error = 'This image from this site is not accesible or inappropriate input'

			if(len(error) == 0):
				return  render_template('success.html' , img  = img , predictions = predictions)
			else:
				return render_template('index.html' , error = error) 

            
		elif (request.files):
			file = request.files['file']
			if file and allowed_file(file.filename):
				file.save(os.path.join(target_img , file.filename))
				img_path = os.path.join(target_img , file.filename)
				img = file.filename

				class_result , prob_result, calorie_result = predict(img_path , model)

				predictions = {
                      "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
						"calorie": calorie_result[0]
                }

			else:
				error = "Please upload images of jpg , jpeg and png extension only"

			if(len(error) == 0):
				return  render_template('success.html' , img  = img , predictions = predictions)
			else:
				return render_template('index.html' , error = error)

	else:
		return render_template('index.html')




if __name__ == '__main__':
	app.run(debug=True)