import os
from flask import Flask, request, render_template, send_from_directory, url_for
from werkzeug import secure_filename
from PIL import Image
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.externals import joblib
import pickle
import translate as tr

#anaconda prompt: activate flask

UPLOAD_FOLDER = os.path.basename('uploads')
ROUND_NUM = 3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def toRound(arg):
	return round(arg, ROUND_NUM)

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/upload', methods = ['POST'])
def upload_file():
	phone = request.form['phone']
	translate = request.form['translate']
	if 'list_num' in request.form:
		list_num = request.form['list_num']
	else:
		list_num = 10
	if 'mc' in request.form:
		mc = request.form['mc']
	else:
		mc = None

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

	x_delta = 36
	y_delta = 64

	# select appropriate model
	if phone == 'gn5movie':
		clf = joblib.load('model/power_svm_gn5_movie.pkl')
	elif phone == 'pxldefault':
		clf = joblib.load('model/power_svm_pxl_default.pkl')
	elif phone == 'pxlpicture':
		clf = joblib.load('model/power_svm_pxl_picture.pkl')

	predicted_power = tr.PredictedPower(im, clf)
	end = tr.toEnd(im)
	end_pixels = tr.toEndPixels(im)
	R, G, B = np.mean(end_pixels, axis=0)
	
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
	for i in range(int(list_num)):
		most = sorted_color_list[i]
		most_rgb = list(map(int, most[0].split(',')))
		mR = most_rgb[0]
		mG = most_rgb[1]
		mB = most_rgb[2]
		most_power = clf.predict([[mR/255, mG/255, mB/255]]) * most[1] / (x_delta * y_delta)
		most_ratio = (most_power / predicted_power * 100).round(ROUND_NUM)
		most_name = ("0x%0.2X" % mR) + ("0x%0.2X" % mG)[2:] + ("0x%0.2X" % mB)[2:]
		most_per = toRound(sorted_color_list[i][1] / (x_delta * y_delta) * 100)

		most_power = most_power.round(ROUND_NUM)

		colorUsage.append([i, most_rgb, most_power, most_ratio[0], most_name, most_per])


	# RGBP
	# To send rounded R, G, B, Power value to index.html 
	# create parameter Red Green Blue, then send R,G,B value
	RGBP = [toRound(R), toRound(G), toRound(B), toRound(predicted_power)]



	# find similar colors

	# similar_color_list = [[[similar colors], num], [], ... []]
	# ex) [[[[0, 0, 0], [0, 2, 0]], 5], [[[255, 255, 255], [248, 255, 255]], 14]]

	similar_color_list = []
	similar_color_num = []

	for index in color_dict:
	    r = int(index.split(',')[0])
	    g = int(index.split(',')[1])
	    b = int(index.split(',')[2])
	    
	    similar = False
	    simIndex = 0
	    for mem in similar_color_list:
	        c = mem[3][0]
	        if abs(c[0] - r) + abs(c[1] - g) + abs(c[2] - b) < 10:
	            similar = True
	            break
	            
	        simIndex += 1
    
	    if similar:
	        similar_color_list[simIndex][0].append([r, g, b])
	        similar_color_list[simIndex][1] += color_dict[index]
	        similar_color_list[simIndex][2].append(color_dict[index])
	        
	        new = similar_color_list[simIndex][3][0]
	        new[0] = (new[0]*similar_color_num[simIndex]+r)/(similar_color_num[simIndex]+1)
	        new[1] = (new[1]*similar_color_num[simIndex]+g)/(similar_color_num[simIndex]+1)
	        new[2] = (new[2]*similar_color_num[simIndex]+b)/(similar_color_num[simIndex]+1)
	        similar_color_list[simIndex][3].append(new)
	        del similar_color_list[simIndex][3][0]
	        similar_color_num[simIndex] += 1
	        
            
	    else:
	        similar_color_list.append([[[r, g, b]], color_dict[index], [color_dict[index]], [[r, g, b]]])
	        similar_color_num.append(1)

	similar_color_list.sort(key=lambda x:x[1], reverse=True)
	
	simColorUsage = []
	for i in range(min(int(list_num), len(similar_color_list))):
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
		most_sper = toRound(similar_color_list[i][1] / (x_delta * y_delta) * 100)

		simColorUsage.append([i, most_srgb, most_spower, most_sratio, most_sname, most_sper])

	#colorUsage.sort(key=lambda x:x[2], reverse=True)
	#simColorUsage.sort(key=lambda x:x[2], reverse=True)

	'''
	Recommended Image
	'''

	if translate == "rgborder":
		trImage = tr.RGBOrder(im, end)
	elif translate == "greyscale":
		trImage = tr.GreyScale(im)
	elif translate == "inverted":
		trImage = tr.Inverted(im, end)

	trImage.save("uploads/translated_image.jpg");

	trPower = tr.PredictedPower(trImage, clf)
	trRate = (predicted_power - trPower) / predicted_power * 100

	trInfo = [toRound(trPower), toRound(trRate)]

	list_max = len(sorted_color_list)
	simlist_max = len(similar_color_list)
	check = [phone, translate, list_num, list_max, simlist_max, mc]

	return render_template('index.html', check = check, filename = filename, RGBP = RGBP, colorUsage = colorUsage, simColorUsage = simColorUsage, trInfo = trInfo)

@app.route('/uploads/<filename>')
def send_file(filename):
	return send_from_directory(UPLOAD_FOLDER, filename)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

if __name__ == '__main__':
	app.run(debug=True)
