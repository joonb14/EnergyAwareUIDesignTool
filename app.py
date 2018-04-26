import os
from flask import Flask, request, render_template, send_from_directory, url_for
from werkzeug import secure_filename
from PIL import Image
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.externals import joblib
import pickle

#anaconda prompt: activate flask

UPLOAD_FOLDER = os.path.basename('uploads')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/upload', methods = ['POST'])



def upload_file():
	file = request.files['image']
	filename = secure_filename(file.filename)
	f = os.path.join(app.config['UPLOAD_FOLDER'], filename)

	file.save(f)

	"""
	image processing code
	"""

	open_filename = 'uploads/' + filename
	im = Image.open(open_filename, 'r') #image that has lots of color 
	# im = Image.open('City.jpg', 'r') # image that has lots of black

	x, y = im.size
	if y > x:
		im = im.rotate(90, expand=True)

	x, y = im.size
	x_delta = 64
	y_delta = 36
	counting_pixels = (x_delta*y_delta) # will be 2304 for almost all resolutions
	all_pixel = im.load()
	x_offset = x//x_delta
	y_offset = y//y_delta

	pixels = []
	for i in range(x_delta):
	    for j in range(y_delta):
	        pixels.append(all_pixel[(i+1)*x_offset-1,(j+1)*y_offset-1])
	        #print((i+1)*x_offset-1,(j+1)*y_offset-1)

	end_pixels = np.array(pixels)
	end = pd.DataFrame(pixels)
	end.rename(columns={0: 'R', 1: 'G', 2: 'B'}, inplace=True)

	"""
	all_pixel = im.load()
	x_offset = x//x_delta
	y_offset = y//y_delta
	pixels = []
	for i in range(x_delta):
	    for j in range(y_delta):
	        pixels.append(all_pixel[i*x_offset+x_offset//2,j*y_offset+y_offset//2])
	        #print(i*x_offset+x_offset//2,j*y_offset+y_offset//2)

	median_pixels = np.array(pixels)
	median = pd.DataFrame(pixels)
	median.rename(columns={0: 'R', 1: 'G', 2: 'B'}, inplace=True)
	"""

	R, G, B = np.mean(end_pixels, axis=0)
	#predicted_power = clf.predict([[R/255, G/255, B/255]])[0] + 200
	predicted_power = 0
	pixel_cnt = 0
	clf = joblib.load('model/power_svm.pkl')
	for i in end_pixels:
		tmp_power = clf.predict([[i[0]/255, i[1]/255, i[2]/255]])[0] + 200
		predicted_power = predicted_power + tmp_power
		pixel_cnt = pixel_cnt + 1
	predicted_power = predicted_power / pixel_cnt
	#print(np.mean(median_pixels,axis=0))
	
	# pick 3 most used colors

	color_dict = {}
	for index, row in end.iterrows():
	    index = str(row['R'])+','+str(row['G'])+','+str(row['B'])
	    #print(index)
	    if index in color_dict:
	        color_dict[index] = color_dict.get(index) + 1
	    else:
	        color_dict[index] = 1
        
	sorted_color_list = sorted(color_dict.items(), key=lambda x:x[1], reverse=True)

	most, most_string, most_power, most_ratio, most_name, most_per = [], [], [], [], [], []
	for i in range(0, 10):
		most.append(sorted_color_list[i])
		most_string.append(list(map(int, most[i][0].split(','))))
		mR = most_string[i][0]
		mG = most_string[i][1]
		mB = most_string[i][2]
		most_power.append(((clf.predict([[mR/255, mG/255, mB/255]]) + 200) * most[i][1] / (x_delta * y_delta)).round(2))
		most_ratio.append((most_power[i] / predicted_power * 100).round(2))
		most_name.append(("0x%0.2X" % mR) + ("0x%0.2X" % mG)[2:] + ("0x%0.2X" % mB)[2:])
		most_per.append(round(sorted_color_list[i][1] / (x_delta * y_delta) * 100, 2))

	# ABCD
	# To send R. G. B value to index.html 
	# create parameter Red Green Blue, then send R,G,B value
	colorUsage = []
	for i in range(0, 10):
		colorUsage.append([i, most_string[i], most_power[i], most_ratio[i], most_name[i], most_per[i]])

	return render_template('index.html', filename = filename ,Red = round(R, 2), Green = round(G, 2), Blue = round(B, 2), Power = round(predicted_power, 2), colorUsage = colorUsage)

@app.route('/uploads/<filename>')
def send_file(filename):
	return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
	app.run(debug=True)
