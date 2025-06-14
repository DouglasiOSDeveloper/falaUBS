from django.shortcuts import render, redirect

# Mocks de usuários
MOCK_USERS = [
    {
        'cpf': '111.111.111-11',
        'senha': 'senha123',
        'nome': 'João Silva',
        'idade': 35,
        'tipo': 'cidadao'
    },
    {
        'cpf': '222.222.222-22',
        'senha': 'senha456',
        'nome': 'Maria Oliveira',
        'idade': 28,
        'tipo': 'cidadao'
    }
]

MOCK_PROFISSIONAIS = [
    {
        'cpf': '333.333.333-33',
        'senha': 'prof123',
        'nome': 'Dr. Carlos Mendes',
        'ubs': 'UBS Central',
        'tipo': 'profissional'
    },
    {
        'cpf': '444.444.444-44',
        'senha': 'prof456',
        'nome': 'Enf. Ana Costa',
        'ubs': 'UBS Norte',
        'tipo': 'profissional'
    }
]

# Dados mockados
mock_vaccines = [
    {
        "name": "Hepatite B",
        "description": "Protege contra a hepatite B",
        "age_group": "Criança, Adulto",
        "status": "Disponível",
        "unit": "UBS Central",
        "scheduling": "Agendamento necessário"
    },
    {
        "name": "Tríplice Viral",
        "description": "Contra sarampo, caxumba e rubéola",
        "age_group": "Criança, Adolescente",
        "status": "Disponível",
        "unit": "UBS Sul",
        "scheduling": "Livre demanda"
    },
    # Pode adicionar mais mockados aqui se quiser
]

# Página de Login
def login_view(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        codigo = request.POST.get('codigo')  # não será usado agora

        # Verifica cidadão
        for user in MOCK_USERS:
            if user['cpf'] == cpf and user['senha'] == senha:
                request.session['usuario'] = user
                return redirect('home')

        # Verifica profissional
        for prof in MOCK_PROFISSIONAIS:
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
    return render(request, 'core/vaccination.html', {'vaccines': mock_vaccines})

# Página de Agendamento
def scheduling_view(request):
    return render(request, 'core/scheduling.html')

# Página de UBS Próximas
def ubs_nearby_view(request):
    return render(request, 'core/ubs_nearby.html')

# Página de UBS Específica
def ubs_detail_view(request, ubs_name):
    context = {
        'ubs_name': ubs_name
    }
    return render(request, 'core/ubs_detail.html', context)
