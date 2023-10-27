function checkAverage(id) {
  let average = $(id);
  if (average.length) {
    average.on('change', function() {
      if ($(this).is(':checked')) {
        checkBox('#read');
        uncheckBox('#nologin');
      } else {
        uncheckBox('#administer');
      }
    });
  }
}
