from flask import Flask


app=None
def init_app():
  kan_app=Flask(__name__)
  kan_app.debug=True
  kan_app.app_context().push()
  print("Kanban application started...")
  return kan_app



app=init_app()
from backend.controllers import *
if __name__=="__main__":
  app.run()