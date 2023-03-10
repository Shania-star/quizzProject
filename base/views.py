from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User
from .models import *
from .forms import SignUpForm  # import the form created to use it
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Avg
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
# When the user clicks a button, a link, views return elements and in the page 


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def index(request):
    return render(request, "base/index.html")


def loginPage(request):
    page = 'login'
    # login
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('categories') # name attribute in urls.py
        else:
            messages.error(request, 'Username or password does not exist')

    return render(request, "registration/login.html")


def logoutUser(request):
    logout(request)
    request.user = None
    return redirect('index')


def signupPage(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)  # when user logs in, he'll get recognized
            return redirect('categories')

    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required(login_url='login')
def categoryPage(request):
    category = Category.objects.all()
    context = {'category': category}
    return render(request, "base/category_component.html", context)


def startQuiz(request, pk):
    # only takes the elements related to the category, 1Q per page
    p = Paginator(Question.objects.filter(category=pk), 1)
    categoryId = pk
    page = request.GET.get('page')
    questions = p.get_page(page)
    context = {'questions': questions, 'categoryId':categoryId}
    return render(request, "base/quiz.html", context)

def deleteCategory(request, pk):
    category = Category.objects.get(id=pk)
    category.delete()
    return redirect('categories')

def addCategory(request):
    context = {}
    if request.method == 'POST':
         form = CategoryForm(request.POST)
         if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect('categories')
            
    else :
        form = CategoryForm()

    context['form'] = form
    return render(request, "base/add_category.html", context)

def updateCategory(request,pk):
    if request.method == 'POST':
        Category.objects.filter(id=pk).update(user=request.user, name=request.POST['name'], description=request.POST['description'])
        return redirect('categories')
    return render("base/edit_category.html")


def editCategory (request, pk):
    category = Category.objects.get(id=pk)
    categoryForm = CategoryForm(instance=category)
    questions = Question.objects.filter(category=pk)
    category_id = pk
    context = {'categoryForm': categoryForm, 'questions': questions, 'category_id': category_id}
    return render(request,"base/edit_category.html", context)

@csrf_exempt
def addQuestion(request, pk):
    context = {}
    questionCatId = pk
    categ = Category.objects.get(id=questionCatId)
    categName = categ.name
    if request.method == 'POST':
        data = request.POST
        data_ = dict(data.lists())
        question = data_['question']
        answer = data_['answer']
        tmpoptions = (data_['options'])[0].split(";")
        options = tmpoptions[:-1]
        explanation = data_['explanation']
        
        
        if question[0] == None or answer[0] == "" or options[0] == "" or explanation[0] == "":
            return JsonResponse("error",safe=False)
        
        elif question != "" and answer != "" and options != "" and explanation != "":
            Question.objects.create(category_id=pk, question=question[0], answer=answer[0],options=options,explanation=explanation[0], user=request.user)
            return JsonResponse("success",safe=False)
    
    form = QuestionForm()
    context = {'form':form, 'questionCatId':questionCatId, 'categName':categName}
    return render(request, "base/add_question.html", context)

def deleteQuestion(request,pk):
    question = Question.objects.get(id=pk)
    categName = question.category
    category = Category.objects.get(name=categName)
    categoryForm = CategoryForm(instance=category)
    questions = Question.objects.filter(category=category.id)
    category_id = category.id
    context = {'categoryForm': categoryForm, 'questions': questions, 'category_id': category_id}
    question.delete()
    return render(request,"base/edit_category.html", context)

def wrongAnswer(request):
    questionId = 0
    countwrongA = 0

    data = request.POST
    data_ = dict(data.lists())  # contains the question and the checked answer
    data_.pop('csrfmiddlewaretoken') # remove this data
    user = request.user
    point = 1
    
    for k in data_.keys(): # key is the id of the question, and the value the number of wrong answer
        questionId = k
        for vall in data_[k]:
            countwrongA = int(vall)
    
    if (countwrongA != 0):
        point = round(1 - (0.4*countwrongA),1)


    if (point <= 0 or point == None):
        point = 0

    Question.objects.filter(id=questionId).update(user = user, number_wa = countwrongA, point = point)
   
    return JsonResponse(countwrongA, safe=False)

def resultsPage(request):
    user = request.user
    categ = request.POST.get('thecategory')
    questions = Question.objects.filter(user=user)
    question_count = questions.count()
    total_pointsDict = Question.objects.filter(user=user).aggregate(Sum('point'))
    total_points = total_pointsDict.get('point__sum')
    average_points = round((question_count / 2), 1)
    print(average_points)
    context = {'questions': questions, 'question_count':question_count, 'total_points': total_points, 'average_points': average_points}

    return render(request, "base/final_result.html", context)
