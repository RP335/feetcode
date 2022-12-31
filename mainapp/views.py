import tempfile
from django.utils import timezone
import filecmp,os,shutil
from django.http import HttpResponse,HttpResponseRedirect
from .models import Problem,Solution,TestCase
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm
import subprocess

# Create your views here.
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request,'Account created for ' + user)
            return redirect('login')
    context = {'form' : form}
    return render(request, 'feetcode/register.html', context)

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Username or password is incorrect')
    context={}
    return render(request, 'feetcode/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def index(request):
    problem_list = Problem.objects.all
    context = {'problem_list': problem_list}
    return render(request, 'feetcode/index.html', context)

@login_required(login_url='login')
def detail(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    return render(request, 'feetcode/detail.html', {'problem': problem})

@login_required(login_url='login')
def submit(request, problem_id):
    code = request.POST.get('solution')
    language = request.POST.get('language')
    print(language)
    sol_java = open('/Users/rahul_peter/Documents/webdev-practice/feetCode/items/solution.java', "wb+")
    sol_py = open('/Users/rahul_peter/Documents/webdev-practice/feetCode/items/solution.py', "wb+")
    temp_py = tempfile.NamedTemporaryFile(suffix=".py", dir='.')
    temp_java = tempfile.NamedTemporaryFile(suffix=".java", dir='.')
    temp_java2 = tempfile.NamedTemporaryFile(suffix = "", dir = ".")

    if language == "Java":
        temp_java.write(str.encode(code))
        temp_java.seek(0)   
    elif language == "Python":
        temp_py.write(str.encode(code))
        temp_py.seek(0)
    s = subprocess.check_output('docker ps', shell=True)
    strPath = os.getcwd()
    print(strPath)
    if (language == "Java"):
        if s.find(str.encode('java-container')) == -1:
            subprocess.run(f'docker run -d -it --name java-container -v {strPath}:/home/:ro openjdk', shell=True)
    if (language == "Python"):
        if s.find(str.encode('python-container')) == -1:
            subprocess.run(f'docker run -d -it --name python-container -v {strPath}:/home/:ro python', shell=True)     

    print("test1")
    strPath = os.getcwd()
    print(strPath)
    problem = get_object_or_404(Problem, pk=problem_id)
    testcase = problem.testcase_set.all()
    if language == 'Java':
        subprocess.run('docker exec java-container javac /home/'+ os.path.basename(temp_java.name), shell=True)
    
    for i in testcase:
        inp = open ('/Users/rahul_peter/Documents/webdev-practice/feetCode/items/inp.txt', "wb+")
        inp.write(str.encode(i.input))
        inp.seek(0)

        actual_out = open ('/Users/rahul_peter/Documents/webdev-practice/feetCode/items/actual_out.txt', "wb+")
        actual_out.write(str.encode(i.output))
        actual_out.seek(0)
        if (language == "Java"):
            subprocess.run('docker exec -i java-container java < /Users/rahul_peter/Documents/webdev-practice/feetCode/items/inp.txt > /Users/rahul_peter/Documents/webdev-practice/feetCode/items/out.txt', shell=True)
        elif (language == "Python"):
            subprocess.run("docker exec -i python-container python /home/"+ os.path.basename(temp_py.name)+ ' < /Users/rahul_peter/Documents/webdev-practice/feetCode/items/inp.txt > /Users/rahul_peter/Documents/webdev-practice/feetCode/items/out.txt', shell=True)
        # if language == 'Java':
        #     subprocess.run('java ' + temp_java2.name + ' < /Users/rahul_peter/Documents/webdev-practice/feetCode/items/inp.txt > /Users/rahul_peter/Documents/webdev-practice/feetCode/items/out.txt', shell = True )
        # elif language == 'Python':
        #     subprocess.run('python ' + os.path.basename(temp_py.name)  + ' < /Users/rahul_peter/Documents/webdev-practice/feetCode/items/inp.txt > /Users/rahul_peter/Documents/webdev-practice/feetCode/items/out.txt', shell = True)
        
        actual_outstring = ""
        outstring = ""
        out1 = '/Users/rahul_peter/Documents/webdev-practice/feetCode/items/out.txt'
        out2 = '/Users/rahul_peter/Documents/webdev-practice/feetCode/items/actual_out.txt'

        with open(out1,'r') as var:
            for line in var:
                line=line.replace('/r',' ')
                outstring=outstring+line

        with open(out2,'r') as var:
            for line in var:
                line=line.replace('/r',' ')
                actual_outstring=actual_outstring+line

        if(actual_outstring.strip() == outstring.strip()):
            verdict = 'Accepted'
        else:
            verdict = 'Wrong Answer'

    if (language == "Java"):
        temp_java.close()
        temp_java2.close()
    elif (language == "Python"):
        temp_py.close()    

    solution = Solution()
    solution.problem = Problem.objects.get(pk=problem_id)
    solution.verdict = verdict
    solution.sub_date = timezone.now()
    solution.sub_code = code
    solution.lang = language
    sol_java.close()
    sol_py.close()
    solution.save()
    return redirect('submissions')

@login_required(login_url='login')
def submissions(request):
    submission = Solution.objects.all().order_by('-sub_date')
    context = {'submission': submission}
    return render(request, 'feetcode/submissions.html', context)
