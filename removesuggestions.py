# Include packages
import apiconnection as app

# Create the updater class and update the store
remover = app.ConnectSacHub('./credits.dat', './token.dat')
remover.connect()
remover.getLiveStore()
remover.removeReportSuggestions()
