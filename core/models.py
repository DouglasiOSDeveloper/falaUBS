from django.db import models
from django.conf import settings
import uuid

class Agendamento(models.Model):
    TIPO_CHOICES = [
        ('Consulta', 'Consulta'),
        ('Exame', 'Exame'),
    ]
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Concluído', 'Concluído'),
        ('Cancelado', 'Cancelado'),
    ]

    protocolo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ou use JSONField, se for usuário mock
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    especialidade = models.CharField(max_length=100)
    ubs = models.CharField(max_length=200)
    data = models.DateField()
    hora = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')
    documentos = models.JSONField(default=list, blank=True)  # lista de nomes de arquivos
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.protocolo} – {self.tipo} em {self.ubs} em {self.data} {self.hora}"
