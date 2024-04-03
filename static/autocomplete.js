let films_title = [];

function MoviesTitle() {
  $.ajax({
    url: "/titles",
    type: "GET",
    contentType: "application/json",
    success: function (response) {
      films_title = response;

      // Attach event listener after updating films_title array
      inputBox.onkeyup = function () {
        let result = [];
        let input = inputBox.value;

        if (input.length > 0) {
          result = films_title.filter((title) => {
            return title.toLowerCase().includes(input.toLowerCase());
          });
          displayResult(result);
        }
        if (!result.length) {
          resultBox.innerHTML = "";
        }
      };
    },
    error: function (error) {
      console.log(error);
    },
  });
}

const resultBox = document.querySelector(".result-box");
const inputBox = document.getElementById("input-box");

// inputBox.onkeyup = function () {
//   let result = [];
//   let input = inputBox.value;

//   if (input.length > 0) {
//     result = films_title.filter((title) => {
//       return title.toLowerCase().includes(input.toLowerCase());
//     });
//     displayResult(result);
//   }
//   if (!result.length) {
//     resultBox.innerHTML = "";
//   }
// };

function displayResult(result) {
  const content = result.map((item) => {
    return `<li onclick=selectItem(this)>${item}</li>`;
  });
  resultBox.innerHTML = `<ul>${content.join("")}</ul>`;
}

function selectItem(element) {
  console.log("selected item", element.innerHTML);
  inputBox.value = element.innerHTML;
  resultBox.innerHTML = "";
}

// Get Movies title
MoviesTitle();
