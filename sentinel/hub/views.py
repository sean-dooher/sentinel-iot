from django.shortcuts import render


# Create your views here.
def main(request):
    return render(request, "index.html")


def fake_in(request):
    return render(request, "fake_rfid.html")


def fake_out(request):
    return render(request, "fake_door.html")


def rfid_demo(request):
    return render(request, "rfid_demo.html")