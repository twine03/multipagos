from django.views.generic.base import TemplateView
import json
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from .models import *
from digitalizacion.models import *
from cartera.models import *
from verificaciones.models import *
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import *


def home(request):
    return HttpResponseRedirect("/admin")


class indexar(TemplateView):
    template_name = "metropolitana/pods.html"


class verificacion_paquete(TemplateView):
    template_name = "metropolitana/verificacion.html"


class entrega_paquete(TemplateView):
    template_name = "metropolitana/entrega.html"


def datos_paquete_(request):

    if request.method == 'GET':
        p = Paquete()
        try:
            p = Paquete.objects.get(barra=request.GET.get('barra', ''))
            datos = {'cliente': p.cliente, 'departamento': p.departamento,
                'municipio': p.municipio, 'lote': 23,
                'cantidad': 5, 'clase': estado(p)[0],
                'valor': estado(p)[1]}
            i = Impresion(paquete=p, user=request.user)
            i.save()
        except p.DoesNotExist:
            datos = {'cliente': 'nada'}
        resp = HttpResponse(json.dumps(datos),
            content_type='application/json')
        resp["Access-Control-Allow-Origin"] = "*"
        resp["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        resp["Access-Control-Allow-Headers"] = "X-Requested-With"
        return resp
    else:
        datos = {'nombre': 'nada'}
        resp = HttpResponse(json.dumps(datos),
            content_type='application/json')
        resp["Access-Control-Allow-Origin"] = "*"
        resp["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        resp["Access-Control-Allow-Headers"] = "X-Requested-With"
        return resp


from django.core import serializers


def datos_paquete(request):
    p = Paquete()
    try:
        p = Paquete.objects.get(barra=request.GET.get('barra', ''))
        i = Impresion(paquete=p, user=request.user)
        i.save()
    except:
        pass
    data = serializers.serialize('json', [p, ])
    struct = json.loads(data)
    data = json.dumps(struct[0])
    return HttpResponse(data, content_type='application/json')


def descarga(request):
    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % "1065.pdf"
    response['X-Sendfile'] = "/home/abel/PDF/1075.pdf"
    return response


def calcular_entregas(barrio):
    return Paquete.objects.filter(idbarrio=barrio, estado='PENDIENTE',
        cerrado=False).count()


def calcular_cobros(barrio):
    return Detalle.objects.filter(idbarrio=barrio, estado='PENDIENTE').count()


def calcular_verificaciones(barrio):
    return Verificacion.objects.filter(idbarrio=barrio,
        estado='PENDIENTE').count()

@csrf_exempt
def get_zonas(request):
    zona_id = int(request.POST.get('zona_id', ''))
    data = []
    z = Zona.objects.get(id=zona_id)
    obj_json = {}
    obj_json['pk'] = z.id
    obj_json['code'] = z.code
    obj_json['name'] = z.name
    barrios = []
    for b in z.barrios():
        bar_json = {}
        bar_json['pk'] = b.id
        bar_json['code'] = b.code
        bar_json['name'] = b.name
        bar_json['entregas'] = calcular_entregas(b)
        bar_json['cobros'] = calcular_cobros(b)
        bar_json['verificaciones'] = calcular_verificaciones(b)
        barrios.append(bar_json)
    obj_json['barrios'] = barrios
    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')


@login_required(login_url='/admin/login/')
def asignacion_paquete(request):
    context = RequestContext(request)
    data = {'zonas': Zona.objects.all().order_by('name'),
        'users': User.objects.all().order_by('username')}
    template_name = "metropolitana/asignacion.html"
    if request.method == "POST":
        pass
    return render_to_response(template_name, data, context_instance=context)