import json
import datetime
import dicom
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.conf import settings
from uploader.models import Study, Series, Image

BASE_DIR = settings.BASE_DIR
MEDIA_DIR = settings.MEDIA_ROOT

@ensure_csrf_cookie
def image(request, dcm_uid):

	try:

		image = Image.objects.get(UID = dcm_uid)
		series = image.dcm_series
		study = series.dcm_study
		images = Image.objects.filter(dcm_series = series).order_by("image_number")

	except ObjectDoesNotExist:

		context = {
			"msg": "Oops, it appears the SOP Instance UID: " + dcm_uid + " does not exist in our system yet."
		}

		return render_to_response('image.html', context, context_instance = RequestContext(request))

	filepath = MEDIA_DIR + '/' + image.filename + '.dcm'
	dcm = dicom.read_file(filepath)
	dcm_dict = getdict(dcm)

	context = {
		"image": image,
		"all_images": images,
		"series": series,
		"study": study,
		"dcm": dcm_dict
	}

	return render_to_response('image.html', context, context_instance = RequestContext(request))

@ensure_csrf_cookie
def study(request, dcm_uid):

	try:
		study = Study.objects.get(UID = dcm_uid)

	except ObjectDoesNotExist:
		context = {
			"msg": "Oops, it appears the Study UID: " + dcm_uid + " does not exist in our system yet."
		}
		return render_to_response('study.html', context, context_instance = RequestContext(request))

	series = Series.objects.filter(dcm_study = study)
	images = Image.objects.filter(dcm_series__in = series).distinct("dcm_series")

	context = {
		"study": study,
		"series": series,
		"images": images
	}

	return render_to_response('study.html', context, context_instance = RequestContext(request))

@ensure_csrf_cookie
def series(request, dcm_uid):

	try:
		series = Series.objects.get(UID = dcm_uid)
		images = Image.objects.filter(dcm_series = series).order_by("image_number")
		study = series.dcm_study

	except ObjectDoesNotExist:
		context = {
			"msg": "Oops, it appears the Series UID: " + dcm_uid + " does not exist in our system yet."
		}

		return render_to_response('series.html', context, context_instance = RequestContext(request))

	context = {
		"images": images,
		"series": series,
		"study": study
	}

	return render_to_response('series.html', context, context_instance = RequestContext(request))


def getdict(dcm):

	mydict = {}
	dont_print = ['Pixel Data', 'File Meta Information']

	for key in dcm:
		
		if key.VR == "SQ":
			pass
		else:
			if key.name in dont_print:
				print "item not printed"
			else:
				repr_value = repr(key.value)
				mydict[key.name] = repr_value

	for key in mydict.keys():
		if type(key) is not str:
			try:
				mydict[str(key)] = mydict[key]
			except:
				try:
					mydict[repr(key)] == mydict[key]
				except:
					del mydict[key]

	return json.dumps(mydict, ensure_ascii=False)