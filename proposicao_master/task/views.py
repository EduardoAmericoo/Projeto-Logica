from django.shortcuts import render, redirect
from .models import Jogador
from .forms import JogadorForm
# Create your views here.


def jogo_view(request):
    return render(request, 'home.html')


valores_iniciais = {'p': 'F', 'q': 'F', 'r': 'F'}

def game_view(request):
    valores = request.session.get('valores', valores_iniciais.copy())
    dicas = [
        "Lembre-se: '~p' significa a negação de p.",
        "Para o operador '^', ambas as proposições devem ser verdadeiras.",
        "Tente ajustar os valores para que cada proposição atenda à condição correta."
    ]
    dicas_vistas = request.session.get('dicas_vistas', 0)
    verificacoes = request.session.get('verificacoes', 0)  # Contagem de verificações
    resultado = None
    resposta_correta = {'p': 'V', 'q': 'V', 'r': 'F'}

    if request.method == 'POST':
        if 'mostrar_dica' in request.POST and dicas_vistas < len(dicas):
            dicas_vistas += 1
        elif 'toggle' in request.POST:
            letra = request.POST['toggle']
            valores[letra] = 'V' if valores[letra] == 'F' else 'F'
        elif 'verificar' in request.POST:
            verificacoes += 1  # Incrementa a contagem de verificações
            if valores == resposta_correta:
                resultado = f"Parabéns! Você acertou com {verificacoes} tentativas."
                # Aqui você pode salvar a contagem no banco de dados, por exemplo:
                # Jogador.objects.create(nome=request.session['nome'], pontuacao=verificacoes)
            else:
                resultado = "Algumas respostas estão incorretas. Tente novamente!"

        # Atualiza a sessão
        request.session['valores'] = valores
        request.session['dicas_vistas'] = dicas_vistas
        request.session['verificacoes'] = verificacoes

    return render(request, 'game.html', {
        'valores': valores,
        'resultado': resultado,
        'dica_atual': dicas[dicas_vistas - 1] if dicas_vistas > 0 else None,
        'mostrar_dica': dicas_vistas < len(dicas),
    })

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
