# From http://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/

import struct
import six
import collections
import cv2
import datetime
import subprocess as sp
import json 
import numpy as np
import time
from threading import Thread
from matplotlib import colors


class FPS:
	def __init__(self):
		# store the start time, end time, and total number of frames
		# that were examined between the start and end intervals
		self._start = None
		self._end = None
		self._numFrames = 0

	def start(self):
		# start the timer
		self._start = datetime.datetime.now()
		return self

	def stop(self):
		# stop the timer
		self._end = datetime.datetime.now()

	def update(self):
		# increment the total number of frames examined during the
		# start and end intervals
		self._numFrames += 1

	def elapsed(self):
		# return the total number of seconds between the start and
		# end interval
		return (self._end - self._start).total_seconds()

	def fps(self):
		# compute the (approximate) frames per second
		return self._numFrames / self.elapsed()


class HLSVideoStream:
	def __init__(self, src):
		# initialize the video camera stream and read the first frame
		# from the stream

		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False

		FFMPEG_BIN = "ffmpeg"

		metadata = {}

		while "streams" not in metadata.keys():
			
			print('ERROR: Could not access stream. Trying again.')

			info = sp.Popen(["ffprobe", 
			"-v", "quiet",
			"-print_format", "json",
			"-show_format",
			"-show_streams", src],
			stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
			out, err = info.communicate(b"ffprobe -v quiet -print_format json -show_format -show_streams http://52.91.28.88:8080/hls/live.m3u8")

			metadata = json.loads(out.decode('utf-8'))
			time.sleep(5)


		print('SUCCESS: Retrieved stream metadata.')

		self.WIDTH = metadata["streams"][0]["width"]
		self.HEIGHT = metadata["streams"][0]["height"]

		self.pipe = sp.Popen([ FFMPEG_BIN, "-i", src,
				 "-loglevel", "quiet", # no text output
				 "-an",   # disable audio
				 "-f", "image2pipe",
				 "-pix_fmt", "bgr24",
				 "-vcodec", "rawvideo", "-"],
				 stdin = sp.PIPE, stdout = sp.PIPE)
		print('WIDTH: ', self.WIDTH)

		raw_image = self.pipe.stdout.read(self.WIDTH*self.HEIGHT*3) # read 432*240*3 bytes (= 1 frame)
		self.frame =  np.fromstring(raw_image, dtype='uint8').reshape((self.HEIGHT,self.WIDTH,3))
		self.grabbed = self.frame is not None


	def start(self):
		# start the thread to read frames from the video stream
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		# if the thread indicator variable is set, stop the thread

		while True:
			if self.stopped:
				return

			raw_image = self.pipe.stdout.read(self.WIDTH*self.HEIGHT*3) # read 432*240*3 bytes (= 1 frame)
			self.frame =  np.fromstring(raw_image, dtype='uint8').reshape((self.HEIGHT,self.WIDTH,3))
			self.grabbed = self.frame is not None

	def read(self):
		# return the frame most recently read
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True



class WebcamVideoStream:
	def __init__(self, src, width, height):
		# initialize the video camera stream and read the first frame
		# from the stream
		self.stream = cv2.VideoCapture(src)
		self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
		self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
		(self.grabbed, self.frame) = self.stream.read()

		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return

			# otherwise, read the next frame from the stream
			(self.grabbed, self.frame) = self.stream.read()

	def read(self):
		# return the frame most recently read
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True


def standard_colors():
	colors = [
		'AliceBlue', 'Chartreuse', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque',
		'BlanchedAlmond', 'BlueViolet', 'BurlyWood', 'CadetBlue', 'AntiqueWhite',
		'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan',
		'DarkCyan', 'DarkGoldenRod', 'DarkGrey', 'DarkKhaki', 'DarkOrange',
		'DarkOrchid', 'DarkSalmon', 'DarkSeaGreen', 'DarkTurquoise', 'DarkViolet',
		'DeepPink', 'DeepSkyBlue', 'DodgerBlue', 'FireBrick', 'FloralWhite',
		'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod',
		'Salmon', 'Tan', 'HoneyDew', 'HotPink', 'IndianRed', 'Ivory', 'Khaki',
		'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue',
		'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGray', 'LightGrey',
		'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue',
		'LightSlateGray', 'LightSlateGrey', 'LightSteelBlue', 'LightYellow', 'Lime',
		'LimeGreen', 'Linen', 'Magenta', 'MediumAquaMarine', 'MediumOrchid',
		'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen',
		'MediumTurquoise', 'MediumVioletRed', 'MintCream', 'MistyRose', 'Moccasin',
		'NavajoWhite', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed',
		'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed',
		'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple',
		'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Green', 'SandyBrown',
		'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue',
		'SlateGray', 'SlateGrey', 'Snow', 'SpringGreen', 'SteelBlue', 'GreenYellow',
		'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White',
		'WhiteSmoke', 'Yellow', 'YellowGreen'
	]
	return colors


def color_name_to_rgb():
	colors_rgb = []
	for key, value in colors.cnames.items():
		colors_rgb.append((key, struct.unpack('BBB', bytes.fromhex(value.replace('#', '')))))
	return dict(colors_rgb)


def draw_boxes_and_labels(
		boxes,
		classes,
		scores,
		instance_masks=None,
		keypoints=None,
		max_boxes_to_draw=None,
		min_score_thresh=.5,
		agnostic_mode=False):
	"""Returns boxes coordinates, class names and colors

	Args:
		boxes: a numpy array of shape [N, 4]
		classes: a numpy array of shape [N]
		scores: a numpy array of shape [N] or None.  If scores=None, then
		this function assumes that the boxes to be plotted are groundtruth
		boxes and plot all boxes as black with no classes or scores.
		category_index: a dict containing category dictionaries (each holding
		category index `id` and category name `name`) keyed by category indices.
		instance_masks: a numpy array of shape [N, image_height, image_width], can
		be None
		keypoints: a numpy array of shape [N, num_keypoints, 2], can
		be None
		max_boxes_to_draw: maximum number of boxes to visualize.  If None, draw
		all boxes.
		min_score_thresh: minimum score threshold for a box to be visualized
		agnostic_mode: boolean (default: False) controlling whether to evaluate in
		class-agnostic mode or not.  This mode will display scores but ignore
		classes.
	"""
	# Create a display string (and color) for every box location, group any boxes
	# that correspond to the same location.
	box_to_display_str_map = collections.defaultdict(list)
	box_to_color_map = collections.defaultdict(str)
	final_box = collections.defaultdict(str)
	box_to_instance_masks_map = {}
	box_to_keypoints_map = collections.defaultdict(list)
	if not max_boxes_to_draw:
		max_boxes_to_draw = boxes.shape[0]
	for i in range(min(max_boxes_to_draw, boxes.shape[0])):
		if scores is None or scores[i] > min_score_thresh:
			box = tuple(boxes[i].tolist())
			if instance_masks is not None:
				box_to_instance_masks_map[box] = instance_masks[i]
			if keypoints is not None:
				box_to_keypoints_map[box].extend(keypoints[i])
			if scores is None:
				box_to_color_map[box] = 'black'
			else:
				display_str = int(100 * scores[i])
				box_to_display_str_map[box].append(display_str)
				if agnostic_mode:
					box_to_color_map[box] = 'DarkOrange'
				else:
					box_to_color_map[box] = standard_colors()[
						classes[i] % len(standard_colors())]
	# my_boxes = [list(elem) for elem in list(box_to_color_map.keys())]
	# my_np_boxes = np.array([np.array(xi) for xi in my_boxes])
	# out_box = non_max_suppression_fast(my_np_boxes, 0.2)
	# if len(out_box)>0:
	# 	box = tuple(out_box[0].tolist())
	# 	final_box[box] = 'DarkOrange'
	# Store all the coordinates of the boxes, class names and colors
	color_rgb = color_name_to_rgb()
	rect_points = []
	class_scores = []
	class_colors = []
	for box, color in six.iteritems(box_to_color_map):
		ymin, xmin, ymax, xmax = box
		rect_points.append(dict(ymin=ymin, xmin=xmin, ymax=ymax, xmax=xmax))
		class_scores.append(box_to_display_str_map[box])
		class_colors.append(color_rgb[color.lower()])
	return rect_points, class_scores, class_colors


def non_max_suppression_fast(boxes, overlapThresh):
    # if there are no boxes, return an empty list
    if len(boxes) == 0:
        return []

    # if the bounding boxes integers, convert them to floats --
    # this is important since we'll be doing a bunch of divisions
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    # initialize the list of picked indexes
    pick = []

    # grab the coordinates of the bounding boxes
    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]

    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)

    # keep looping while some indexes still remain in the indexes
    # list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        # compute the ratio of overlap
        overlap = (w * h) / area[idxs[:last]]

        # delete all indexes from the index list that have
        idxs = np.delete(idxs, np.concatenate(([last],
                                               np.where(overlap > overlapThresh)[0])))

    # return only the bounding boxes that were picked using the
    # integer data type
    return boxes[pick]