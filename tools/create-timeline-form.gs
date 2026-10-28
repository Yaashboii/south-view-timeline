/**
 * South-View Timeline: build the "Add a person" Google Form
 * ---------------------------------------------------------
 * Run this ONCE from the timeline's Google Sheet. It creates a Google Form whose answers
 * land in a new tab called "Form Responses". The timeline reads that tab automatically,
 * so anything submitted through the form shows up on the timeline.
 *
 * How to run it:
 *   1. Open the timeline's Google Sheet.
 *   2. Extensions → Apps Script. Delete anything in the editor and paste this whole file.
 *   3. Click Save, choose "createTimelineForm" in the function menu, and click Run.
 *   4. Google asks for permission the first time. Click through and allow it.
 *   5. Open the form (link is in the Execution log, or in the Sheet: Form → Edit form).
 *   6. Add the photo question by hand (Google doesn't let scripts create it):
 *        + Add question → change the type to "File upload" → title it exactly:  Photo
 *        Allow only "Image", maximum 1 file.
 *   7. Back in Apps Script, choose "sharePhotoFolder" and click Run, so uploaded photos
 *      can be seen on the website.
 */

const FORM_TITLE = 'Add a person to the South-View timeline';
const RESPONSES_TAB = 'Form Responses';   // the timeline looks for a tab with exactly this name

const THEMES = [
  'Civil Rights',
  'Educators',
  'Civic Leadership',
  'Business & Entrepreneurship',
  'Healthcare',
  'Arts & Athletes',
];

// People who share one of these are linked to each other on the timeline.
const CONNECTIONS = [
  'the Atlanta Black Crackers',
  'Atlanta Life Insurance',
  'the Atlanta NAACP',
  'the Atlanta Negro Voters League',
  'the Atlanta Public Library',
  'Atlanta University',
  'Auburn Avenue',
  'Booker T. Washington High School',
  'the Carrie Steele-Pitts Home',
  'Citizens Trust Bank',
  'Clark College',
  'Ebenezer Baptist Church',
  'the Fox Theatre opera protest',
  'Grady Memorial Hospital',
  'Mercy Hospital',
  'the Metro Atlanta Chamber of Commerce',
  'Morehouse College',
  'Morris Brown College',
  'the Niagara Movement',
  'the Prince Hall Masons',
  'the Royal Peacock',
  'the SCLC',
  'Spelman College',
  'the Top Hat club',
  'Wheat Street Baptist Church',
  'the Whitman Sisters',
];

function createTimelineForm() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  if (ss.getSheetByName(RESPONSES_TAB)) {
    throw new Error('This Sheet already has a "' + RESPONSES_TAB + '" tab, so the form was probably created already. Check Form → Edit form.');
  }
  const tabsBefore = ss.getSheets().map(function (s) { return s.getSheetId(); });

  const form = FormApp.create(FORM_TITLE);
  form.setDescription(
    'Use this form to add someone to the South-View Cemetery timeline. ' +
    'Each submission appears on the timeline the next time the page is opened.\n\n' +
    'To correct someone who is already on the timeline, either edit their row in the Google Sheet, ' +
    'or submit this form again with the exact same name. The newest submission replaces the older one.');
  form.setCollectEmail(false);
  form.setAllowResponseEdits(false);
  form.setConfirmationMessage('Thank you! This person will appear on the timeline the next time the page is opened.');

  const year = FormApp.createTextValidation()
    .requireTextMatchesPattern('^\\d{4}$')
    .setHelpText('Please enter a four-digit year, like 1907.')
    .build();

  form.addTextItem().setTitle('Name').setRequired(true)
    .setHelpText('Full name as it should appear on the timeline. Example: Grace Towns Hamilton');
  form.addTextItem().setTitle('Born').setValidation(year)
    .setHelpText('Year only. Leave blank if it is not known; the person will then appear as a marker at the year they died.');
  form.addTextItem().setTitle('Died').setRequired(true).setValidation(year)
    .setHelpText('Year only.');
  form.addTextItem().setTitle('Dates shown')
    .setHelpText('Optional. Only fill this in if the dates should read differently, for example "c. 1874–1969".');
  form.addListItem().setTitle('Theme').setRequired(true).setChoiceValues(THEMES)
    .setHelpText('Which group on the timeline this person belongs to.');
  form.addParagraphTextItem().setTitle('Summary').setRequired(true)
    .setHelpText('One or two sentences about who they were. Example: "The first African American woman elected to the Georgia General Assembly."');

  for (var i = 1; i <= 5; i++) {
    form.addTextItem().setTitle('Milestone ' + i).setRequired(i === 1)
      .setHelpText(i === 1
        ? 'Write the year, a colon, then what happened. Example:  1943: Becomes executive director of the Atlanta Urban League'
        : 'Optional. Same format:  year: what happened');
  }

  form.addCheckboxItem().setTitle('Connected through').setChoiceValues(CONNECTIONS).showOtherOption(true)
    .setHelpText('Optional. Tick any places or groups this person shares with others on the timeline. ' +
                 'People who share one are linked to each other. Use "Other" to start a new one.');
  form.addParagraphTextItem().setTitle('Sources').setRequired(true)
    .setHelpText('Where the facts came from. Separate sources with semicolons. Example: ' +
                 'Henderson, South-View: An Atlanta City of the Dead (2018), p. 204; Georgia Women of Achievement');
  form.addParagraphTextItem().setTitle('Source links')
    .setHelpText('Optional. Web links for the sources above, in the same order, separated by semicolons. ' +
                 'Leave a blank between semicolons for a source with no link (like a book).');
  form.addTextItem().setTitle('Photo credit')
    .setHelpText('Who took or owns the photo. Example: Courtesy of the Hamilton family');

  // Send answers to this Sheet, then rename the new tab and move it to the end.
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  SpreadsheetApp.flush();
  const tab = ss.getSheets().filter(function (s) { return tabsBefore.indexOf(s.getSheetId()) < 0; })[0];
  if (tab) {
    tab.setName(RESPONSES_TAB);
    ss.setActiveSheet(tab);
    ss.moveActiveSheet(ss.getNumSheets());
    ss.setActiveSheet(ss.getSheets()[0]);
  }

  Logger.log('Form created. Edit it here (add the Photo question next): ' + form.getEditUrl());
  Logger.log('Share this link with staff to fill it out: ' + form.getPublishedUrl());
}

// Run after adding the "Photo" file-upload question. Makes uploaded photos viewable on the website.
function sharePhotoFolder() {
  const folders = DriveApp.getFoldersByName(FORM_TITLE + ' (File responses)');
  if (!folders.hasNext()) {
    throw new Error('Could not find the photo folder. Add the "Photo" file-upload question to the form first, then run this again.');
  }
  const top = folders.next();
  top.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  const subs = top.getFolders();
  while (subs.hasNext()) subs.next().setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  Logger.log('Done. Photos uploaded through the form can now be seen on the timeline. Folder: ' + top.getUrl());
}
