/**
 * Adds a Docs Terminal menu and handles command execution via sidebar.
 */
function onOpen() {
  DocumentApp.getUi()
    .createMenu('Docs Terminal')
    .addItem('Open Terminal', 'showSidebar')
    .addToUi();
}

/**
 * Opens the terminal sidebar.
 */
function showSidebar() {
  var html = HtmlService.createHtmlOutputFromFile('Sidebar')
      .setTitle('Docs Terminal');
  DocumentApp.getUi().showSidebar(html);
}

/**
 * Executes a command by POSTing to the back-end /exec endpoint.
 * @param {string} input The command input from the terminal.
 * @return {string} The back-end response text.
 */
function runCommand(input) {
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty('API_TOKEN');
  var url = 'https://your-api.example.com/exec';
  var options = {
    method: 'post',
    contentType: 'application/json',
    headers: { 'Authorization': 'Bearer ' + token },
    payload: JSON.stringify({ cmd: input })
  };
  var response = UrlFetchApp.fetch(url, options);
  return response.getContentText();
}