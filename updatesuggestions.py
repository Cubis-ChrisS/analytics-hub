# Include packages
import apiconnection as app

# Create the updater class and update the store
updater = app.ConnectSacHub('./credits.dat', './token.dat')
updater.connect()
updater.getLiveStore()
<<<<<<< HEAD
=======
updater.getAssetStructure()
>>>>>>> d7e4aa1f398dab07602ce386be5a720d2301acc2
# Standard functionality to update the report suggestions (all assets and up to 3 suggestions)
updater.updateReportSuggestions()
# (uncomment any of the following to run)
## For a specific asset
# updater.updateReportSuggestions(assets='1')
<<<<<<< HEAD
## Lower number of assets (e.g., 1)
=======
## Lower number of assets provided as suggestions (e.g., 1)
>>>>>>> d7e4aa1f398dab07602ce386be5a720d2301acc2
# updater.updateReportSuggestions(nSuggestions=1)
