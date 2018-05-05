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
ROUND_NUM = 3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/upload', methods = ['POST'])
def upload_file():
	phone = request.form['phone']

	if 'image' in request.files:
		file = request.files['image']
		filename = secure_filename(file.filename)
		f = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file.save(f)
	else:
		filename = request.form['hidden']

	open_filename = 'uploads/' + filename

	"""
	image processing code
	"""

	im = Image.open(open_filename, 'r') # image that has lots of color 
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
	#predicted_power = clf.predict([[R/255, G/255, B/255]])[0]
	predicted_power = 0
	pixel_cnt = 0

	# select appropriate model
	if phone == 'gn5movie':
		clf = joblib.load('model/power_svm_gn5_movie.pkl')
	elif phone == 'pxldefault':
		clf = joblib.load('model/power_svm_pxl_default.pkl')
	elif phone == 'pxlpicture':
                clf = joblib.load('model/power_svm_pxl_picture.pkl')

	for i in end_pixels:
		tmp_power = clf.predict([[i[0]/255, i[1]/255, i[2]/255]])[0]
		predicted_power = predicted_power + tmp_power
		pixel_cnt = pixel_cnt + 1
	predicted_power = predicted_power / pixel_cnt
	#print(np.mean(median_pixels,axis=0))
	
	# pick n most used colors
	color_dict = {}
	for index, row in end.iterrows():
	    index = str(row['R'])+','+str(row['G'])+','+str(row['B'])
	    
	    if index in color_dict:
	        color_dict[index] = color_dict.get(index) + 1
	    else:
	        color_dict[index] = 1
        
	sorted_color_list = sorted(color_dict.items(), key=lambda x:x[1], reverse=True)

	colorUsage = []
	for i in range(0, 10):
		most = sorted_color_list[i]
		most_rgb = list(map(int, most[0].split(',')))
		mR = most_rgb[0]
		mG = most_rgb[1]
		mB = most_rgb[2]
		most_power = clf.predict([[mR/255, mG/255, mB/255]]) * most[1] / (x_delta * y_delta)
		most_ratio = (most_power / predicted_power * 100).round(ROUND_NUM)
		most_name = ("0x%0.2X" % mR) + ("0x%0.2X" % mG)[2:] + ("0x%0.2X" % mB)[2:]
		most_per = round(sorted_color_list[i][1] / (x_delta * y_delta) * 100, ROUND_NUM)

		most_power = most_power.round(ROUND_NUM)

		colorUsage.append([i, most_rgb, most_power, most_ratio, most_name, most_per])


	# RGBP
	# To send rounded R, G, B, Power value to index.html 
	# create parameter Red Green Blue, then send R,G,B value
	RGBP = [round(R, ROUND_NUM), round(G, ROUND_NUM), round(B, ROUND_NUM), round(predicted_power, ROUND_NUM)]



	# find similar colors

	# similar_color_list = [[[similar colors], num], [], ... []]
	# ex) [[[[0, 0, 0], [0, 2, 0]], 5], [[[255, 255, 255], [248, 255, 255]], 14]]

	similar_color_list = []

	for index in color_dict:
	    r = int(index.split(',')[0])
	    g = int(index.split(',')[1])
	    b = int(index.split(',')[2])
	    
	    similar = False
	    simIndex = 0
	    for mem in similar_color_list:
	        c = mem[0][0]
	        if abs(c[0] - r) + abs(c[1] - g) + abs(c[2] - b) < 10:
	            similar = True
	            break
	            
	        simIndex += 1
    
	    if similar:
	        similar_color_list[simIndex][0].append([r, g, b])
	        similar_color_list[simIndex][1] += color_dict[index]
	        similar_color_list[simIndex][2].append(color_dict[index])
	    else:
	        similar_color_list.append([[[r, g, b]], color_dict[index], [color_dict[index]]])

	similar_color_list.sort(key=lambda x:x[1], reverse=True)
	
	simColorUsage = []
	for i in range(0, 10):
		most = similar_color_list[i]

		most_srgb = []
		most_spower = 0
		most_sname = []
		most_sper = 0
		for j in range(len(most[0])):
			most_srgb.append(most[0][j])
			mR = most[0][j][0]
			mG = most[0][j][1]
			mB = most[0][j][2]
			most_spower += clf.predict([[mR/255, mG/255, mB/255]]) * most[2][j] / (x_delta * y_delta)
			most_sname.append(("0x%0.2X" % mR) + ("0x%0.2X" % mG)[2:] + ("0x%0.2X" % mB)[2:])

		most_sratio = most_spower / predicted_power * 100
		most_spower = most_spower.round(ROUND_NUM)
		most_sratio = most_sratio.round(ROUND_NUM)
		most_sper = round(similar_color_list[i][1] / (x_delta * y_delta) * 100, ROUND_NUM)

		simColorUsage.append([i, most_srgb, most_spower, most_sratio, most_sname, most_sper])

	#colorUsage.sort(key=lambda x:x[2], reverse=True)
	#simColorUsage.sort(key=lambda x:x[2], reverse=True)

	return render_template('index.html', phone = phone, filename = filename, RGBP = RGBP, colorUsage = colorUsage, simColorUsage = simColorUsage)

@app.route('/uploads/<filename>')
def send_file(filename):
	return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
	app.run(debug=True)
