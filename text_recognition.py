from imutils.object_detection import non_max_suppression
import numpy as np
import pytesseract
import argparse
import cv2
import os
import base64

def decode_predictions(scores, geometry, min_confidence):
	# grab 
	(numRows, numCols) = scores.shape[2:4]
	rects = []
	confidences = []

	# loop 
	for y in range(0, numRows):
		# extract
		scoresData = scores[0, 0, y]
		xData0 = geometry[0, 0, y]
		xData1 = geometry[0, 1, y]
		xData2 = geometry[0, 2, y]
		xData3 = geometry[0, 3, y]
		anglesData = geometry[0, 4, y]

		# loop over the number in columns
		for x in range(0, numCols):
			# ignore it
			if scoresData[x] < min_confidence:
				continue

			(offsetX, offsetY) = (x * 4.0, y * 4.0)

			# extract the rotation angle 
			angle = anglesData[x]
			cos = np.cos(angle)
			sin = np.sin(angle)

			#bounding box
			h = xData0[x] + xData2[x]
			w = xData1[x] + xData3[x]

			# compute
			endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
			endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
			startX = int(endX - w)
			startY = int(endY - h)

			# added bounding box
			rects.append((startX, startY, endX, endY))
			confidences.append(scoresData[x])

	return (rects, confidences)


def data_uri_to_cv2_img(uri):

	encoded_data = str(uri).split(',')[1]
	img_b64decode = base64.b64decode(encoded_data)
	img_array = np.fromstring(img_b64decode, np.uint8)
	img = cv2.imdecode(img_array, cv2.COLOR_BGR2RGB)
	# print(imgdata)
	# nparr = np.fromstring(codecs.decode(uri, 'base64'), np.uint8)
	# img = cv2.imdecode(imgdata, cv2.IMREAD_COLOR)
	return img




def text_recognition(img_data, min_confidence, width, height, padding):
	# dimensions
	image = data_uri_to_cv2_img(img_data)
	# print(img)
	# image = cv2.imread(img)
	orig = image.copy()
	(origH, origW) = image.shape[:2]

	# height
	(newW, newH) = (width, height)
	rW = origW / float(newW)
	rH = origH / float(newH)

	# grab dimensions
	image = cv2.resize(image, (newW, newH))
	(H, W) = image.shape[:2]

	layerNames = [
		"feature_fusion/Conv_7/Sigmoid",
		"feature_fusion/concat_3"]

	# load EAST text detector
	print("[INFO] loading EAST text detector...")
	net = cv2.dnn.readNet("frozen_east_text_detection.pb")

	# construct a blob from the image and then perform a forward pass of
	# the model to obtain the two output layer sets
	blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
		(123.68, 116.78, 103.94), swapRB=True, crop=False)
	net.setInput(blob)
	(scores, geometry) = net.forward(layerNames)

	# decode the predictions, then  apply non-maxima suppression to
	# suppress weak, overlapping bounding boxes
	(rects, confidences) = decode_predictions(scores, geometry, min_confidence)
	boxes = non_max_suppression(np.array(rects), probs=confidences)

	# init
	results = []

	# loop over the bounding boxes
	for (startX, startY, endX, endY) in boxes:
		# bounding box coordinates respectively
		# the ratios
		startX = int(startX * rW)
		startY = int(startY * rH)
		endX = int(endX * rW)
		endY = int(endY * rH)

		# in
		dX = int((endX - startX) * padding)
		dY = int((endY - startY) * padding)

		startX = max(0, startX - dX)
		startY = max(0, startY - dY)
		endX = min(origW, endX + (dX * 2))
		endY = min(origH, endY + (dY * 2))

		# extract ROI
		roi = orig[startY:endY, startX:endX]
		config = ("-l eng --oem 1 --psm 7")
		text = pytesseract.image_to_string(roi, config=config)

		results.append(((startX, startY, endX, endY), text))

	# sort the results bounding box coordinates from top to bottom
	results = sorted(results, key=lambda r:r[0][1])

	# loop over the results
	# for ((startX, startY, endX, endY), text) in results:
	# 	# display the text OCR'd by Tesseract
	# 	print("OCR TEXT")
	# 	print("========")
	# 	print("{}\n".format(text))
	#
	# 	# strip out non-ASCII text so we can draw the text on the image
	# 	# using OpenCV, then draw the text and a bounding box surrounding
	# 	# the text region of the input image
	# 	text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
	# 	output = orig.copy()
	# 	cv2.rectangle(output, (startX, startY), (endX, endY),
	# 		(0, 0, 255), 2)
	# 	cv2.putText(output, text, (startX, startY - 20),
	# 		cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
	#
	# 	# show the output image
	# 	cv2.imshow("Text Detection", output)
	# 	cv2.waitKey(0)

	((startX, startY, endX, endY), text) = results[0]
	# display the text OCR'd by Tesseract
	print("OCR TEXT")
	print("========")
	print("{}\n".format(text))

	# strip out non-ASCII text so we can draw the text on the image
	# using OpenCV, then draw the text and a bounding box surrounding
	# the text region of the input image
	text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
	output = orig.copy()
	cv2.rectangle(output, (startX, startY), (endX, endY),
		(0, 0, 255), 2)
	cv2.putText(output, text, (startX, startY - 20),
		cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

	# show the output image
	# cv2.imshow("Text Detection", output)
	# ret, jpeg = cv2.imencode('.jpg', output)
	print("output")
	print(output)
	# converted = cv2.imencode('.jpg', output)[1].tostring()
	retval, buffer = cv2.imencode('.jpg', output)
	jpg_as_text = base64.b64encode(buffer)
	return jpg_as_text, text



