from django.db import models

# Create your models here.
from django.db import models

class Problem(models.Model):
    statement = models.TextField()
    name = models.CharField(max_length=200)
    code = models.TextField()
    difficulty = models.CharField(max_length=200)

class Solution(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    verdict = models.CharField(max_length=200)
    lang = models.CharField(max_length=50, default='Java')
    sub_date = models.DateTimeField('date published') #submission ka date and time
    sub_code = models.TextField(default='Sytstem.out.println("hello_world")')
    
class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input = models.TextField()
    output = models.TextField()