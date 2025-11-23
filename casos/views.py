from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Caso, Expediente, Carpeta,EventoExpediente
from .forms import CasoForm, EquipoCasoForm, ParteProcesalForm, ExpedienteForm, CarpetaForm
from actores.models import Actor, Cliente
from datetime import date
from .utils import registrar_evento_exp
from django.db.models import Q
from django.views.decorators.http import require_POST
from documentos.models import Documento


# ======= CASOS ======= #
def caso_list(request):
    # Recuperamos los parámetros enviados desde el formulario
    q = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "").strip()
    prioridad = request.GET.get("prioridad", "").strip()
    desde = request.GET.get("desde", "").strip()
    hasta = request.GET.get("hasta", "").strip()

    # Base Query
    casos = Caso.objects.all().order_by("-fechaInicio")

    # 🔍 Filtro de búsqueda libre
    if q:
        casos = casos.filter(
            Q(nroCaso__icontains=q)
            | Q(tipoCaso__icontains=q)
            | Q(descripcion__icontains=q)
        )

    # 🔍 Filtro por estado
    if estado:
        casos = casos.filter(estado=estado)

    # 🔍 Filtro por prioridad
    if prioridad:
        casos = casos.filter(prioridad=prioridad)

    # 🔍 Filtro por rango de fechas
    if desde:
        casos = casos.filter(fechaInicio__gte=desde)
    if hasta:
        casos = casos.filter(fechaInicio__lte=hasta)

    context = {
        "casos": casos,
        "q": q,
        "estado": estado,
        "prioridad": prioridad,
        "desde": desde,
        "hasta": hasta,
    }
    return render(request, "casos/caso_list.html", context)


def caso_create(request):
    if request.method == "POST":
        form = CasoForm(request.POST)
        if form.is_valid():
            caso = form.save(commit=False)
            caso.creado_por = request.user  # 👈 Registro de usuario que crea
            caso.save()

            # Crear expediente automáticamente
            nro_auto = f"EXP-{caso.id:04d}"
            Expediente.objects.create(
                caso=caso,
                nroExpediente=nro_auto,
                estado="ABIERTO",
                fechaCreacion=date.today(),
                creado_por=request.user  # 👈 también registramos quién lo crea
            )

            messages.success(request, f"Caso y expediente '{nro_auto}' creados correctamente.")
            return redirect("casos:case_list")
    else:
        form = CasoForm()
    return render(request, "casos/caso_form.html", {"form": form})


def caso_edit(request, pk):
    caso = get_object_or_404(Caso, pk=pk)
    if request.method == "POST":
        form = CasoForm(request.POST, instance=caso)
        if form.is_valid():
            caso = form.save(commit=False)
            caso.modificado_por = request.user  # 👈 registro de modificación
            caso.save()
            messages.success(request, "Caso actualizado correctamente.")
            return redirect("casos:case_list")
    else:
        form = CasoForm(instance=caso)
    return render(request, "casos/caso_form.html", {"form": form, "caso": caso})


# ======= EQUIPO DE CASO ======= #
def equipo_caso_list(request, caso_id):
    caso = get_object_or_404(Caso, pk=caso_id)
    equipo = caso.equipocaso_set.select_related("actor")
    return render(request, "casos/equipo_list.html", {"caso": caso, "equipo": equipo})


def equipo_caso_add(request, caso_id):
    caso = get_object_or_404(Caso, pk=caso_id)
    if request.method == "POST":
        form = EquipoCasoForm(request.POST)
        if form.is_valid():
            equipo = form.save(commit=False)
            equipo.caso = caso
            equipo.creado_por = request.user  # 👈 auditoría
            equipo.save()
            messages.success(request, "Actor agregado al equipo del caso.")
            return redirect("casos:equipo_list", caso_id=caso.id)
    else:
        form = EquipoCasoForm()
    return render(request, "casos/equipo_form.html", {"form": form, "caso": caso})

@require_POST
def equipo_caso_delete(request, pk):
    """
    Elimina un miembro del equipo de un caso con confirmación y auditoría.
    """
    equipo = get_object_or_404(EquipoCaso, pk=pk)
    caso_id = equipo.caso.id
    actor_nombre = f"{equipo.actor.nombres} {equipo.actor.apellidoPaterno}"

    # ⚙️ Auditoría (opcional)
    if hasattr(equipo, "modificado_por"):
        equipo.modificado_por = request.user

    equipo.delete()

    messages.success(request, f"Se eliminó del equipo al actor {actor_nombre}.")
    return redirect("casos:equipo_list", caso_id=caso_id)

# ======= PARTE PROCESAL ======= #
def parte_procesal_list(request, caso_id):
    caso = get_object_or_404(Caso, pk=caso_id)
    partes = caso.parteprocesal_set.select_related("cliente")
    return render(request, "casos/parte_list.html", {"caso": caso, "partes": partes})


