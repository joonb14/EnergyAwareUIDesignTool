# Energy Aware UI Design Tool

This tool is designed for UI designers and App developers. <br/>
Who are not considering about Power Usage of Mobile device. <br/>
Today most Mobile devices uses OLED display. <br/>
OLED display's power usage is related to color of UI<br/>
To be simple, white based UIs are bad and black based UIs are good for Power saving<br/>

<hr/>
This work includes tutorials in my repository. <br/>
Somethings are for experiments before making UI tool <br/>
And somethings are included in the UI tool <br/>
followings are the projects that is used in UI tool<br/>
Python3_Monsoon_ADB: https://github.com/joonb14/Python3_Monsoon_ADB.git <br/>
Python3_Image_Clustering: https://github.com/joonb14/Python3_Image_Clustering.git <br/>
PowerUsageofPixelXL_SVM_modeling: https://github.com/joonb14/PowerUsageofPixelXL_SVM_modeling.git

<hr/>

## To run some of the special Features

to use option GreyScale Recovery, first download<br/>
colorize.lua<br/>
colornet.t7<br/>
from: https://github.com/satoshiiizuka/siggraph2016_colorization<br/>
<img width="800" src="https://user-images.githubusercontent.com/30307587/45686673-eb739600-bb87-11e8-9369-3520c51b4149.PNG">
then store these two files into model directory<br/>
<br/>

you might need to change the port number in app.py<br/>
run this by python app.py<br/>
not flask run!<br>
<br/>

<del>Test it in: http://css2.yonsei.ac.kr:13000<br/>

<hr/>

## IDEA: Current UIs are not Practical in Power Consumption Issue

<br/>

<img width="800" src="https://user-images.githubusercontent.com/30307587/45682521-71d5ab00-bb7b-11e8-9b2d-b4750a8ea0c3.JPG">
<img width="800" src="https://user-images.githubusercontent.com/30307587/45682528-74380500-bb7b-11e8-89fd-cc60962ac828.JPG">
<img width="800" src="https://user-images.githubusercontent.com/30307587/45682548-844fe480-bb7b-11e8-938c-0e86319a3186.JPG">

<hr/>

<br/>

## To achieve SVM model for Power estimation

<br/>
<img width="800" src="https://user-images.githubusercontent.com/30307587/45682644-d8f35f80-bb7b-11e8-80fb-3a296779e6b8.JPG">
<img width="800" src="https://user-images.githubusercontent.com/30307587/45682382-1b686c80-bb7b-11e8-9551-42cfbff5ad81.JPG">

<hr/>

<br/>

## UI Design Tool on flask

<br/>

<img width="800" src="https://user-images.githubusercontent.com/30307587/45682626-c711bc80-bb7b-11e8-99b1-635eaea5d0c0.JPG">
<img width="800" src="https://user-images.githubusercontent.com/30307587/45687009-7f456200-bb88-11e8-8bc2-591988086b34.JPG">

## Tried Methods to change UI colors
##### RGB Order reconstruction
<img width="800" src="https://user-images.githubusercontent.com/30307587/45687214-1c07ff80-bb89-11e8-951c-22acde1b8429.JPG">

##### Achromatic Invert
<img width="800" src="https://user-images.githubusercontent.com/30307587/45687215-1c07ff80-bb89-11e8-8225-61710098abf0.JPG">

##### GreyScale Recovery
from: https://github.com/satoshiiizuka/siggraph2016_colorization<br/>
<img width="800" src="https://user-images.githubusercontent.com/30307587/45686673-eb739600-bb87-11e8-9369-3520c51b4149.PNG">

# UI Tool Screenshot

<img width="800" src="https://user-images.githubusercontent.com/30307587/45687106-d0555600-bb88-11e8-995c-4f6a57078e85.PNG">

# Result
Probably not much of difference in power usage unless you give up the pretty UI<br/>
Such as using Achromatic Invert or Invert<br/>
Which is not a good idea for UI Designers<br/>
So Working on Ver.2 of UI Design Tool<br/>
