function getMovieDetailsById(movie_id) {
  return new Promise((resolve, reject) => {
    const URL = "https://api.themoviedb.org/3/movie/" + movie_id;
    const params = {
      URL: URL,
    };

    $.ajax({
      url: "/proxy",
      type: "GET",
      contentType: "application/json",
      data: { params: JSON.stringify(params) },
      success: function (response) {
        // console.log("Additional Details for Movie ID:", movie_id);
        // console.log("Response from Flask:", response);

        let genresArray = response["genres"];
        let genres = [];
        for (let genre of genresArray) {
          genres.push(genre["name"]);
        }

        let runtime = parseInt(response["runtime"]);
        runtime =
          Math.floor(runtime / 60) + " hours " + (runtime % 60) + " minutes";

        const MovieDetails = {
          imdb_id: response["imdb_id"],
          poster:
            "https://image.tmdb.org/t/p/original" + response["poster_path"],
          title: response["original_title"],
          overview: response["overview"],
          // poster_path: response["poster_path"],
          rating: response["vote_average"],
          release_date: response["release_date"],
          genre: genres,
          runtime: runtime,
          // Add more details as needed
        };

        resolve(MovieDetails); // Resolve the Promise with MovieDetails
      },
      error: function (error) {
        console.error("Error:", error);
        reject(error); // Reject the Promise with the error
      },
    });
  });
}

function getSimilarMovies(title) {
  var server_data = [
    {
      query: title,
    },
  ];
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/similar",
      type: "POST",
      contentType: "application/json",
      dataType: "json",
      data: JSON.stringify(server_data),
      success: function (response) {
        // console.log("Similar Movies for Title:", title);
        // console.log("Response from Flask:", response);
        let movieList = []; // Initialize an empty array
        for (const movie of response) {
          // Iterate over the response array
          movieList.push(movie); // Push each movie to the array
        }
        resolve(movieList); // Resolve the Promise with movieList
      },
      error: function (error) {
        console.error("Error in getSimilarMovies:", error);
        reject(error); // Reject the Promise with the error

        $("#loader").delay(500).fadeOut();
      },
    });
  });
}

function getMovieId(title) {
  return new Promise((resolve, reject) => {
    var server_data = [
      {
        URL: "https://api.themoviedb.org/3/search/movie",
        query: title,
      },
    ];
    $.ajax({
      url: "/movie_id",
      type: "POST",
      contentType: "application/json",
      dataType: "json",
      data: JSON.stringify(server_data),
      success: function (response) {
        // console.log("Movie ID for Title:", title);
        // console.log("Response from Flask:", response);
        const movieId = response["results"][0]["id"];
        resolve(movieId); // Resolve the Promise with the movieId
      },
      error: function (error) {
        console.error("Error in getMovieId:", error);
        reject(error); // Reject the Promise with the error

        $("#loader").delay(500).fadeOut();
      },
    });
  });
}

function getCastDetails(cast) {
  const cast_bdays = [];
  const cast_bios = [];
  const cast_places = [];
  for (let cast_id in cast.cast_ids) {
    const URL = "https://api.themoviedb.org/3/person/" + cast.cast_ids[cast_id];
    var server_data = [
      {
        URL: URL,
      },
    ];
    $.ajax({
      type: "POST",
      url: "/CastesDetails",
      async: false,
      dataType: "json",
      contentType: "application/json",
      data: JSON.stringify(server_data),
      success: function (cast_details) {
        cast_bdays.push(
          new Date(cast_details.birthday)
            .toDateString()
            .split(" ")
            .slice(1)
            .join(" ")
        );
        cast_bios.push(cast_details.biography);
        cast_places.push(cast_details.place_of_birth);
      },
    });
  }
  return {
    cast_bdays: cast_bdays,
    cast_bios: cast_bios,
    cast_places: cast_places,
  };
}

