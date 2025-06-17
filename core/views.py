import json
import os
import uuid
from django.shortcuts import render, redirect
from pathlib import Path
from django.conf import settings
from .models import Agendamento
from uuid import uuid4

# Mocks de usuários JSON
def carregar_usuarios_mock():
    path = os.path.join(settings.BASE_DIR, 'core', 'data', 'usuarios.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# Mocks de profissionais JSON
def carregar_profissionais_mock():
    path = os.path.join(settings.BASE_DIR, 'core', 'data', 'profissionais.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# Página de Login
def login_view(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')

        usuarios = carregar_usuarios_mock()
        profissionais = carregar_profissionais_mock()

        for user in usuarios:
            if user['cpf'] == cpf and user['senha'] == senha:
                request.session['usuario'] = user
                return redirect('home')

        for prof in profissionais:
            if prof['cpf'] == cpf and prof['senha'] == senha:
                request.session['usuario'] = prof
                return redirect('home')

        return render(request, 'core/login.html', {'erro': 'CPF ou senha incorretos.'})

    return render(request, 'core/login.html')

# Página de Home
def home_view(request):
    user = request.session.get('usuario')
    if not user:
        return redirect('login')
    return render(request, 'core/home.html', {'usuario': user})

# Página de Vacinação
def vaccination_view(request):
    json_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'ubs_data.json')

    with open(json_path, 'r', encoding='utf-8') as file:
        ubs_data = json.load(file)

    vaccines = []
    for ubs in ubs_data.get("ubsList", []):
        for vaccine in ubs.get("vaccines", []):
            # Mapeia o campo corretamente
            vaccines.append({
                "name": vaccine["name"],
                "description": vaccine["description"],
                "age_group": vaccine["ageGroup"],  # <-- esse é o ponto importante
                "status": vaccine["status"],
                "scheduling": vaccine["scheduling"],
                "unit": vaccine["unit"]
            })

    return render(request, 'core/vaccination.html', {'vaccines': vaccines})


# Página de Agendamento
def scheduling_view(request):
    user = request.session.get('usuario')
    if not user:
        return redirect('login')

    # carrega dados das UBSs para popular os selects
    json_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'ubs_data.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        ubs_data = json.load(f)

    if request.method == 'POST':
        # lê os campos do form
        tipo         = request.POST.get('tipo')
        especialidade = request.POST.get('especialidade', '')
        ubs_name     = request.POST.get('ubs')
        data         = request.POST.get('data')
        hora         = request.POST.get('hora')

        # cria o agendamento no banco
        Agendamento.objects.create(
            protocolo    = uuid4(),
            usuario_id   = user['cpf'],
            tipo         = tipo,
            especialidade = especialidade,
            ubs          = ubs_name,
            data         = data,
            hora         = hora,
            status       = 'Pendente',
        )

        return redirect('agenda_pessoal')

    return render(request, 'core/scheduling.html', {
        'ubs_data': json.dumps(ubs_data, ensure_ascii=False),
        'user_data': user,
    })


# Página de UBS Próximas
def ubs_nearby_view(request):
    json_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'ubs_data.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ubs_list = []
    for ubs in data.get('ubsList', []):
        ubs_list.append({
            'name': ubs['name'],
            'address': ubs['address'],
            'district': ubs.get('district', 'Centro'),
            'phone': ubs['phone'],
            'hours': ubs['openingHours'],
            'services': ubs['services'],
            'vaccines': [v['name'] for v in ubs['vaccines']],
            'accessibility': ubs['accessibility'],
            'age_groups': list({v['ageGroup'] for v in ubs['vaccines']}),
            'distance_km': 1.2
        })

    # EXTRAÇÃO FORA DO LOOP
    vaccine_names = sorted({
        v['name']
        for ubs in data.get('ubsList', [])
        for v in ubs.get('vaccines', [])
    })

    service_names = sorted({
        s
        for ubs in data.get('ubsList', [])
        for s in ubs.get('services', [])
    })

    return render(request, 'core/ubs_nearby.html', {
        'ubs_list': ubs_list,
        'vaccine_names': vaccine_names,
        'service_names': service_names
    })

# Página de UBS Específica
def ubs_detail_view(request, ubs_name):
    data = load_mock_ubs_data()
    ubs = next((u for u in data['ubsList'] if u['name'] == ubs_name), None)

    if not ubs:
        return render(request, 'core/ubs_detail.html', {'ubs': None})

    return render(request, 'core/ubs_detail.html', {'ubs': ubs})

#Load dos dados mockados das UBSs
def load_mock_ubs_data():
    file_path = Path(__file__).resolve().parent / 'data' / 'ubs_data.json'
    with open(file_path, encoding='utf-8') as f:
        return json.load(f)

# Página de Agenda Pessoal
def personal_schedule_view(request):
    user = request.session.get('usuario')
    if not user:
        return redirect('login')

    # Inicializa lista de agendamentos na sessão, se necessário
    if 'agendamentos' not in request.session:
        request.session['agendamentos'] = []

    # === POST: criação, remarcação ou cancelamento (mantém igual) ===
    if request.method == 'POST':
        action    = request.POST.get('action')
        protocolo = request.POST.get('protocol')
        ags       = request.session.get('agendamentos', [])

        if action and protocolo:
            for ag in ags:
                if ag['protocolo'] == protocolo:
                    if action == 'cancel':
                        ag['status'] = 'Cancelado'
                    elif action == 'reschedule':
                        ag['data']   = request.POST.get('new_date')
                        ag['hora']   = request.POST.get('new_time')
                        ag['status'] = 'Pendente'
                    break
        else:
            # criação de novo agendamento
            tipo          = request.POST.get('tipo')
            especialidade = request.POST.get('especialidade', '')
            ubs           = request.POST.get('ubs')
            data          = request.POST.get('data')
            hora          = request.POST.get('hora')
            new_proto     = str(uuid.uuid4())[:8].upper()

            novo = {
                'tipo': tipo,
                'especialidade': especialidade or ('Vacinação' if tipo == 'Exame' else ''),
                'ubs': ubs,
                'data': data,
                'hora': hora,
                'status': 'Pendente',
                'protocolo': new_proto,
                'documentos': []
            }
            ags.insert(0, novo)

        request.session['agendamentos'] = ags
        return redirect('agenda_pessoal')

    # === GET: exibe e filtra agendamentos ===

    # Carrega todos os agendamentos da sessão
    agendamentos = request.session.get('agendamentos', []).copy()

    # Obtém parâmetros de busca/filtro
    q            = request.GET.get('q', '').strip().lower()
    status_f     = request.GET.get('status', '')
    tipo_f       = request.GET.get('tipo', '')
    espec_f      = request.GET.get('especialidade', '')
    ubs_f        = request.GET.get('ubs', '')
    date_from    = request.GET.get('date_from', '')
    date_to      = request.GET.get('date_to', '')

    def in_range(date_str):
        # compara date_str (YYYY-MM-DD) com os limites, se fornecidos
        if date_from and date_str < date_from:
            return False
        if date_to and date_str > date_to:
            return False
        return True

    filtered = []
    for ag in agendamentos:
           # filtro de texto livre (q) sobre tipo, especialidade, status, protocolo ou UBS
        if q:
            hay = f"{ag['tipo']} {ag['especialidade']} {ag['status']} {ag['protocolo']} {ag['ubs']}".lower()
            if q not in hay:
                continue

        # filtros específicos (acumulativos)
        if status_f and ag['status'] != status_f:
            continue
        if tipo_f   and ag['tipo']   != tipo_f:
            continue
        if espec_f  and ag['especialidade'] != espec_f:
            continue
        if ubs_f     and ag['ubs']    != ubs_f:
            continue
        if (date_from or date_to) and not in_range(ag['data']):
            continue

        filtered.append(ag)

    # Carrega dados das UBSs só para o JS da modal (permanece igual)
    json_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'ubs_data.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        ubs_data = json.load(f)
        
        
    # Gera listas de opções para filtros
    status_choices = ['Pendente', 'Concluído', 'Cancelado']
    tipo_choices   = ['Consulta', 'Exame']
    # Remove None ou string vazia antes de ordenar
    espec_choices = sorted({
    ag.get('especialidade')
    for ag in agendamentos
        if ag.get('especialidade')
    })
    ubs_choices = sorted({
    ag.get('ubs')
    for ag in agendamentos
        if ag.get('ubs')
    })

    return render(request, 'core/agenda_pessoal.html', {
        'usuario': user,
        'agendamentos': filtered,
        'ubs_data': json.dumps(ubs_data, ensure_ascii=False),

        # Também repassamos os valores atuais dos filtros para o template,
        # assim podemos marcar as opções selecionadas nos <select> e preencher o input:
        'filter_q': q,
        'filter_status': status_f,
        'filter_tipo': tipo_f,
        'filter_especialidade': espec_f,
        'filter_ubs': ubs_f,
        'filter_date_from': date_from,
        'filter_date_to': date_to,
        'status_choices': status_choices,
        'tipo_choices': tipo_choices,
        'espec_choices': espec_choices,
        'ubs_choices': ubs_choices,
    })