def parte_procesal_add(request, caso_id):
    caso = get_object_or_404(Caso, pk=caso_id)
    if request.method == "POST":
        form = ParteProcesalForm(request.POST)
        if form.is_valid():
            parte = form.save(commit=False)
            parte.caso = caso
            parte.creado_por = request.user  # 👈 auditoría
            parte.save()
            messages.success(request, "Parte procesal añadida correctamente.")
            return redirect("casos:parte_list", caso_id=caso.id)
    else:
        form = ParteProcesalForm()
    return render(request, "casos/parte_form.html", {"form": form, "caso": caso})


# ======= EXPEDIENTES ======= #
def expediente_list(request):
    expedientes = Expediente.objects.select_related("caso").order_by("-fechaCreacion")
    return render(request, "casos/expediente_list.html", {"expedientes": expedientes})


def expediente_create(request, caso_id):
    caso = get_object_or_404(Caso, pk=caso_id)

    # Evita duplicar expediente por caso
    if hasattr(caso, "expediente"):
        messages.warning(request, "Este caso ya tiene un expediente asociado.")
        return redirect("casos:expediente_list")

    if request.method == "POST":
        form = ExpedienteForm(request.POST)
        if form.is_valid():
            expediente = form.save(commit=False)
            expediente.caso = caso
            expediente.creado_por = request.user  # 👈 auditoría
            expediente.save()
            messages.success(request, "Expediente creado correctamente.")
            return redirect("casos:expediente_list")
    else:
        form = ExpedienteForm()

    return render(request, "casos/expediente_form.html", {"form": form, "caso": caso})


# ======= CARPETAS ======= #
def carpeta_list(request, expediente_id):
    expediente = get_object_or_404(Expediente, pk=expediente_id)
    carpetas = Carpeta.objects.filter(expediente=expediente, carpetaPadre__isnull=True).order_by("nombre")

    return render(request, "casos/carpeta_list.html", {"expediente": expediente, "carpetas": carpetas})


def carpeta_create(request, expediente_id):
    expediente = get_object_or_404(Expediente, pk=expediente_id)

    if request.method == "POST":
        form = CarpetaForm(request.POST, expediente=expediente)
        if form.is_valid():
            carpeta = form.save(commit=False)
            carpeta.expediente = expediente

            # 👇 Solo si tu modelo Carpeta tiene campos de auditoría (creado_por)
            if hasattr(carpeta, "creado_por"):
                carpeta.creado_por = request.user

            carpeta.save()

            # 👇 Registrar evento en el timeline del expediente
            from .utils import registrar_evento_exp
            registrar_evento_exp(
                request.user,
                expediente,
                "CARPETA",
                f"Se creó la carpeta '{carpeta.nombre}'."
            )

            messages.success(request, f"Carpeta '{carpeta.nombre}' creada correctamente.")
            return redirect("casos:carpeta_list", expediente_id=expediente.id)
    else:
        form = CarpetaForm(expediente=expediente)

    return render(
        request,
        "casos/carpeta_form.html",
        {"form": form, "expediente": expediente},
    )


def carpeta_global_list(request):
    carpetas = Carpeta.objects.select_related("expediente", "carpetaPadre").order_by("expediente", "nombre")
    return render(request, "casos/carpeta_global_list.html", {"carpetas": carpetas})


# ======= TIMELINE DEL EXPEDIENTE ======= #

def expediente_timeline(request, expediente_id):
    """
    Muestra la línea de tiempo (timeline) de eventos asociados a un expediente.
    """
    expediente = get_object_or_404(Expediente, pk=expediente_id)
    eventos = expediente.eventos.select_related("usuario").order_by("-fecha")

    return render(
        request,
        "casos/expediente_timeline.html",
        {"expediente": expediente, "eventos": eventos},
    )

def expediente_detail(request, expediente_id):
    """
    Vista unificada del expediente:
    - Información general del expediente
    - Datos del caso
    - Timeline de eventos
    - Carpetas vinculadas
    """
    expediente = get_object_or_404(
        Expediente.objects.select_related("caso"), pk=expediente_id
    )
    eventos = expediente.eventos.select_related("usuario").order_by("-fecha")[:5]  # últimos 5 eventos
    carpetas = Carpeta.objects.filter(expediente=expediente, carpetaPadre__isnull=True).order_by("nombre")

    context = {
        "expediente": expediente,
        "eventos": eventos,
        "carpetas": carpetas,
    }
    return render(request, "casos/expediente_detail.html", context)

def expediente_by_caso(request, caso_id):
    caso = get_object_or_404(Caso, pk=caso_id)
    expediente = getattr(caso, "expediente", None)
    if expediente is None:
        expediente = Expediente.objects.create(
            caso=caso,
            nroExpediente=f"EXP-{caso.id:04d}",
            estado="ABIERTO",
            fechaCreacion=date.today(),
            creado_por=getattr(caso, "creado_por", None),
        )
    return redirect("casos:expediente_detail", expediente_id=expediente.id)





