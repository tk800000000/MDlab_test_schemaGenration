from flask import Flask, render_template, request, redirect, url_for
from flaApp.DSP import Schema, csvOpener

app = Flask(__name__)

import flaApp.views
