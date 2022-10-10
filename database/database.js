// database.py - Software for handling incoming database messages
// NOTE - this software runs on Google Apps Script servers

// Handle POST requests
function doPost(e) {
    // Load both Sheets in the spreadsheet
    const his_sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('History')
    const rat_sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Ratings')
    // If POST contains a list of new visitors
    if (e.parameter.type == "0"){
        var num_vis = Number(e.parameter.numvis)
        var visitors = e.parameter.visitors
        vis_arr = visitors.split(',')

        // For each new user
        for (let i = 0; i < num_vis; i++) {
            var visitor = vis_arr[i]
            var textFinder = rat_sheet.createTextFinder(visitor)
            var search = textFinder.findNext()
            // If user already in database
            if (search != null){
                // Add -1 to appropriate column if they have not rated the location
                var search_row = search.getRow()
                var range = rat_sheet.getRange(search_row, Number(e.parameter.location) + 2)
                if (range.isBlank)
                    range.setValue(-1);
            }
            // If user is not in database
            else{
                // Add user to database and add -1 to appropriate column
                var nextEmptyRow = rat_sheet.getLastRow() + 1;
                var range = rat_sheet.getRange(nextEmptyRow, 1)
                range.setValue(visitor)
                range = rat_sheet.getRange(nextEmptyRow, Number(e.parameter.location) + 2)
                range.setValue(-1)
            }
        }
    }
    // If POST contains a user's rating
    else if (e.parameter.type == "1"){
        var textFinder = rat_sheet.createTextFinder(e.parameter.user)
        var search = textFinder.findNext()
    
        // If user is already in database, get user row
        if (search != null){
            var search_row = search.getRow()
            var range = rat_sheet.getRange(search_row, Number(e.parameter.location) + 2)
            range.setValue(e.parameter.rating);
        }
        // If user is not in database, add to database
        else{
            var nextEmptyRow = rat_sheet.getLastRow() + 1;
            var range = rat_sheet.getRange(nextEmptyRow, 1)
            range.setValue(e.parameter.user)
            range = rat_sheet.getRange(nextEmptyRow, Number(e.parameter.location) + 2)
            range.setValue(e.parameter.rating)
        }
        
        // Add rating to the appropriate column
        var nextEmptyRow = his_sheet.getLastRow() + 1;
        var range = his_sheet.getRange(nextEmptyRow, 1)
        range.setValue(e.parameter.user)
        range = his_sheet.getRange(nextEmptyRow, 2)
        range.setValue(e.parameter.location)
        range = his_sheet.getRange(nextEmptyRow, 3)
        timezone = "GMT"
        var date = Utilities.formatDate(new Date(), timezone, "yyyy-MM-dd HH:mm");
        range.setValue(date)
    }
    return ContentService.createTextOutput("Done.");
  }

// Handle GET requests
function doGet(e) {
    // Load ratings sheet
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Ratings')

    var textFinder = sheet.createTextFinder(e.parameter.user)
    var search = textFinder.findNext()

    // If user exists in database, get their ratings
    if (search != null){
        var search_row = search.getRow()
        var range = sheet.getRange(search_row, 1, 1, 21)
        var ratings = range.getValues();
        return ContentService.createTextOutput(ratings);
    }
    // If user does not exist in database, send message
    else{
        return ContentService.createTextOutput("User doesn't exist");
    }
}