function getCastes(movieId) {
  const cast_ids = [];
  const cast_names = [];
  const cast_chars = [];
  const cast_profiles = [];

  const URL = "https://api.themoviedb.org/3/movie/" + movieId + "/credits";
  var server_data = [
    {
      URL: URL,
    },
  ];
  $.ajax({
    url: "/MovieCastes",
    async: false,
    type: "POST",
    dataType: "json",
    contentType: "application/json",
    data: JSON.stringify(server_data),
    success: function (response) {
      // console.log("Caste Details for Movie ID:", movieId);
      // console.log("Response from Flask:", response);

      if (response["cast"].length >= 10) {
        top_cast = 10;
      } else {
        top_cast = 5;
      }

      for (let i = 0; i < top_cast; i++) {
        cast_ids.push(response["cast"][i]["id"]);
        cast_names.push(response["cast"][i]["name"]);
        cast_chars.push(response["cast"][i]["character"]);
        cast_profiles.push(
          "https://image.tmdb.org/t/p/original" +
            response["cast"][i]["profile_path"]
        );
      }
    },
    error: function (error) {
      console.error("Error:", error);
      $("#loader").delay(500).fadeOut();
    },
  });

  return {
    cast_ids: cast_ids,
    cast_names: cast_names,
    cast_chars: cast_chars,
    cast_profiles: cast_profiles,
  };
}

async function getPosters(movies) {
  let posters = [];
  let promises = [];

  for (let movie of movies) {
    let movieIdPromise = getMovieId(movie);
    promises.push(movieIdPromise);
  }

  let movieIds = await Promise.all(promises);

  let movieDetailsPromises = movieIds.map((movieId) =>
    getMovieDetailsById(movieId)
  );

  let movieDetailsArray = await Promise.all(movieDetailsPromises);

  for (let movieDetails of movieDetailsArray) {
    const poster = movieDetails["poster"];
    posters.push(poster);
  }

  return posters;
}

function MovieDetails(title) {
  let movieId;
  let cast_details;
  let SimilarMovies;
  let cast;
  let posters;
  let movie_details;

  getMovieId(title)
    .then((movId) => {
      movieId = movId;
      console.log("Movie ID:", movieId);
      return getMovieDetailsById(movieId);
    })
    .then((movieDetails) => {
      movie_details = movieDetails;
      console.log("Movie details are", movieDetails);
      return getSimilarMovies(title); // Return the Promise from getSimilarMovies
    })
    .then((simMovies) => {
      SimilarMovies = simMovies;
      console.log("Similar movies are", SimilarMovies);

      cast = getCastes(movieId);
      console.log("Casts are", cast);

      return getCastDetails(cast); // Return the Promise from getCastDetails
    })
    .then((castDetails) => {
      cast_details = castDetails; // Assign the castDetails to cast_details
      console.log("Cast details are", cast_details);

      return getPosters(SimilarMovies); // Return the Promise from getPosters
    })
    .then((pors) => {
      posters = pors;
      console.log("Posters are", posters);
      console.log("Movie poster:", movie_details.poster);
      // All asynchronous operations have completed here
      let details = {
        title: title,
        cast_ids: JSON.stringify(cast.cast_ids),
        cast_names: JSON.stringify(cast.cast_names),
        cast_chars: JSON.stringify(cast.cast_chars),
        cast_profiles: JSON.stringify(cast.cast_profiles),
        cast_bdays: JSON.stringify(cast_details.cast_bdays),
        cast_bios: JSON.stringify(cast_details.cast_bios),
        cast_places: JSON.stringify(cast_details.cast_places),
        imdb_id: movie_details["imdb_id"],
        poster: movie_details["poster"],
        rating: movie_details["rating"],
        release_date: movie_details["release_date"],
        runtime: movie_details["runtime"],
        overview: movie_details["overview"],
        recommended_movies: JSON.stringify(SimilarMovies),
        genres: JSON.stringify(movie_details["genre"]),
        posters: JSON.stringify(posters),
      };

      $.ajax({
        type: "POST",
        data: details,
        url: "/recommend",
        dataType: "html",
        complete: function () {
          $("#loader").delay(500).fadeOut();
        },
        success: function (response) {
          $(".results").html(response);
          $("#input-box").val("");
          $(window).scrollTop(0);
        },
      });
    })
    .catch((error) => {
      console.error(
        "Error in getMovieId, getMovieDetailsById, getSimilarMovies, getCastes, getCastDetails, or getPosters:",
        error
      );
    });
}

function searchMovie() {
  console.log("Search for movie started");
  let title = inputBox.value;
  console.log("title", title);
  // if title not in films_title

  if (title == "" || title == null || !films_title.includes(title)) {
    alert("Movie not found in our database");
  } else {
    console.log("Movie found in our database", title);
    MovieDetails(title);
  }
}

function recommendcard(e) {
  var title = e.getAttribute("title");
  console.log("clicked movie title", title);
  MovieDetails(title);
}
