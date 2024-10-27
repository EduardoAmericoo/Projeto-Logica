from django.db import models

# Create your models here.


class Jogador(models.Model):
    nome = models.CharField(max_length=100)
    pontuacao = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nome} - {self.pontuacao} pts"
