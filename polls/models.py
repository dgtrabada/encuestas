from django.db import models


class Questionarie(models.Model):
    questionarie_text = models.CharField(max_length=200)
    questionarie_group = models.CharField(max_length=200)
    total = models.IntegerField(default=0)
    def __str__(self):
        return self.questionarie_text

class Question(models.Model):
    questionarie = models.ForeignKey(Questionarie, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    total = models.IntegerField(default=0)
    question_type = models.CharField(max_length=200) 
    pub_date = models.DateTimeField('date published')
    question_answer = models.CharField(max_length=20000,default="")
    value = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    porc = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    def __str__(self):
        return self.choice_text

#class Text(models.Model):
#    question = models.ForeignKey(Question, on_delete=models.CASCADE)
#    question_answer = models.CharField(max_length=20000)
#    def __str__(self):
#        return self.question_answer

# Create your models here.
