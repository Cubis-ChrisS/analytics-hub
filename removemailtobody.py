# Include packages
import apiconnection as app

# Create the updater class and update the store
remover = app.ConnectSacHub('./credits.dat', './token.dat')
remover.connect()
remover.getLiveStore()
# Standard functionality to remove the subject and body (all assets)
remover.removeMailtoBody()
# ==  remover.removeMailtoBody(assets='all')
