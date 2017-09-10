var debounce;
var selected_movies = [];
var chart;
var ctx;
var current_selection = -1;

/**
 * Makes an API call to fetch the auto-complete data.
 * Look at the auto_complete view in views.py for more info.
 *
 * Creates the auto-complete list from the result with data-id
 * set to the primary key of the target movie.  This will be used
 * to actually fetch all relevant info for a movie from the database.
 */
function auto_complete(keyword) {
  $.ajax({
    method: "GET",
    url: "/imdb_graph/auto_complete?keyword=" + keyword,
    dataType: "json"
  }).done(function(result) {
    var data = jQuery.parseJSON(result);
    var html_string = "";
    for (var i = 0; i < data.length; i++) {
      html_string += "<li class='entry' data-id='" + data[i].pk + "'>" +
                  data[i].fields.title + " (" + data[i].fields.year + ")" +
                  "</li>";
    }
    $("#auto-complete-results").html(html_string);
    $("#auto-complete-results").show();
    current_selection = -1;
  });
}

/**
 * Makes an API call to get all the information for a particular movie.
 * This includes loading the appropriate card template to render,
 * and updating the chartjs information.
 */
function add_movie(movie_id) {
  $.ajax({
    method: "GET",
    url: "/imdb_graph/get_movie?movie_id=" + movie_id,
    dataType: "json"
  }).done(function(result) {
    var movie = jQuery.parseJSON(result);
    var arr_index = selected_movies.findIndex(x => x.pk == movie.pk);
    // Doesn't exist
    if (arr_index == -1) {
      selected_movies.push(movie);
      draw_chart();
      $("#auto-complete-results").hide();
      $("#auto-complete-results").empty();
      $("#input-keyword").val("");
      $("#input-keyword").focus();
      current_selection = -1;

      $.ajax({
        method: "GET",
        url: "/imdb_graph/movie_card?movie_id=" + movie_id
      }).done(function(result) {
        $("#movie-cards").append(result);
      });
    }
  });
}

/**
 * Credit where it's due: https://stackoverflow.com/questions/149055/how-can-i-format-numbers-as-dollars-currency-string-in-javascript
 * Very similar to one of the solutions.  We don't have decimals though so
 * we just change matching the literal \. to end line.
 */
function format_money(number) {
  return "$" + number.toString().replace(/(\d)(?=(\d{3})+$)/g, "$1,");
}

/**
 * Returns the data from selected movies in an easy to parse format
 * for chartjs.
 */
function get_scatter_data() {
  return selected_movies.map(movie => {
    return {
      x: movie.fields.imdb_score,
      // toFixed converts to a string...
      y: parseFloat((movie.fields.domestic_gross / movie.fields.budget).toFixed(3)),
      title: movie.fields.title + " (" + movie.fields.year + ")",
      domestic_gross: format_money(movie.fields.domestic_gross),
      budget: format_money(movie.fields.budget)
    };
  });
}

/**
 * Returns an m & b value for the regression line.
 * Credit where it's due: https://dracoblue.net/dev/linear-least-squares-in-javascript/
 */
function do_regression(scatter_data) {
  var m = 0;
  var b = 0;
  var sum_x = 0;
  var sum_y = 0;
  var sum_xy = 0;
  var sum_xx = 0;
  var min_x = Infinity;
  var max_x = -Infinity;
  var point;

  for (var i = 0; i < scatter_data.length; i++) {
    point = scatter_data[i];
    sum_x += point.x;
    sum_y += point.y;
    sum_xx += point.x * point.x;
    sum_xy += point.x * point.y;
    if (point.x > max_x) {
      max_x = point.x;
    }
    if (point.x < min_x) {
      min_x = point.x;
    }
  }

  var m = (scatter_data.length * sum_xy - sum_x * sum_y) / (scatter_data.length * sum_xx - sum_x * sum_x);
  var b = (sum_y / scatter_data.length) - (m * sum_x / scatter_data.length);

  return {m: m, b: b, min_x: min_x, max_x: max_x}
}

function get_regression_data(scatter_data) {
  var regression = do_regression(scatter_data);
  return [
    {
      x: regression.min_x,
      y: regression.m * regression.min_x + regression.b
    },
    {
      x: regression.max_x,
      y: regression.m * regression.max_x + regression.b
    }
  ]
}

/**
 * Updates the chart based on the currently selcted_movies.
 * Creates individual data points and a regression line.
 */
function draw_chart() {
  var scatter_data = get_scatter_data();
  if (scatter_data.length > 0) {
    $("#chart-container").show();
    var regression_data = get_regression_data(scatter_data);
    chart.data.datasets[0].data = scatter_data;
    chart.data.datasets[1].data = regression_data;
    chart.update();
  } else {
    $("#chart-container").hide();
  }
}

