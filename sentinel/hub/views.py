from django.shortcuts import render

# Create your views here.
def main(request):
	return render(request, "index.html")

def fake(request):
	return render(request, "fakeleaf.html")