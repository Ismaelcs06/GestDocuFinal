from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Documento, VersionDocumento, TipoDocumento, EtapaProcesal
from .forms import DocumentoForm, VersionDocumentoForm, TipoDocumentoForm, EtapaProcesalForm
from django.db.models import Max
from django.utils import timezone
from casos.models import Carpeta
from django.db.models import Q
from datetime import datetime
from django.core.paginator import Paginator
# Create your views here.


# ======= DOCUMENTOS ======= #

def documento_list(request):
    """
    Lista los documentos con filtros, paginación, orden dinámico y búsqueda.
    """
    # 🔹 Captura de parámetros
    q = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "")
    etapa = request.GET.get("etapa", "")
    desde = request.GET.get("desde", "")
    hasta = request.GET.get("hasta", "")
    ordenar = request.GET.get("ordenar", "-fechaDoc")

    # 🔹 Consulta base
    documentos = Documento.objects.select_related("carpeta", "tipoDocumento", "etapaProcesal").all()

    # 🔍 Búsqueda por texto o palabra clave
    if q:
        documentos = documentos.filter(
            Q(nombreDocumento__icontains=q) | Q(palabraClave__icontains=q)
        )

    # 🔍 Filtros específicos
    if tipo:
        documentos = documentos.filter(tipoDocumento__id=tipo)

    if etapa:
        documentos = documentos.filter(etapaProcesal__id=etapa)

    # 🔍 Rango de fechas
    if desde:
        try:
            documentos = documentos.filter(fechaDoc__gte=datetime.strptime(desde, "%Y-%m-%d").date())
        except ValueError:
            pass

    if hasta:
        try:
            documentos = documentos.filter(fechaDoc__lte=datetime.strptime(hasta, "%Y-%m-%d").date())
        except ValueError:
            pass

    # 🔄 Orden dinámico
    if ordenar in ["nombreDocumento", "-nombreDocumento", "fechaDoc", "-fechaDoc"]:
        documentos = documentos.order_by(ordenar)
    else:
        documentos = documentos.order_by("-fechaDoc")

    # 📄 Paginación
    paginator = Paginator(documentos, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # 📦 Contexto
    context = {
        "documentos": page_obj,
        "page_obj": page_obj,
        "tipos": TipoDocumento.objects.filter(activo=True).order_by("nombre"),
        "etapas": EtapaProcesal.objects.filter(estado="ACTIVO").order_by("nombre"),
        "q": q,
        "tipo": tipo,
        "etapa": etapa,
        "desde": desde,
        "hasta": hasta,
        "ordenar": ordenar,
    }

    return render(request, "documentos/documento_list.html", context)


def documento_create(request):
    """
    Crea un nuevo documento. Si se pasa ?carpeta=<id>, el documento
    se asocia automáticamente a esa carpeta y el formulario se preinicializa.
    """
    carpeta_id = request.GET.get("carpeta")
    carpeta_preseleccionada = None

    # Si viene una carpeta específica
    if carpeta_id:
        carpeta_preseleccionada = get_object_or_404(Carpeta, pk=carpeta_id)

    if request.method == "POST":
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.creado_por = request.user

            # Asigna carpeta preseleccionada si corresponde
            if carpeta_preseleccionada:
                documento.carpeta = carpeta_preseleccionada

            documento.save()

            # 🧾 Registrar evento en el timeline del expediente
            try:
                from casos.utils import registrar_evento_exp
                expediente = documento.carpeta.expediente
                registrar_evento_exp(
                    request.user,
                    expediente,
                    "DOCUMENTO",
                    f"Se registró el documento '{documento.nombreDocumento}'."
                )
            except Exception as e:
                print("⚠️ No se pudo registrar evento de documento:", e)

            messages.success(request, f"Documento '{documento.nombreDocumento}' registrado correctamente.")

            # Si venía desde una carpeta, volver allí
            if carpeta_preseleccionada:
                return redirect("documentos:carpeta_detalle", carpeta_id=carpeta_preseleccionada.id)
            else:
                return redirect("documentos:documento_list")

        else:
            messages.error(request, "Corrige los errores del formulario antes de continuar.")
    else:
        form = DocumentoForm(initial={"carpeta": carpeta_preseleccionada})

    context = {"form": form, "carpeta": carpeta_preseleccionada}
    return render(request, "documentos/documento_form.html", context)


def documento_edit(request, doc_id):
    documento = get_object_or_404(Documento, pk=doc_id)
    if request.method == "POST":
        form = DocumentoForm(request.POST, request.FILES, instance=documento)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.modificado_por = request.user  # 👈 registra quién lo editó
            documento.save()
            messages.success(request, "Documento actualizado correctamente.")
            return redirect("documentos:documento_list")
    else:
        form = DocumentoForm(instance=documento)
    return render(request, "documentos/documento_form.html", {"form": form, "documento": documento})


# ======= VERSIONES ======= #
def version_list(request, doc_id):
    documento = get_object_or_404(Documento, pk=doc_id)
    versiones = documento.versiones.select_related("creado_por").all()
    return render(request, "documentos/version_list.html", {"documento": documento, "versiones": versiones})


def version_create(request, doc_id):
    documento = get_object_or_404(Documento, pk=doc_id)

    if request.method == "POST":
        form = VersionDocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            ultima = documento.versiones.aggregate(Max("numeroVersion"))["numeroVersion__max"] or 0
            nueva = form.save(commit=False)
            nueva.documento = documento
            nueva.creado_por = request.user
            nueva.numeroVersion = ultima + 1
            nueva.fechaCambio = timezone.now()
            nueva.save()

            # 🧾 Registrar evento en el timeline del expediente
            try:
                from casos.utils import registrar_evento_exp
                expediente = documento.carpeta.expediente
                registrar_evento_exp(
                    request.user,
                    expediente,
                    "VERSION",
                    f"Se creó la versión {nueva.numeroVersion} del documento '{documento.nombreDocumento}'."
                )
            except Exception as e:
                print("⚠️ No se pudo registrar evento de versión:", e)

            # (Opcional) Registrar en bitácora si la tienes activa
            try:
                from seguridad.signals import registrar_detalle
                registrar_detalle(
                    request.user,
                    "Nueva versión",
                    "VersionDocumento",
                    f"Versión {nueva.numeroVersion} creada para {documento.nombreDocumento}"
                )
            except Exception as e:
                print("⚠️ No se pudo registrar detalle de bitácora:", e)

            messages.success(request, f"Versión {nueva.numeroVersion} registrada correctamente.")
            return redirect("documentos:version_list", doc_id=documento.id)
    else:
        form = VersionDocumentoForm()

    return render(request, "documentos/version_form.html", {"form": form, "documento": documento})



# === TIPO DE DOCUMENTO ===

def tipo_documento_list(request):
    tipos = TipoDocumento.objects.all().order_by("nombre")
    return render(request, "documentos/tipo_documento_list.html", {"tipos": tipos})


def tipo_documento_create(request):
    if request.method == "POST":
        form = TipoDocumentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tipo de documento creado correctamente.")
            return redirect("documentos:tipo_documento_list")
    else:
        form = TipoDocumentoForm()
    return render(request, "documentos/tipo_documento_form.html", {"form": form})


# === ETAPA PROCESAL ===

def etapa_procesal_list(request):
    etapas = EtapaProcesal.objects.all().order_by("nombre")
    return render(request, "documentos/etapa_procesal_list.html", {"etapas": etapas})


def etapa_procesal_create(request):
    if request.method == "POST":
        form = EtapaProcesalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Etapa procesal creada correctamente.")
            return redirect("documentos:etapa_procesal_list")
    else:
        form = EtapaProcesalForm()
    return render(request, "documentos/etapa_procesal_form.html", {"form": form})

# PARA NAVEGACION DEL CONTENIDO EN LAS CARPETAS

def carpeta_detalle(request, carpeta_id=None):
    if carpeta_id:
        carpeta = get_object_or_404(Carpeta, pk=carpeta_id)
        subcarpetas = Carpeta.objects.filter(carpetaPadre=carpeta)
        documentos = Documento.objects.filter(carpeta=carpeta)
    else:
        carpeta = None
        subcarpetas = Carpeta.objects.filter(carpetaPadre__isnull=True)
        documentos = Documento.objects.none()

    return render(
        request,
        "documentos/carpeta_detalle.html",
        {"carpeta": carpeta, "subcarpetas": subcarpetas, "documentos": documentos},
    )


#TipoDocumentoViewSet
from rest_framework import viewsets
from .models import TipoDocumento
from .serializers import TipoDocumentoSerializer

class TipoDocumentoViewSet(viewsets.ModelViewSet):
    queryset = TipoDocumento.objects.all()
    serializer_class = TipoDocumentoSerializer

#EtapaProcesalViewSet
from .models import EtapaProcesal
from .serializers import EtapaProcesalSerializer

class EtapaProcesalViewSet(viewsets.ModelViewSet):
    queryset = EtapaProcesal.objects.all()
    serializer_class = EtapaProcesalSerializer

#DocumentoViewSet
from .models import Documento
from .serializers import DocumentoSerializer

class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer

#VersionDocumentoViewSet
from .models import VersionDocumento
from .serializers import VersionDocumentoSerializer

class VersionDocumentoViewSet(viewsets.ModelViewSet):
    queryset = VersionDocumento.objects.all()
    serializer_class = VersionDocumentoSerializer
