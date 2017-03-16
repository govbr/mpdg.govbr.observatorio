==============================================================================
mpdg.govbr.observatorio
==============================================================================

Instalação do Produto
------------

Instale o mpdg.govbr.observatorio adicionando-o ao seu buildout ::

    [buildout]

    ...

    eggs =
        mpdg.govbr.observatorio


Observação::
Se o produto apresentar problemas de “UnicodeDecodeError”, implementar no buildout o seguinte código

parts =
    ...
    unicode

[unicode]
recipe = plone.recipe.command
command =
    export ENV_PATH=${buildout:directory}/../Python-2.7
    echo "import sys; sys.setdefaultencoding('utf-8')" > $ENV_PATH/lib/python2.7/sitecustomize.py
update-command = ${unicode:command}


Salvar e fechar o arquivo e rodar o buildout: ./bin/buldout -Nv


Dependencias

Instalação do docsplit (procedimento feito no Debian 8)

1. instalar o gen

.. sudo gem install docsplit

2. instalar o  comando GraphicsMagick.É usado para gerar imagens. 
Ou compilá-lo a partir da origem, ou usar um gerenciador de pacotes:

.. sudo aptitude install graphicsmagick

3. Instalar o Poppler

.. sudo aptitude install poppler-utils poppler-data

((Agora são opicional)) 

4. Instalar o Ghostscript:

.. sudo aptitude install ghostscript

5. Instalar o Tesseract:
.. sudo aptitude tesseract-ocr

.. obs.: Sem Tesseract instalado, você ainda será 
.. capaz de extrair texto de documentos, mas você 
.. não será capaz de automaticamente OCR-los.


Contribuinte
----------

- Rastreador de Problemas: https://github.com/collective/mpdg.govbr.observatorio/issues
- Código fonte: https://github.com/collective/mpdg.govbr.observatorio
- Documentação: https://docs.plone.org/foo/bar


Lincença
-------

O projeto é licenciado sob a GPLv2.
