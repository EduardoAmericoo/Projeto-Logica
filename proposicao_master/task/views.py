from django.shortcuts import render, redirect
from .models import Jogador, PlayerScore
from .forms import JogadorForm
# Create your views here.


def jogo_view(request):
    return render(request, 'home.html')

# Exibir a leaderboard


def leaderboard_view(request):
    jogadores = Jogador.objects.order_by('-pontuacao')[:10]
    return render(request, 'leaderboard.html', {'jogadores': jogadores})


def inicio_jogo_view(request):
    if request.method == 'POST':
        form = JogadorForm(request.POST)
        if form.is_valid():
            jogador = form.save()  # Salva o nome do jogador no banco de dados
            # Redireciona para o leaderboard após o envio
            return redirect('leaderboard')
    else:
        form = JogadorForm()
    jogadores = Jogador.objects.order_by('-pontuacao')[:5]
    return render(request, 'home.html', {'jogadores': jogadores})

def endgame_view(request):
    # Recuperar o jogador atual (supondo que o nome esteja salvo na sessão)
    jogador_nome = request.session.get('jogador_nome', 'Jogador Desconhecido')
    jogador = Jogador.objects.filter(nome=jogador_nome).first()

    # Preparar o contexto com informações do jogador ou valores padrão se o jogador não for encontrado
    context = {
        'jogador_nome': jogador.nome if jogador else 'Desconhecido',
        'pontuacao': jogador.pontuacao if jogador else 0,
        'tentativas': jogador.tentativas if jogador else 'N/A',
        'tempo_gasto': jogador.tempo_gasto if jogador else 'N/A'
    }

    return render(request, 'endgame.html', context)