$(function() {

  /**
   * Initialize chartjs stuff here.  Currently the #chart-container
   * class is hidden, we will show it iff there is data to show.
   */
  ctx = document.getElementById("movie-chart").getContext("2d");
  chart = new Chart(ctx, {
    type: "bubble",
    data: {
      datasets: [
        // Scatter point chart
        {
          type: "bubble",
          label: "Scatter Data",
          backgroundColor: "rgb(28, 168, 221)",
          borderColor: "rgb(28, 168, 221)",
          fill: false,
          data: []
        },
        // regression line chart
        {
          type: "line",
          label: "Regression",
          data: [],
          fill: false,
          backgroundColor: "rgb(10, 120, 200)",
          borderColor: "rgb(10, 120, 200)",
          pointRadius: 0
        }
      ]
    },
    options: {
      scales: {
        xAxes: [{
          type: "linear",
          position: "bottom",
          gridLines: {
            // "Everything else is fontColor, so let's make this option
            // be just 'color'." -- ChartJs devs
            color: "rgb(100, 100, 100)"
          },
          scaleLabel: {
            display: true,
            fontColor: "rgb(230, 230, 230)",
            labelString: "Imdb Score"
          },
          ticks: {
            fontColor: "rgb(230, 230, 230)"
          }
        }],
        yAxes: [{
          gridLines: {
            color: "rgb(100, 100, 100)"
          },
          scaleLabel: {
            display: true,
            fontColor: "rgb(230, 230, 230)",
            labelString: "Profit (Gross / Budget)"
          },
          ticks: {
            fontColor: "rgb(230, 230, 230)"
          }
        }]
      },
      tooltips: {
        callbacks: {
          title: function(tooltipArray, data) {
            // Why?  WHY!!!
            // "Let's make it take an array of one item instead of just the item
            // because that makes more fucking sense." -- ChartJs devs
            var tooltipItem = tooltipArray[0];
            return data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index].title;
          },
          label: function(tooltipItem, data) {
            var point = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
            return [
              "Imdb Score: " + point.x,
              "Profit: " + point.y,
              "Domestic Gross: " + point.domestic_gross,
              "Budget: " + point.budget
            ];
          },
        },
        // Style the tooltip
        titleFontSize: 16,
        titleFontColor: "rgb(28, 168, 221)",
        bodyFontSize: 14,
        bodyFontColor: "rgb(230, 230, 230)",
        titleFontSize: 16,
        displayColors: false
      }
    }
  });

  /**
   * Aww yiss, roll your own debounce.
   */
  $("#input-keyword").on("input", function() {
    clearTimeout(debounce);
    var keyword = $("#input-keyword").val();
    if (keyword.length > 0) {
      debounce = setTimeout(function() {
        auto_complete(keyword);
      }, 250);
    } else {
      $("#auto-complete-results").hide();
      $("#auto-complete-results").empty();
    }
  });

  /**
   * When the user clicks on an auto-complete result, add it to
   * the selected movies list.
   */
  $("#auto-complete-results").on("click", ".entry", function() {
    var movie_id = $(this).attr("data-id");
    add_movie(movie_id);
  });

  $("#auto-complete-results").on("mouseenter", ".entry", function() {
    $(this).addClass("selected");
  });

  $("#auto-complete-results").on("mouseleave", ".entry", function() {
    $(this).removeClass("selected");
  });

  /**
   * Make our movie cards beautiful with an opacity overlay
   * with more info.
   */
  $("#movie-cards").on("mouseenter", ".movie-card", function() {
    $(this).find(".movie-info").css("display", "flex");
  });

  $("#movie-cards").on("mouseleave", ".movie-card", function() {
    $(this).find(".movie-info").css("display", "none");
  });

  /**
   * Remove the clicked movie from the model and from the DOM.
   * Make sure the movie-card has the correct data-id attribute set.
   */
  $("#movie-cards").on("click", ".close-icon", function() {
    var movie_card = $(this).closest(".movie-card");
    var movie_id = movie_card.attr("data-id");
    var arr_index = selected_movies.findIndex(x => x.pk == movie_id);
    if (arr_index != -1) {
      selected_movies.splice(arr_index, 1);
      movie_card.remove();
      draw_chart();
    }
  });

  $("#input-keyword").on("focus", function() {
    if ($("#auto-complete-results").children().length > 0) {
      $("#auto-complete-results").show();
    }
  });

  $("#input-keyword").on("focusout", function() {
    // Set timeout so that click event still fires... gross.
    setTimeout(function() {
      $("#auto-complete-results").hide();
    }, 10);
  });

  $("#input-keyword").on("keydown", function(event) {
    // Scroll the selected class
    if (event.key == "ArrowDown" || event.key == "ArrowUp") {
      if ($("#auto-complete-results").children().length > 0) {
        var direction = (event.key == "ArrowUp") ? -1 : 1;
        if (current_selection > -1) {
          $($("#auto-complete-results").children()[current_selection]).removeClass("selected");
        }
        current_selection = (current_selection + direction + 5) % 5;
        $($("#auto-complete-results").children()[current_selection]).addClass("selected");
      }
    // Add the selected movie
    } else if (event.key == "Enter") {
      if (current_selection > -1) {
        var movie_id = $($("#auto-complete-results").children()[current_selection]).attr("data-id");
        add_movie(movie_id);
      }
    }
  });

});
