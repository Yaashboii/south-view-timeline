# South-View Cemetery: Lives That Shaped Atlanta

Interactive timeline of notable people buried at South-View Cemetery in Atlanta, built with TimelineJS (Knight Lab) for a Georgia Tech class project in partnership with South-View Cemetery and the Praise House Project.

## Updating the timeline

The timeline reads the "South-View Timeline Data" Google Sheet every time the page opens. To add or change a person, edit the sheet and refresh the page. No code changes are needed.

- One row per person. Name, Born, Died and Theme are required.
- Milestones are written as `year: what happened`, for example `1952: Opened the pavilion`.
- People who share a value in "Connected through" are linked to each other. Separate several values with a semicolon.
- Photo can be a file in the `images` folder (`images/name.jpg`) or a full web address.

If the sheet can't be reached, the page shows the copy saved in `index.html` and says so in the header.

Content is preliminary and pending review by South-View. Photos are used with permission from South-View Cemetery or credited to their sources.
