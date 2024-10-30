from django.shortcuts import render, redirect
from .models import Jogador
from .forms import JogadorForm
# Create your views here.


def jogo_view(request):
    return render(request, 'home.html')

def game_view(request):
    return render(request, 'game.html')

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
