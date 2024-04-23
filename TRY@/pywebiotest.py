from asyncio import start_server
from pywebio.platform import go, run_js
from pywebio.input import *
from pywebio.output import *

def main_page():
    put_buttons(['Go to Second Page'], onclick=lambda: go('/second_page'))

def second_page():
    put_text("This is the second page")
    put_buttons(['Go back to Main Page'], onclick=lambda: go('/'))

if __name__ == '__main__':
    routes = {
        '/': main_page,
        '/second_page': second_page,
    }
    start_server(routes, debug=True)
