from django.shortcuts import render, redirect
from .models import Jogador, PlayerScore
from .forms import JogadorForm
from datetime import datetime


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
    inicio_jogo_str = request.session.get('inicio_jogo')
    if inicio_jogo_str:
        inicio_jogo = datetime.strptime(inicio_jogo_str, '%Y-%m-%d %H:%M:%S')
        tempo_gasto = datetime.now() - inicio_jogo
        minutos, segundos = divmod(tempo_gasto.total_seconds(), 60)
        tempo_formatado = f'{int(minutos)}min {int(segundos)}s'
    else:
        tempo_formatado = 'N/A'

    pontuacao_atual = max(1000 - (verificacoes * 10), 0)

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
                    pontuacao_base = 1000  # Pontuação inicial
                    desconto_por_tentativa = 10  # Penalidade por tentativa
                    pontuacao_final = max(pontuacao_base - (verificacoes * desconto_por_tentativa), 0)  # Garante que a pontuação nunca seja negativa
                    jogador.pontuacao = pontuacao_final

                    jogador.save()
                    
                    # Limpar variáveis de sessão e redirecionar para a página de fim de jogo
                    request.session['fase_atual'] = 1
                    request.session['valores'] = valores_iniciais.copy()
                    request.session['tentativas_finais'] = verificacoes
                    request.session['verificacoes'] = 0
                    request.session['dicas_vistas'] = 0
                    
                    return redirect('endgame')  # Certifique-se de que 'endgame' é a URL correta
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
        'proposicao': proposicao_atual['proposicao'],
        'pontuacao_atual': pontuacao_atual,
        'tempo_gasto': tempo_formatado,
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
            request.session['inicio_jogo'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

def endgame_view(request):
    jogador_id = request.session.get('jogador_id')
    if jogador_id:
        jogador=Jogador.objects.get(id=jogador_id)
        pontuacao = jogador.pontuacao
        tentativas = request.session.get('tentativas_finais', 'N/A')
        inicio_jogo_str = request.session.get('inicio_jogo')
        if inicio_jogo_str:
            inicio_jogo = datetime.strptime(inicio_jogo_str, '%Y-%m-%d %H:%M:%S')
            tempo_gasto = datetime.now() - inicio_jogo  # Calcula a diferença
            minutos, segundos = divmod(tempo_gasto.total_seconds(), 60)
            tempo_formatado = f'{int(minutos)}min {int(segundos)}s'
        else:
            tempo_formatado = 'N/A'

        return render(request, 'endgame.html', {'jogador_nome': jogador.nome, 'pontuacao': pontuacao, 'tentativas': tentativas, 'tempo_gasto': tempo_formatado})
    else:
        return render(request, 'endgame.html', {'jogador_nome': 'Desconhecido', 'pontuacao': 0, 'tentativas': 'N/A', 'tempo_gasto': 'N/A'})
    