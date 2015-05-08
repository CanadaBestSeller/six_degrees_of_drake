import six_degrees_of_drake.views

query_url = """
http://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srwhat=text&srlimit=3&continue=&srprop=snippet&srsearch=%22associated%20acts%22+intitle:daniel
"""

response_object = views.json_to_response_object(query_url)
name = response_object['query']['search'][1]['title']
