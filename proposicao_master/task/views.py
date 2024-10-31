from django.shortcuts import render, redirect
from .models import Jogador
from .forms import JogadorForm

# Proposições e respostas corretas para cada fase
proposicoes_fases = [
    {"proposicao": "p → q ∧ ~r", "resposta_correta": {'p': 'F', 'q': 'V', 'r': 'F'},
     "dicas": ["Lembre-se: a proposição implica que p deve ser falso se q é verdadeiro.", "Tente ajustar r para falso também."]},
    {"proposicao": "(p ∧ q) → ~r", "resposta_correta": {'p': 'V', 'q': 'V', 'r': 'F'},
     "dicas": ["A implicação é verdadeira se r é falso quando p e q são verdadeiros.", "Tente ajustar p e q para verdadeiros."]},
    {"proposicao": "~p ∨ (q ↔ r)", "resposta_correta": {'p': 'F', 'q': 'V', 'r': 'V'},
     "dicas": ["Lembre-se que ~p significa que p é falso.", "Verifique a equivalência entre q e r."]},
    {"proposicao": "(p ↔ q) ∧ (q → ~r)", "resposta_correta": {'p': 'V', 'q': 'V', 'r': 'F'},
     "dicas": ["A equivalência entre p e q deve ser verdadeira.", "Lembre-se: se q é verdadeiro, então r precisa ser falso."]},
    {"proposicao": "(p ∨ ~q) → (r ∧ q)", "resposta_correta": {'p': 'F', 'q': 'V', 'r': 'V'},
     "dicas": ["A implicação deve ser verdadeira com r e q como verdadeiros.", "Verifique se p é falso e q é verdadeiro para atender a condição."]}
]


def game_view(request):
    # Carregar a fase atual e dados do jogador da sessão
    fase_atual = request.session.get('fase_atual', 1)
    valores = request.session.get('valores', valores_iniciais.copy())
    verificacoes = request.session.get('verificacoes', 0)
    jogador_id = request.session.get('jogador_id')
    resultado = None

    # Verificar se o jogador_id existe e é válido
    if not jogador_id or not Jogador.objects.filter(id=jogador_id).exists():
        # Redirecionar para a página inicial se o jogador não estiver registrado
        return redirect('home')

    # Obter o jogador com segurança
    jogador = Jogador.objects.get(id=jogador_id)

    # Proposição e controle de dicas da fase atual
    proposicao_atual = proposicoes_fases[fase_atual - 1]
    dicas_vistas = request.session.get('dicas_vistas', 0)
    dica_atual = proposicao_atual["dicas"][dicas_vistas] if dicas_vistas < len(proposicao_atual["dicas"]) else None

    if request.method == 'POST':
        if 'mostrar_dica' in request.POST:
            if dicas_vistas < len(proposicao_atual["dicas"]):
                dicas_vistas += 1
        elif 'toggle' in request.POST:
            letra = request.POST['toggle']
            valores[letra] = 'V' if valores[letra] == 'F' else 'F'
        elif 'verificar' in request.POST:
            verificacoes += 1
            if valores == proposicao_atual['resposta_correta']:
                fase_atual += 1
                if fase_atual > len(proposicoes_fases):
                    resultado = f"Parabéns! Você completou todas as fases com {verificacoes} tentativas."
                    jogador.pontuacao = verificacoes
                    jogador.save()
                    fase_atual = 1
                    verificacoes = 0
                    valores = valores_iniciais.copy()
                    dicas_vistas = 0
                else:
                    resultado = f"Fase {fase_atual - 1} concluída! Avançando para a fase {fase_atual}."
                    valores = valores_iniciais.copy()
                    dicas_vistas = 0

                proposicao_atual = proposicoes_fases[fase_atual - 1]
            else:
                resultado = "Algumas respostas estão incorretas. Tente novamente!"

        request.session['fase_atual'] = fase_atual
        request.session['valores'] = valores
        request.session['verificacoes'] = verificacoes
        request.session['dicas_vistas'] = dicas_vistas

    return render(request, 'game.html', {
        'valores': valores,
        'resultado': resultado,
        'dica_atual': dica_atual,
        'mostrar_dica': dicas_vistas < len(proposicao_atual["dicas"]),
        'fase_atual': fase_atual,
        'proposicao': proposicao_atual['proposicao']
    })


valores_iniciais = {'p': 'F', 'q': 'F', 'r': 'F'}

def inicio_jogo_view(request):
    if request.method == 'POST':
        form = JogadorForm(request.POST)
        if form.is_valid():
            jogador = form.save()
            request.session.flush()  # Limpa a sessão atual
            request.session['fase_atual'] = 1
            request.session['valores'] = valores_iniciais.copy()
            request.session['jogador_id'] = jogador.id
            request.session['verificacoes'] = 0
            # Redireciona para a página de jogo
            return redirect('game')
    else:
        form = JogadorForm()

    jogadores = Jogador.objects.order_by('-pontuacao')[:5]
    return render(request, 'home.html', {'jogadores': jogadores, 'form': form})
 

def leaderboard_view(request):
    jogadores = Jogador.objects.order_by('-pontuacao')[:10]  # Exibe os top 10 jogadores
    return render(request, 'leaderboard.html', {'jogadores': jogadores})