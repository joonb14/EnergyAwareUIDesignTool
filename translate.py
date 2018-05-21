from PIL import Image
import numpy as np
import pandas as pd
import subprocess

def toPixels(im):
	x, y = im.size
	x_delta = 36
	y_delta = 64
	counting_pixels = (x_delta*y_delta) # will be 2304 for almost all resolutions
	all_pixel = im.load()
	x_offset = x//x_delta
	y_offset = y//y_delta

	pixels = []
	for i in range(x_delta):
	    for j in range(y_delta):
	        pixels.append(all_pixel[(i+1)*x_offset-1,(j+1)*y_offset-1])

	return pixels

def toEndPixels(im):
	pixels = toPixels(im)
	end_pixels = np.array(pixels)

	return end_pixels

def toEnd(im):
	pixels = toPixels(im)
	end = pd.DataFrame(pixels)
	end.rename(columns={0: 'R', 1: 'G', 2: 'B'}, inplace=True)

	return end

def PredictedPower(im, clf):
	end_pixels = toEndPixels(im)

	R, G, B = np.mean(end_pixels, axis=0)

	predicted_power = 0
	pixel_cnt = 0

	for i in end_pixels:
		tmp_power = clf.predict([[i[0]/255, i[1]/255, i[2]/255]])[0]
		predicted_power += tmp_power
		pixel_cnt += 1
	predicted_power /= pixel_cnt

	return predicted_power

def RGBOrder(im, end):
	#minimum difference to count number
	Diff = 10

	#initialize
	Red_num,Green_num, Blue_num = 0, 0, 0

	for index, row in end.iterrows():
		if int(row['R']) > (int(row['G']) + Diff) and int(row['R']) > (int(row['B']) + Diff):
			Red_num+=1
		elif int(row['B']) > (int(row['G']) + Diff) and int(row['B']) > (int(row['R']) + Diff):
			Blue_num+=1
		elif int(row['G']) > (int(row['B']) + Diff) and int(row['G']) > (int(row['R']) + Diff):
			Green_num+=1


	r, g, b = im.split()
	        
	if Red_num >= Blue_num and Blue_num >= Green_num:
	    out = Image.merge("RGB", (r, b, g))
	elif Red_num >= Green_num and Green_num >= Blue_num:
	    out = Image.merge("RGB", (r, g, b))
	elif Green_num >= Blue_num and Blue_num >= Red_num:
	    out = Image.merge("RGB", (g, b, r))
	elif Green_num >= Red_num and Red_num >= Blue_num:
	    out = Image.merge("RGB", (g, r, b))
	elif Blue_num >= Red_num and Red_num >= Green_num:
	    out = Image.merge("RGB", (b, r, g))
	elif Blue_num >= Green_num and Green_num >= Red_num:
	    out = Image.merge("RGB", (b, g, r))

	return out

def GreyScale(im):
	greyscale = im.convert("L")
	grey_arr = greyscale.split()
	#Don't know why but need these 
	#grey scale images have only one value not rgb
	#grey_arr[0] is image! not like ones above
	greyscale = Image.merge("RGB", (grey_arr[0], grey_arr[0], grey_arr[0]))
	
	return greyscale

def Inverted(im, end):
	inverted_end = 255 - end

	#minimum difference to count number
	Diff = 10

	#initialize
	Red_num,Green_num, Blue_num = 0, 0, 0

	for index, row in inverted_end.iterrows():
	    if int(row['R']) > (int(row['G']) + Diff) and int(row['R']) > (int(row['B']) + Diff):
	        Red_num+=1
	    elif int(row['B']) > (int(row['G']) + Diff) and int(row['B']) > (int(row['R']) + Diff):
	        Blue_num+=1
	    elif int(row['G']) > (int(row['B']) + Diff) and int(row['G']) > (int(row['R']) + Diff):
	        Green_num+=1
	        
	print(Red_num, Blue_num, Green_num)

	inverted_im = im.point(lambda i: 255 - i)
	r, g, b = inverted_im.split()
	        
	if Red_num >= Blue_num and Blue_num >= Green_num:
	    out = Image.merge("RGB", (r, b, g))
	elif Red_num >= Green_num and Green_num >= Blue_num:
	    out = Image.merge("RGB", (r, g, b))
	elif Green_num >= Blue_num and Blue_num >= Red_num:
	    out = Image.merge("RGB", (g, b, r))
	elif Green_num >= Red_num and Red_num >= Blue_num:
	    out = Image.merge("RGB", (g, r, b))
	elif Blue_num >= Red_num and Red_num >= Green_num:
	    out = Image.merge("RGB", (b, r, g))
	elif Blue_num >= Green_num and Green_num >= Red_num:
	    out = Image.merge("RGB", (b, g, r))

	return out

def GreyRecovery(im):
        out = GreyScale(im)
        out.save("uploads/greyscale_temp.jpg")

        model_path="model/colorize.lua"
        set_path="model/colornet.t7"
        inputfilename = "uploads/greyscale_temp.jpg"
        outfilename = "uploads/translated_image.jpg"

        subprocess.call(["th",model_path,inputfilename,outfilename,set_path])
        out = Image.open("uploads/translated_image.jpg", "r")

        return out

def AchromaticInvert(im):
	out = im
	width, height = im.size
	# Process every pixel
	for x in range(width):
	    for y in range(height):
	        cur = im.getpixel((x,y))
	        if (abs(cur[0] - cur[1]) < 16) and (abs(cur[0] - cur[2])) < 16 and (abs(cur[1] - cur[2])) < 16:
	            new = (255 - cur[0], 255 - cur[1], 255 - cur[2])
	        else:
	            new2 = cur
	        out.putpixel((x,y), new)

	return out