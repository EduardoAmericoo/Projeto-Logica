from django.db import models

# Create your models here.


class Jogador(models.Model):
    nome = models.CharField(max_length=100)
    pontuacao = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nome} - {self.pontuacao} pts"
    
class PlayerScore(models.Model):
    jogador = models.ForeignKey(Jogador, on_delete=models.CASCADE, related_name='scores')  # Relaciona o desempenho ao jogador
    pontuacao = models.IntegerField(default=0)  # Pontuação da sessão de jogo
    tentativas = models.IntegerField(default=0)  # Número de tentativas na sessão de jogo
    tempo_gasto = models.DurationField(null=True, blank=True)  # Tempo gasto na sessão de jogo
    data_jogo = models.DateTimeField(auto_now_add=True)  # Data e hora da sessão de jogo

    def __str__(self):
        return f"{self.jogador.nome} - Pontuação: {self.pontuacao} em {self.data_jogo}"