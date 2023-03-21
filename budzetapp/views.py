from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
# Create your views here.
import datetime

from django.utils.encoding import smart_str, force_str
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.template import loader

from .utils.charts import months, colorPrimary, colorSuccess, colorDanger, generate_color_palette, get_year_dict
from .forms import CreateUserForm
from django.db.models import Count, F, Sum, Avg
from django.db.models.functions import ExtractYear, ExtractMonth
from django.http import JsonResponse
from .models import Transaction, Category
from django.template import RequestContext
from django.db.models import Sum
from .forms import FilterForm, FilterFormDate, FormularzWydatkiPrzychody,FilterFormDateSlupkowy
from django.shortcuts import redirect
from datetime import datetime


def pdf(request):
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    # Create the HttpResponse object
    response = HttpResponse(content_type='application/pdf')

    # This line force a download
    response['Content-Disposition'] = 'attachment; filename="transakcje.pdf"'

    # READ Optional GET param
    get_param = request.GET.get('name', 'World')

    # Generate unique timestamp
    ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    p = canvas.Canvas(response)
   # pdfmetrics.registerFont(TTFont('Comic Sans MS', 'COMIC.TTF'))
    pdfmetrics.registerFont(TTFont('Tahoma', 'Tahoma.TTF'))
    p.setFont('Tahoma', 12)
    # Write content on the PDF
    p.drawString(150, 750, "Przychody i wydatki " + ts)
    #p.drawString(80, 700, "{0:<15}  {1:<20}  {2:<10}  {3:20.16}".format("typ", "kategoria", "suma", "data_transakcji"))
    p.drawString(80, 700, "{0:<15}".format("typ"))
    p.drawString(180, 700, "{0:<20}".format("kategoria"))
    p.drawString(280, 700, "{0:<10}".format("suma"))
    p.drawString(380, 700, "{0:<20}".format("data transakcji"))

    line_height = 650
    for obiekt in Transaction.objects.filter(user=request.user):
        line = str(obiekt.type).format() + " " + force_str(obiekt.category.name, encoding=' ISO-8859-2',
                                                           strings_only=False, errors='strict') \
               + " " + str(obiekt.sum) + " " + str(obiekt.trans_date)
        typ = str(obiekt.type).format()
        kategoria = force_str(obiekt.category.name, encoding=' ISO-8859-2', strings_only=False, errors='strict')
        suma = str(obiekt.sum)
        data_transakcji = str(obiekt.trans_date)
        #p.drawString(80,line_height,"{0:<15}  {1:<20}  {2:<10}  {3:20.16}".format(typ,kategoria,suma,data_transakcji))
        p.drawString(80, line_height, "{0:<15}".format(typ))
        p.drawString(180, line_height, "{0:<20}".format(kategoria))
        p.drawString(280, line_height, "{0:<10}".format(suma))
        p.drawString(380, line_height, "{0:20.16}".format(data_transakcji))
        line_height = line_height - 50

        #print("{0:<15}  {1:<20}  {2:<10}  {3:20.15}".format(typ, kategoria, suma, data_transakcji))
    # Close the PDF object.
    p.showPage()
    p.save()

    # Show the result to the user
    return response


def home(request):
    template = loader.get_template('budzetapp/home.html')
    return render(request, 'budzetapp/home.html')


def userInterface(request):
    template = loader.get_template('budzetapp/userInterface.html')
    return render(request, 'budzetapp/userInterface.html')


def przychody(request):
    if request.method == 'POST':
        form = FormularzWydatkiPrzychody(request.POST)
    else:
        form = FormularzWydatkiPrzychody()

    if form.is_valid():
        transaction = Transaction()
        transaction.type = 'przychody'
        transaction.sum = request.POST.get('suma')
        transaction.category = Category.objects.filter(name=request.POST.get('kategoria'))[0]
        transaction.trans_date = request.POST.get('data')
        transaction.user = request.user
        transaction.save()

        return render(request, 'budzetapp/przychody.html', {"form": FormularzWydatkiPrzychody})

    else:
        return render(request, 'budzetapp/przychody.html', {"form": form})


def wydatki(request):
    if request.method == 'POST':
        form = FormularzWydatkiPrzychody(request.POST)
    else:
        form = FormularzWydatkiPrzychody()

    if form.is_valid():
        transaction = Transaction()
        transaction.type = 'wydatki'
        transaction.sum = request.POST.get('suma')
        transaction.category = Category.objects.filter(name=request.POST.get('kategoria'))[0]
        transaction.trans_date = request.POST.get('data')
        transaction.user = request.user
        transaction.save()

        return render(request, 'budzetapp/wydatki.html', {"form": FormularzWydatkiPrzychody})

    else:
        return render(request, 'budzetapp/wydatki.html', {"form": form})


def wykresy_filtrowanie(request):
    template = loader.get_template('budzetapp/wykresy_filtrowanie.html')
    return render(request, 'budzetapp/wykresy_filtrowanie.html')


def transakcje(request):
    template = loader.get_template('budzetapp/transakcje.html')
    listaTransakcji = Transaction.objects.filter(user=request.user)
    return render(request, 'budzetapp/transakcje.html', {"listaTransakcji": listaTransakcji})


