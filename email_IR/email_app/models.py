from django.db import models


class Email(models.Model):
    '''Enron Email'''
    ID = models.IntegerField(primary_key=True)
    MessageID = models.CharField(max_length=50)
    Date = models.CharField(max_length=50, null=True, blank=True)
    UserFrom = models.TextField(null=True)
    UserTo = models.TextField(null=True)
    Subject = models.TextField(null=True)
    Payload = models.TextField(null=True)

    def __str__(self):
        return self.MessageID