import pytest
import requests
import json

headerz = {'Content-Type': 'application/json'}

def post_and_check(data, response):
    res = requests.post('http://127.0.0.1', data=json.dumps(data), headers=headerz)
    clean = res.text.replace(' ', '').replace('\n', '')
    assert clean == response

def test_circle():
    """ We can move each direction one place and arrive back"""
    post_and_check({
	  "roomSize" : [5, 5],
	  "coords" : [2, 2],
	  "patches" : [],
	  "instructions" : "NESW"
	}, '{"coords":[2,2],"patches":0}')

def test_example():
    """ We got given example data in the description, test that """
    post_and_check({
	  "roomSize" : [5, 5],
	  "coords" : [1, 2],
	  "patches" : [
	    [1, 0],
	    [2, 2],
	    [2, 3]
	  ],
	  "instructions" : "NNESEESWNWW"
	}, '{"coords":[1,3],"patches":1}')

def test_hit_wall():
    """ Want to make sure we can't exceed max size of the room."""
    post_and_check({
	  "roomSize" : [5, 5],
	  "coords" : [5, 5],
	  "patches" : [],
	  "instructions" : "N"
	}, '{"coords":[5,5],"patches":0}')

def test_bad_instructions():
    """ We don't do anything with bad instructions right?"""
    post_and_check({
	  "roomSize" : [5, 5],
	  "coords" : [5, 5],
	  "patches" : [],
	  "instructions" : "XXX"
	}, '{"coords":[5,5],"patches":0}')


def test_bad_json():
    """ We don't do anything with bad instructions right?"""
    post_and_check({
	  "roomSize" : [5, 5],
	}, '{"success":false}')
