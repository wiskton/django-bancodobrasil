# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings


def retiraAcento(a, b):
    import re
    import unicodedata
    ext = b.split('.')[-1] # pega ultima ocorrência do split
    url = unicodedata.normalize('NFKD', b).encode('ascii', 'ignore')
    return url.encode('utf-8')


class BB(models.Model):

    idConv = models.PositiveIntegerField(
        u'Código do convênio', max_length=6, default=settings.BB_ID_CONV,
        help_text=u'Código do convênio de Comércio Eletrônico fornecido pelo Banco'
    )
    idConvRecebimento = models.PositiveIntegerField(
        u'Código do convênio de recebimento', max_length=6, default=settings.BB_ID_CONV_RECEBIMENTO,
        help_text=u'Código do convênio de recebimento de Comércio Eletrônico fornecido pelo Banco'
    )
    idConvCobranca = models.PositiveIntegerField(
        u'Código do convênio de cobrança', max_length=7, default=settings.BB_ID_CONV_COBRANCA,
        help_text=u'Código do convênio de cobrança de Comércio Eletrônico fornecido pelo Banco'
    )
    refTran = models.PositiveIntegerField(
        u'Referencia da transação', max_length=17,
        help_text=u'7 digitos - primeiros número do convênio de cobrança e 10 digitos livres identificação do produto id do pedido'
    )
    valor = models.PositiveIntegerField(
        u'Valor em centavos', max_length=17,
        help_text=u'195,72 exemplo: 19572'
    )
    tpPagamento = models.PositiveIntegerField(
        u'Tipo de Pagamento', max_length=2,
        help_text=u'0 – Todas as modalidades contratadas pelo convenente\n2 – Boleto bancário\n21 – 2ª Via de boleto bancário, já gerado anteriormente\n3 – Débito em Conta via Internet – PF e PJ\n5 – BB Crediário Internet\n7 - Débito em Conta via Internet PF'
    )
    dtVenc = models.CharField(
        u'Data de Vencimento', max_length=8,
        help_text=u'DDMMAAAA exemplo: 17112013'
    )
    urlRetorno = models.URLField(
        u'Url de retorno', max_length=60, default=settings.BB_URL_RETORNO,
        help_text=u'Exemplo: https://www.site.com.br/retorno/'
    )
    urlInforma = models.URLField(
        u'Url de informação', max_length=60, default=settings.BB_URL_INFORMA,
        help_text=u'Exemplo: https://www.site.com.br/informa/'
    )
    nome = models.CharField(
        u'Data de Vencimento', max_length=60,
        help_text=u'Nome do comprador, que será apresentado no boleto de cobrança.'
    )
    endereco = models.CharField(
        u'Data de Vencimento', max_length=60,
        help_text=u'Endereço do comprador, que será apresentado no boleto de cobrança.'
    )
    cidade = models.CharField(
        u'Cidade do comprador', max_length=18
    )
    uf = models.CharField(
        u'Sigla do estado do comprador', max_length=2, help_text=u'Ex: SP'
    )
    cep = models.CharField(
        u'CEP', max_length=8, help_text=u'14090150'
    )
    msgLoja = models.TextField(
        help_text='Instruções do cedente, que serão apresentadas no boleto de cobrança.',
        default=settings.BB_MSG_LOJA
    )


    class Meta:
        ordering = ('nome', )
        verbose_name = 'Banco do Brasil'
        verbose_name_plural = 'Banco do Brasil'


    def __unicode__(self):
        return self.nome


    def getRefTran(self):
        return "%s%s" % ( self.idConvCobranca, self.refTran)


    def VARS(self):
        VARS = {
                'idConv': self.idConv,
                'refTran': self.getRefTran(),
                'valor': self.valor,
                'tpPagamento': self.tpPagamento,
                'dtVenc': self.dtVenc,
                'urlRetorno': self.urlRetorno,
                'urlInforma': self.urlInforma,
                'nome': retiraAcento(1, unicode(self.nome)),
                'endereco': retiraAcento(1, unicode(self.endereco)),
                'cidade': retiraAcento(1, unicode(self.cidade)),
                'uf': self.uf,
                'cep': self.cep,
                'msgLoja': retiraAcento(1, unicode(self.msgLoja))
            }
        return VARS


    def envia(self):
        import urllib
        import urllib2
        params = urllib.urlencode(self.VARS())
        req = urllib2.Request(settings.BB_URL_BB_PAGAMENTO, params)
        response = urllib2.urlopen(req)
        retorno = response.read()
        return retorno


    def form(self):
        from django.template import Context, loader
        t = loader.get_template('bancodobrasil/bb_form.html')
        f = Context({
            'bb': self,
            'url': settings.BB_URL_BB_PAGAMENTO,
            'STATIC_URL': settings.STATIC_URL
        })
        return t.render(f)
