# coding=utf-8
# main.py
# 2016, all rights reserved
import click as click

from csv2guiabolso.guia_bolso import GuiaBolso

@click.command()
@click.option('--email', prompt=True, help="Email utilizado no Guiabolso")
@click.option('--password', prompt=True, hide_input=True)
@click.option('--file', default=None, help="Arquivo CSV")

def main(email, password, file):
    """Download GuiaBolso transactions in a csv format."""
    gb = GuiaBolso(email, password)
    
    if file:
        gb.upload_csv(file)
    else:
        gb.get_manual_accounts()
        gb.get_categories()

if __name__ == '__main__':
    main()