class wykresslupkowy(TemplateView):
    template_name = 'budzetapp/wykresslupkowy.html'
    form_class = FilterFormDateSlupkowy

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            return render(request, 'budzetapp/wykresslupkowywykres.html',
                          {'qs': Transaction.objects.filter(user=self.request.user,
                                                            trans_date__gte=form.cleaned_data['date1'],
                                                            trans_date__lte=form.cleaned_data['date2'])})

        return render(request, '/budzetapp/wykresslupkowy')

    def get_context_data(self, **kwargs):
        context = super(wykresslupkowy, self).get_context_data(**kwargs)

        if self.request.method == 'POST':
            form = FilterFormDateSlupkowy(self.request.POST)
        else:
            form = FilterFormDateSlupkowy()
        context["form"] = form
        if form.is_valid():
            context["qs"] = Transaction.objects.filter(user=self.request.user,
                                                       trans_date__gte=form.cleaned_data['date1'],
                                                       trans_date__lte=form.cleaned_data['date2'])
        else:
            context["qs"] = Transaction.objects.filter(user=self.request.user)
        return context
    # template = loader.get_template('budzetapp/wykreskolowy.html')
    # return render(request, 'budzetapp/wykreskolowy.html')


class wykreskolowy(TemplateView):
    template_name = 'budzetapp/wykreskolowy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["qs"] = Transaction.objects.filter(user=self.request.user)
        transakcjeWydatkow = Transaction.objects.filter(user=self.request.user, type="wydatki")
        Wydatki = transakcjeWydatkow.aggregate(Sum('sum'))
        transakcjePrzychodow = Transaction.objects.filter(user=self.request.user, type="przychody")
        Przychody = transakcjePrzychodow.aggregate(Sum('sum'))
        sumaWydatkow = Wydatki['sum__sum']
        sumaPrzychodow = Przychody['sum__sum']
        context.update({'sumaWydatkow': sumaWydatkow, 'sumaPrzychodow': sumaPrzychodow})
        print("wydatki: ", sumaWydatkow)
        print("przychody: ", sumaPrzychodow)
        return context
    # template = loader.get_template('budzetapp/wykreskolowy.html')
    # return render(request, 'budzetapp/wykreskolowy.html')


def transakcjefiltrowanie(request):
    if request.method == 'POST':
        form = FilterForm(request.POST)
    else:
        form = FilterForm()

    if form.is_valid():
        template = loader.get_template('budzetapp/transakcjefiltrowanie.html')
        listaTransakcji = Transaction.objects.filter(user=request.user)
        if Transaction.objects.filter(category__name=form.cleaned_data['category']).count() == 0:
            return render(request, 'budzetapp/transakcjefiltrowanie.html',
                          {"form": FilterForm, "output": form.cleaned_data['category']})
        return render(request, 'budzetapp/transakcjefiltrowanie.html',
                      {"form": FilterForm, "output": form.cleaned_data['category'], "listaTransakcji": listaTransakcji})
    template = loader.get_template('budzetapp/transakcjefiltrowanie.html')
    listaTransakcji = Transaction.objects.all()
    return render(request, 'budzetapp/transakcjefiltrowanie.html', {"form": FilterForm})


def transakcjefiltrowaniedatapomiedzy(request):
    if request.method == 'POST':
        form = FilterFormDate(request.POST)
    else:
        form = FilterFormDate()
    if form.is_valid():
        print("data1", form.cleaned_data['date1'])
        print("data2", form.cleaned_data['date2'])
        template = loader.get_template('budzetapp/transakcjefiltrowaniedatapomiedzy.html')
        listaTransakcji = Transaction.objects.filter(user=request.user, trans_date__gte=form.cleaned_data['date1'],
                                                     trans_date__lte=form.cleaned_data['date2'])
        if Transaction.objects.filter(trans_date__gte=form.cleaned_data['date1'],
                                      trans_date__lte=form.cleaned_data['date2']).count() == 0:
            return render(request, 'budzetapp/transakcjefiltrowaniedatapomiedzy.html',
                          {"form": FilterFormDate, "data1": form.cleaned_data['date1'],
                           "data2": form.cleaned_data['date2']})
        return render(request, 'budzetapp/transakcjefiltrowaniedatapomiedzy.html',
                      {"form": FilterFormDate, "data1": form.cleaned_data['date1'], "data2": form.cleaned_data['date2'],
                       "listaTransakcji": listaTransakcji})
    template = loader.get_template('budzetapp/transakcjefiltrowaniedatapomiedzy.html')
    listaTransakcji = Transaction.objects.all()
    return render(request, 'budzetapp/transakcjefiltrowaniedatapomiedzy.html', {"form": FilterFormDate})


from .forms import LoginForm


def get_name(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = LoginForm()

    return render(request, 'name.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            password = form.cleaned_data['email']
    form = LoginForm()
    return render(request, 'budzetapp/userInterface.html', {'form': form})


def createTransaction(request):
    if request.method == 'POST':
        if request.POST.get('type') and request.POST.get('sum') and request.POST.get('category'):
            transaction = Transaction()
            transaction.type = request.POST.get('type')
            transaction.sum = -request.POST.get('sum')
            transaction.category = request.POST.get('category')
            transaction.user = User.objects.filter(pk=1)
            transaction.save()

            return render(request, 'budzetapp/userInterface.html')

    else:
        return render(request, 'budzetapp/userInterface.html')


def rejestracja(request):
    form = CreateUserForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return render(request, 'budzetapp/userInterface.html', {"form": form})
    return render(request, 'budzetapp/rejestracja.html', {"form": form})


def wykresslupkowywykres(request):
    qs = Transaction.objects.filter(user=request.user,
                                    trans_date__gte=request.data1,
                                    trans_date__lte=request.data2)
    return render(request, 'budzetapp/wykresslupkowywykres.html', qs)
