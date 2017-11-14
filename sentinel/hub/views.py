from django.shortcuts import render

# Create your views here.
def main(request):
	return render(request, "index.html")

def fake(request):
	return render(request, "fakeleaf.html")

def rfid_demo(request):
	return render(request, "rfid_demo.html")