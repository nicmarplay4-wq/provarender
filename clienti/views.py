from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import AppuntamentoForm

def prenota_appuntamento(request):
    if request.method == 'POST':
        form = AppuntamentoForm(request.POST)
        if form.is_valid():
            appuntamento = form.save()
            
            # Invia email al cliente
            send_mail(
                'Richiesta Appuntamento Ricevuta - Negozio Cucine',
                f"""
                Gentile {appuntamento.cliente.get_nome_completo()},
                
                Abbiamo ricevuto la sua richiesta di appuntamento per il giorno 
                {appuntamento.data_ora.strftime('%d/%m/%Y alle %H:%M')}.
                
                La contatteremo a breve per confermare.
                
                Cordiali saluti,
                Negozio Cucine
                """,
                settings.DEFAULT_FROM_EMAIL,
                [appuntamento.cliente.email],
                fail_silently=True,
            )
            
            # Invia notifica all'admin
            send_mail(
                'Nuova Richiesta Appuntamento',
                f"""
                Nuovo appuntamento richiesto:
                Cliente: {appuntamento.cliente.get_nome_completo()}
                Email: {appuntamento.cliente.email}
                Telefono: {appuntamento.cliente.telefono}
                Data: {appuntamento.data_ora.strftime('%d/%m/%Y alle %H:%M')}
                Tipo: {appuntamento.get_tipo_consulenza_display()}
                """,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=True,
            )
            
            messages.success(
                request,
                'Appuntamento richiesto con successo! Riceverai una conferma via email.'
            )
            return redirect('clienti:appuntamento_successo')
    else:
        form = AppuntamentoForm()
    
    return render(request, 'clienti/prenota_appuntamento.html', {'form': form})

def appuntamento_successo(request):
    return render(request, 'clienti/appuntamento_successo.html')
