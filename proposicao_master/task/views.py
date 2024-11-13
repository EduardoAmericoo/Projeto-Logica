from django.shortcuts import render, redirect
from .models import Jogador, PlayerScore
from .forms import JogadorForm


# Proposições e respostas corretas para cada fase
proposicoes_fases = [
    {"proposicao": "p ∧ ~q ∧ r",
     "resposta_correta": [{'p': 'V', 'q': 'F', 'r': 'V'}],
     "dicas": [
         "A negação de q torna esse valor importante para satisfazer a proposição.",
         "Analise o impacto de r ser verdadeiro no resultado geral."
     ]},
    {"proposicao": "(p ∨ q) ∧ ~r",
     "resposta_correta": [{'p': 'V', 'q': 'V', 'r': 'F'}, {'p': 'F', 'q': 'V', 'r': 'F'}, {'p': 'V', 'q': 'F', 'r': 'F'}],
     "dicas": [
         "A disjunção permite que pelo menos um dos valores de p ou q seja verdadeiro.",
         "Considere como o valor de r pode invalidar a proposição."
     ]},
    {"proposicao": "(~p → q) ∧ (r → ~q)",
     "resposta_correta": [{'p': 'V', 'q': 'V', 'r': 'F'},{'p': 'F', 'q': 'V', 'r': 'F'}],
     "dicas": [
         "Explore como a implicação (~p → q) se comporta quando q é falso.",
         "Pense sobre como a relação entre r e q afeta a segunda parte."
     ]},
    {"proposicao": "(~p ∨ q) ↔ (~r ∧ p)",
     "resposta_correta": [{'p': 'V', 'q': 'F', 'r': 'V'},{ 'p': 'V', 'q': 'V', 'r': 'F'}, {'p':'V', 'q': 'F', 'r':'V'}],
     "dicas": [
         "A equivalência exige que ambos os lados compartilhem o mesmo valor lógico.",
         "Reflita sobre como a negação de p no lado esquerdo interage com q.",
         "Lembre-se de que o lado direito depende fortemente de p ser verdadeiro."
     ]},
    {"proposicao": "[(~p ∨ q) ∧ (p → r)] → [(~q ∨ ~r) ∧ (~p ↔ ~q)]",
     "resposta_correta": [{'p': 'V', 'q': 'V', 'r': 'F'},{'p': 'V', 'q': 'F', 'r': 'V'},{'p': 'V', 'q': 'F', 'r': 'F'},{'p': 'F', 'q': 'V', 'r': 'F'}],
     "dicas": [
         "A condição inicial combina disjunção e implicação; estude como isso restringe os valores de p, q e r.",
         "Observe como o lado direito da implicação depende de ~q e ~p para satisfazer as condições.",
         "A análise dos operadores ↔ e ∧ é fundamental para fechar as lacunas entre o antecedente e o consequente."
     ]}
]



def game_view(request):
    fase_atual = request.session.get('fase_atual', 1)
    valores = request.session.get('valores', valores_iniciais.copy())
    verificacoes = request.session.get('verificacoes', 0)
    jogador_id = request.session.get('jogador_id')
    resultado = None
    dica_atual = None

    if not jogador_id or not Jogador.objects.filter(id=jogador_id).exists():
        return redirect('home')

    jogador = Jogador.objects.get(id=jogador_id)
    proposicao_atual = proposicoes_fases[fase_atual - 1]
    dicas_vistas = request.session.get('dicas_vistas', 0)

    if request.method == 'POST':
        if 'mostrar_dica' in request.POST:
            if dicas_vistas < len(proposicao_atual["dicas"]):
                dicas_vistas += 1
                dica_atual = proposicao_atual["dicas"][dicas_vistas - 1]
        elif 'toggle' in request.POST:
            letra = request.POST['toggle']
            valores[letra] = 'V' if valores[letra] == 'F' else 'F'
        elif 'verificar' in request.POST:
            verificacoes += 1
            respostas = proposicao_atual['resposta_correta']
            if not isinstance(respostas, list):
                respostas = [respostas]  # Converte para lista, se necessário
            resposta_correta = valores in respostas

            if resposta_correta:

                fase_atual += 1
                if fase_atual > len(proposicoes_fases):
                    resultado = f"Parabéns! Você completou todas as fases com {
                        verificacoes} tentativas."
                    jogador.pontuacao = verificacoes
                    jogador.save()
                    fase_atual = 1
                    verificacoes = 0
                    valores = valores_iniciais.copy()
                    dicas_vistas = 0
                else:
                    resultado = f"Fase {
                        fase_atual - 1} concluída! Avançando para a fase {fase_atual}."
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
    jogadores = Jogador.objects.order_by(
        '-pontuacao')[:10]  # Exibe os top 10 jogadores
    return render(request, 'leaderboard.html', {'jogadores': jogadores})
