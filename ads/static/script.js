// JavaScript

let profilePic = document.querySelector(".card img"); // Selecting the image element within the card
let inputFile = document.getElementById("input-file"); // Getting the file input element by its ID

inputFile.onchange = function () {
  profilePic.src = URL.createObjectURL(inputFile.files[0]); // Changing the source of the image to the selected file
  // TODO: send the image to the model. This will be simple and we will work on this as a team
};
