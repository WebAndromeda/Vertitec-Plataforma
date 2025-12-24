from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from utils.decorators import roles_required
from django.contrib.auth.decorators import login_required
from schedule.models import schedule
from .models import Report
from .forms import ReportForm, ReportFilterForm
import datetime
from django.db.models import Case, When, IntegerField
from django.core.paginator import Paginator
from django.contrib import messages
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from io import BytesIO
import tempfile
from django.http import FileResponse


# Vista para crear reporte
@roles_required("Administrador", "Técnico")
def createReport(request, schedule_id):

    sched = get_object_or_404(schedule, id=schedule_id)

    # Obtener el edificio correcto
    building = sched.tower.building
    building_name = building.user.first_name   

    # ---------- MÉTODO GET ----------
    if request.method == "GET":

        # Obtiene o crea el reporte
        report, created = Report.objects.get_or_create(
            schedule=sched,
            defaults={"check_in_time": timezone.localtime().time()}
        )

        # Si es la primera vez → Cambiar estado a "En producción"
        if created:
            sched.status = "in_production"
            sched.save()

            hora_inicial = report.check_in_time.strftime("%H:%M")

            messages.success(
                request,
                f"✅ Haz iniciado el reporte correctamente en {building_name} a las {hora_inicial}."
            )

        else:
            hora_registrada = report.check_in_time.strftime("%H:%M")
            messages.info(
                request,
                f"ℹ️ Ya habías iniciado este reporte en {building_name} a las {hora_registrada}."
            )

        form = ReportForm(instance=report)

        return render(request, "createReport.html", {
            "schedule": sched,
            "report": report,
            "form": form,
        })

    
    # ---------- MÉTODO POST ----------
    if request.method == "POST":
        
        report = get_object_or_404(Report, schedule=sched)
        form = ReportForm(request.POST, instance=report)

        if form.is_valid():

            updated_report = form.save(commit=False)

            # Registrar automáticamente la hora de salida
            updated_report.check_out_time = timezone.localtime().time()

            # Calcular automáticamente time_spent
            if updated_report.check_in_time and updated_report.check_out_time:
                t1 = datetime.datetime.combine(timezone.now().date(), updated_report.check_in_time)
                t2 = datetime.datetime.combine(timezone.now().date(), updated_report.check_out_time)
                updated_report.time_spent = t2 - t1

            updated_report.save()

            # Cambiar status del agendamiento a "Realizado"
            sched.status = "complete"
            sched.save()

            messages.success(
                request,
                f"✅ El reporte del edificio {building_name} fue finalizado correctamente."
            )

            # 🔁 Redirigir al listado de reportes
            return redirect("listReports")
        

# Vista para descargar reporte
@login_required
def download_report_pdf(request, report_id):

    report = get_object_or_404(Report, id=report_id)
    sched = report.schedule
    building = sched.tower.building

    # ----------------------------
    # SEGURIDAD POR ROL
    # ----------------------------
    if request.user.groups.filter(name="Técnico").exists():
        if sched.technician != request.user:
            return HttpResponse("No autorizado", status=403)

    if request.user.groups.filter(name="Cliente").exists():
        if sched.client != request.user:
            return HttpResponse("No autorizado", status=403)

    # ----------------------------
    # GENERAR PDF TEMPORAL
    # ----------------------------
    html_content = render_to_string("report_pdf_template.html", {
        "schedule": sched,
        "report": report,
        "building": building,
        "technician": sched.technician,
    })

    temp_pdf = tempfile.NamedTemporaryFile(delete=True, suffix=".pdf")

    HTML(
        string=html_content,
        base_url=request.build_absolute_uri('/')  # 🔥 CLAVE PARA FUENTES
    ).write_pdf(target=temp_pdf.name)

    temp_pdf.seek(0)

    # ----------------------------
    # DESCARGA
    # ----------------------------
    return FileResponse(
        temp_pdf,
        as_attachment=True,
        filename=f"Reporte_{sched.id}.pdf"
    )


# Vista para listar los reportes
@login_required
def listReports(request):

    # ----------------------------
    # QUERYSET BASE
    # ----------------------------
    # Se priorizan primero los reportes "En producción"
    # y luego se ordenan por fecha (más recientes primero)
    reports = Report.objects.select_related(
        "schedule",
        "schedule__tower",
        "schedule__tower__building",
        "schedule__tower__building__user"
    ).annotate(
        # Campo virtual para priorizar el estado
        status_priority=Case(
            When(schedule__status="in_production", then=0),  # 👈 Primero
            default=1,                                      # 👈 El resto después
            output_field=IntegerField(),
        )
    ).order_by(
        "status_priority",        # 1️⃣ Orden por estado
        "-schedule__date"         # 2️⃣ Orden por fecha
    )

    # ----------------------------
    # FORMULARIO DE FILTROS
    # ----------------------------
    form = ReportFilterForm(request.GET or None)

    if form.is_valid():
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        technician = form.cleaned_data.get("technician")
        building_name = form.cleaned_data.get("building")
        status = form.cleaned_data.get("status")
        programmed = form.cleaned_data.get("programmed")

        # ----------------------------
        # FILTRO POR FECHA / RANGO
        # ----------------------------
        if start_date:
            reports = reports.filter(schedule__date__gte=start_date)

        if end_date:
            reports = reports.filter(schedule__date__lte=end_date)

        # ----------------------------
        # FILTRO POR TÉCNICO
        # ----------------------------
        if technician:
            reports = reports.filter(schedule__technician=technician)

        # ----------------------------
        # FILTRO POR EDIFICIO
        # schedule -> tower -> building -> user -> first_name
        # ----------------------------
        if building_name:
            reports = reports.filter(
                schedule__tower__building__user__first_name__icontains=building_name
            )

        # ----------------------------
        # FILTRO POR ESTADO
        # ----------------------------
        if status:
            reports = reports.filter(schedule__status=status)

        # ----------------------------
        # FILTRO POR PROGRAMADO / NO PROGRAMADO
        # ----------------------------
        if programmed:
            reports = reports.filter(schedule__programmed=programmed)

    # ----------------------------
    # FILTRO POR ROL DEL USUARIO
    # ----------------------------
    # Administrador → ve todos
    if request.user.groups.filter(name="Administrador").exists():
        pass

    # Técnico → solo sus reportes
    elif request.user.groups.filter(name="Técnico").exists():
        reports = reports.filter(schedule__technician=request.user)

    # Cliente → solo sus reportes
    else:
        reports = reports.filter(schedule__client=request.user)

    # ----------------------------
    # PAGINACIÓN
    # ----------------------------
    paginator = Paginator(reports, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ----------------------------
    # FORMATEAR time_spent PARA EL TEMPLATE
    # ----------------------------
    for report in page_obj:
        if report.time_spent:
            total_seconds = int(report.time_spent.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            report.time_spent_formatted = f"{hours}h {minutes}min"
        else:
            report.time_spent_formatted = ""

    return render(request, 'listReports.html', {
        "reports": page_obj,
        "form": form,
    })



# Vista para eliminar reporte
@roles_required("Administrador", "Técnico")
def deleteReport(request, report_id):

    # ✅ Mensaje de éxito y redirección al listado
    messages.success(request, "✅ El reporte se ha eliminado.")

    report = get_object_or_404(Report, id=report_id)

    # Guardar el schedule antes de borrar el reporte
    sched = report.schedule

    # Eliminar el reporte
    report.delete()

    # Resetear estado del agendamiento
    sched.status = "to_be_done"
    sched.save()

    return redirect("listReports")