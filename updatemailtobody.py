# Include packages
import apiconnection as app

# Create the updater class and update the store
updater = app.ConnectSacHub('./credits.dat', './token.dat')
updater.connect()
updater.getLiveStore()
updater.updateMailtoBody()
