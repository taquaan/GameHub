// Get all open popup buttons
let openPopupButtons = document.querySelectorAll(".delete-icon");

// Get all popups
let popups = document.querySelectorAll(".delete-user-confirm");


// Add event listener to each open popup button
openPopupButtons.forEach(function (button, index) {
  button.addEventListener("click", function () {
    // Check if the corresponding popup exists
    if (popups[index]) {
      // Toggle the "popup-hidden" of the correspond popup
      popups[index].classList.toggle("popup-hidden");
    }
  });
});

// Get all close popup buttons
const closePopupButtons = document.querySelectorAll(".cancel-button");

// Add event listener to each close popup
closePopupButtons.forEach(function (button) {
  button.addEventListener("click", function () {
    const popup = button.closest(".delete-user-confirm");
    popup.classList.toggle("popup-hidden");
  });
});