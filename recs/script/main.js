(function (window, document, undefined) {
    "use strict";

    // Variables
    var form = document.querySelector("#form-search");
    var input = document.querySelector("#input-search");
    var resultList = document.querySelector("#search-results");

    // Methods
    var createHTML = function (fic) {
      var html =
        '<li>' +
        '<a href="' + "https://www.fanfiction.net/s/" + fic.id + "/1/" + '" target="_blank">' +
        fic.name +
        "<br>" +
        "<span> " + fic.recs + " recs (" + fic.score + " points)" + "</span>" +
        '</a>'+
        "</li>";
      return html;
    };

    // Create the markup when no results are found
    var createNoResultsHTML = function () {
      return "<p>Sorry, no matches were found.</p>";
    };

    // Create the markup for results
    var createResultsHTML = function (results) {
      var html = "<p>Found " + results.length + " matching stories.</p>";
      html += results
        .map(function (article, index) {
          return createHTML(article, index);
        })
        .join("");
      return html;
    };

    // Search for matches
    var search = function (query) {
      const regex = /\/s\/\d+/g;
      var found = query.match(regex);
      if (found != null && found.length == 1) {
        query = found[0]
        query = query.slice(3, query.length)
      }

      var results_map = {};
      var submissions = data["fic_id_to_submissions"][query];
      submissions.map(function (submission) {
        var fics = data["submissions_to_fics"][submission];
        fics.map(function (fic) {
          var name = DOMPurify.sanitize(fic[0]);
          var id = fic[1]
          var score = fic[2];

          if (id in results_map) {
            results_map[id].score += parseInt(score)
            results_map[id].recs += 1
          } else {
            results_map[id] = {
            "name": name,
            "id": id,
            "score": parseInt(score),
            "recs": 1
            }
          }
        });
      });

      var results = [];
      for (var id in results_map) {
        if (results_map[id].score < 1) { continue; }
        results.push(results_map[id]);
      }

      function fic_comparator(a, b) {
          if (a.recs < b.recs) return -1;
          if (a.recs > b.recs) return 1;
          if (a.score < b.score) return -1;
          if (a.score > b.score) return 1;
          if (a.name < b.name) return -1;
          if (a.name > b.name) return 1;
          return 0;
      }

      results.sort(fic_comparator).reverse();

      // Display the results
      resultList.innerHTML =
        results.length < 1
          ? createNoResultsHTML()
          : createResultsHTML(results);
    };

    // Handle submit events
    var submitHandler = function (event) {
      resultList.innerHTML = createNoResultsHTML()
      event.preventDefault();
      search(input.value);
    };

    // // Remove site: from the input
    var clearInput = function () {
      input.value = "";
    };

    // // Make sure required content exists
    // if (!form || !input || !resultList || !data) return;

    // // Clear the input field
    clearInput();

    // // Create a submit handler
    form.addEventListener("input", submitHandler, false);
  })(window, document);