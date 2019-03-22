# Include packages
import apiconnection as app

# Create the updater class and update the store
updater = app.ConnectSacHub('./credits.dat', './token.dat')
updater.connect()
updater.getLiveStore()
updater.getAssetStructure()
# Standard functionality to update the report suggestions (all assets and up to 3 suggestions)
updater.updateReportSuggestions()
# (uncomment any of the following to run)
## For a specific asset
# updater.updateReportSuggestions(assets='1')
## Lower number of assets provided as suggestions (e.g., 1)
# updater.updateReportSuggestions(nSuggestions=1)
