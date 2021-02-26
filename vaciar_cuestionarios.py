#!/usr/bin/env python3

import os
import sys
from polls.models import Questionarie, Question, Choice
from django.utils import timezone


for questionarie in Questionarie.objects.filter():
	questionarie.total=0
	print(questionarie.questionarie_text)
	for q in questionarie.question_set.all():
		q.value=0
		q.total=0
		q.question_answer=""
		if q.question_type == "Choice4" or q.question_type == "Choice":
			for c in q.choice_set.all():
				c.votes=0
				c.porc=0
				c.save()
		print("guardar vacia "+q.question_text)
		q.save()
	questionarie.save()
	print("guardar vacia "+questionarie.questionarie_text)

