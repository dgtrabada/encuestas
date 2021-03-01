#!/usr/bin/env python3
  
import os
import sys
from polls.models import Questionarie, Question, Choice
from django.utils import timezone
from django.contrib.auth.models import Group, User



def votar(user,Questionarie_selected):
    import random
    #print("::: vota",user,Questionarie_selected.id)
    question_list=Questionarie_selected.question_set.all()
    for question in question_list: 
        c=str("")+str(question.id)+str("")
        if question.question_type == "Text":
            res=question.question_answer+' ; usuario = '+user.username+' ; '+str(random.random())
            question.question_answer=res
            question.save()
    for question in question_list:
        if question.question_type == "Choice" or question.question_type == "Choice4":
            selected_choice = random.choice(question.choice_set.all())
            selected_choice.votes += 1
            selected_choice.save()
    Questionarie_selected.total=0
    for question in question_list:
        if question.question_type == "Choice" or question.question_type == "Choice4":
            question.total=0
            valor_total=0
            for choice in question.choice_set.all() :
                question.total += choice.votes
                valor_total=valor_total + float(choice.choice_text[0])*choice.votes
            if question.total==0:
               question.value = 0
            else:
               question.value = valor_total/question.total
               
            for choice in question.choice_set.all() :
                if question.total==0:
                    choice.porc = 0.0
                else:
                    choice.porc = choice.votes*100/question.total
            if question.total > Questionarie_selected.total:
                Questionarie_selected.total=question.total
            question.save()
    Questionarie_selected.save()
    print('ntotal',question.total)


for user in User.objects.all():
  #print(user.username+" "+str(user.is_active))
  for questionarie in Questionarie.objects.filter():
    #print(user.first_name,questionarie.questionarie_group)
    if user.first_name == questionarie.questionarie_group:
      print(questionarie.questionarie_text+" "+questionarie.questionarie_group)
      votar(user,questionarie)

