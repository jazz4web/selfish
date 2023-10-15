function formatFooter() {
  let year = luxon.DateTime.now().year;
  let f = $('#footer-link').text().trim() + ', ' + year + ' г.';
  $('#footer-link').text(f);
}
