// Function to show popup
let popupShow = document.querySelector(".delete-icon");
// Function to toggle the class 'hidden' on popup div
function toggleShowClass() {
  const popup = document.querySelector(".delete-user-confirm");
  console.log(popup);
  popup.classList.toggle("popup-hidden");
}
// Add event listener to the delete icon
popupShow.addEventListener("click", toggleShowClass);

// Function to hide popup
let popupHide = document.querySelector(".cancel-button");
// Function to toggle the class 'hidden' on popup div
function toggleHideClass() {
  const popup = document.querySelector(".delete-user-confirm");
  console.log(popup);
  popup.classList.toggle("popup-hidden");
}
// Add event listener to the delete icon
popupHide.addEventListener("click", toggleHideClass);
