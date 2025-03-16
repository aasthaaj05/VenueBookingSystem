from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request , 'home/index.html')



from django.shortcuts import render

def blog_details(request):
    print('in home : blog_details()')
    return render(request, 'home/blog-details.html')


from django.shortcuts import render

def blog(request):
    return render(request, 'blog.html')
