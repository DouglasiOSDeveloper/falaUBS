import json
import os
from django.shortcuts import render, redirect
from pathlib import Path
from django.conf import settings

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
    user_data = request.session.get('usuario')
    if not user_data:
        return redirect('login')  # Garantir autenticação

    # Carrega dados das UBSs
    json_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'ubs_data.json')
    with open(json_path, 'r', encoding='utf-8') as file:
        ubs_data = json.load(file)

    # Serializa para string JSON segura
    ubs_data_json = json.dumps(ubs_data, ensure_ascii=False)

    return render(request, 'core/scheduling.html', {
        'ubs_data': ubs_data_json,
        'user_data': user_data
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

    # MOCK de agendamentos apenas para exibição inicial
    agendamentos_mock = [
        {
            'tipo': 'Consulta',
            'especialidade': 'Pediatra',
            'ubs': 'UBS Norte',
            'data': '2025-06-19',
            'hora': '09:00',
            'status': 'Pendente',
            'protocolo': 'ANP685',
            'documentos': ['laudo_exame.pdf']
        },
        {
            'tipo': 'Exame',
            'especialidade': 'Ginecologia',
            'ubs': 'UBS Central',
            'data': '2025-05-25',
            'hora': '11:00',
            'status': 'Concluído',
            'protocolo': 'VYYG85',
            'documentos': []
        },
        {
            'tipo': 'Consulta',
            'especialidade': 'Clínico geral',
            'ubs': 'UBS Central',
            'data': '2025-05-10',
            'hora': '08:00',
            'status': 'Cancelado',
            'protocolo': 'JYCG8',
            'documentos': []
        }
    ]

    return render(request, 'core/agenda_pessoal.html', {
        'usuario': user,
        'agendamentos': agendamentos_mock
    })