def carpeta_detalle(request, carpeta_id):
    """
    Muestra el contenido de una carpeta: subcarpetas y documentos asociados.
    """
    carpeta = get_object_or_404(Carpeta, pk=carpeta_id)

    # Subcarpetas directas
    subcarpetas = Carpeta.objects.filter(carpetaPadre=carpeta).order_by("nombre")

    # Documentos dentro de esta carpeta
    documentos = Documento.objects.filter(carpeta=carpeta).select_related(
        "tipoDocumento", "etapaProcesal"
    ).order_by("-fechaDoc")

    context = {
        "carpeta": carpeta,
        "subcarpetas": subcarpetas,
        "documentos": documentos,
    }

    return render(request, "casos/carpeta_detalle.html", context)


















from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Caso
from .forms import CasoForm, EquipoCasoForm, ParteProcesalForm
from actores.models import Actor, Cliente
from rest_framework import viewsets


def caso_list(request):
    casos = Caso.objects.all().order_by("-fechaInicio")
    return render(request, "casos/caso_list.html", {"casos": casos})


""" def caso_create(request):
    if request.method == "POST":
        form = CasoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Caso creado correctamente.")
            return redirect("casos:case_list")
    else:
        form = CasoForm()
    return render(request, "casos/caso_form.html", {"form": form}) """

def caso_edit(request, pk):
    caso = get_object_or_404(Caso, pk=pk)
    if request.method == "POST":
        form = CasoForm(request.POST, instance=caso)
        if form.is_valid():
            form.save()
            messages.success(request, "Caso actualizado correctamente.")
            return redirect("casos:case_list")
    else:
        form = CasoForm(instance=caso)
    return render(request, "casos/caso_form.html", {"form": form, "caso": caso})


# ======= EQUIPO DE CASO ======= #
def equipo_caso_list(request, caso_id):
    caso = get_object_or_404(Caso, pk=caso_id)
    equipo = caso.equipocaso_set.select_related("actor")
    return render(request, "casos/equipo_list.html", {"caso": caso, "equipo": equipo})


def equipo_caso_add(request, caso_id):
    caso = get_object_or_404(Caso, pk=caso_id)
    if request.method == "POST":
        form = EquipoCasoForm(request.POST)
        if form.is_valid():
            equipo = form.save(commit=False)
            equipo.caso = caso
            equipo.save()
            messages.success(request, "Actor agregado al equipo del caso.")
            return redirect("casos:equipo_list", caso_id=caso.id)
    else:
        form = EquipoCasoForm()
    return render(request, "casos/equipo_form.html", {"form": form, "caso": caso})


# ======= PARTE PROCESAL ======= #
def parte_procesal_list(request, caso_id):
    caso = get_object_or_404(Caso, pk=caso_id)
    partes = caso.parteprocesal_set.select_related("cliente")
    return render(request, "casos/parte_list.html", {"caso": caso, "partes": partes})


def parte_procesal_add(request, caso_id):
    caso = get_object_or_404(Caso, pk=caso_id)
    if request.method == "POST":
        form = ParteProcesalForm(request.POST)
        if form.is_valid():
            parte = form.save(commit=False)
            parte.caso = caso
            parte.save()
            messages.success(request, "Parte procesal añadida correctamente.")
            return redirect("casos:parte_list", caso_id=caso.id)
    else:
        form = ParteProcesalForm()
    return render(request, "casos/parte_form.html", {"form": form, "caso": caso})

#CasoViewSet

from .models import Caso
from .serializers import CasoSerializer

class CasoViewSet(viewsets.ModelViewSet):
    queryset = Caso.objects.all()
    serializer_class = CasoSerializer

#EquipoCasoViewSet
from rest_framework import viewsets
from .models import EquipoCaso
from .serializers import EquipoCasoSerializer

class EquipoCasoViewSet(viewsets.ModelViewSet):
    queryset = EquipoCaso.objects.all()
    serializer_class = EquipoCasoSerializer

#ParteProcesalViewSet
from rest_framework import viewsets
from .models import ParteProcesal
from .serializers import ParteProcesalSerializer

class ParteProcesalViewSet(viewsets.ModelViewSet):
    queryset = ParteProcesal.objects.all()
    serializer_class = ParteProcesalSerializer

#ExpedienteViewSet
from rest_framework import viewsets
from .models import Expediente
from .serializers import ExpedienteSerializer

class ExpedienteViewSet(viewsets.ModelViewSet):
    queryset = Expediente.objects.all()
    serializer_class = ExpedienteSerializer

#CarpetaViewSet
from rest_framework import viewsets
from .models import Carpeta
from .serializers import CarpetaSerializer

class CarpetaViewSet(viewsets.ModelViewSet):
    queryset = Carpeta.objects.all()
    serializer_class = CarpetaSerializer